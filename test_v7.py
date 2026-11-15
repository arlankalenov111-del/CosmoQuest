"""COSMOQUEST v7: actual browser checks for the former 'dead' or misleading CTAs."""
from pathlib import Path
from playwright.sync_api import sync_playwright
import traceback,json,sys
R=Path(__file__).parent
HTML=(R/'index.html').read_text(encoding='utf8')
CSS=(R/'styles.css').read_text(encoding='utf8')
JS=(R/'app.js').read_text(encoding='utf8')
JS=JS.replace('if(savedCorrupt)setTimeout(',"window.__CQTEST={get state(){return state},get ui(){return ui},words:WORDS,recordLessonLearning,render,save};if(savedCorrupt)setTimeout(")
errors=[];checks=[]

def check(name,fn):
 try:
  r=fn()
  if r is False:raise AssertionError('False')
  checks.append(('PASS',name));print('PASS',name,flush=True)
 except Exception as exc:
  checks.append(('FAIL',name));print('FAIL',name,repr(exc)[:450],flush=True)

def expect(val):
 assert val

def action(page,name):
 page.locator(f'[data-action="{name}"]').first.click(timeout=5000)

with sync_playwright() as pw:
 browser=pw.chromium.launch(headless=True,executable_path='/usr/bin/chromium',args=['--no-sandbox','--disable-dev-shm-usage','--disable-gpu'])
 page=browser.new_page(viewport={'width':1280,'height':900},reduced_motion='reduce',accept_downloads=True)
 page.set_default_timeout(5000)
 page.on('pageerror',lambda e:errors.append(str(e)))
 page.set_content(HTML)
 page.add_style_tag(content=CSS)
 page.evaluate('''() => Object.defineProperty(window,'localStorage',{configurable:true,value:{_v:{},getItem(k){return this._v[k]??null},setItem(k,v){this._v[k]=v},removeItem(k){delete this._v[k]}}})''')
 page.add_script_tag(content=JS)
 check('onboarding renders',lambda:expect(page.locator('[data-action="skip-onboard"]').count()==1))
 action(page,'skip-onboard')
 check('Home MOXIE is a targeted action',lambda:expect(page.locator('[data-action="home-moxie"]').count()==1))
 action(page,'home-moxie')
 check('MOXIE opens extended science content',lambda:expect(page.locator('.modal .science-more h3').count()==3 and page.locator('#main .science-card').count()==6))
 action(page,'science-activity')
 check('Science to mission is not a dead end',lambda:expect(page.locator('[data-action="mission-start"]').count()==1))
 page.locator('[data-nav="academy"]').first.click()
 page.locator('[data-action="academy-tab"][data-tab="dictionary"]').click()
 page.locator('[data-action="word-detail"]').first.click()
 check('Glossary details show extra info and navigation',lambda:expect(page.locator('.modal .card').count()>=2 and page.locator('.modal [data-action="open-lesson"]').count()==1))
 page.locator('.modal [data-action="word-detail"]').first.click()
 check('Related vocabulary opens another concept',lambda:expect(page.locator('.modal h2').count()==1))
 page.locator('.modal [data-action="open-lesson"]').click()
 check('Glossary-to-lesson closes overlay',lambda:expect(page.locator('.modal').count()==0 and page.locator('[data-action="lesson-intro-next"]').count()==1))
 page.locator('[data-nav="academy"]').first.click()
 page.locator('[data-action="academy-tab"][data-tab="match"]').click()
 # first concept w0; wrong answer -> retry same question.
 page.locator('[data-action="vocab-choice"]:not([data-value="w0"])').first.click()
 check('Incorrect concept does not reveal answer',lambda:expect(page.locator('.game-feedback').count()==1 and 'Планета —' not in page.locator('.game-feedback').inner_text()))
 action(page,'vocab-next')
 check('Retry preserves same question',lambda:expect(page.locator('[data-action="vocab-choice"][data-value="w0"]').count()==1 and '1/36' in page.locator('.game-shell').inner_text()))
 page.locator('[data-action="vocab-choice"][data-value="w0"]').click()
 action(page,'vocab-next')
 check('Correct concept advances next question',lambda:expect('2/36' in page.locator('.game-shell').inner_text()))
 # Science cards: actual extra text and activity link to water loop.
 page.locator('[data-nav="science"]').first.click()
 page.locator('[data-action="science-open"][data-id="water"]').click()
 check('NASA card detail has 3 distinct sections',lambda:expect(page.locator('.modal .science-more h3').count()==3))
 action(page,'science-activity')
 check('NASA water activity enters Water Loop',lambda:expect('Water Loop' in page.locator('#main').inner_text() and page.locator('[data-action="game-begin"]').count()==1))
 # Shop: preview comparison actually compares two avatars; purchase enabled / shortage links to games.
 page.locator('[data-nav="shop"]').first.click()
 page.locator('[data-action="shop-preview"][data-id="monster-zippy"]').first.click()
 check('Shop preview compares current and new monster',lambda:expect(page.locator('.modal .compare-avatar svg').count()==2))
 before_coins=page.evaluate("JSON.parse(localStorage.getItem('cosmoquest-mission-survival-v2')).coins")
 page.locator('.modal [data-action="shop-buy"]').click()
 check('Monster purchase updates owned & balance',lambda:expect(page.evaluate("(()=>{let s=JSON.parse(localStorage.getItem('cosmoquest-mission-survival-v2'));return s.monster==='zippy'&&s.owned.includes('monster-zippy')})()") and page.evaluate("JSON.parse(localStorage.getItem('cosmoquest-mission-survival-v2')).coins")==before_coins-60))
 page.locator('[data-action="shop-preview"][data-id="monster-lumi"]').first.click()
 check('Shortage offers an earn-coins action, not dead buy',lambda:expect(page.locator('.modal [data-action="shop-earn"]').count()==1 and 'Не хватает' in page.locator('.modal').inner_text()))
 action(page,'shop-earn')
 check('Earn-coins takes user to mini-games',lambda:expect(page.locator('#main .game-grid').count()==1))
 # Review all words after academy completion can satisfy word daily task.
 page.evaluate('''() => {let a=window.__CQTEST;for(let w of a.words){a.state.words[w.id]={correct:1,streak:1,mistakes:0,intervalDays:1,due:'2020-01-01',lastReviewed:'2020-01-01'};a.state.lessons.push(w.id);}a.state.daily.progress.words=0;a.state.daily.newWords=[];a.save();}''')
 page.locator('[data-nav="daily"]').first.click()
 action(page,'daily-go')
 check('Daily word CTA points at review after all 36 words',lambda:expect(page.locator('.due-review').count()==1))
 page.evaluate("window.__CQTEST.recordLessonLearning('w0',0)")
 page.evaluate("window.__CQTEST.recordLessonLearning('w1',0)")
 page.evaluate("window.__CQTEST.recordLessonLearning('w2',0)")
 page.locator('[data-nav="daily"]').first.click()
 check('Daily concept goal works for mastered concepts',lambda:expect(page.locator('[data-action="daily-claim"][data-key="words"]').count()==1))
 # Detailed report instead of repeating results.
 page.evaluate("() => {window.__CQTEST.state.settings.difficulty='easy';window.__CQTEST.save()}")
 page.locator('[data-nav="mission"]').first.click()
 action(page,'mission-start')
 for sol,choice in enumerate([2,0,2,0,1]):
  page.locator(f'[data-action="mission-select"][data-index="{choice}"]').click()
  action(page,'mission-commit')
  if sol<4 and page.locator('[data-action="mission-next"]').count():action(page,'mission-next')
  elif sol<4:break
 if page.locator('[data-action="mission-report"]').count():action(page,'mission-report')
 check('Full mission report includes choice-by-choice log',lambda:expect(page.locator('.report-entry').count()>=3 and page.locator('.report-history').count()==1))
 # Show explanations only for the active question; timer off to avoid race.
 page.evaluate("() => {window.__CQTEST.state.settings.timers=false;window.__CQTEST.state.settings.explanations=false;window.__CQTEST.save()}")
 page.locator('[data-nav="games"]').first.click()
 page.locator('[data-action="game-open"][data-game="recall"]').click()
 action(page,'game-begin')
 page.locator('#recall-answer').fill('nonsensical-test-answer')
 action(page,'recall-submit')
 check('Hidden answer explanation is on-demand',lambda:expect(page.locator('[data-action="show-explanation"]').count()==1))
 action(page,'show-explanation')
 check('Explanation button reveals current explanation',lambda:expect(page.locator('[data-action="show-explanation"]').count()==0))
 action(page,'recall-next')
 page.locator('#recall-answer').fill('wrong-again')
 action(page,'recall-submit')
 check('Explanation does not leak into later question',lambda:expect(page.locator('[data-action="show-explanation"]').count()==1))
 check('No JS exceptions',lambda:expect(not errors))
 # screenshot meaningful new UI
 page.locator('[data-nav="science"]').first.click()
 page.locator('[data-action="science-open"][data-id="moxie"]').click()
 page.screenshot(path=str(R/'science-details-v7.png'),full_page=True)
 browser.close()

print('SUMMARY',sum(x[0]=='PASS' for x in checks),'PASS',sum(x[0]=='FAIL' for x in checks),'FAIL', 'JS',errors[:4]);
if any(c[0]=='FAIL' for c in checks) or errors:sys.exit(1)
