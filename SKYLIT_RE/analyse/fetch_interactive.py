from pathlib import Path
from urllib.parse import urlparse
import asyncio, hashlib, csv
from playwright.async_api import async_playwright

ROOT = Path("/Volumes/EAGET/SKYLIT_RE")
OUT = ROOT / "fetch_interactive"
NOTES = ROOT / "notes"

OUT.mkdir(parents=True, exist_ok=True)
NOTES.mkdir(parents=True, exist_ok=True)

seen_urls = set()
seen_hashes = set()
records = []

EXT = (
    ".js", ".css", ".json", ".svg", ".png",
    ".jpg", ".jpeg", ".webp", ".woff", ".woff2"
)

def filename(url, digest):
    p = urlparse(url)
    name = p.path.strip("/").replace("/", "__") or "index"
    return f"{digest[:10]}__{name}"

async def main():
    async with async_playwright() as pw:
        browser = await pw.webkit.launch(headless=False)
        context = await browser.new_context()
        page = await context.new_page()

        async def capture(resp):
            url = resp.url
            p = urlparse(url)

            if p.hostname != "app.skylit.ai":
                return

            low = p.path.lower()

            # Assets frontend uniquement
            if low.startswith("/api/") or "/auth/" in low:
                return

            if not ("/_next/" in low or low.endswith(EXT)):
                return

            if url in seen_urls:
                return

            seen_urls.add(url)

            try:
                body = await resp.body()
            except:
                return

            digest = hashlib.sha256(body).hexdigest()

            if digest in seen_hashes:
                return

            seen_hashes.add(digest)

            dest = OUT / filename(url, digest)
            dest.write_bytes(body)

            records.append({
                "url": url,
                "file": dest.name,
                "bytes": len(body),
                "sha256": digest,
            })

            print("NEW", len(body), dest.name)

        page.on("response", capture)

        await page.goto(
            "https://app.skylit.ai",
            wait_until="domcontentloaded",
            timeout=15000
        )

        print()
        print("==============================================")
        print("NAVIGUE MAINTENANT MANUELLEMENT DANS WEBKIT")
        print("Ouvre HeatSeeker, FlowSeeker, Falcon, Midas,")
        print("Atlas, Talon, Metrics, Levels, etc.")
        print()
        print("Le Terminal capture automatiquement les assets.")
        print("Quand tu as terminé, reviens ici et appuie ENTRÉE.")
        print("==============================================")
        print()

        await asyncio.to_thread(input)

        inventory = NOTES / "INTERACTIVE_INVENTORY.csv"

        with inventory.open(
            "w", newline="", encoding="utf-8-sig"
        ) as f:
            w = csv.DictWriter(
                f,
                fieldnames=["url","file","bytes","sha256"]
            )
            w.writeheader()
            w.writerows(records)

        print()
        print("===== CAPTURE TERMINÉE =====")
        print("Assets uniques :", len(seen_hashes))
        print("Inventaire :", inventory)

        await browser.close()

asyncio.run(main())
