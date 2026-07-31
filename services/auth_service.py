import json, hashlib, secrets
from datetime import datetime, timezone
from pathlib import Path

from services.config import CONFIG

ROOT=Path(__file__).resolve().parent.parent/'data'; FILE=ROOT/'users.json'
ROLES={'admin','operator','viewer'}
def _now(): return datetime.now(timezone.utc).isoformat()
def _hash(s,p): return hashlib.sha256((s+p).encode()).hexdigest()
def _strong(password):
 p=str(password or '')
 return len(p)>=8 and any(c.islower() for c in p) and any(c.isupper() for c in p) and any(c.isdigit() for c in p)
def _ensure():
 ROOT.mkdir(exist_ok=True)
 if not FILE.exists():
  salt=secrets.token_hex(8)
  pwd=CONFIG.get("DEFAULT_ADMIN_PASSWORD") or "admin123"
  FILE.write_text(json.dumps({'users':[{'username':CONFIG['ADMIN_USERNAME'],'role':'admin','active':True,'created_at':_now(),'last_login':None,'must_change_password':True,'salt':salt,'password_hash':_hash(salt,pwd)}]},ensure_ascii=False,indent=2))
def _load(): _ensure(); return json.loads(FILE.read_text())
def _save(data): ROOT.mkdir(exist_ok=True); FILE.write_text(json.dumps(data,ensure_ascii=False,indent=2))
def list_users():
 data=_load();
 return [{'username':u['username'],'role':u['role'],'active':u.get('active',True),'created_at':u.get('created_at'),'last_login':u.get('last_login'),'must_change_password':u.get('must_change_password',False)} for u in data['users']]
def create_user(username,password,role='viewer'):
 data=_load(); username=str(username).strip(); role=role if role in ROLES else 'viewer'
 if not username or not password: raise ValueError('Vyplň uživatele i heslo.')
 if not _strong(password): raise ValueError('Heslo musí mít min. 8 znaků, velké a malé písmeno a číslo.')
 if any(u['username']==username for u in data['users']): raise ValueError('Uživatel už existuje.')
 salt=secrets.token_hex(8); data['users'].append({'username':username,'role':role,'active':True,'created_at':_now(),'last_login':None,'must_change_password':True,'salt':salt,'password_hash':_hash(salt,password)}); _save(data); return {'username':username,'role':role,'active':True}
def set_role(username,role):
 if role not in ROLES: raise ValueError('Neplatná role.')
 data=_load();
 for u in data['users']:
  if u['username']==username: u['role']=role; _save(data); return {'username':username,'role':role}
 raise ValueError('Uživatel nebyl nalezen.')
def toggle_active(username):
 data=_load();
 for u in data['users']:
  if u['username']==username: u['active']=not u.get('active',True); _save(data); return {'username':username,'active':u['active']}
 raise ValueError('Uživatel nebyl nalezen.')
def delete_user(username):
 data=_load(); before=len(data['users']); data['users']=[u for u in data['users'] if u['username']!=username or u['username']=='admin']
 if len(data['users'])==before: raise ValueError('Uživatel nebyl nalezen nebo nelze smazat bootstrap admin účet.')
 _save(data); return {'deleted':username}
def reset_password(username,new_password):
 if not _strong(new_password): raise ValueError('Heslo musí mít min. 8 znaků, velké a malé písmeno a číslo.')
 data=_load()
 for u in data['users']:
  if u['username']==username:
   salt=secrets.token_hex(8); u['salt']=salt; u['password_hash']=_hash(salt,new_password); u['must_change_password']=True; _save(data); return {'username':username,'reset':True}
 raise ValueError('Uživatel nebyl nalezen.')
def change_password(username,old_password,new_password):
 if not _strong(new_password): raise ValueError('Nové heslo musí mít min. 8 znaků, velké a malé písmeno a číslo.')
 data=_load()
 for u in data['users']:
  if u['username']==username and _hash(u['salt'],old_password)==u['password_hash']:
   salt=secrets.token_hex(8); u['salt']=salt; u['password_hash']=_hash(salt,new_password); u['must_change_password']=False; _save(data); return {'username':username,'changed':True}
 raise ValueError('Původní heslo nesouhlasí.')
def verify(username,password):
 data=_load()
 for u in data['users']:
  if u['username']==username and u.get('active',True) and _hash(u['salt'],password)==u['password_hash']:
   u['last_login']=_now(); _save(data); return {'username':u['username'],'role':u['role'],'must_change_password':u.get('must_change_password',False)}
 return None

