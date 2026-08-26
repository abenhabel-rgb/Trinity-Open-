from pathlib import Path
from urllib.parse import urlparse
import asyncio, hashlib, csv, time
from playwright.async_api import async_playwright

ROOT = Path("/Volumes/EAGET/SKYLIT_RE")
OUT = ROOT / "fetch_interactive_v2"
PROFILE = ROOT / "webkit_profile"
NOTES = ROOT / "notes"

OUT.mkdir(parents=True, exist_ok=True)
PROFILE.mkdir(parents=True, exist_ok=True)
NOTES.mkdir(parents=True, exist_ok=True)

seen_urls = set()
seen_hashes = set()
visited_pages = set()
records = []

EXT = (
    ".js", ".css", ".json", ".svg", ".png",
    ".jpg", ".jpeg", ".webp", ".woff", ".woff2"
)

def safe_name(url, digest):
    p = urlparse(url)
    name = p.path.strip("/").replace("/", "__") or "index"

    if p.query:
        q = hashlib.sha256(p.query.encode()).hexdigest()[:10]
        name += "__" + q

    return f"{digest[:10]}__{name}"

async def main():
    async with async_playwright() as pw:

        context = await pw.webkit.launch_persistent_context(
            user_data_dir=str(PROFILE),
            headless=False,
            viewport={"width": 1500, "height": 950}
        )

        pages = context.pages
        page = pages[0] if pages else await context.new_page()

        async def capture(resp):
            url = resp.url
            p = urlparse(url)

            if p.hostname != "app.skylit.ai":
                return

            low = p.path.lower()

            # On archive le frontend normalement chargé.
            # Pas de rejeu d'API privées.
            if low.startswith("/api/"):
                return

            if not (
                "/_next/" in low
                or low.endswith(EXT)
            ):
                return

            if url in seen_urls:
                return

            seen_urls.add(url)

            try:
                body = await resp.body()
            except Exception:
                return

            digest = hashlib.sha256(body).hexdigest()

            if digest in seen_hashes:
                return

            seen_hashes.add(digest)

            dest = OUT / safe_name(url, digest)
            dest.write_bytes(body)

            records.append({
                "url": url,
                "file": dest.name,
                "bytes": len(body),
                "sha256": digest,
                "captured_at": time.strftime("%Y-%m-%d %H:%M:%S"),
            })

            print(
                "NEW",
                len(body),
                dest.name,
                flush=True
            )

        async def register_page(p):
            p.on("response", capture)

            def nav(frame):
                if frame == p.main_frame:
                    u = frame.url
                    if u.startswith("https://app.skylit.ai"):
                        if u not in visited_pages:
                            visited_pages.add(u)
                            print("PAGE", u, flush=True)

            p.on("framenavigated", nav)

        for p in context.pages:
            await register_page(p)

        context.on(
            "page",
            lambda p: asyncio.create_task(register_page(p))
        )

        try:
            await page.goto(
                "https://app.skylit.ai",
                wait_until="domcontentloaded",
                timeout=15000
            )
        except:
            pass

        print()
        print("===================================================")
        print("CAPTURE ACTIVE — NE PAS APPUYER SUR ENTRÉE")
        print()
        print("1. Connecte-toi normalement.")
        print("2. Ouvre toutes les pages accessibles :")
        print("   HeatSeeker / FlowSeeker / Falcon / Midas")
        print("   Atlas / Talon / Athena / Aegis / Metrics / Levels")
        print("3. Dans chaque outil, change de sous-page/ticker si possible.")
        print()
        print("Quand TOUT est terminé, tape exactement : STOP")
        print("===================================================")
        print()

        while True:
            cmd = await asyncio.to_thread(input, "Commande (STOP pour finir) > ")

            if cmd.strip().upper() == "STOP":
                break

            print("Capture toujours active. Tape STOP seulement à la fin.")

        inventory = NOTES / "INTERACTIVE_V2_INVENTORY.csv"

        with inventory.open(
            "w",
            newline="",
            encoding="utf-8-sig"
        ) as f:
            w = csv.DictWriter(
                f,
                fieldnames=[
                    "url",
                    "file",
                    "bytes",
                    "sha256",
                    "captured_at"
                ]
            )
            w.writeheader()
            w.writerows(records)

        routes = NOTES / "INTERACTIVE_V2_PAGES.txt"
        routes.write_text(
            "\n".join(sorted(visited_pages)),
            encoding="utf-8"
        )

        print()
        print("========== CAPTURE TERMINÉE ==========")
        print("Pages réellement visitées :", len(visited_pages))
        print("Assets uniques             :", len(seen_hashes))
        print("Inventaire :", inventory)
        print("Pages      :", routes)

        await context.close()

asyncio.run(main())
