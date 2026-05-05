"""
OS Strateji Sınıfları
Her işletim sistemi için ilgili modül klasörünü tanımlar.
global_os_detect.sh çıktısıyla birebir eşleşir.
"""

import os


class OSHardeningStrategy:
    """Tüm işletim sistemleri için temel (Base) Sınıf."""
    os_name = "unknown"

    def get_module_path(self, module_name: str) -> str:
        """
        'moduls' klasörü içindeki ilgili bash dosyasının yolunu döndürür.
        Örn: ../moduls/metasploitable2/ssh_harden.sh
        """
        base = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        return os.path.join(base, "moduls", self.os_name, f"{module_name}.sh")


class UbuntuStrategy(OSHardeningStrategy):
    os_name = "ubuntu"

class RhelCentosStrategy(OSHardeningStrategy):
    os_name = "rhel_centos"

class FedoraStrategy(OSHardeningStrategy):
    os_name = "fedora"

class ArchStrategy(OSHardeningStrategy):
    os_name = "arch"

class MetasploitableStrategy(OSHardeningStrategy):
    os_name = "metasploitable2"


def get_strategy_by_name(os_string: str) -> OSHardeningStrategy:
    """Bash scriptinden gelen string'e göre doğru strateji sınıfını döndürür."""
    strategies = {
        "ubuntu":         UbuntuStrategy(),
        "rhel_centos":    RhelCentosStrategy(),
        "fedora":         FedoraStrategy(),
        "arch":           ArchStrategy(),
        "metasploitable2": MetasploitableStrategy(),
    }
    return strategies.get(os_string, None)
