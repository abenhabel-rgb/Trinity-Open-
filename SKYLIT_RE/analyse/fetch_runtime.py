from pathlib import Path
from urllib.parse import urlparse
import asyncio, hashlib
from playwright.async_api import async_playwright

ROOT = Path("/Volumes/EAGET/SKYLIT_RE")
OUT = ROOT / "fetch_runtime"
OUT.mkdir(parents=True, exist_ok=True)

BASE = "https://app.skylit.ai"

ASSET_EXT = (
    ".js", ".css", ".json", ".svg", ".png", ".jpg",
    ".jpeg", ".webp", ".woff", ".woff2"
)

seen_urls = set()
seen_hashes = set()

def safe_name(url):
    p = urlparse(url)
    name = p.path.strip("/").replace("/", "__") or "index"
    if p.query:
        q = hashlib.sha256(p.query.encode()).hexdigest()[:10]
        name += "__" + q
    return name

async def main():
    async with async_playwright() as pw:
        browser = await pw.webkit.launch(headless=False)

        context = await browser.new_context()
        page = await context.new_page()

        async def on_response(resp):
            url = resp.url
            p = urlparse(url)

            if p.hostname != "app.skylit.ai":
                return

            low = p.path.lower()

            # Archive uniquement les ressources frontend.
            # Ne rejoue pas les API privées.
            if not (
                "/_next/" in low
                or low.endswith(ASSET_EXT)
            ):
                return

            if url in seen_urls:
                return
            seen_urls.add(url)

            try:
                body = await resp.body()
            except Exception:
                return

            h = hashlib.sha256(body).hexdigest()
            if h in seen_hashes:
                return
            seen_hashes.add(h)

            dest = OUT / safe_name(url)
            dest.write_bytes(body)

            print("SAVE", len(body), dest.name)

        page.on("response", on_response)

        print()
        print("========================================")
        print("Connecte-toi à Skylit dans la fenêtre.")
        print("Ensuite reviens ici et appuie sur ENTRÉE.")
        print("========================================")
        print()

        await page.goto(BASE)

        await asyncio.to_thread(input)

        visited = set()
        queue = [BASE]

        while queue and len(visited) < 200:
            url = queue.pop(0)

            if url in visited:
                continue
            visited.add(url)

            print("\nVISIT", url)

            try:
                await page.goto(
                    url,
                    wait_until="domcontentloaded",
                    timeout=12000
                )
            except Exception:
                pass

            await page.wait_for_timeout(1500)

            try:
                links = await page.eval_on_selector_all(
                    "a[href]",
                    """els => els.map(e => e.href)"""
                )
            except Exception:
                links = []

            for link in links:
                p = urlparse(link)

                if p.hostname != "app.skylit.ai":
                    continue

                # Ignore logout/auth actions
                low = p.path.lower()
                if any(x in low for x in [
                    "logout", "signout", "delete", "billing"
                ]):
                    continue

                clean = link.split("#")[0]

                if clean not in visited and clean not in queue:
                    queue.append(clean)

        print()
        print("========================================")
        print("RUNTIME FETCH TERMINÉ")
        print("Pages visitées :", len(visited))
        print("Assets uniques :", len(seen_hashes))
        print("Dossier :", OUT)
        print("========================================")

        await browser.close()

asyncio.run(main())
