"""
Controller — ServerNode sınıfı
SSH bağlantısı kurar, global_os_detect.sh çalıştırır,
OS'e göre doğru stratejiyi atar.
"""

import paramiko
import queue
import threading
import time
import os

from modules.os_strategies import get_strategy_by_name

# global_os_detect.sh'ın proje içindeki yolu
DETECT_SCRIPT_PATH = os.path.join(
    os.path.dirname(os.path.abspath(__file__)),
    "core_scripts", "global_os_detect.sh"
)


class ServerNode:
    """Hedef sunucu — bağlantı, OS tespiti ve modül çalıştırma."""

    def __init__(self, config: dict):
        self.ip       = config["host"]
        self.port     = int(config.get("port", 22))
        self.username = config["username"]
        self.password = config["password"]
        self.timeout  = config.get("timeout", 10)
        self.os_strategy = None   # detect_os() çağrılana kadar None
        self._client  = None

    # ── SSH ──────────────────────────────────────────────────────────

    def connect(self):
        """Paramiko SSH bağlantısı kur."""
        self._client = paramiko.SSHClient()
        self._client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        self._client.connect(
            hostname=self.ip,
            port=self.port,
            username=self.username,
            password=self.password,
            timeout=self.timeout
        )

    def close(self):
        if self._client:
            self._client.close()
            self._client = None

    def run_command_raw(self, command: str) -> str:
        """Komutu çalıştır, stdout'u string olarak döndür."""
        _, stdout, _ = self._client.exec_command(command)
        return stdout.read().decode("utf-8", errors="replace")

    # ── OS Tespiti ───────────────────────────────────────────────────

    def detect_os(self) -> str:
        """
        global_os_detect.sh içeriğini oku, hedefe pipe ile çalıştır.
        DETECTED_OS=xxx satırını parse edip stratejiyi ata.
        Tespit edilen os_name string'ini döndürür.
        """
        # Script dosyasını oku
        try:
            with open(DETECT_SCRIPT_PATH, "r") as f:
                script_content = f.read()
        except FileNotFoundError:
            # Script yoksa fallback: /etc/os-release'e bak
            script_content = (
                "if [ -f /etc/os-release ]; then source /etc/os-release; "
                "ID_LOW=$(echo $ID | tr '[:upper:]' '[:lower:]'); "
                "VER=$VERSION_ID; "
                "if [[ \"$ID_LOW\" == 'ubuntu' && \"$VER\" == '8.04' ]]; then "
                "echo DETECTED_OS=metasploitable2; "
                "elif [[ \"$ID_LOW\" == 'ubuntu' || \"$ID_LOW\" == 'debian' || \"$ID_LOW\" == 'kali' ]]; then "
                "echo DETECTED_OS=ubuntu; "
                "else echo DETECTED_OS=unknown; fi; "
                "else echo DETECTED_OS=unknown; fi"
            )

        # Bash -s ile stdin'den çalıştır
        transport = self._client.get_transport()
        channel = transport.open_session()
        channel.get_pty()
        channel.exec_command("bash -s")
        channel.sendall(script_content.encode() + b"\nexit\n")

        output = ""
        while True:
            if channel.recv_ready():
                output += channel.recv(4096).decode("utf-8", errors="replace")
            if channel.exit_status_ready():
                break
            time.sleep(0.05)

        # DETECTED_OS=xxx satırını parse et
        detected = "unknown"
        for line in output.splitlines():
            line = line.strip()
            if line.startswith("DETECTED_OS="):
                detected = line.split("=", 1)[1].strip()
                break

        self.os_strategy = get_strategy_by_name(detected)
        return detected

    # ── Stream Komut ─────────────────────────────────────────────────

    def stream_command(self, command: str, output_queue: queue.Queue):
        """Komutu çalıştır, çıktıyı satır satır kuyruğa at."""
        try:
            transport = self._client.get_transport()
            channel = transport.open_session()
            channel.get_pty()
            channel.exec_command(command)

            while True:
                if channel.recv_ready():
                    data = channel.recv(4096).decode("utf-8", errors="replace")
                    output_queue.put({"type": "stdout", "data": data})
                if channel.recv_stderr_ready():
                    data = channel.recv_stderr(4096).decode("utf-8", errors="replace")
                    output_queue.put({"type": "stderr", "data": data})
                if channel.exit_status_ready():
                    output_queue.put({"type": "exit", "code": channel.recv_exit_status()})
                    break
                time.sleep(0.05)
        except Exception as e:
            output_queue.put({"type": "error", "data": str(e)})
            output_queue.put({"type": "exit", "code": -1})
        finally:
            output_queue.put(None)  # Sentinel
