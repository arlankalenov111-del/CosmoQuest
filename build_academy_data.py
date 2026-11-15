"""Export Academy terminology and microstep prompts for editors.
Runtime remains bundled in app.js for offline, no-server startup.
"""
from pathlib import Path
import subprocess, json
R=Path(__file__).parent
s=(R/'app.js').read_text(encoding='utf-8')
start=s.index('const WORDS=[')
end=s.index('WORDS.forEach(',start)
js=s[start:end] + ';WORDS.forEach((w,i)=>{w.kk=KK_WORDS[i][0];w.defkk=KK_WORDS[i][1]});console.log(JSON.stringify({WORDS,KK_WORDS}));'
p=subprocess.run(['node','-e',js],capture_output=True,text=True,check=True)
words=json.loads(p.stdout)['WORDS']
raw=json.loads((R/'academy_questions.json').read_text(encoding='utf-8'))
byId={q['id']:q for q in raw.get('questions',raw.get('lessons',[]))}
modules=['space-basics','spacecraft','life-support','energy-engineering','space-environment','mission-planning']
linksets=[[1,0,2],[6,7,8],[12,14,17],[18,19,21],[25,24,29],[30,31,35]]
questions=[]
for index,w in enumerate(words):
 q=byId[w['id']]
 base=w['module']*6
 pool=[v for v in words if v['module']==w['module'] and v['id']!=w['id']]
 offset=(index*3+1)%len(pool)
 choices=[w,pool[offset],pool[(offset+2)%len(pool)]]
 matchIndices=[index,base+(index-base+2)%6,base+(index-base+4)%6]
 questions.append({
    'id':w['id'],'moduleId':modules[w['module']],
    'concept':{'ru':w['ru'],'en':w['en'],'kk':w['kk']},
    'definition':{'ru':w['defru'],'en':w['defen'],'kk':w['defkk']},
    'visual':{'emoji':w['icon'],'relatedConceptIds':['w'+str(i) for i in linksets[w['module']]]},
    'microsteps':{
       'intro':{'context':q.get('context',q.get('microsteps',{}).get('intro',{}).get('context')),'memorizationRequired':False},
       'multipleChoice':{'questionType':'definition-to-term','correctId':w['id'],'optionIds':sorted([x['id'] for x in choices],key=lambda z:int(z[1:]))},
       'matching':{'pairConceptIds':['w'+str(i) for i in matchIndices],'clockEnabledBySetting':True},
       'fillGap':{'sentence':q.get('fillGap',q.get('microsteps',{}).get('fillGap',{}).get('sentence')),'answerId':w['id'],'caseInsensitive':True},
       'errorReview':{'repeatUntilCorrect':True,'questionTypes':['multipleChoice','matching','fillGap']}
    }
 })
output={'schemaVersion':1,'name':'COSMOQUEST Space Academy','languages':['ru','en','kk'],'modules':modules,'spacedRepetition':{'strategy':'simple interval ladder','intervalDays':[1,3,7,14,30],'afterMistakeDays':1,'storage':'localStorage, under words[id].due','note':'Not full SM-2; no reminders or server scheduling.'},'lessons':questions}
(R/'academy_questions.json').write_text(json.dumps(output,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print('Exported',len(questions),'lessons with complete 5-step question definitions')
