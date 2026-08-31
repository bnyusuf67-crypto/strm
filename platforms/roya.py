import requests
from urllib.parse import urljoin
import os

session = requests.Session()
session.headers.update({
    "User-Agent": "Mozilla/5.0",
    "Accept-Encoding": "identity",
})


def get_all_variants(api_url):
    """
    Master playlist'i ayrıştırır ve mevcut tüm kalite alternatiflerini 
    (stream info etiketi ve tam URL) çift olarak döndürür.
    """
    # 1. API'den secured URL'yi al
    r = session.get(api_url, timeout=10)
    r.raise_for_status()
    secured_url = r.json()["data"]["secured_url"]

    # 2. Master m3u8 içeriğini çek
    r = session.get(secured_url, timeout=10)
    r.raise_for_status()
    playlist = r.text

    variants = []
    lines = playlist.splitlines()
    
    # 3. Stream etiketi ve ona karşılık gelen URL'leri eşleştir
    for i, line in enumerate(lines):
        line = line.strip()
        if line.startswith("#EXT-X-STREAM-INF:"):
            stream_info = line
            # Bir sonraki boş olmayan ve # ile başlamayan satır ilgili URL'dir
            for j in range(i + 1, len(lines)):
                next_line = lines[j].strip()
                if next_line and not next_line.startswith("#"):
                    full_url = urljoin(secured_url, next_line)
                    variants.append((stream_info, full_url))
                    break

    if not variants:
        raise Exception(f"Yayın URL'leri bulunamadı: {api_url}")

    return variants


def write_master_m3u8(filename, variants):
    """
    Yakalanan tüm kalite alternatiflerini m3u8 dosyasına yazar.
    """
    # Hedef klasör yoksa oluştur
    os.makedirs(os.path.dirname(filename), exist_ok=True)

    content_lines = [
        "#EXTM3U",
        "#EXT-X-VERSION:3"
    ]

    for stream_info, variant_url in variants:
        content_lines.append(stream_info)
        content_lines.append(variant_url)

    content = "\n".join(content_lines) + "\n"

    with open(filename, "w", encoding="utf-8") as f:
        f.write(content)


# --- ÇALIŞTIRMA ---

channels = [
    ("https://ticket.roya-tv.com/api/v5/fastchannel/1", "platforms/links/roya1.m3u8"),
    ("https://ticket.roya-tv.com/api/v5/fastchannel/21", "platforms/links/roya2.m3u8"),
    ("https://ticket.roya-tv.com/api/v5/fastchannel/48", "platforms/links/roya3.m3u8"),
]

for api_url, output_path in channels:
    try:
        variants = get_all_variants(api_url)
        write_master_m3u8(output_path, variants)
        print(f"Başarıyla kaydedildi ({len(variants)} kalite seçeneği): {output_path}")
    except Exception as e:
        print(f"Hata [{api_url}]: {e}")
