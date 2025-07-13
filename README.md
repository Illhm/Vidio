# Vidio Account Checker

Script ini digunakan untuk memeriksa status langganan akun Vidio.

## Persyaratan

- Python 3.8+
- Dependensi dapat diinstal melalui `pip install -r requirements.txt`

## Variabel Lingkungan


```bash
export X_API_AUTH=token_api_anda
```

## Penggunaan

```bash
python main.py [daftar_akun] [--use-proxy]
```

- `daftar_akun` dapat berupa path file lokal atau URL.
- Gunakan `--use-proxy` untuk mengaktifkan penggunaan proxy dari daftar gratis.

Script ini sekarang memvalidasi daftar proxy secara paralel sehingga proses pencarian lebih cepat. Setiap proxy akan otomatis diblacklist setelah digunakan sebanyak tujuh kali.

## Format Daftar Akun

Setiap baris harus berformat seperti berikut:

```
https://vidio.com:email@example.com:password
```

