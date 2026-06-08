# 🌐 NetProbe: UDP Tabanlı Güvenilir Dosya Aktarımı ve Ağ Performans Analiz Platformu

> **BLM0326 – Bilgisayar Ağları Dönem Projesi | Bursa Teknik Üniversitesi**

[![Python](https://img.shields.io/badge/Python-3.8%2B-blue?logo=python)](https://www.python.org/)
[![License](https://img.shields.io/badge/License-MIT-green)](LICENSE)
[![Protocol](https://img.shields.io/badge/Protocol-UDP%20%2B%20Stop--and--Wait-orange)]()
[![Status](https://img.shields.io/badge/Status-Tamamlandı-brightgreen)]()

---

## 👥 Grup Üyeleri

| Öğrenci No | Ad Soyad | Sorumluluk |
|---|---|---|
| 22360859070 | Rumeysa Ersoy | Çekirdek ağ altyapısı, Stop-and-Wait protokolü, ACK/Checksum mekanizmaları |
| 23360859057 | Elif Kara | Ağ trafiği loglama (CSV), paket kaybı simülasyonu (LOSS_RATE) |
| 23360859726 | Selenay Bulut | Performans analizi, Throughput/Goodput hesabı, veri görselleştirme |

---

## 📖 Proje Hakkında

**NetProbe**, UDP protokolü üzerine inşa edilmiş güvenilir bir dosya aktarım sistemi ve ağ performans analiz platformudur. UDP'nin doğasındaki güvensizlik sorunları (paket kaybı, sıra bozulması, veri bozulması) **uygulama katmanında** aşağıdaki mekanizmalarla çözüme kavuşturulmuştur:

- 📦 **Stop-and-Wait ARQ** protokolü ile güvenilir sıralı iletim
- 🔢 **Sequence Number** ile paket sıralama ve çift yazma tespiti
- ✅ **ACK (Onay)** mekanizması ile teslimat doğrulama
- 🔐 **SHA-256 Checksum** ile veri bütünlüğü kontrolü
- 📝 **Base64 kodlaması** ile binary/JSON uyumu
- 📊 **CSV loglama** ve **Throughput/Goodput analizi** ile ağ performansı ölçümü

### Ölçülen Performans Sonuçları

| Metrik | Değer |
|---|---|
| **Throughput** | 3337,23 Kbps |
| **Goodput** | 3188,00 Kbps |
| **Overhead** | ~149,23 Kbps |
| **Protokol Verimliliği (η)** | %95,53 |

> Testler %20 paket kaybı (LOSS_RATE) simülasyonu altında `localhost` ortamında gerçekleştirilmiştir.

---

## 🗂️ Dizin Yapısı

```
netprobe/
├── protocol/
│   └── packet.py          # Paket serileştirme, ACK, Checksum, Base64 kodlaması
├── client/
│   └── client.py          # UDP gönderici, Stop-and-Wait döngüsü, yeniden iletim
├── server/
│   └── server.py          # UDP alıcı, LOSS_RATE simülasyonu, CSV loglama
├── analysis/
│   └── analyzer.py        # Throughput/Goodput hesabı, matplotlib grafik üretimi
├── logs/
│   └── transfer_log.csv   # Zaman damgalı paket olay kayıtları (otomatik oluşur)
├── client/test_files/
│   └── test.txt           # Transfer edilecek örnek dosya
├── server/
│   └── received.txt       # Alınan dosyanın kaydedileceği konum
├── main.py                # Orkestratör – tüm modülleri koordine eder
└── README.md
```

---

## ⚙️ Gereksinimler

- Python **3.8** veya üzeri
- `matplotlib` (grafik üretimi için)

```bash
pip install matplotlib
```

---

## 🚀 Kurulum ve Çalıştırma

### 1. Repoyu Klonlayın

```bash
git clone https://github.com/kullanici_adi/netprobe.git
cd netprobe
```

### 2. Bağımlılıkları Yükleyin

```bash
pip install -r requirements.txt
```

### 3. `main.py` ile Çalıştırın (Önerilen)

```bash
python main.py
```

Açılan menüden istediğiniz modu seçin:

```
================================================
  NETPROBE: UDP GÜVENİLİR DOSYA AKTARIM SİSTEMİ
================================================
1. Sadece Sunucuyu (Server) Başlat
2. Sadece İstemciyi (Client) Başlat
3. Performans Analizini (Grafik) Çalıştır
4. TAM SİMÜLASYON (Server -> Client -> Analiz)
0. Çıkış
================================================
```

### 4. Manuel Çalıştırma (İki Terminal)

**Terminal 1 – Sunucuyu başlatın:**
```bash
python -m server.server
```

**Terminal 2 – İstemciyi başlatın:**
```bash
python -m client.client
```

**Terminal 3 – Analizi çalıştırın:**
```bash
python -m analysis.analyzer
```

---

## 🔬 Protokol Mimarisi

### Stop-and-Wait ARQ

Gönderici her paketi gönderdikten sonra ACK almadan bir sonrakine geçmez. Zaman aşımında yeniden iletim başlar.

```
Gönderici                        Alıcı
    |                               |
    |------- [seq=0] DATA --------->|
    |<------ [seq=0] ACK -----------|
    |                               |
    |------- [seq=1] DATA --------->|
    |        (paket kayboldu)       |
    |  [TIMEOUT]                    |
    |------- [seq=1] DATA --------->|  ← Yeniden iletim
    |<------ [seq=1] ACK -----------|
    |                               |
```

**Verimlilik formülü:** `η = 1 / (1 + 2a)` — burada `a = Tp/Tt` (yayılma/iletim süresi oranı)

### Paket Yapısı (JSON Header)

Her UDP datagramı aşağıdaki JSON yapısıyla serileştirilir:

```json
{
  "seq_num": 0,
  "total_chunks": 10,
  "checksum": "sha256_hash_degeri",
  "data": "base64_kodlanmis_veri",
  "type": "DATA"
}
```

| Alan | Tür | Açıklama |
|---|---|---|
| `seq_num` | int | Paketin sıra numarası |
| `total_chunks` | int | Toplam parça sayısı |
| `checksum` | str | SHA-256 bütünlük karması |
| `data` | str | Base64 kodlanmış dosya içeriği |
| `type` | str | `"DATA"` veya `"ACK"` |

> **Neden Base64?** RFC 4648 — binary veri doğrudan JSON'a gömülemez; Base64 ile %33 boyut artışı karşılığında platform bağımsız ASCII temsil elde edilir.

---

## ⚙️ Yapılandırma Parametreleri

`protocol/packet.py` veya ilgili modüllerde aşağıdaki sabitler ayarlanabilir:

| Parametre | Varsayılan | Açıklama |
|---|---|---|
| `CHUNK_SIZE` | `1024` bayt | UDP parça boyutu — MTU (1500B) ile dengede |
| `TIMEOUT_VAL` | `1.0` saniye | ACK bekleme süresi (RTO) |
| `MAX_RETRIES` | `5` | Maksimum yeniden deneme sayısı |
| `LOSS_RATE` | `0.20` (% 20) | Sunucuda simüle edilen paket kaybı oranı |
| `HOST` | `127.0.0.1` | Hedef IP adresi |
| `PORT` | `5000` | UDP port numarası |

### Parametre Gerekçeleri

- **CHUNK_SIZE = 1024:** JSON header (~200B) + Base64 genişlemesi (%33) ile toplam paket ~1500B → Ethernet MTU sınırında, fragmentation yok.
- **TIMEOUT_VAL = 1.0s:** localhost RTT < 1ms olsa da disk I/O + CSV yazma gecikmesini absorbe etmek için 1s seçilmiştir.
- **MAX_RETRIES = 5:** %20 kayıp oranında 5 denemenin tamamının başarısız olma olasılığı = `0.20^5 = 0.00032` → ihmal edilebilir.

---

## 📊 Performans Analizi

Aktarım tamamlandıktan sonra analiz modülünü çalıştırın:

```bash
python -m analysis.analyzer
```

Bu komut:
1. `logs/transfer_log.csv` dosyasını ayrıştırır
2. **Throughput** ve **Goodput** değerlerini hesaplar
3. Karşılaştırmalı çubuk grafiği üretir

### Formüller

```
Throughput = (Toplam Gönderilen Bayt × 8) / Aktarım Süresi [bps]
Goodput    = (Başarıyla Alınan Net Bayt × 8) / Aktarım Süresi [bps]
η          = Goodput / Throughput   →   0 < η ≤ 1
```

### Log Formatı (`transfer_log.csv`)

```csv
timestamp,event_type,seq,size_bytes,status
1780644500.995,DATA_RCV,0,1454,NEW
1780644500.998,DATA_RCV,1,1454,NEW
1780698480.964,DATA_DROP,1,1454,DROPPED
1780698482.984,DATA_RCV,1,1454,NEW
```

---

## 🐛 Çözülen Teknik Sorunlar

### 1. Binary / JSON Uyumsuzluğu
**Sorun:** `open(file, "rb")` ile okunan `bytes` nesnesi doğrudan `json.dumps()` ile serileştirilemiyor → `TypeError`.

**Çözüm:** RFC 4648 Base64 kodlaması:
```python
# Gönderici
encoded = base64.b64encode(chunk).decode("ascii")

# Alıcı
decoded = base64.b64decode(encoded_str.encode("ascii"))
```

---

### 2. Kayıp ACK → Çift Yazma (Duplicate Write)
**Sorun:** ACK kaybolduğunda istemci aynı paketi yeniden gönderir, sunucu aynı veriyi iki kez diske yazar → dosya bozulur.

**Çözüm:** İdempotent alıcı — daha önce işlenmiş seq_num'ları dictionary ile takip etme:
```python
received_chunks = {}

if seq_num not in received_chunks:
    # Diske yaz
    received_chunks[seq_num] = True

# Her durumda ACK gönder
send_ack(seq_num)
```

---

### 3. Timeout Kalibrasyonu
**Sorun:** `TIMEOUT_VAL = 0.1s` — sunucunun disk I/O + CSV yazma süresi zaman zaman bu limiti aşıyor, gereksiz yeniden iletimler artıyor.

**Çözüm:** Sistematik ölçüm sonucunda `1.0s` olarak güncellendi.

---

## 🔬 Sistem Doğrulaması

Aktarım tamamlandıktan sonra SHA-256 hash karşılaştırmasıyla dosya bütünlüğü doğrulanabilir:

**Linux/macOS:**
```bash
sha256sum client/test_files/test.txt
sha256sum server/received.txt
# İki hash değeri eşit olmalıdır
```

**Windows (PowerShell):**
```powershell
Get-FileHash "client\test_files\test.txt"
Get-FileHash "server\received.txt"
# Hash değerleri eşleşmelidir
```

---

## 🔮 Gelecekte Yapılabilecek Geliştirmeler

| Geliştirme | Açıklama | Kazanım |
|---|---|---|
| **Sliding Window (Go-Back-N / Selective Repeat)** | W boyutlu pencereyle eş zamanlı çoklu paket iletimi | `η = W / (1 + 2a)` — throughput artışı |
| **Multi-threading** | Her istemci oturumu için ayrı iş parçacığı (`threading.Thread` / `asyncio`) | Eş zamanlı bağlantı desteği |
| **Adaptive RTO (RFC 6298)** | Karn/Jacobson algoritması: `RTO = SRTT + 4×RTTVAR` | Dinamik timeout optimizasyonu |
| **AES-256-GCM Şifreleme** | Uçtan uca veri gizliliği ve kimlik doğrulama | Üretim ortamı güvenliği |

---

## 📚 Referanslar

1. J. Postel, *"User Datagram Protocol"*, RFC 768, IETF, 1980.
2. J. Postel, *"Transmission Control Protocol"*, RFC 793, IETF, 1981.
3. S. Josefsson, *"The Base16, Base32, and Base64 Data Encodings"*, RFC 4648, IETF, 2006.
4. V. Paxson et al., *"Computing TCP's Retransmission Timer"*, RFC 6298, IETF, 2011.
5. J. Iyengar, M. Thomson, *"QUIC: A UDP-Based Multiplexed and Secure Transport"*, RFC 9000, IETF, 2021.
6. A. Tanenbaum, D. Wetherall, *Computer Networks*, 5th ed., Prentice Hall, 2010.
7. W. R. Stevens et al., *UNIX Network Programming*, Vol. 1, 3rd ed., Addison-Wesley, 2004.

---

## 📄 Lisans

Bu proje MIT Lisansı ile lisanslanmıştır. Detaylar için [LICENSE](LICENSE) dosyasına bakınız.

---

<div align="center">
  <b>Bursa Teknik Üniversitesi — Bilgisayar Mühendisliği Bölümü</b><br>
  BLM0326 Bilgisayar Ağları | 2025-2026
</div>
