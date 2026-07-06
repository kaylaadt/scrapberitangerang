import asyncio
import pandas as pd

from scrapingberita import (
    scrap_tangerangkab,
    scrap_tangerangnews
)


async def jalankan_scraping(
    sumber,
    keyword,
    tanggal_mulai,
    tanggal_akhir,
    jumlah
):
    """
    Menjalankan scraping dan mengembalikan DataFrame.
    """

    if sumber == "TangerangKab":

        hasil = await scrap_tangerangkab(
            keyword,
            jumlah,
            tanggal_mulai,
            tanggal_akhir
        )

    elif sumber == "TangerangNews":

        hasil = await scrap_tangerangnews(
            keyword,
            jumlah,
            tanggal_mulai,
            tanggal_akhir
        )

    else:
        raise ValueError("Sumber berita tidak valid.")

    df = pd.DataFrame(hasil)

    if not df.empty:
        df = df.sort_values(
            by="Tanggal",
            ascending=False
        ).reset_index(drop=True)

    return df