# kelas-analisis-data-dicoding

# Proyek Analisis Data E-Commerce 📦

## Deskripsi Proyek
Proyek ini merupakan submission tugas akhir dari kelas **Belajar Analisis Data dengan Python** di Dicoding. Proyek ini bertujuan untuk mengeksplorasi dataset E-Commerce guna menghasilkan *insight* bisnis terkait performa logistik (pengaruh lama waktu keterlambatan terhadap kepuasan) dan analisis pola waktu transaksi untuk penjadwalan *Flash Sale*.

## Struktur Direktori
- `/data`: Berisi dataset mentah yang digunakan.
- `/dashboard`: Berisi script `dashboard.py` untuk menjalankan Streamlit.
- `notebook.ipynb`: Berkas Jupyter Notebook yang berisi alur analisis data secara lengkap.
- `requirements.txt`: Daftar library Python yang dibutuhkan.

## Setup Environment & Run Dashboard

### Menggunakan Anaconda (Rekomendasi)
Jika Anda menggunakan Anaconda, buka Anaconda Prompt dan jalankan perintah berikut:
```bash
conda create --name proyek_ds python=3.9
conda activate proyek_ds
pip install -r requirements.txt
cd dashboard
streamlit run dashboard.py
```

### Menggunakan Python venv (Bawaan Windows/Mac)
Jika Anda tidak menggunakan Anaconda, buka Terminal / Command Prompt dan jalankan:
```bash
mkdir proyek_analisis_data
cd proyek_analisis_data
python -m venv env
# Untuk pengguna Windows:
env\Scripts\activate
# Untuk pengguna Mac/Linux:
source env/bin/activate

pip install -r requirements.txt
cd dashboard
streamlit run dashboard.py```
