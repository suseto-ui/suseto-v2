import re, json, zipfile, io, base64
from collections import Counter,defaultdict
from datetime import datetime, timezone
from pathlib import Path
from .registry_store import _load, _save, export_csv_text, import_csv_text
ROOT=Path(__file__).resolve().parent.parent/'data'; SESS=ROOT/'sessions.json'; USERS=ROOT/'users.json'
def _now():return datetime.now(timezone.utc).isoformat()
def _sessions():
 try:return json.loads(SESS.read_text()) if SESS.exists() else []
 except Exception:return []
def _write(x):ROOT.mkdir(exist_ok=True);SESS.write_text(json.dumps(x,ensure_ascii=False,indent=2))
def session_create(name):
 x={'id':datetime.now().strftime('%Y%m%d%H%M%S%f'),'name':str(name or 'Inventura').strip()[:80],'created_at':_now(),'scans':[]};s=_sessions();s.insert(0,x);_write(s);return x
def session_add(i,payload):
 s=_sessions()
 for x in s:
  if x['id']==i:
   x['scans'].append({'payload':str(payload).strip(),'at':_now()});_write(s);return x
 raise ValueError('Relace nebyla nalezena.')
def session_list():return _sessions()
def profile(payload):
 p=str(payload or '');alpha={'digits':bool(re.fullmatch(r'\d+',p)),'hex':bool(re.fullmatch(r'[0-9A-Fa-f]+',p)) and len(p)%2==0,'base64':bool(re.fullmatch(r'[A-Za-z0-9+/=_-]{8,}',p)),'url':p.startswith(('http://','https://')),'wifi':p.startswith('WIFI:'),'jwt_like':p.count('.')==2}
 seps=sorted(set(c for c in p if not c.isalnum()))
 return {'payload':p,'length':len(p),'alphabet':alpha,'separators':seps,'prefix':re.split(r'[^A-Za-z0-9]+',p)[0] if p else '', 'segments':re.split(r'[^A-Za-z0-9]+',p),'hex':p.encode().hex(' ').upper()}
def diff(values):
 vals=[str(v) for v in values if str(v)]
 if not vals:return {'rows':[],'common_prefix':'','common_suffix':''}
 pre='';
 for chars in zip(*vals):
  if len(set(chars))==1:pre+=chars[0]
  else:break
 rev=[x[::-1] for x in vals];suf=''
 for chars in zip(*rev):
  if len(set(chars))==1:suf+=chars[0]
  else:break
 maxlen=max(map(len,vals));rows=[]
 for i in range(maxlen):
  chars=[v[i] if i<len(v) else '∅' for v in vals];rows.append({'position':i,'values':chars,'same':len(set(chars))==1})
 return {'rows':rows,'common_prefix':pre,'common_suffix':suf[::-1]}
def patterns(values):
 groups=defaultdict(list)
 for x in values:
  p=profile(x);key=f"{p['prefix']}|{p['length']}|{','.join(p['separators'])}";groups[key].append(x)
 return [{'pattern':k,'count':len(v),'examples':v[:5]} for k,v in groups.items()]
def gs1(raw):
 x=re.sub(r'\D','',str(raw));
 if len(x) not in (8,12,13,14):return {'valid':False,'reason':'GTIN musí mít 8, 12, 13 nebo 14 číslic včetně kontrolní.'}
 total=sum(int(d)*(3 if i%2==0 else 1) for i,d in enumerate(x[-2::-1]));check=(10-total%10)%10
 return {'valid':check==int(x[-1]),'digits':x,'expected_check':check,'type':f'GTIN-{len(x)}'}
def backup():
 data=_load();buf=io.BytesIO()
 with zipfile.ZipFile(buf,'w',zipfile.ZIP_DEFLATED) as z:
  z.writestr('registry.json',json.dumps(data,ensure_ascii=False,indent=2));z.writestr('registry.csv',export_csv_text());z.writestr('sessions.json',json.dumps(_sessions(),ensure_ascii=False,indent=2));
  z.writestr('users.json', USERS.read_text() if USERS.exists() else json.dumps({'users':[]},ensure_ascii=False));z.writestr('manifest.json',json.dumps({'format':'suseto-backup-v1','created_at':_now()}))
 return buf.getvalue()
def restore(raw):
 try:
  with zipfile.ZipFile(io.BytesIO(raw)) as z:
   if 'registry.json' not in z.namelist():raise ValueError('Záloha neobsahuje registry.json.')
   reg=json.loads(z.read('registry.json')); 
   if not isinstance(reg,dict) or not isinstance(reg.get('items'),list):raise ValueError('Neplatná struktura Registry.')
   _save(reg)
   if 'sessions.json' in z.namelist():_write(json.loads(z.read('sessions.json')))
   if 'users.json' in z.namelist(): USERS.write_bytes(z.read('users.json'))
 except zipfile.BadZipFile:raise ValueError('Neplatný ZIP soubor.')
 return {'restored_items':len(reg['items'])}
