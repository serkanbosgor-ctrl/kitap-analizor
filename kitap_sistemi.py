# -*- coding: utf-8 -*-
import tkinter as tk
from tkinter import messagebox, ttk, scrolledtext, filedialog
import os
import re
import collections
from pypdf import PdfReader

class KitapSistemi:
    def __init__(self, root):
        self.root = root
        self.root.title("📜 POLEMOS - Akıllı İmla ve Kitap Editörlüğü Sistemi")
        self.root.geometry("950x650")
        self.root.configure(bg="#f4f1ea") # Antika kağıt tonu
        
        # Stil ayarları
        style = ttk.Style()
        style.configure("TButton", font=("Georgia", 11), padding=5)
        style.configure("TLabel", font=("Georgia", 12), background="#f4f1ea")
        
        # --- SOL PANEL: Sayfalar Listesi ---
        self.sol_frame = tk.Frame(root, bg="#e8e4d9", width=250, bd=2, relief="groove")
        self.sol_frame.pack(side="left", fill="y", padx=10, pady=10)
        
        self.lbl_liste = tk.Label(self.sol_frame, text="📖 Kitap Sayfaları", font=("Georgia", 12, "bold"), bg="#e8e4d9", fg="#4a3b32")
        self.lbl_liste.pack(pady=5)
        
        self.liste_box = tk.Listbox(self.sol_frame, font=("Georgia", 10), bg="#faf9f5", fg="#2b221a")
        self.liste_box.pack(fill="both", expand=True, padx=5, pady=5)
        self.liste_box.bind("<<ListboxSelect>>", self.sayfa_getir)
        
        self.btn_yenile = ttk.Button(self.sol_frame, text="🔄 Listeyi Yenile", command=self.listeyi_guncelle)
        self.btn_yenile.pack(fill="x", padx=5, pady=5)

        # --- SAĞ PANEL: Editör Alanı ---
        self.sag_frame = tk.Frame(root, bg="#f4f1ea")
        self.sag_frame.pack(side="right", fill="both", expand=True, padx=10, pady=10)
        
        # Üst Araç Çubuğu
        self.ust_bar = tk.Frame(self.sag_frame, bg="#f4f1ea")
        self.ust_bar.pack(fill="x", pady=5)
        
        self.lbl_editor = tk.Label(self.ust_bar, text="✍️ Akıllı Editör Paneli", font=("Georgia", 12, "bold"), fg="#4a3b32")
        self.lbl_editor.pack(side="left")
        
        self.btn_pdf_sec = ttk.Button(self.ust_bar, text="📁 PDF'ten İmla Düzelterek Yükle", command=self.pdf_yükle)
        self.btn_pdf_sec.pack(side="right", padx=5)
        
        # Metin Giriş Alanı
        self.metin_alani = scrolledtext.ScrolledText(self.sag_frame, font=("Georgia", 12), bg="#faf9f5", fg="#2b221a", wrap="word")
        self.metin_alani.pack(fill="both", expand=True, pady=5)
        
        # Alt Butonlar Paneli
        self.buton_frame = tk.Frame(self.sag_frame, bg="#f4f1ea")
        self.buton_frame.pack(fill="x", pady=5)
        
        self.btn_kaydet = ttk.Button(self.buton_frame, text="💾 İmla Düzelt ve Sayfa Olarak Ekle", command=self.sayfa_kaydet)
        self.btn_kaydet.pack(side="right", padx=5)
        
        self.btn_temizle = ttk.Button(self.buton_frame, text="🗑️ Ekranı Temizle", command=self.ekrani_temizle)
        self.btn_temizle.pack(side="left", padx=5)
        
        # Klasör Kontrolü
        self.kitap_klasoru = "kitap_sayfalari"
        if not os.path.exists(self.kitap_klasoru):
            os.makedirs(self.kitap_klasoru)
            
        self.listeyi_guncelle()

    def imla_ve_noktalama_duzelt(self, metin):
        """Metindeki bariz noktalama, boşluk ve imla hatalarını temizler."""
        if not metin:
            return ""
            
        # 1. Noktalama işaretlerinden önceki gereksiz boşlukları sil (Örn: "elma . " -> "elma. ")
        metin = re.sub(r'\s+([.,;:!?])', r'\1', metin)
        
        # 2. Noktalama işaretlerinden sonra boşluk yoksa otomatik boşluk ekle (Örn: "elma.araba" -> "elma. araba")
        # Sayısal ifadeleri (Örn: 1.5 veya 10:30) bozmamak için harf kontrolü ekliyoruz
        metin = re.sub(r'([.,;:!?])(?=[a-zA-ZğüşıöçĞÜŞİÖÇ])', r'\1 ', metin)
        
        # 3. Birden fazla yan yana gelmiş gereksiz boşlukları tek boşluğa indirger
        metin = re.sub(r'[ \t]+', ' ', metin)
        
        # 4. Satır başlarındaki ve sonlarındaki görünmez boşlukları temizler
        satirlar = metin.split('\n')
        temiz_satirlar = []
        for satir in satirlar:
            s = satir.strip()
            if s:
                # Cümle başlangıcındaki ilk harfi otomatik büyük yapma kuralı
                s = s[0].upper() + s[1:] if len(s) > 0 else s
                temiz_satirlar.append(s)
        
        return '\n'.join(temiz_satirlar)

    def anahtar_kelime_bul(self, metin):
        kelimeler = re.findall(r'\b\w+\b', metin.lower())
        gereksizler = {"ve", "veya", "bir", "bu", "da", "de", "için", "ile", "o", "en", "ki", "daha", "ama", "yani", "olan", "gibi", "değildir", "artık", "böyle", "ise", "şu", "her"}
        temiz_kelimeler = [k for k in kelimeler if k not in gereksizler and len(k) > 2]
        
        if not temiz_kelimeler:
            return "DOKUMAN"
            
        kelime_sayici = collections.Counter(temiz_kelimeler)
        en_cok_gecenler = [kelime for kelime, adet in kelime_sayici.most_common(2)]
        return "-".join(en_cok_gecenler).upper()

    def metni_formatla_ve_kaydet(self, icerik, kaynak_tipi="SAYFA"):
        # Önce imla motorunu çalıştırıp metni temizliyoruz
        temiz_metin = self.imla_ve_noktalama_duzelt(icerik)
        
        vurgulanan = self.anahtar_kelime_bul(temiz_metin)
        paragraflar = temiz_metin.split("\n")
        
        duzenli_metin = f"=== BÖLÜM ODAĞI ({kaynak_tipi}): {vurgulanan} ===\n\n"
        for p in paragraflar:
            if p.strip():
                # Kitap estetiği için paragraf başlarına 4 boşluk girinti bırakıyoruz
                duzenli_metin += "    " + p.strip() + "\n\n"
                
        dosya_adi = f"{kaynak_tipi}_{vurgulanan}.txt"
        dosya_yolu = os.path.join(self.kitap_klasoru, dosya_adi)
        
        with open(dosya_yolu, "w", encoding="utf-8") as f:
            f.write(duzenli_metin)
            
        self.listeyi_guncelle()
        return dosya_adi, temiz_metin

    def sayfa_kaydet(self):
        icerik = self.metin_alani.get("1.0", tk.END).strip()
        if not icerik:
            messagebox.showwarning("Uyarı", "Lütfen boş metni kaydetmeye çalışmayın!")
            return
        dosya_adi, temiz_metin = self.metni_formatla_ve_kaydet(icerik, "SAYFA")
        
        # Ekrandaki metni de düzeltilmiş haliyle güncelliyoruz ki kullanıcı görsün
        self.metin_alani.delete("1.0", tk.END)
        self.metin_alani.insert(tk.END, temiz_metin)
        
        messagebox.showinfo("İmla Düzeltildi", f"Metindeki noktalama ve yazım hataları düzeltildi!\n'{dosya_adi}' olarak kaydedildi.")

    def pdf_yükle(self):
        dosya_yolu = filedialog.askopenfilename(filetypes=[("PDF Dosyaları", "*.pdf;*.PDF")])
        if not dosya_yolu:
            return
            
        try:
            reader = PdfReader(dosya_yolu)
            pdf_metni = ""
            for sayfa in reader.pages:
                text = sayfa.extract_text()
                if text:
                    pdf_metni += text + "\n"
            
            if not pdf_metni.strip():
                messagebox.showerror("Hata", "Bu PDF'in içi boş veya taranmış resim formatında.")
                return
                
            dosya_adi, temiz_metin = self.metni_formatla_ve_kaydet(pdf_metni, "PDF")
            
            # Düzeltilmiş metni editör ekranına basıyoruz
            self.metin_alani.delete("1.0", tk.END)
            self.metin_alani.insert(tk.END, temiz_metin)
            
            messagebox.showinfo("Başarılı", f"PDF'teki imla hataları ayıklandı!\n'{dosya_adi}' adıyla kitaba işlendi.")
            
        except Exception as e:
            messagebox.showerror("Hata", f"PDF işlenirken hata oluştu:\n{str(e)}")

    def listeyi_guncelle(self):
        self.liste_box.delete(0, tk.END)
        if os.path.exists(self.kitap_klasoru):
            dosyalar = [d for d in os.listdir(self.kitap_klasoru) if d.endswith(".txt")]
            for dosya in dosyalar:
                self.liste_box.insert(tk.END, dosya)

    def sayfa_getir(self, event):
        secili_indis = self.liste_box.curselection()
        if secili_indis:
            dosya_adi = self.liste_box.get(secili_indis[0])
            dosya_yolu = os.path.join(self.kitap_klasoru, dosya_adi)
            
            with open(dosya_yolu, "r", encoding="utf-8") as f:
                icerik = f.read()
                
            self.metin_alani.delete("1.0", tk.END)
            self.metin_alani.insert(tk.END, icerik)

    def ekrani_temizle(self):
        self.metin_alani.delete("1.0", tk.END)

if __name__ == "__main__":
    root = tk.Tk()
    app = KitapSistemi(root)
    root.mainloop()