import sys
from playwright.sync_api import sync_playwright

url = sys.argv[1] if len(sys.argv) > 1 else "http://localhost:8510"
with sync_playwright() as p:
    b = p.chromium.launch()
    pg = b.new_page(viewport={"width": 1440, "height": 900})
    pg.goto(url, wait_until="domcontentloaded")
    pg.get_by_text("Halo,", exact=False).first.wait_for(timeout=60000)
    pg.wait_for_timeout(1500)
    out = pg.evaluate("""() => {
        const btns = Array.from(document.querySelectorAll('button'));
        const target = btns.find(b => b.textContent.trim() === 'Ringkasan');
        if (!target) return 'NO BUTTON';
        let chain = [];
        let el = target;
        for (let i = 0; i < 6 && el; i++) {
            chain.push(el.tagName + ' | testid=' + (el.getAttribute('data-testid') || '') +
                       ' | class=' + (el.className || '').toString().slice(0, 120) +
                       ' | kind=' + (el.getAttribute('kind') || '') +
                       ' | aria=' + (el.getAttribute('aria-pressed') || el.getAttribute('aria-checked') || ''));
            el = el.parentElement;
        }
        return 'TARGET outerHTML: ' + target.outerHTML.slice(0, 600) + '\\nCHAIN:\\n' + chain.join('\\n');
    }""")
    print(out)
    b.close()
