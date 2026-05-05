"""
BlueTeam Hardener - Ana Flask Uygulaması
Kali üzerinde çalışır, Metasploitable2'ye SSH ile bağlanır.
"""

from flask import Flask, render_template, request, jsonify, Response
import threading
import queue
import json

from modules.module_registry import MODULE_REGISTRY
from controller import ServerNode   # ← Takım arkadaşının controller'ı

app = Flask(__name__)

DEFAULT_CONFIG = {
    "host":     "192.168.1.100",
    "port":     22,
    "username": "msfadmin",
    "password": "msfadmin",
    "timeout":  10
}


# ─── ROUTES ────────────────────────────────────────────────────────────────────

@app.route("/")
def index():
    return render_template("index.html", modules=MODULE_REGISTRY)


@app.route("/api/test-connection", methods=["POST"])
def test_connection():
    body = request.json or {}
    config = body.get("config", body) or {}
    for k, v in DEFAULT_CONFIG.items():
        config.setdefault(k, v)
    try:
        node = ServerNode(config)
        node.connect()
        output = node.run_command_raw("uname -a && whoami").strip()
        node.close()
        return jsonify({"success": True, "output": output})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)})


@app.route("/api/run/<module_id>", methods=["POST"])
def run_module(module_id):
    """Modülü çalıştır — OS tespiti otomatik yapılır."""
    module = next((m for m in MODULE_REGISTRY if m["id"] == module_id), None)
    if not module:
        return jsonify({"error": "Modül bulunamadı"}), 404

    body = request.json or {}
    config = body.get("config", {}) or {}
    for k, v in DEFAULT_CONFIG.items():
        config.setdefault(k, v)
    mode = body.get("mode", "scan")

    def generate():
        node = None
        try:
            # 1. SSH Bağlantısı
            yield f"data: {json.dumps({'type': 'status', 'data': 'SSH bağlantısı kuruluyor...'})}

            "
            node = ServerNode(config)
            node.connect()
            yield f"data: {json.dumps({'type': 'status', 'data': 'Bağlantı başarılı.'})}

            "

            # 2. OS Tespiti
            yield f"data: {json.dumps({'type': 'step', 'data': 'İşletim sistemi tespit ediliyor...'})}

            "
            detected = node.detect_os()
            os_label = node.os_strategy.os_name if node.os_strategy else "unknown"
            yield f"data: {json.dumps({'type': 'stdout', 'data': f'[OS-DETECT] DETECTED_OS={detected}  →  Strateji: {os_label}'})}

            "

            if detected == "unknown" or not node.os_strategy:
                yield f"data: {json.dumps({'type': 'stderr', 'data': '[UYARI] OS tespit edilemedi, modül yine de çalıştırılıyor...'})}

            "

            # 3. Modül Komutları
            commands = module.get(f"commands_{mode}", module.get("commands_scan", []))

            for cmd_info in commands:
                label   = cmd_info.get("label", "Komut çalıştırılıyor")
                command = cmd_info["cmd"]

                yield f"data: {json.dumps({'type': 'step', 'data': label})}

            "
                yield f"data: {json.dumps({'type': 'cmd',  'data': f'$ {command}'})}

            "

                q = queue.Queue()
                t = threading.Thread(target=node.stream_command, args=(command, q))
                t.start()

                while True:
                    item = q.get()
                    if item is None:
                        break
                    yield f"data: {json.dumps(item)}

            "

                t.join()

            node.close()
            yield f"data: {json.dumps({'type': 'done', 'data': 'Modül tamamlandı.'})}

            "

        except Exception as e:
            if node:
                node.close()
            yield f"data: {json.dumps({'type': 'error', 'data': str(e)})}

            "
            yield f"data: {json.dumps({'type': 'done',  'data': 'Hata ile sonlandı.'})}

            "

    return Response(generate(), mimetype="text/event-stream",
                    headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"})


@app.route("/api/modules")
def list_modules():
    return jsonify(MODULE_REGISTRY)


if __name__ == "__main__":
    print("\n[*] BlueTeam Hardener başlatılıyor...")
    print("[*] Arayüz: http://localhost:5000")
    print("[*] Hedef varsayılan IP:", DEFAULT_CONFIG["host"])
    print("[!] Metasploitable2 IP'sini arayüzden değiştirebilirsiniz.\n")
    app.run(host="0.0.0.0", port=5000, debug=True, threaded=True)
