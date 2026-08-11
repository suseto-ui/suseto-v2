import base64, datetime, hashlib, hmac, re

def _b36(n):
 chars='0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ';out='0'
 if n:
  out=''
  while n:n,r=divmod(n,36);out=chars[r]+out
 return out
def analyze(value,key=''):
 v=str(value or '')
 out={'input':v,'length':len(v),'utf8_hex':v.encode().hex().upper(),'binary':' '.join(f'{b:08b}' for b in v.encode()),'base64':base64.b64encode(v.encode()).decode()}
 try:out['base64_decoded']=base64.b64decode(v+'===').decode('utf-8')
 except Exception:out['base64_decoded']='—'
 if re.fullmatch(r'[0-9A-Fa-f]+',v or 'x') and len(v)%2==0:
  try:out['hex_decoded']=bytes.fromhex(v).decode('utf-8')
  except UnicodeDecodeError:out['hex_decoded']='(binární data)'
 else:out['hex_decoded']='—'
 if key:
  raw=bytes(v,'utf-8');k=bytes(str(key),'utf-8');out['xor_hex']=bytes(b^k[i%len(k)] for i,b in enumerate(raw)).hex().upper();out['hmac_sha256']=hmac.new(k,raw,hashlib.sha256).hexdigest()
 return out
def time_formats():
 now=datetime.datetime.now(datetime.timezone.utc);unix=int(now.timestamp());gps=unix-315964800+18
 return {'utc':now.isoformat(),'unix':unix,'unix_hex':f'{unix:X}','unix_base36':_b36(unix),'unix_binary':f'{unix:b}','gps_seconds':gps,'date':now.strftime('%Y-%m-%d'),'iso_week':now.strftime('%G-W%V-%u'),'day_of_year':now.strftime('%Y-%j')}
