"""
Scraping data pelabuhan Pelni dengan Session Management
Script ini menggunakan requests session untuk lebih efisien
"""

import json
import time

import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
from seleniumbase import BaseCase


class PelniScraperWithSession(BaseCase):
    """
    Scraper Pelni dengan kombinasi Selenium dan Requests
    Selenium hanya untuk mendapatkan token awal,
    Requests untuk mengambil data destinasi (lebih cepat)
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.results = []
        self.session = requests.Session()
        self.token = None
        self.cookies = None
        
        # Setup retry strategy untuk handle koneksi yang gagal
        retry_strategy = Retry(
            total=3,  # Total retry attempts
            backoff_factor=1,  # Wait 1, 2, 4 seconds between retries
            status_forcelist=[429, 500, 502, 503, 504],
        )
        adapter = HTTPAdapter(max_retries=retry_strategy)
        self.session.mount("http://", adapter)
        self.session.mount("https://", adapter)

    def get_initial_data(self):
        """Mengambil token dan cookies menggunakan Selenium"""
        print("🔗 Navigasi ke halaman Pelni...")
        self.open("https://pelni.co.id/")

        print("⏳ Mengambil CSRF token dan cookies...")
        self.wait_for_element("select[name='ticket_org']", timeout=20)

        # Ambil CSRF token
        self.token = self.get_attribute("input[name='_token']", "value")
        if not self.token:
            raise Exception("❌ CSRF token tidak ditemukan.")

        # Ambil cookies dari Selenium
        selenium_cookies = self.get_cookies()

        # Convert ke format requests
        self.session.cookies.update(
            {cookie["name"]: cookie["value"] for cookie in selenium_cookies}
        )

        # Set headers
        self.session.headers.update(
            {
                "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36",
                "Content-Type": "application/x-www-form-urlencoded;",
                "Accept": "*/*",
                "Referer": "https://pelni.co.id/",
                "Origin": "https://pelni.co.id",
            }
        )

        print("✅ Token dan cookies didapatkan")
        return self.token

    def get_origin_ports(self):
        """Mengambil semua opsi kota asal dari halaman"""
        options = self.find_elements("select[name='ticket_org'] option")
        valid_options = []

        for opt in options:
            value = opt.get_attribute("value")
            if value:
                text = opt.text
                parts = text.split("|")
                city = parts[0].strip()

                if len(parts) > 1:
                    code_name = parts[1].split("-")
                    code = code_name[0].strip()
                    name = code_name[1].strip() if len(code_name) > 1 else city
                else:
                    code = ""
                    name = city

                valid_options.append(
                    {"id": int(value), "city": city, "code": code, "name": name}
                )

        return valid_options

    def fetch_destinations_via_requests(self, city_id):
        """Mengambil destinasi menggunakan requests (lebih cepat)"""
        url = "https://pelni.co.id/getdes"
        data = {"ticket_org": str(city_id), "_token": self.token}

        try:
            # Timeout: (connect timeout, read timeout)
            # 10 detik untuk establish connection, 60 detik untuk menunggu response
            response = self.session.post(url, data=data, timeout=(10, 60))

            if response.status_code == 200:
                # Parse HTML response
                from bs4 import BeautifulSoup

                soup = BeautifulSoup(response.text, "html.parser")

                options = soup.find_all("option")
                dest_values = [opt.get("value") for opt in options if opt.get("value")]

                return ",".join(dest_values)
            else:
                print(f"  ⚠️ HTTP Status: {response.status_code}")

        except requests.exceptions.ConnectTimeout:
            print(f"  ❌ Connection timeout - Gagal connect ke server")
        except requests.exceptions.ReadTimeout:
            print(f"  ❌ Read timeout - Server terlalu lama merespons")
        except requests.exceptions.RequestException as e:
            print(f"  ⚠️ Request error: {e}")
        except Exception as e:
            print(f"  ⚠️ Unexpected error: {e}")

        return None

    def scrape_all_ports(self):
        """Scraping semua data pelabuhan"""
        # Dapatkan data awal (token dan kota asal)
        self.get_initial_data()
        origin_ports = self.get_origin_ports()

        print(f"\n📊 Menemukan {len(origin_ports)} pelabuhan asal")
        print(f"{'=' * 60}\n")

        for idx, port in enumerate(origin_ports, 1):
            city = port["city"]
            code = port["code"]
            name = port["name"]
            city_id = port["id"]

            print(f"[{idx}/{len(origin_ports)}] {city} | {code} - {name}")

            # Ambil destinasi
            dest = self.fetch_destinations_via_requests(city_id)

            result = {
                "name": name,
                "code": code,
                "city": city,
                "id": city_id,
                "dest": dest if dest else "",
            }

            self.results.append(result)

            if dest:
                dest_count = len(dest.split(","))
                print(f"  ✓ {dest_count} destinasi")
            else:
                print(f"  ⚠️ Tidak ada destinasi")

            time.sleep(0.05)  # Delay kecil

    def save_results(self, filename="pelni-destinations.json"):
        """Simpan hasil ke file JSON"""
        # Sort by ID
        self.results.sort(key=lambda x: x["id"])

        with open(filename, "w", encoding="utf-8") as f:
            json.dump(self.results, f, indent=2, ensure_ascii=False)

        return filename

    def test_scrape_pelni_with_session(self):
        """Main test method"""
        start_time = time.time()

        print("=" * 60)
        print("🚢 PELNI PORT SCRAPER (Session Mode)")
        print("=" * 60)

        self.scrape_all_ports()

        filename = self.save_results()
        duration = time.time() - start_time

        print(f"\n{'=' * 60}")
        print(f"✅ SELESAI")
        print(f"{'=' * 60}")
        print(f"📁 Output: {filename}")
        print(f"⏱️  Durasi: {duration:.2f} detik")
        print(f"📊 Total: {len(self.results)} pelabuhan")
        print(f"{'=' * 60}")


if __name__ == "__main__":
    PelniScraperWithSession.main(__name__, __file__, "--headless")
