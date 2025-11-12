import sys, asyncio, pathlib
from playwright.async_api import async_playwright

async def html_to_pdf(html_path: str, pdf_path: str):
    async with async_playwright() as p:
        browser = await p.chromium.launch()
        page = await browser.new_page()
        content = pathlib.Path(html_path).read_text(encoding="utf-8")
        await page.set_content(content, wait_until="load")
        await page.pdf(path=pdf_path, format="A4", print_background=True)
        await browser.close()

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python scripts/render_pdf.py <in.html> <out.pdf>")
        sys.exit(1)
    asyncio.run(html_to_pdf(sys.argv[1], sys.argv[2]))
