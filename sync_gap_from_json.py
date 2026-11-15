"""Synchronize edited Academy fill-gap sentences from JSON into the offline JS bundle.
Usage: python sync_gap_from_json.py; python test_v5.py; python test_bundle_v5.py
"""
import json,re
from pathlib import Path
R=Path(__file__).parent
items=json.loads((R/'academy_questions.json').read_text(encoding='utf8'))['lessons']
assert len(items)==36 and [v['id'] for v in items]==[f'w{i}' for i in range(36)]
gaps=[q['microsteps']['fillGap']['sentence'] for q in items]
assert all(set(x)=={'ru','en','kk'} and all(x[l].count('____')==1 for l in ['ru','en','kk']) for x in gaps)
source=(R/'app.js').read_text(encoding='utf8')
new='const LESSON_GAPS='+json.dumps(gaps,ensure_ascii=False,separators=(',',':'))+';\n'
source,n=re.subn(r'const LESSON_GAPS=.*?;\n(?=const MODULES=)',lambda _:new,source,count=1,flags=re.S)
assert n==1,'Cannot find LESSON_GAPS constant'
(R/'app.js').write_text(source,encoding='utf8')
print('Embedded',len(gaps),'localized fill-gap prompts for offline use.')
