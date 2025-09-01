import puppeteer from 'puppeteer';
import fs from 'fs';
import path from 'path';

// Interface untuk struktur data hasil scrapping
interface DestinationData {
  name: string;
  code: string;
  city: string;
  id: number;
  dest: string;
}

(async () => {
  const browser = await puppeteer.launch({ headless: true, protocolTimeout: 990000 }); // headless: false untuk melihat proses browser
  const page = await browser.newPage();
  
  // Menyesuaikan user-agent untuk menghindari deteksi bot
  await page.setUserAgent('Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36');

  console.log('🔗 Navigasi ke halaman Pelni...');
  await page.goto('https://pelni.co.id/', { waitUntil: 'networkidle2' });

  // Mengeksekusi script di dalam konteks halaman browser
  const results: DestinationData[] = await page.evaluate(async () => {
    // Fungsi untuk mendapatkan token dan data awal (seperti pada script Anda)
    const token = (document.querySelector("input[name='_token']") as HTMLInputElement)?.value;
    const options = Array.from(document.querySelectorAll("select[name='ticket_org'] option")).filter(x => x.getAttribute("value") != "");
    const scrapedResults: DestinationData[] = [];

    if (!token) {
        throw new Error('CSRF token tidak ditemukan.');
    }

    // Mengambil data destinasi untuk setiap kota asal
    for (const option of options) {
      const ids = option.getAttribute("value");
      const b = option.innerText;
      let dest = "";
      
      try {
        const f = await fetch("https://pelni.co.id/getdes", {
          "headers": {
            "content-type": "application/x-www-form-urlencoded;",
          },
          "body": "ticket_org=" + ids + "&_token=" + token,
          "method": "POST",
        });
        
        const text = await f.text();
        const div = document.createElement('div');
        div.innerHTML = text;
        
        dest = Array.from(div.querySelectorAll("option"))
            .filter(x => x.getAttribute("value") != "")
            .map(x => x.getAttribute("value"))
            .join(",");
            
        // Menambahkan jeda untuk menghindari throttling atau rate limiting
        await new Promise(resolve => setTimeout(resolve, 100));
        
      } catch (e) {
        console.error(`❌ Gagal mengambil destinasi untuk ID ${ids}:`, e);
      }

      const name = b.split("|")[1].split("-")[1].trim();
      const code = b.split("|")[1].split("-")[0].trim();
      const city = b.split("|")[0].trim();
      
      const result: DestinationData = {
        name,
        code,
        city,
        id: parseInt(ids as string),
        dest,
      };
      
      scrapedResults.push(result);
    }

    return scrapedResults;
  });

  // Menyimpan hasil scrapping ke file JSON
  const outputFilePath = path.join(__dirname, 'pelni-destinations.json');
  fs.writeFileSync(outputFilePath, JSON.stringify(results, null, 2));

  console.log(`✅ Data berhasil disimpan ke ${outputFilePath}`);

  await browser.close();
  console.log('Tutup browser.');
})();
