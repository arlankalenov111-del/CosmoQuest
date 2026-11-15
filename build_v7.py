"""Create a self-contained COSMOQUEST HTML file with JS at the end of BODY.
No package manager, backend or build dependency required.
"""
from pathlib import Path
ROOT=Path(__file__).resolve().parent
html=(ROOT/'index.html').read_text(encoding='utf-8')
css=(ROOT/'styles.css').read_text(encoding='utf-8')
js=(ROOT/'app.js').read_text(encoding='utf-8').replace('</script','<\\/script')
assert '<link rel="stylesheet" href="styles.css">' in html
assert '<script src="app.js" defer></script>' in html
html=html.replace('<link rel="stylesheet" href="styles.css">','<style>\n'+css+'\n</style>')
html=html.replace('<script src="app.js" defer></script>','')
html=html.replace('</body>','<script>\n'+js+'\n</script>\n</body>')
assert html.count('function modalContent()')==1
assert 'src="app.js"' not in html
assert 'href="styles.css"' not in html
(ROOT/'COSMOQUEST_single.html').write_text(html,encoding='utf-8')
(ROOT.parent/'COSMOQUEST_v7.html').write_text(html,encoding='utf-8')
print(f'Generated standalone HTML ({len(html.encode("utf8")):,} bytes)')
