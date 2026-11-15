from pathlib import Path
from playwright.sync_api import sync_playwright
import json
root=Path(__file__).parent; html=(root/'index.html').read_text();css=(root/'styles.css').read_text();js=(root/'app.js').read_text();key='cosmoquest-mission-survival-v2'
with sync_playwright() as p:
 b=p.chromium.launch(headless=True,executable_path='/usr/bin/chromium',args=['--no-sandbox'])
 def page_with(data={}):
  pg=b.new_page(viewport={'width':1024,'height':800})
  pg.set_content(html)
  pg.add_style_tag(content=css)
  pg.evaluate('''init => { Object.defineProperty(window,'localStorage',{configurable:true,value:{_v:{...init},getItem(k){return this._v[k]??null},setItem(k,v){this._v[k]=v},removeItem(k){delete this._v[k]}}});}''',data)
  pg.add_script_tag(content=js)
  return pg
 pg=page_with();pg.locator('[data-action="skip-onboard"]').click();pg.locator('[data-nav="mission"]').first.click();pg.locator('[data-action="mission-start"]').click();pg.locator('[data-action="mission-select"]').first.click();pg.locator('[data-action="mission-commit"]').click()
 before=json.loads(pg.evaluate("localStorage.getItem('"+key+"')"))
 print('POST-COMMIT',before['mission']['sol'],before['mission']['completed'],before['mission']['resources'])
 assert before['mission']['sol']==1
 pg.locator('[data-nav="home"]').first.click()
 pg.locator('[data-nav="mission"]').first.click()
 assert pg.locator('.sol-tag').inner_text().startswith('⚡ SOL 2')==False # different sol icon expected
 assert 'SOL 2' in pg.locator('.sol-tag').inner_text()
 after=json.loads(pg.evaluate("localStorage.getItem('"+key+"')"))
 assert before['mission']==after['mission']
 pg.close()
 pg2=page_with({key:json.dumps(after,ensure_ascii=False)})
 assert pg2.locator('#top-coins').inner_text()==str(after['coins'])
 pg2.locator('[data-nav="mission"]').first.click()
 assert 'SOL 2' in pg2.locator('.sol-tag').inner_text()
 print('RESTORE OK')
 pg2.locator('[data-nav="games"]').first.click()
 pg2.locator('[data-action="game-open"][data-game="power"]').click();pg2.locator('[data-action="game-begin"]').click();[pg2.locator('#power-'+k).fill(v) for k,v in [('life','45'),('heat','30'),('science','25')]];pg2.locator('[data-action="power-submit"]').click()
 mid=json.loads(pg2.evaluate("localStorage.getItem('"+key+"')"));print('GAME WINS',mid['miniWins'],mid['coins'])
 pg2.locator('[data-action="game-retry"]').click();pg2.locator('[data-action="game-begin"]').click();[pg2.locator('#power-'+k).fill(v) for k,v in [('life','45'),('heat','30'),('science','25')]];pg2.locator('[data-action="power-submit"]').click()
 duplicate=json.loads(pg2.evaluate("localStorage.getItem('"+key+"')"))
 assert mid['coins']==duplicate['coins']
 print('NO DUPLICATE GAME REWARD')
 pg2.locator('[data-nav="daily"]').first.click();pg2.locator('[data-action="daily-claim"][data-key="games"]').click()
 claimed=json.loads(pg2.evaluate("localStorage.getItem('"+key+"')"));pg2.locator('[data-nav="home"]').first.click();pg2.locator('[data-nav="daily"]').first.click()
 assert pg2.locator('[data-action="daily-claim"][data-key="games"]').count()==0
 assert claimed['coins']==json.loads(pg2.evaluate("localStorage.getItem('"+key+"')"))['coins']
 print('NO DUPLICATE DAILY REWARD')
 b.close()
