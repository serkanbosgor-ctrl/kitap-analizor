# -*- coding: utf-8 -*-
import os
import collections
import re
from pypdf import PdfReader

def kitabi_tasarla_ve_isimlendir():
    # Masaüstündeki PDF dosyasının adı
    pdf_adi = "anlamin_hareketliligi.pdf"
    
    if not os.path.exists(pdf_adi):
        # Küçük-büyük harf duyarlılığı için alternatif kontrol (.PDF kontrolü)
        if os.path.exists("anlamin_hareketliligi.PDF"):
            pdf_adi = "anlamin_hareketliligi.PDF"
        else:
            print(f"\nHata: '{pdf_adi}' adında bir PDF dosyası bulunamadı!")
            print("Lütfen bu kod dosyasının ve PDF dosyanızın aynı masaüstü klasöründe yan yana olduğundan emin olun.")
            return

    print("\n📖 PDF okunuyor, editörlük ve analiz işlemleri başlatıldı...")
    reader = PdfReader(pdf_adi)
    
    # Tüm PDF sayfalarındaki metni tek bir yapıda toplayalım
    ham_metin = ""
    for sayfa in reader.pages:
        text = sayfa.extract_text()
        if text:
            ham_metin += text + "\n"

    # --- EN ÇOK VURGULANAN KELİMELERİ BULMA (SAYFA/DOSYA İSMİ İÇİN) ---
    # Noktalama işaretlerini temizleyip kelimeleri ayıklıyoruz
    kelimeler = re.findall(r'\b\w+\b', ham_metin.lower())
    
    # Anlam taşımayan bağlaçları ve ekleri filtreleyelim
    gereksizler = {"ve", "veya", "bir", "bu", "da", "de", "için", "ile", "o", "en", "ki", "daha", "ama", "yani", "olan", "gibi"}
    temiz_kelimeler = [k for k in kelimeler if k not in gereksizler and len(k) > 2]
    
    kelime_sayici = collections.Counter(temiz_kelimeler)
    
    # En çok vurgulanan (en çok tekrar eden) ilk 3 anahtar kelimeyi yakalıyoruz
    en_cok_gecenler = [kelime for kelime, adet in kelime_sayici.most_common(3)]
    
    # İstediğin gibi vurgulanan kelimeleri dosya/sayfa ismine koyuyoruz
    vurgulanan_isim = "-".join(en_cok_gecenler).upper()
    cikis_dosyasi = f"kitap_{vurgulanan_isim}.txt"

    # --- KİTAP FORMATI DÜZENLEME ---
    paragraflar = ham_metin.split("\n")
    kitap_metni = "==================================================\n"
    kitap_metni += f"      ANLAMIN HAREKETLİLİĞİ - DÜZENLENMİŞ KİTAP\n"
    kitap_metni += f"      TEMATİK ODAK: {vurgulanan_isim.replace('-', ' / ')}\n"
    kitap_metni += "==================================================\n\n"

    for p in paragraflar:
        p_temiz = p.strip()
        if p_temiz:
            # Her paragraf başına kitap düzeni için 4 boşluk (girinti) bırakıyoruz
            kitap_metni += "    " + p_temiz + "\n\n"

    # Yeni kitap dosyasını kaydetme
    with open(cikis_dosyasi, "w", encoding="utf-8") as f:
        f.write(kitap_metni)

    print("\n==================================================")
    print("🎉 KİTAP ASİSTANI İŞLEMİ TAMAMLADI!")
    print(f"📊 Toplam Kelime Sayısı: {len(kelimeler)}")
    print(f"🔑 En Sık Vurgulanan Kavramlar: {', '.join(en_cok_gecenler)}")
    print(f"💾 Yeni Dosya İsmi: '{cikis_dosyasi}' olarak başarıyla oluşturuldu.")
    print("==================================================")

if __name__ == "__main__":
    kitabi_tasarla_ve_isimlendir()