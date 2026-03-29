from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
from kivy.uix.scrollview import ScrollView
from kivy.uix.gridlayout import GridLayout
from kivy.uix.spinner import Spinner
import requests
import json
import os

class DonTakipSistemi(BoxLayout):
    def __init__(self, **kwargs):
        super().__init__(orientation='vertical', padding=10, spacing=5, **kwargs)
        
        self.dosya = "teknofest_super_v14.json"
        self.bahceler = self.yukle()
        
        self.hazir_meyveler = {
            "Kayısı (-2.0°C)": -2.0,
            "Elma (-3.0°C)": -3.0,
            "Kiraz (-2.2°C)": -2.2,
            "Ceviz (-1.0°C)": -1.0,
            "ÖZEL (Kendim Gireceğim)": 0.0
        }

        # --- ÜST PANEL ---
        self.add_widget(Label(text="48 SAATLİK AKILLI DON RADARI", font_size='20sp', bold=True, color=(0, 1, 1, 1), size_hint_y=None, height=50))
        
        self.gps_btn = Button(text="📍 KONUMUMU OTOMATİK DOLDUR", background_color=(0.1, 0.6, 0.9, 1), size_hint_y=None, height=70, bold=True)
        self.gps_btn.bind(on_press=self.konum_getir)
        self.add_widget(self.gps_btn)

        # --- GİRİŞ ALANLARI ---
        self.isim_in = TextInput(hint_text="Bahçe İsmi", multiline=False, size_hint_y=None, height=60)
        self.lat_in = TextInput(hint_text="Enlem", multiline=False, size_hint_y=None, height=60)
        self.lon_in = TextInput(hint_text="Boylam", multiline=False, size_hint_y=None, height=60)
        
        self.meyve_secici = Spinner(text='Meyve Seçin', values=(list(self.hazir_meyveler.keys())), size_hint_y=None, height=70)
        self.meyve_secici.bind(text=self.meyve_kontrol)
        
        self.ozel_ad_in = TextInput(hint_text="Özel Meyve Adı", multiline=False, size_hint_y=None, height=60, disabled=True)
        self.ozel_derece_in = TextInput(hint_text="Özel Donma Derecesi", multiline=False, size_hint_y=None, height=60, disabled=True)

        for w in [self.isim_in, self.lat_in, self.lon_in, self.meyve_secici, self.ozel_ad_in, self.ozel_derece_in]:
            self.add_widget(w)

        self.kaydet_btn = Button(text="BAHÇEYİ KAYDET VE KORUMAYA AL", background_color=(0, 0.8, 0.3, 1), size_hint_y=None, height=80, bold=True)
        self.kaydet_btn.bind(on_press=self.ekle)
        self.add_widget(self.kaydet_btn)

        # --- KIYASLAMA BUTONU (YENİ!) ---
        self.karsilastir_btn = Button(text="📊 TÜM BAHÇELERİ KIYASLA (RİSK TABLOSU)", background_color=(1, 0.5, 0, 1), size_hint_y=None, height=90, bold=True)
        self.karsilastir_btn.bind(on_press=self.bahceleri_kiyasla)
        self.add_widget(self.karsilastir_btn)

        # --- RAPOR ALANI ---
        self.scroll_rapor = ScrollView(size_hint=(1, 0.8))
        self.rapor_label = Label(text="Rapor için aşağıdan bahçe seçin veya kıyasla butonuna basın.", size_hint_y=None, font_size='13sp', halign='left', valign='top', markup=True)
        self.rapor_label.bind(size=self.rapor_label.setter('text_size'))
        self.scroll_rapor.add_widget(self.rapor_label)
        self.add_widget(self.scroll_rapor)

        # --- LİSTE ---
        self.liste_grid = GridLayout(cols=1, spacing=5, size_hint_y=None)
        self.liste_grid.bind(minimum_height=self.liste_grid.setter('height'))
        scroll_l = ScrollView(size_hint=(1, 0.4))
        scroll_l.add_widget(self.liste_grid)
        self.add_widget(scroll_l)
        
        self.yenile()

    # --- ESKİ FONKSİYONLARIN (AYNEN KORUNDU) ---
    def konum_getir(self, instance):
        try:
            res = requests.get('https://ipapi.co/json/', timeout=5).json()
            self.lat_in.text = str(res.get('latitude'))
            self.lon_in.text = str(res.get('longitude'))
            self.gps_btn.text = f"📍 KONUM ALINDI: {res.get('city')}"
        except: self.gps_btn.text = "❌ Hata! Manuel Girin."

    def meyve_kontrol(self, spinner, text):
        durum = False if "ÖZEL" in text else True
        self.ozel_ad_in.disabled = durum
        self.ozel_derece_in.disabled = durum

    def yukle(self):
        if os.path.exists(self.dosya):
            try:
                with open(self.dosya, "r") as f: return json.load(f)
            except: return {}
        return {}

    def ekle(self, instance):
        isim = self.isim_in.text
        m_secim = self.meyve_secici.text
        if isim and self.lat_in.text and m_secim != 'Meyve Seçin':
            if "ÖZEL" in m_secim:
                m_adi = self.ozel_ad_in.text
                esik = float(self.ozel_derece_in.text)
            else:
                m_adi = m_secim.split(" (")[0]
                esik = self.hazir_meyveler[m_secim]
            self.bahceler[isim] = {"lat": self.lat_in.text, "lon": self.lon_in.text, "meyve": m_adi, "esik": esik}
            with open(self.dosya, "w") as f: json.dump(self.bahceler, f)
            self.yenile()

    def sil(self, isim):
        if isim in self.bahceler:
            del self.bahceler[isim]
            with open(self.dosya, "w") as f: json.dump(self.bahceler, f)
            self.yenile()

    def yenile(self):
        self.liste_grid.clear_widgets()
        for isim in self.bahceler:
            row = BoxLayout(size_hint_y=None, height=80, spacing=5)
            btn = Button(text=f"{isim.upper()} ({self.bahceler[isim]['meyve']})", background_color=(0.2, 0.5, 0.8, 1))
            btn.bind(on_press=lambda x, n=isim: self.analiz_et(n))
            btn_sil = Button(text="SİL", size_hint_x=0.2, background_color=(0.8, 0.1, 0.1, 1), bold=True)
            btn_sil.bind(on_press=lambda x, n=isim: self.sil(n))
            row.add_widget(btn); row.add_widget(btn_sil)
            self.liste_grid.add_widget(row)

    def analiz_et(self, isim):
        b = self.bahceler[isim]
        url = f"https://api.open-meteo.com/v1/forecast?latitude={b['lat']}&longitude={b['lon']}&hourly=temperature_2m&forecast_days=2"
        try:
            r = requests.get(url, timeout=8).json()
            saatler, temps = r['hourly']['time'], r['hourly']['temperature_2m']
            rapor = f"[b]🛡️ {isim} ({b['meyve']}) 48 SAATLİK ANALİZ[/b]\n"
            rapor += f"Donma Eşiği: {b['esik']}°C\n----------------------------\n"
            for i in range(len(saatler)):
                t, s = saatler[i].split("T")
                derece = temps[i]
                renk = "ff4444" if derece <= b['esik'] else "44ff44"
                durum = "TEHLİKE!" if derece <= b['esik'] else "Güvenli"
                rapor += f"[color={renk}]{t} {s}: {derece}°C - {durum}[/color]\n"
            self.rapor_label.text = rapor
            self.rapor_label.height = self.rapor_label.texture_size[1] + 50
        except: self.rapor_label.text = "Veri hatası!"

    # --- YENİ: KARŞILAŞTIRMA FONKSİYONU ---
    def bahceleri_kiyasla(self, instance):
        if not self.bahceler:
            self.rapor_label.text = "Lütfen önce bahçe ekleyin!"
            return

        tablo = "[b]📊 BAHÇELER ARASI DON RİSK TABLOSU[/b]\n"
        tablo += "{:<12} {:<8} {:<8} {:<8}\n".format("BAHÇE", "HAVA", "EŞİK", "DURUM")
        tablo += "------------------------------------------\n"

        for isim, veri in self.bahceler.items():
            try:
                # Anlık sıcaklığı çekiyoruz
                url = f"https://api.open-meteo.com/v1/forecast?latitude={veri['lat']}&longitude={veri['lon']}&current_weather=true"
                r = requests.get(url, timeout=5).json()
                anlik = r['current_weather']['temperature']
                esik = veri['esik']

                # Karşılaştırma Mantığı
                if anlik <= esik:
                    durum = "[color=ff3333]KRİTİK[/color]" # Don başladı
                elif (anlik - esik) <= 2:
                    durum = "[color=ffcc00]RİSKLİ[/color]" # Don yaklaşıyor (2 derece fark kaldı)
                else:
                    durum = "[color=33ff33]GÜVENLİ[/color]" # Sorun yok

                tablo += "{:<12} {:<8} {:<8} {:<8}\n".format(isim[:10], anlik, esik, durum)
            except:
                tablo += f"{isim}: Veri alınamadı!\n"

        self.rapor_label.text = tablo
        self.rapor_label.height = self.rapor_label.texture_size[1] + 50

class DonApp(App):
    def build(self): return DonTakipSistemi()

if __name__ == "__main__":
    DonApp().run()