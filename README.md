# BlueTeam Hardener — Otomatik Linux Sıkılaştırma Aracı

## Proje Tanımı

BlueTeam Hardener, **Kali Linux** üzerinde çalışan ve **SSH üzerinden uzak Linux makineleri (Metasploitable2 vb.) otomatik olarak sıkılaştıran** web tabanlı bir sistemdir.

### Temel Özellikler:
- 🔍 **6 Modül**: Güvenlik açıklarını tespit ve düzelt
- 🖥️ **Terminal Tema Arayüzü**: Linux-focused, basit ve anlaşılır
- 🔐 **SSH Bağlantı**: Paramiko üzerinden uzak makine komutlarını çalıştır
- 🎯 **OS Tespit**: Otomatik olarak işletim sistemini algıla
- 📊 **Real-time Output**: SSE (Server-Sent Events) ile canlı çıktı akışı

---

## Modüller

### Mod 01 — Parola Olmayan Kullanıcılar
- **Risk**: YÜKSEK
- **Scan**: `/etc/shadow` dosyasında boş parolalı hesapları bulur
- **Fix**: Bu hesapları kilitler (`passwd -l`)

### Mod 02 — SSH Sıkılaştırma
- **Risk**: YÜKSEK
- **Scan**: `sshd_config` ayarlarını kontrol eder (PermitRootLogin, PermitEmptyPasswords, vb.)
- **Fix**: Güvenli SSH ayarlarını uygulanır

### Mod 03 — Herkese Yazılabilir Dosyalar
- **Risk**: ORTA
- **Scan**: World-writable (`o+w`) dosyaları ve dizinleri bulur
- **Fix**: İzinleri düzeltir ve sticky bit ekler

### Mod 04 — SUID/SGID Denetimi
- **Risk**: YÜKSEK
- **Scan**: SUID/SGID bitli tehlikeli dosyaları listeler
- **Fix**: Gereksiz SUID bitlerini kaldırır

### Mod 05 — Açık Port Envanteri
- **Risk**: ORTA
- **Scan**: Dinleyen TCP/UDP portlarını ve servislerini listeler
- **Fix**: Gereksiz servisleri kapatır

### Mod 06 — Sistem Log Analizi
- **Risk**: BİLGİ
- **Scan**: Auth loglarında başarısız girişleri, sudo kullanımını tarar
- **Fix**: Yalnızca tarama modu (log değiştirilmez)

---

## Kurulum & Çalıştırma

### Gereksinimler:
- **Kali Linux** (veya Ubuntu)
- **Python 3.7+**
- **pip3**
- **Hedef makineye SSH erişimi** (msfadmin:msfadmin gibi)

### Adımlar:

```bash
# 1. Projeyi klonla
git clone https://github.com/benmevic/hardeningtool.git
cd hardeningtool

# 2. Bağımlılıkları kur
pip3 install -r requirements.txt

# 3. Sunucuyu başlat
chmod +x run.sh
./run.sh

# 4. Tarayıcıda aç
# http://localhost:5000
```

---

## Proje Yapısı

```
hardeningtool/
├── app.py                           # Flask ana uygulaması
├── controller.py                    # SSH controller (ServerNode)
├── requirements.txt                 # Python bağımlılıkları
├── run.sh                           # Başlangıç scripti
├── modules/
│   ├── __init__.py
│   ├── module_registry.py           # Modül tanımları (metadata + komutlar)
│   └── os_strategies.py             # OS tespit stratejileri
├── core_scripts/
│   └── global_os_detect.sh          # OS detection bash scripti
├── templates/
│   └── index.html                   # Web arayüzü (terminal tema)
├── moduls/                          # Bash scriptleri (OS-specific)
│   ├── metasploitable2/
│   ├── ubuntu/
│   ├── rhel_centos/
│   ├── fedora/
│   └── arch/
└── README.md                        # Bu dosya
```

---

## Kullanım

### 1. Hedef Bağlantısı
Sağ üst köşede:
- **TARGET**: Hedef makinenin IP'si (Metasploitable2)
- **USER**: SSH kullanıcı adı
- **PASS**: SSH şifresi
- **[TEST-CONN]**: Bağlantıyı test et

### 2. Modül Seçimi
Sol panelden bir modül seçin.

### 3. Tarama veya Düzeltme
- **[SCAN]**: Değişiklik yapmadan sorunu raporla
- **[FIX]**: Otomatik olarak düzelt

---

## Mimari

```
Kali Machine (Flask Server)
    ↓
    ├── controller.py → SSH bağlantı (Paramiko)
    │   └── ServerNode.detect_os() → global_os_detect.sh çalıştır
    │
    ├── app.py → /api/run/<module_id>
    │   └── module_registry.py → Komut tanımları
    │
    └── templates/index.html → Terminal tema UI
         └── Real-time SSE output stream
           ↓
      Metasploitable2 (Hedef)
          ↓
      SSH üzerinden remote komutlar çalıştır
```

---

## Planlanan Özellikler (Future)

- [ ] **Kullanıcı Script Ekleme**: Dashboard'da custom bash scriptleri ekle
- [ ] **Veritabanı**: Kullanıcı scriptlerini ve geçmişi kaydet
- [ ] **Script Validasyon**: Tehlikeli komutları filtreleme
- [ ] **Execution History**: Kim, ne, kaç dakika öncesini göster
- [ ] **Script Sandboxing**: Timeout ve resource limits

---

## Güvenlik Notları

⚠️ **Bu araç SADECE test ortamlarında (Metasploitable2 gibi) kullanılır.**

- Production sistemlerde önce SCAN modunda test edin
- FIX modunu çalıştırmadan sistemin yedeğini alın
- SSH kimlik bilgilerini safe bir yerde saklayın

---

## Katkı

Bug report'lar ve feature request'ler için issue aç veya PR gönder.

---

## Lisans

MIT License
