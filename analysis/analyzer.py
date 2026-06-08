# analysis/analyzer.py
import pandas as pd
import matplotlib.pyplot as plt
import os

def generate_performance_charts():
    client_log_path = "logs/client_log.csv"
    server_log_path = "logs/server_log.csv"
    
    if not os.path.exists(client_log_path) or not os.path.exists(server_log_path):
        print("Hata: Log dosyaları bulunamadı! Lütfen önce client ve server'ı çalıştırın.")
        return

    # Logları oku
    
    column_names = ['timestamp', 'event_type', 'seq', 'size_bytes', 'status']
    
    df_client = pd.read_csv(client_log_path, names=column_names, header=None)
    
    # 1. METRİK HESAPLAMALARI
    total_time = df_client['timestamp'].max() - df_client['timestamp'].min()
    
    # Throughput: Yolda harcanan tüm byte'lar (Yeniden gönderimler dahil)
    total_bytes_sent = df_client[df_client['event_type'].isin(['DATA', 'END'])]['size_bytes'].sum()
    throughput_bps = (total_bytes_sent * 8) / total_time if total_time > 0 else 0
    
    # Goodput: Sadece başarıyla iletilen ve özgün olan paketlerin boyutu
    # Tekrarlanan (duplicate olmayan) başarılı süreçleri filtrele
    success_acks = df_client[df_client['event_type'] == 'ACK_RCV']['seq'].unique()
    # İlk gönderilen başarılı paketlerin boyut toplamı (Header'sız saf veri tahmini için basitleştirilmiş iletişim)
    # Proje kapsamında overhead dahil/hariç tartışması raporda yapılabilir.
    goodput_bytes = len(success_acks) * 1024 # CHUNK_SIZE varsayılanı
    goodput_bps = (goodput_bytes * 8) / total_time if total_time > 0 else 0

    print("\n====== NETPROBE PERFORMANS ANALİZ RAPORU ======")
    print(f"Toplam Aktarım Süresi : {total_time:.4f} saniye")
    print(f"Toplam Gönderilen Veri: {total_bytes_sent} Byte (Yeniden gönderimler dahil)")
    print(f"Throughput            : {throughput_bps / 1000:.2f} Kbps")
    print(f"Goodput               : {goodput_bps / 1000:.2f} Kbps")
    print("===============================================")

    # 2. GRAFİK ÇİZİMİ
    categories = ['Throughput', 'Goodput']
    values = [throughput_bps / 1000, int(goodput_bps / 1000)] # Kbps cinsinden
    
    plt.figure(figsize=(8, 5))
    colors = ['#3498db', '#2ecc71']
    bars = plt.bar(categories, values, color=colors, width=0.4)
    
    plt.title('NetProbe Ağ Performans Analizi (Kbps)', fontsize=14, fontweight='bold')
    plt.ylabel('Veri İletim Hızı (Kbps)', fontsize=12)
    
    # Barların üzerine değerlerini yazma
    for bar in bars:
        yval = bar.get_height()
        plt.text(bar.get_x() + bar.get_width()/2.0, yval + (max(values)*0.01), f"{yval:.2f} Kbps", ha='center', va='bottom', fontweight='bold')
    
    plt.grid(axis='y', linestyle='--', alpha=0.7)
    
    # Grafiği kaydet
    output_image = "analysis/performance_chart.png"
    plt.savefig(output_image)
    print(f"\n✔ Grafik başarıyla oluşturuldu ve kaydedildi: {output_image}")
    plt.show()

if __name__ == "__main__":
    generate_performance_charts()