from pathlib import Path
from playwright.sync_api import sync_playwright
R=Path(__file__).parent
html=(R/'COSMOQUEST_single.html').read_text(encoding='utf8')
assert 'src="app.js"' not in html and 'href="styles.css"' not in html
assert html.index('id="modal"')<html.index('function modalContent()'), 'JS must run after the DOM'
errs=[]
with sync_playwright() as pw:
 browser=pw.chromium.launch(headless=True,executable_path='/usr/bin/chromium',args=['--no-sandbox','--disable-dev-shm-usage','--disable-gpu'])
 for width in (360,390,768,1024,1440):
  page=browser.new_page(viewport={'width':width,'height':850},reduced_motion='reduce')
  page.on('pageerror',lambda err:errs.append(str(err)))
  page.set_content(html)
  assert page.locator('[data-action="skip-onboard"]').count()==1
  page.locator('[data-action="skip-onboard"]').click()
  page.locator('[data-nav="academy"]:visible').first.click()
  page.locator('[data-action="academy-tab"][data-tab="dictionary"]').click()
  page.locator('[data-action="word-detail"]').first.click()
  assert page.locator('.modal [data-action="open-lesson"]').count()==1
  assert page.evaluate('document.documentElement.scrollWidth<=window.innerWidth+2'), f'horizontal overflow at {width}'
  page.locator('.modal [data-action="modal-close"]').first.click()
  page.locator('#top-avatar').click()
  page.locator('[data-action="go-shop"]').click()
  assert page.locator('.shop-item').count()==8
  page.locator('[data-action="shop-preview"]').first.click()
  assert page.locator('.monster-compare .compare-avatar').count()==2
  assert page.evaluate('document.documentElement.scrollWidth<=window.innerWidth+2'), f'shop overflow at {width}'
  print('PASS standalone CSS/JS + glossary/shop + no overflow',width)
  page.close()
 browser.close()
assert not errs,errs
print('PASS standalone has no JavaScript exceptions')
