import asyncio
import pandas as pd

from datetime import datetime
from playwright.async_api import async_playwright

# ==================================================
# KONVERSI BULAN INDONESIA (UNTUK TANGERANGNEWS)
# ==================================================

bulan_indonesia = {
    "Januari": 1,
    "Februari": 2,
    "Maret": 3,
    "April": 4,
    "Mei": 5,
    "Juni": 6,
    "Juli": 7,
    "Agustus": 8,
    "September": 9,
    "Oktober": 10,
    "November": 11,
    "Desember": 12
}


def ubah_tanggal(tanggal_text):

    tanggal = tanggal_text.split("|")[0].strip()

    if "," in tanggal:
        tanggal = tanggal.split(",")[1].strip()

    bagian = tanggal.split()

    hari = int(bagian[0])
    bulan = bulan_indonesia[bagian[1]]
    tahun = int(bagian[2])

    return datetime(tahun, bulan, hari)


# ==================================================
# SCRAPING TANGERANGKAB
# ==================================================

async def scrap_tangerangkab(keyword,
                             jumlah_muat,
                             tanggal_mulai,
                             tanggal_akhir):

    hasil = []

    url = f"https://tangerangkab.go.id/pencarian?keyword={keyword}"

    async with async_playwright() as p:

        browser = await p.chromium.launch(
            headless=True,
            args=["--no-sandbox",
                  "--disable-dev-shm-usage"]
        )

        page = await browser.new_page(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/137.0.0.0 Safari/537.36"
        )

        await page.set_extra_http_headers({
            "Accept-Language": "id-ID,id;q=0.9",
        })

        await page.goto(
            url,
            wait_until="networkidle"
        )
        
        try:
            await page.wait_for_selector(
                "li.search-item",
                timeout=30000
            )
        
        except Exception:
            raise Exception(
                f"""
        URL:
        {page.url}
        
        TITLE:
        {await page.title()}
        
        HTML:
        {(await page.content())[:1500]}
        """
            )

        tombol = page.locator("#loadMore")

        for i in range(jumlah_muat):

            try:

                before = await page.locator(
                    "li.search-item"
                ).count()

                await tombol.click(timeout=5000)

                await page.wait_for_timeout(5000)

                after = await page.locator(
                    "li.search-item"
                ).count()

                if before == after:
                    break

            except:
                break

        items = page.locator("li.search-item")

        total = await items.count()

        for i in range(total):

            try:

                item = items.nth(i)

                judul = await item.locator(
                    "h2.search-title"
                ).inner_text()

                tanggal_text = await item.locator(
                    "div.date"
                ).inner_text()

                link = await item.locator(
                    "xpath=ancestor::a"
                ).get_attribute("href")

                tanggal = datetime.strptime(
                    tanggal_text.strip(),
                    "%d %b %Y"
                )

                if tanggal_mulai <= tanggal <= tanggal_akhir:

                    hasil.append({

                        "Judul": judul,

                        "Tanggal": tanggal.strftime("%Y-%m-%d"),

                        "Link": link

                    })

            except Exception as e:

                print(e)

        await browser.close()
                                 
    return hasil


# ==================================================
# SCRAPING TANGERANGNEWS
# ==================================================

async def scrap_tangerangnews(keyword,
                              jumlah_halaman,
                              tanggal_mulai,
                              tanggal_akhir):

    hasil = []

    async with async_playwright() as p:

        browser = await p.chromium.launch(
            headless=True,
            args=[
                "--no-sandbox",
                "--disable-dev-shm-usage"
            ]
        )

        page = await browser.new_page()

        for halaman in range(1, jumlah_halaman + 1):

            if halaman == 1:

                url = f"https://www.tangerangnews.com/page/search?q={keyword}"

            else:

                offset = (halaman - 1) * 20

                url = (
                    f"https://www.tangerangnews.com/page/search?"
                    f"q={keyword}&per_page={offset}"
                )

            await page.goto(url)

            await page.wait_for_load_state("networkidle")

            await page.wait_for_timeout(2000)

            items = page.locator("div.list-index ul li")

            total = await items.count()

            if total == 0:
                break

            for i in range(total):

                try:

                    item = items.nth(i)

                    judul = await item.locator(
                        "h1 a"
                    ).inner_text()

                    link = await item.locator(
                        "h1 a"
                    ).get_attribute("href")

                    tanggal_text = await item.locator(
                        "h2"
                    ).inner_text()

                    tanggal = ubah_tanggal(tanggal_text)

                    if tanggal_mulai <= tanggal <= tanggal_akhir:

                        hasil.append({

                            "Judul": judul,

                            "Tanggal": tanggal.strftime("%Y-%m-%d"),

                            "Link": link

                        })

                except Exception as e:

                    print(e)

        await browser.close()

    return hasil


# ==================================================
# MAIN PROGRAM
# ==================================================

async def main():

    print("=" * 50)
    print("PILIH SUMBER BERITA")
    print("=" * 50)
    print("1. TangerangKab")
    print("2. TangerangNews")

    pilihan = input("Masukkan pilihan (1/2): ")

    keyword = input("Masukkan keyword: ")

    tanggal_mulai = datetime.strptime(
        input("Tanggal mulai (YYYY-MM-DD): "),
        "%Y-%m-%d"
    )

    tanggal_akhir = datetime.strptime(
        input("Tanggal akhir (YYYY-MM-DD): "),
        "%Y-%m-%d"
    )

    if pilihan == "1":

        jumlah_muat = int(
            input("Klik 'Muat Berita Lainnya' berapa kali? ")
        )

        hasil = await scrap_tangerangkab(
            keyword,
            jumlah_muat,
            tanggal_mulai,
            tanggal_akhir
        )

        sumber = "TangerangKab"

    elif pilihan == "2":

        jumlah_halaman = int(
            input("Ambil sampai halaman berapa? ")
        )

        hasil = await scrap_tangerangnews(
            keyword,
            jumlah_halaman,
            tanggal_mulai,
            tanggal_akhir
        )

        sumber = "TangerangNews"

    else:

        print("Pilihan tidak valid.")
        return

    df = pd.DataFrame(hasil)

    nama_file = (
        f"hasil_{sumber}_{keyword}_"
        f"{tanggal_mulai.strftime('%Y%m%d')}_"
        f"{tanggal_akhir.strftime('%Y%m%d')}.xlsx"
    )

    df.to_excel(nama_file, index=False)

    print()
    print("=" * 50)
    print("SELESAI")
    print("=" * 50)
    print("Sumber :", sumber)
    print("Jumlah berita :", len(df))
    print("File :", nama_file)


if __name__ == "__main__":
    asyncio.run(main())
