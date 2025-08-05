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
python main.py [daftar_akun] [--use-proxy] [--output file] [--workers N]
```

- `daftar_akun` dapat berupa path file lokal atau URL.
- Gunakan `--use-proxy` untuk mengaktifkan penggunaan proxy dari daftar gratis.
- Gunakan `--output` untuk menentukan file hasil akun aktif (default: `live.txt`).
- Atur `--workers` untuk menentukan jumlah thread yang digunakan saat memproses akun (default: 20).


## Format Daftar Akun

Setiap baris harus berformat:

```
https://{domain}:email@example.com:password
```

Bagian `{domain}` dapat berupa subdomain apapun dari layanan Vidio.

