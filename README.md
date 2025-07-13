# Vidio Account Checker

Script ini digunakan untuk memeriksa status langganan akun Vidio.

## Persyaratan

- Python 3.8+
- Dependensi dapat diinstal melalui `pip install -r requirements.txt`

## Variabel Lingkungan

Sebelum menjalankan skrip, set variabel `X_API_AUTH` dengan token API Vidio Anda:

```bash
export X_API_AUTH=token_api_anda
```

## Penggunaan

```bash
python main.py [daftar_akun] [--use-proxy]
```

- `daftar_akun` dapat berupa path file lokal atau URL.
- Gunakan `--use-proxy` untuk mengaktifkan penggunaan proxy dari daftar gratis.

## Format Daftar Akun

Setiap baris harus berformat seperti berikut:

```
https://vidio.com:email@example.com:password
```

Hasil akun dengan langganan aktif akan disimpan ke `live.txt`.
