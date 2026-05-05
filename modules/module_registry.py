"""
Modül Kayıt Defteri
Her modül: id, başlık, açıklama, kategori, risk seviyesi,
scan komutları ve fix komutları içerir.
"""

MODULE_REGISTRY = [
    {
        "id": "mod_01_empty_passwords",
        "title": "Modul 01 — Parola Olmayan Kullanıcılar",
        "short": "Parolasız hesapları tespit eder ve kilitler.",
        "description": (
            "Sistemdeki tüm kullanıcı hesaplarını tarar. "
            "/etc/shadow dosyasını analiz ederek boş parola alanına sahip "
            "hesapları tespit eder. Fix modunda bu hesapların parolalarını "
            "kilitleyerek ('!') oturum açmayı engeller."
        ),
        "category": "Kimlik Doğrulama",
        "risk": "YÜKSEK",
        "risk_color": "high",
        "commands_scan": [
            {
                "label": "Shadow dosyası okunuyor...",
                "cmd": "sudo awk -F: '($2==\"\" || $2==\"!!\") {print \"[BOŞPAROLA] \" $1}' /etc/shadow"
            },
            {
                "label": "Tüm kullanıcı listesi alınıyor...",
                "cmd": "cut -d: -f1,3 /etc/passwd | awk -F: '$2>=1000 {print \"[KULLANICI] \" $1}'"
            }
        ],
        "commands_fix": [
            {
                "label": "Parolasız hesaplar tespit ediliyor...",
                "cmd": "sudo awk -F: '($2==\"\") {print $1}' /etc/shadow"
            },
            {
                "label": "Boş parolalı hesaplar kilitleniyor...",
                "cmd": (
                    "for user in $(sudo awk -F: '($2==\"\") {print $1}' /etc/shadow); do "
                    "sudo passwd -l $user && echo \"[KILITLEDI] $user\"; "
                    "done; echo '[TAMAM] İşlem tamamlandi'"
                )
            },
            {
                "label": "Sonuç doğrulanıyor...",
                "cmd": "sudo awk -F: '($2==\"\" || $2==\"!!\") {print \"[UYARI] Hâlâ açık: \" $1}' /etc/shadow || echo '[OK] Tüm hesaplar güvende'"
            }
        ]
    },
    {
        "id": "mod_02_ssh_hardening",
        "title": "Modul 02 — SSH Sıkılaştırma",
        "short": "Güvensiz SSH ayarlarını tespit eder ve düzeltir.",
        "description": (
            "sshd_config dosyasını analiz eder. Root girişi, boş parola ile "
            "giriş, protokol versiyonu ve port gibi kritik SSH parametrelerini "
            "denetler. Fix modunda güvenli değerler yazar ve SSH servisini yeniden başlatır."
        ),
        "category": "Ağ Güvenliği",
        "risk": "YÜKSEK",
        "risk_color": "high",
        "commands_scan": [
            {
                "label": "SSH konfigürasyonu okunuyor...",
                "cmd": "sudo cat /etc/ssh/sshd_config | grep -E 'PermitRootLogin|PermitEmptyPasswords|Protocol|Port|PasswordAuthentication'"
            },
            {
                "label": "Mevcut SSH bağlantıları listeleniyor...",
                "cmd": "netstat -tnlp 2>/dev/null | grep :22 || ss -tnlp | grep :22"
            }
        ],
        "commands_fix": [
            {
                "label": "Mevcut SSH ayarları yedekleniyor...",
                "cmd": "sudo cp /etc/ssh/sshd_config /etc/ssh/sshd_config.bak.$(date +%Y%m%d) && echo '[YEDEK] sshd_config yedeklendi'"
            },
            {
                "label": "Root girişi devre dışı bırakılıyor...",
                "cmd": "sudo sed -i 's/^PermitRootLogin.*/PermitRootLogin no/' /etc/ssh/sshd_config && echo '[OK] PermitRootLogin no'"
            },
            {
                "label": "Boş parola ile giriş engelleniyor...",
                "cmd": "sudo sed -i 's/^PermitEmptyPasswords.*/PermitEmptyPasswords no/' /etc/ssh/sshd_config && echo '[OK] PermitEmptyPasswords no'"
            },
            {
                "label": "Protokol 2 zorunlu kılınıyor...",
                "cmd": "grep -q '^Protocol' /etc/ssh/sshd_config && sudo sed -i 's/^Protocol.*/Protocol 2/' /etc/ssh/sshd_config || echo 'Protocol 2' | sudo tee -a /etc/ssh/sshd_config; echo '[OK] Protocol 2'"
            },
            {
                "label": "SSH servisi yeniden başlatılıyor...",
                "cmd": "sudo service ssh restart && echo '[OK] SSH servisi yeniden başlatıldı'"
            }
        ]
    },
    {
        "id": "mod_03_world_writable",
        "title": "Modul 03 — Herkese Yazılabilir Dosyalar",
        "short": "World-writable dosya ve dizinleri bulur, izinleri düzeltir.",
        "description": (
            "Tüm sistemde world-writable (o+w) izinli dosyaları ve dizinleri arar. "
            "Bu tür izinler saldırganlara dosya manipülasyon imkânı verir. "
            "Fix modunda sticky bit eklenir veya yazma izni kaldırılır."
        ),
        "category": "Dosya Sistemi",
        "risk": "ORTA",
        "risk_color": "medium",
        "commands_scan": [
            {
                "label": "World-writable dosyalar taranıyor...",
                "cmd": "find / -xdev -type f -perm -0002 2>/dev/null | head -30 | while read f; do echo \"[WRITABLE] $f\"; done"
            },
            {
                "label": "World-writable dizinler taranıyor...",
                "cmd": "find / -xdev -type d -perm -0002 2>/dev/null | head -20 | while read d; do echo \"[WRITABLE-DIR] $d\"; done"
            }
        ],
        "commands_fix": [
            {
                "label": "Sisteme ait world-writable dosyaların izni düzeltiliyor...",
                "cmd": "find /etc /usr /bin /sbin -xdev -type f -perm -0002 2>/dev/null | while read f; do sudo chmod o-w \"$f\" && echo \"[DUZELTILDI] $f\"; done; echo '[TAMAM] Sistem dizinleri tarandı'"
            },
            {
                "label": "World-writable dizinlere sticky bit ekleniyor...",
                "cmd": "find /tmp /var/tmp -xdev -type d -perm -0002 ! -perm -1000 2>/dev/null | while read d; do sudo chmod +t \"$d\" && echo \"[STICKY] $d\"; done; echo '[TAMAM] Geçici dizinler güvende'"
            }
        ]
    },
    {
        "id": "mod_04_suid_audit",
        "title": "Modul 04 — SUID/SGID Denetimi",
        "short": "Anormal SUID/SGID bitli dosyaları tespit eder.",
        "description": (
            "SUID/SGID bitli dosyalar root yetki yükseltme vektörü olabilir. "
            "Bu modül tüm sistemdeki SUID/SGID dosyaları listeler ve bilinen "
            "tehlikeli dosyaları (nmap, vim, python, perl vb.) işaretler. "
            "Fix modunda gereksiz olanların SUID biti kaldırılır."
        ),
        "category": "Ayrıcalık Yönetimi",
        "risk": "YÜKSEK",
        "risk_color": "high",
        "commands_scan": [
            {
                "label": "SUID bitli dosyalar taranıyor...",
                "cmd": "find / -xdev -type f \\( -perm -4000 -o -perm -2000 \\) 2>/dev/null | while read f; do echo \"[SUID/SGID] $f\"; done"
            },
            {
                "label": "Tehlikeli SUID dosyaları kontrol ediliyor...",
                "cmd": "for bin in nmap vim python perl ruby bash sh find wget curl; do path=$(which $bin 2>/dev/null); [ -n \"$path\" ] && stat -c '%A %n' $path 2>/dev/null | grep -E '^-..s' && echo \"[TEHLİKELİ-SUID] $path\"; done; echo '[TARAMA-BITTI]'"
            }
        ],
        "commands_fix": [
            {
                "label": "Tehlikeli araçlardan SUID biti kaldırılıyor...",
                "cmd": "for bin in nmap vim python python3 perl ruby find wget curl; do path=$(which $bin 2>/dev/null); if [ -n \"$path\" ] && [ -u \"$path\" ]; then sudo chmod u-s \"$path\" && echo \"[KALDIRILDI] $path SUID biti kaldırıldı\"; fi; done; echo '[TAMAM] Tehlikeli SUID bitleri temizlendi'"
            }
        ]
    },
    {
        "id": "mod_05_open_ports",
        "title": "Modul 05 — Açık Port Envanteri",
        "short": "Dinleyen servisleri ve gereksiz açık portları listeler.",
        "description": (
            "Sistemde dinleyen tüm TCP/UDP portları ve servislerini listeler. "
            "Metasploitable2 üzerinde çok sayıda gereksiz servis çalışmaktadır. "
            "Bu modül bir envanter çıkarır; hangi servislerin kapatılması "
            "gerektiğini raporlar."
        ),
        "category": "Ağ Güvenliği",
        "risk": "ORTA",
        "risk_color": "medium",
        "commands_scan": [
            {
                "label": "Açık portlar listeleniyor...",
                "cmd": "netstat -tulnp 2>/dev/null || ss -tulnp"
            },
            {
                "label": "Çalışan servisler kontrol ediliyor...",
                "cmd": "ps aux | grep -E 'telnet|ftp|rsh|rlogin|finger|rexec' | grep -v grep | while read line; do echo \"[TEHLİKELİ-SERVİS] $line\"; done; echo '[TARAMA-BITTI]'"
            },
            {
                "label": "İnetd servisleri kontrol ediliyor...",
                "cmd": "[ -f /etc/inetd.conf ] && grep -v '^#' /etc/inetd.conf | grep -v '^$' | while read line; do echo \"[INETD] $line\"; done || echo '[INFO] inetd.conf bulunamadı'"
            }
        ],
        "commands_fix": [
            {
                "label": "Telnet servisi devre dışı bırakılıyor...",
                "cmd": "sudo update-rc.d telnet disable 2>/dev/null || sudo systemctl disable telnet 2>/dev/null; sudo service openbsd-inetd stop 2>/dev/null; echo '[OK] Telnet/inetd durduruldu'"
            }
        ]
    },
    {
        "id": "mod_06_log_check",
        "title": "Modul 06 — Sistem Log Analizi",
        "short": "Auth loglarında şüpheli giriş denemelerini arar.",
        "description": (
            "auth.log ve syslog dosyalarını analiz eder. Başarısız SSH giriş "
            "denemelerini, sudo kullanımını ve kritik sistem mesajlarını listeler. "
            "Bu modül sadece scan modunda çalışır — log dosyaları değiştirilmez."
        ),
        "category": "İzleme",
        "risk": "BİLGİ",
        "risk_color": "info",
        "commands_scan": [
            {
                "label": "Başarısız giriş denemeleri aranıyor...",
                "cmd": "sudo grep 'Failed password' /var/log/auth.log 2>/dev/null | tail -20 | while read line; do echo \"[BAŞARISIZ-GİRİŞ] $line\"; done || echo '[INFO] auth.log erişilemiyor'"
            },
            {
                "label": "Başarılı root girişleri kontrol ediliyor...",
                "cmd": "sudo grep 'Accepted.*root' /var/log/auth.log 2>/dev/null | tail -10 | while read line; do echo \"[ROOT-GİRİŞ] $line\"; done || echo '[INFO] Root girişi kaydı yok'"
            },
            {
                "label": "Sudo kullanımı kontrol ediliyor...",
                "cmd": "sudo grep 'sudo' /var/log/auth.log 2>/dev/null | tail -15 | while read line; do echo \"[SUDO] $line\"; done || echo '[INFO] Sudo kaydı yok'"
            }
        ],
        "commands_fix": [
            {
                "label": "Bu modül yalnızca tarama yapar.",
                "cmd": "echo '[INFO] Log analizi sadece okuma modunda çalışır. Fix gerekli değil.'"
            }
        ]
    }
]
