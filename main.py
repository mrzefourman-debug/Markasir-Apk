import json
from kivy.app import App
from kivy.lang import Builder
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.popup import Popup
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
from kivy.properties import StringProperty, BooleanProperty, ListProperty, NumericProperty
import os

NAMA_FILE_DATA = "data_barang_toko.json"
ADMIN_USER = "admin"
ADMIN_PASS = "admin"

KV_FILE = 'aplikasitoko.kv'
Builder.load_file(KV_FILE)


class AplikasiKasirRoot(BoxLayout):
    status_text = StringProperty("Aplikasi siap digunakan.")
    total_text = StringProperty("TOTAL: Rp 0")
    kembalian_text = StringProperty("Kembalian: Rp 0")
    is_admin = BooleanProperty(False)
    keranjang = ListProperty([])
    total = NumericProperty(0)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.data_barang = {}
        self.load_data()
        self.update_total_display()
        self.update_admin_ui()

    # ---- File data ----
    def load_data(self):
        if os.path.exists(NAMA_FILE_DATA):
            try:
                with open(NAMA_FILE_DATA, 'r') as f:
                    self.data_barang = json.load(f)
            except:
                self.data_barang = {}
                self.save_data()
        else:
            self.data_barang = {}
            self.save_data()

    def save_data(self):
        try:
            with open(NAMA_FILE_DATA, 'w') as f:
                json.dump(self.data_barang, f, indent=4)
        except Exception as e:
            self.show_msg('Error', f'Gagal menulis file data: {e}')

    # ---- Utilities ----
    def format_rupiah(self, angka):
        try:
            return f"Rp {int(angka):,}".replace(',', '.')
        except:
            return 'Rp 0'

    def show_msg(self, title, text):
        popup = Popup(title=title, content=Label(text=text), size_hint=(.8, .4))
        popup.open()

    # ---- Admin ----
    def open_login(self):
        content = BoxLayout(orientation='vertical', spacing=10, padding=10)
        ti_user = TextInput(hint_text='Username', multiline=False)
        ti_pass = TextInput(hint_text='Password', password=True, multiline=False)
        btn_box = BoxLayout(size_hint_y=None, height='40dp', spacing=10)
        btn_ok = Button(text='Login')
        btn_cancel = Button(text='Batal')

        def do_login(instance):
            if ti_user.text == ADMIN_USER and ti_pass.text == ADMIN_PASS:
                self.is_admin = True
                self.status_text = 'Mode: Admin aktif'
                login_popup.dismiss()
                self.update_admin_ui()
                self.show_msg('Sukses', 'Login Admin berhasil')
            else:
                self.show_msg('Gagal', 'Username atau password salah')

        btn_ok.bind(on_release=do_login)
        btn_cancel.bind(on_release=lambda *a: login_popup.dismiss())
        btn_box.add_widget(btn_ok)
        btn_box.add_widget(btn_cancel)
        content.add_widget(ti_user)
        content.add_widget(ti_pass)
        content.add_widget(btn_box)

        login_popup = Popup(title='Login Admin', content=content, size_hint=(.8, .5))
        login_popup.open()

    def logout(self):
        self.is_admin = False
        self.status_text = 'Mode: Kasir/Publik'
        self.update_admin_ui()
        self.show_msg('Logout', 'Anda telah logout')

    def update_admin_ui(self):
        try:
            self.ids.btn_tambah.disabled = not self.is_admin
            self.ids.btn_lihat.disabled = not self.is_admin
            if self.is_admin:
                self.ids.status_admin.text = 'Status: Admin Berhasil Login'
                self.ids.status_admin.color = (0, 1, 0, 1)
            else:
                self.ids.status_admin.text = 'Status: Mode Kasir/Publik'
                self.ids.status_admin.color = (0.5, 0.5, 0.5, 1)
        except:
            pass

    # ---- Tambah / Update barang ----
    def open_tambah_barang(self):
        if not self.is_admin:
            self.show_msg('Akses Ditolak', 'Login sebagai admin terlebih dahulu')
            return

        content = BoxLayout(orientation='vertical', spacing=10, padding=10)
        ti_nama = TextInput(hint_text='Nama Barang', multiline=False)
        ti_harga = TextInput(hint_text='Harga (angka saja)', multiline=False)
        btn_box = BoxLayout(size_hint_y=None, height='40dp', spacing=10)
        btn_ok = Button(text='Simpan')
        btn_cancel = Button(text='Batal')

        def do_simpan(instance):
            nama = ti_nama.text.strip().title()
            try:
                harga = int(ti_harga.text.replace('.', '').replace(',', ''))
            except:
                self.show_msg('Error', 'Harga harus angka positif')
                return
            if nama:
                self.data_barang[nama] = harga
                self.save_data()
                self.show_msg('Sukses', f'Data {nama} disimpan')
                tambah_popup.dismiss()
                self.ids.input_nama.text = ''
                self.update_suggestions()
            else:
                self.show_msg('Error', 'Nama barang tidak boleh kosong')

        btn_ok.bind(on_release=do_simpan)
        btn_cancel.bind(on_release=lambda *a: tambah_popup.dismiss())
        btn_box.add_widget(btn_ok)
        btn_box.add_widget(btn_cancel)
        content.add_widget(ti_nama)
        content.add_widget(ti_harga)
        content.add_widget(btn_box)

        tambah_popup = Popup(title='Tambah / Update Barang', content=content, size_hint=(.9, .6))
        tambah_popup.open()

    def lihat_semua(self):
        if not self.is_admin:
            self.show_msg('Akses Ditolak', 'Login sebagai admin terlebih dahulu')
            return
        teks = "--- DAFTAR HARGA BARANG ---\n"
        if self.data_barang:
            for nama, harga in sorted(self.data_barang.items()):
                teks += f"{nama:<30} : {self.format_rupiah(harga)}\n"
        else:
            teks += 'Daftar barang kosong.'
        popup = Popup(title='Daftar Semua Barang', content=Label(text=teks), size_hint=(.9, .9))
        popup.open()

    # ---- Saran / Autocomplete ----
    def update_suggestions(self, *args):
        input_text = self.ids.input_nama.text.strip().lower()
        box = self.ids.saran_box
        box.clear_widgets()
        if not input_text:
            self.ids.label_saran.text = 'Ketik nama barang untuk melihat saran.'
            return
        suggestions = [nama for nama in self.data_barang.keys() if input_text in nama.lower()]
        suggestions.sort()
        if suggestions:
            self.ids.label_saran.text = 'Mungkin barang yang Anda cari:'
            for nama in suggestions[:7]:
                b = Button(text=nama, size_hint_y=None, height='36dp')
                b.bind(on_release=lambda inst, x=nama: self.select_suggestion(x))
                box.add_widget(b)
        else:
            self.ids.label_saran.text = 'Tidak ada saran yang cocok.'

    def select_suggestion(self, nama):
        self.ids.input_nama.text = nama
        self.open_qty_popup(nama)

    # ---- Keranjang / Kasir ----
    def open_qty_popup(self, nama_barang):
        content = BoxLayout(orientation='vertical', spacing=10, padding=10)
        ti_qty = TextInput(hint_text='Jumlah (angka)', multiline=False, input_filter='int')
        ti_qty.text = '1'
        btn_box = BoxLayout(size_hint_y=None, height='40dp', spacing=10)
        btn_ok = Button(text='OK')
        btn_cancel = Button(text='Batal')

        def do_ok(instance):
            try:
                qty = int(ti_qty.text)
                if qty <= 0:
                    raise ValueError
            except:
                self.show_msg('Error', 'Jumlah harus angka positif')
                return
            harga = self.data_barang.get(nama_barang, 0)
            subtotal = harga * qty
            found = False
            for it in self.keranjang:
                if it['nama'] == nama_barang:
                    it['qty'] += qty
                    it['subtotal'] += subtotal
                    found = True
                    break
            if not found:
                self.keranjang.append({'nama': nama_barang, 'harga_satuan': harga, 'qty': qty, 'subtotal': subtotal})
            self.update_keranjang_ui()
            qty_popup.dismiss()
            self.ids.input_nama.text = ''
            self.ids.label_status.text = f"'{nama_barang}' ({qty}x) ditambahkan."

        btn_ok.bind(on_release=do_ok)
        btn_cancel.bind(on_release=lambda *a: qty_popup.dismiss())
        btn_box.add_widget(btn_ok)
        btn_box.add_widget(btn_cancel)
        content.add_widget(Label(text=f"Tambah: {nama_barang}"))
        content.add_widget(ti_qty)
        content.add_widget(btn_box)

        qty_popup = Popup(title='Masukkan Jumlah', content=content, size_hint=(.8, .5))
        qty_popup.open()

    def update_keranjang_ui(self):
        box = self.ids.keranjang_box
        box.clear_widgets()
        if not self.keranjang:
            box.add_widget(Label(text='(Keranjang kosong)', size_hint_y=None, height='30dp'))
        else:
            for i, item in enumerate(self.keranjang):
                txt = f"{i+1}. {item['nama'][:20]:<20} ({item['qty']}x) | {self.format_rupiah(item['subtotal'])}"
                lbl = Label(text=txt, size_hint_y=None, height='30dp', color=(0,0,0,1))
                box.add_widget(lbl)
        self.hitung_total()

    def hapus_item(self):
        if not self.keranjang:
            self.show_msg('Peringatan', 'Keranjang kosong')
            return
        item = self.keranjang.pop()
        self.update_keranjang_ui()
        self.ids.label_status.text = f"Item '{item['nama']}' dihapus."

    def hitung_total(self):
        self.total = sum(it['subtotal'] for it in self.keranjang)
        self.update_total_display()

    def update_total_display(self):
        self.total_text = f"TOTAL: {self.format_rupiah(self.total)}"
        self.kembalian_text = 'Kembalian: Rp 0'
        try:
            self.ids.input_bayar.text = ''
        except:
            pass

    def proses_bayar(self):
        if self.total == 0:
            self.show_msg('Peringatan', 'Keranjang masih kosong')
            return
        bayar_text = self.ids.input_bayar.text.replace('.', '').replace(',', '')
        try:
            bayar = int(bayar_text)
        except:
            self.show_msg('Error', 'Nominal bayar harus angka')
            return
        if bayar < self.total:
            self.show_msg('Error', 'Uang pembayaran kurang')
            return
        kembalian = bayar - self.total
        self.kembalian_text = f"KEMBALIAN: {self.format_rupiah(kembalian)}"
        self.ids.label_status.text = 'Pembayaran berhasil!'
        conf = Popup(title='Transaksi Selesai',
                     content=Label(text=f"Total: {self.format_rupiah(self.total)}\nBayar: {self.format_rupiah(bayar)}\nKembalian: {self.format_rupiah(kembalian)}"),
                     size_hint=(0.8, 0.5))
        conf.open()

    def reset_transaksi(self):
        self.keranjang = []
        self.total = 0
        self.update_keranjang_ui()
        self.update_total_display()
        self.ids.label_status.text = 'Transaksi baru dimulai.'


class AplikasiKasirApp(App):
    def build(self):
        return AplikasiKasirRoot()


if __name__ == '__main__':
    AplikasiKasirApp().run()