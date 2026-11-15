"""End-to-end behavior checks for Academy v5 + existing COSMOQUEST features."""
from pathlib import Path
from http.server import ThreadingHTTPServer, SimpleHTTPRequestHandler
from playwright.sync_api import sync_playwright
import threading, sys, json, time
ROOT=Path(__file__).parent
KEY='cosmoquest-mission-survival-v2'
class Handler(SimpleHTTPRequestHandler):
    def __init__(self,*a,**k): super().__init__(*a,directory=str(ROOT),**k)
    def log_message(self,*args):pass
passes=[]; failures=[];errors=[]
def check(name,fn):
 try:
  result=fn()
  if result is False:raise AssertionError('returned False')
  passes.append(name);print('PASS',name,flush=True)
 except Exception as e:
  failures.append((name,str(e)[:400]));print('FAIL',name,str(e)[:350],flush=True)
def val(page):return page.evaluate(f'JSON.parse(localStorage.getItem("{KEY}"))')
def click(page,a):page.locator('[data-action="'+a+'"]').first.click(timeout=4000)
def openlesson(page,id):page.locator(f'[data-action="open-lesson"][data-id="{id}"]').click()
def match_all(page, base=0):
 for id in page.locator('[data-lesson-match]').evaluate_all('(els)=>els.map(el=>el.dataset.lessonMatch)'):
  page.locator(f'[data-lesson-match="{id}"]').select_option(id)
def lesson(page,word_index,language='ru',wrong=False):
 id='w'+str(word_index)
 defs=page.locator('[data-action="open-lesson"][data-id="'+id+'"]')
 if defs.count(): defs.click()
 else: assert page.locator('h2').filter(has_text=('Урок' if language=='ru' else 'Lesson' if language=='en' else 'Сабақ')).count()
 assert page.locator('.lesson-step-label').count()==1
 click(page,'lesson-intro-next')
 if wrong:
  page.locator('[data-action="lesson-choice"]').filter(has_not=page.locator('[data-value="'+id+'"]').first).first.click() if False else page.locator('[data-action="lesson-choice"]:not([data-value="'+id+'"])').first.click()
 else:page.locator('[data-action="lesson-choice"][data-value="'+id+'"]').click()
 click(page,'lesson-go-matching')
 if not wrong:match_all(page)
 else:
  pairs=page.locator('[data-lesson-match]').evaluate_all('(els)=>els.map(el=>el.dataset.lessonMatch)')
  page.locator(f'[data-lesson-match="{pairs[0]}"]').select_option(pairs[0])
 click(page,'lesson-check-matching');click(page,'lesson-go-gap')
 words=[x for x in val(page).get('lessons',[])]; _=words
 if wrong:ans='deliberately wrong'
 else:
  # selected language correct term from source JSON stored in app words but visible at intro H2 'Урок: Ракета'.
  # We set answer from a tested localization corpus.
  ans=page.locator('h2').first.inner_text().split(':',1)[-1].strip()
 page.locator('#lesson-gap-input').fill(ans)
 page.locator('[data-form="lesson-gap"] button[type="submit"]').click()
 click(page,'lesson-go-review')
 if wrong:
  assert page.locator('[data-action="lesson-complete"]').count()==0
  for _ in range(8):
   if page.locator('[data-action="lesson-review-choice"]').count():
    page.locator(f'[data-action="lesson-review-choice"][data-value="{id}"]').click()
   elif page.locator('[data-action="lesson-review-match"]').count():
    # correct id is displayed as the correct option in list with definition; derive from choices + error progress and matching dictionary: we use source word mapping. 
    definition=page.locator('.academy-lesson .lead').first.inner_text()
    source=['w'+str(i) for i in range(word_index//6*6,word_index//6*6+6)]
    # choose from matching options by matching definition from original source? use title stored in data via beginning words list,
    # using source JS content cannot access lexical WORDS via global. For item use explicit correct matching selector index calculation.
    pairs=page.locator('#lesson-review-select option').all()
    # compare text to matching title from full original data parsed fixture variable.
    term_by_definition = defs_ru.get(definition)
    assert term_by_definition,('definition missing', definition)
    page.locator('#lesson-review-select').select_option(label=term_by_definition)
    click(page,'lesson-review-match')
   elif page.locator('.academy-lesson [data-form="lesson-gap"]').count():
    page.locator('#lesson-gap-input').fill(ans if ans!='deliberately wrong' else page.locator('h2').first.inner_text().split(':',1)[-1].strip())
    page.locator('.academy-lesson [data-form="lesson-gap"] button[type="submit"]').click()
   else:break
 assert page.locator('[data-action="lesson-complete"]').count()==1
 click(page,'lesson-complete')
 assert page.locator('[data-action="lesson-next"]').count()==1
# Parse glossary defs/labels from app source regex not needed derive by visiting glossary beforehand.
with sync_playwright() as playwright:
 browser=playwright.chromium.launch(headless=True,executable_path='/usr/bin/chromium',args=['--no-sandbox','--disable-dev-shm-usage','--disable-gpu'])
 page=browser.new_page(viewport={'width':1280,'height':800},reduced_motion='reduce')
 page.on('pageerror',lambda exc:errors.append(str(exc)))
 page.set_default_timeout(3500)
 page.set_content((ROOT/'index.html').read_text(encoding='utf-8'))
 page.add_style_tag(content=(ROOT/'styles.css').read_text(encoding='utf-8'))
 page.evaluate("() => {Object.defineProperty(window,'localStorage',{configurable:true,value:{_v:{},getItem(k){return this._v[k]??null},setItem(k,v){this._v[k]=v},removeItem(k){delete this._v[k]}}})}")
 page.add_script_tag(content=(ROOT/'app.js').read_text(encoding='utf-8'))
 check('Initial onboarding',lambda:page.locator('[data-action="skip-onboard"]').count()==1)
 click(page,'skip-onboard')
 page.locator('[data-nav="academy"]').first.click()
 defs_ru={}
 for item in page.locator('.vocab-item').all():pass
 page.locator('[data-action="academy-tab"][data-tab="dictionary"]').click()
 for row in page.locator('.vocab-item').all():
  key=row.locator('small').first.inner_text()
  value=row.locator('strong').first.inner_text()
  defs_ru[key]=value
 page.locator('[data-action="academy-tab"][data-tab="modules"]').click()
 check('Review tab exists',lambda:page.locator('[data-action="academy-tab"][data-tab="review"]').count()==1)
 check('Six modules still available',lambda:page.locator('.module-card').count()==6)
 openlesson(page,'w0')
 check('First step shows context and no forced answer',lambda:page.locator('.lesson-context').count()==1 and page.locator('[data-action="lesson-choice"]').count()==0)
 check('Progress bar has five steps',lambda:page.locator('.lesson-step-dots span').count()==5)
 check('Intro localized in Russian',lambda:'Планета' in page.locator('.lesson-context').inner_text())
 click(page,'lesson-intro-next')
 check('Multiple choice now follows introduction',lambda:page.locator('[data-action="lesson-choice"]').count()==3)
 page.locator('[data-action="lesson-choice"]:not([data-value="w0"])').first.click()
 check('Incorrect answer recorded with feedback',lambda:page.locator('.lesson-feedback.is-try').count()==1)
 click(page,'lesson-go-matching')
 check('Matching has three pairs',lambda:page.locator('[data-lesson-match]').count()==3)
 check('Visible timer in match when enabled',lambda:page.locator('#lesson-match-time').count()==1)
 pairs=page.locator('[data-lesson-match]').evaluate_all('(els)=>els.map(el=>el.dataset.lessonMatch)')
 page.locator(f'[data-lesson-match="{pairs[0]}"]').select_option(pairs[0])
 click(page,'lesson-check-matching')
 check('Wrong matches marked, feedback shown',lambda:page.locator('.lesson-wrong').count()==2 and page.locator('.lesson-feedback').count()==1)
 click(page,'lesson-go-gap')
 check('Fill gap has meaningful sentence',lambda:'обращается вокруг звезды' in page.locator('.academy-lesson').inner_text())
 page.locator('#lesson-gap-input').fill('faketerm')
 page.locator('[data-form="lesson-gap"] button[type="submit"]').click()
 check('Wrong gap feeds into remedial stage',lambda:page.locator('.lesson-feedback.is-try').count()==1)
 click(page,'lesson-go-review')
 check('Must correct errors, not bypass them',lambda:page.locator('[data-action="lesson-complete"]').count()==0)
 # First error: incorrect multiple choice, repeat once incorrectly then correctly
 page.locator('[data-action="lesson-review-choice"]:not([data-value="w0"])').first.click()
 check('Wrong repeat does not advance',lambda:page.locator('[data-action="lesson-review-choice"]').count()==3)
 page.locator('[data-action="lesson-review-choice"][data-value="w0"]').click()
 check('Next erroneous matching pair offered',lambda:page.locator('[data-action="lesson-review-match"]').count()==1)
 for _ in range(2):
  text=page.locator('.academy-lesson .lead').first.inner_text()
  page.locator('#lesson-review-select').select_option(label=defs_ru[text])
  click(page,'lesson-review-match')
 page.locator('#lesson-gap-input').fill('Планета')
 page.locator('[data-form="lesson-gap"] button[type="submit"]').click()
 check('Finishing only after all mistakes resolved',lambda:page.locator('[data-action="lesson-complete"]').count()==1)
 before=val(page)['coins'];click(page,'lesson-complete');after=val(page)
 check('Mistake lesson saved once',lambda:'w0' in after['lessons'] and after['words']['w0']['mistakes']>0 and after['words']['w0']['intervalDays']==1 and after['coins']>before)
 check('Next lesson available immediately',lambda:page.locator('[data-action="lesson-next"]').count()==1)
 click(page,'lesson-next')
 check('Next lesson opened without map',lambda:'Звезда' in page.locator('h2').first.inner_text() and page.locator('.lesson-context').count()==1)
 # All six lessons for one module using Next each time
 for i in range(1,6):
  click(page,'lesson-intro-next')
  page.locator(f'[data-action="lesson-choice"][data-value="w{i}"]').click()
  click(page,'lesson-go-matching')
  match_all(page);click(page,'lesson-check-matching');click(page,'lesson-go-gap')
  label=page.locator('h2').first.inner_text().split(':',1)[-1].strip()
  page.locator('#lesson-gap-input').fill(label)
  page.locator('[data-form="lesson-gap"] button[type="submit"]').click()
  click(page,'lesson-go-review');click(page,'lesson-complete')
  check('Lesson '+str(i+1)+' complete',lambda i=i:f'w{i}' in val(page)['lessons'])
  click(page,'lesson-next')
 check('Last lesson Next enters final module challenge',lambda:page.locator('[data-action="final-submit"]').count()==1)
 for i in range(6):page.locator('[data-final="w'+str(i)+'"]').select_option('w'+str(i))
 click(page,'final-submit')
 check('Module final still works',lambda:0 in val(page)['moduleFinals'])
 check('Learnt words have due dates',lambda:all(val(page)['words'][f'w{i}']['due'] for i in range(6)))
 click(page,'final-back')
 page.locator('[data-action="academy-tab"][data-tab="review"]').click()
 check('Review due tab displays schedule',lambda:'Повторение по расписанию' in page.locator('#main').inner_text())
 check('No reviews due on first day',lambda:page.locator('[data-action="review-open"]').count()==0)
 # Repeat first lesson deliberately without mistakes, measure no duplicate lesson coins.
 page.locator('[data-action="academy-tab"][data-tab="modules"]').click()
 first=val(page);openlesson(page,'w0')
 click(page,'lesson-intro-next');page.locator('[data-action="lesson-choice"][data-value="w0"]').click();click(page,'lesson-go-matching');match_all(page);click(page,'lesson-check-matching');click(page,'lesson-go-gap');page.locator('#lesson-gap-input').fill('Планета');page.locator('[data-form="lesson-gap"] button[type="submit"]').click();click(page,'lesson-go-review');click(page,'lesson-complete')
 second=val(page)
 check('No duplicate lesson completion',lambda:len(second['lessons'])==len(first['lessons']) and second['stats']['lessonCompleted']==first['stats']['lessonCompleted'])
 check('Repetition updates interval',lambda:second['words']['w0']['streak']==1 and second['words']['w0']['due'])
 # RU EN KK selected language, correct gap input
 for lng,idx,label in [('en',6,'Rocket'),('kk',12,'Оттегі'),('ru',18,'Солнечная панель')]:
  page.locator('[data-nav="settings"]').first.click()
  page.locator('[data-setting="language"]').select_option(lng)
  page.locator('[data-nav="academy"]').first.click()
  openlesson(page,'w'+str(idx))
  check(lng+' localized intro',lambda label=label:label in page.locator('.lesson-context').inner_text())
  click(page,'lesson-intro-next');page.locator(f'[data-action="lesson-choice"][data-value="w{idx}"]').click();click(page,'lesson-go-matching');match_all(page);click(page,'lesson-check-matching');click(page,'lesson-go-gap')
  page.locator('#lesson-gap-input').fill(label)
  page.locator('[data-form="lesson-gap"] button[type="submit"]').click();click(page,'lesson-go-review')
  check(lng+' localized gap accepted',lambda:page.locator('[data-action="lesson-complete"]').count()==1)
  click(page,'lesson-complete');click(page,'lesson-back')
 # No unrelated parts changed.
 page.locator('[data-nav="science"]').first.click()
 check('NASA source buttons preserved',lambda:page.locator('.science-card a[href]').count()==6)
 check('NASA Explore buttons remain removed',lambda:page.locator('.science-card .btn[data-action="science-open"]').count()==0)
 page.locator('[data-nav="games"]').first.click()
 for game in ['recall','relay','power','water','sort','fix']:
  page.locator('[data-action="game-open"][data-game="'+game+'"]').click()
  check('Mini-game opens '+game,lambda:page.locator('[data-action="game-begin"]').count()==1)
  click(page,'game-begin');click(page,'game-back')
 page.locator('[data-nav="shop"]').first.click()
 check('Monster shop preserved',lambda:page.locator('.monster-product').count()>=8)
 for width in [360,390,768,1024,1440]:
  page.set_viewport_size({'width':width,'height':850})
  check(f'No horizontal overflow {width}',lambda:page.evaluate('document.documentElement.scrollWidth <= innerWidth'))
 page.screenshot(path=str(ROOT/'academy-preview-v5.png'),full_page=True)
 check('No JS errors',lambda:not errors)
 print('TOTAL',len(passes)+len(failures),'PASS',len(passes),'FAIL',len(failures),'ERRORS',errors)
 browser.close()
sys.exit(1 if failures or errors else 0)
