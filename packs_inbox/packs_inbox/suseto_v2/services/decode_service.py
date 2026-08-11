import base64, re, urllib.parse, math
from collections import Counter,defaultdict

def entropy(s):
    if not s: return 0.0
    n=len(s); c=Counter(s)
    return round(-sum((v/n)*math.log2(v/n) for v in c.values()),4)

def _ascii_ratio(s):
    if not s: return 0
    good=sum(1 for ch in s if 32 <= ord(ch) < 127 or ch in '\n\r\t')
    return round(good/len(s),4)

def try_hex(payload):
    p=re.sub(r'\s+','',str(payload))
    if len(p)%2 or not re.fullmatch(r'[0-9A-Fa-f]+',p): return None
    try:
        raw=bytes.fromhex(p); txt=raw.decode('utf-8','replace')
        return {'type':'hex->utf8','output':txt,'confidence':0.72+0.2*_ascii_ratio(txt),'reason':'Platný HEX vstup a dekódovatelný text.'}
    except Exception: return None

def try_b64(payload):
    p=str(payload).strip()
    if not re.fullmatch(r'[A-Za-z0-9+/=_-]{8,}',p): return None
    for alt in (False,True):
        try:
            raw=base64.urlsafe_b64decode(p + '=' * (-len(p)%4)) if alt else base64.b64decode(p + '=' * (-len(p)%4))
            txt=raw.decode('utf-8','replace')
            return {'type':'base64->utf8','output':txt,'confidence':0.68+0.25*_ascii_ratio(txt),'reason':'Platný Base64 vstup a čitelný text.'}
        except Exception:
            pass
    return None

def try_url(payload):
    p=str(payload)
    if '%' not in p and '+' not in p: return None
    out=urllib.parse.unquote_plus(p)
    return {'type':'url-decode','output':out,'confidence':0.6+0.2*_ascii_ratio(out),'reason':'Obsahuje URL escape sekvence.'}

def classify(payload):
    p=str(payload or '')
    patterns=[]
    if p.startswith(('http://','https://')): patterns.append({'name':'URL','detail':'Web adresa','confidence':0.95})
    if p.startswith('WIFI:'): patterns.append({'name':'WIFI','detail':'Wi‑Fi QR payload','confidence':0.96})
    if p.count('.')==2: patterns.append({'name':'JWT-like','detail':'Tři segmenty oddělené tečkou','confidence':0.82})
    if re.fullmatch(r'\d{8}|\d{12}|\d{13}|\d{14}', p): patterns.append({'name':'GTIN-like','detail':'Číselná délka odpovídá GTIN','confidence':0.8})
    if re.fullmatch(r'[0-9A-Fa-f\s]+', p) and len(re.sub(r'\s+','',p))>=8: patterns.append({'name':'HEX-like','detail':'Hexadecimální abeceda','confidence':0.78})
    if re.search(r'\(01\)|\(10\)|\(17\)|\(21\)', p): patterns.append({'name':'GS1-like','detail':'Obsahuje běžné AI segmenty','confidence':0.84})
    return patterns

def chain(payload):
    raw=str(payload or '')
    candidates=[{'type':'raw','output':raw,'confidence':0.5,'reason':'Původní payload.'}]
    for fn in (try_hex,try_b64,try_url):
        item=fn(raw)
        if item: candidates.append(item)
    seen={}
    for c in candidates:
        key=(c['type'],c['output'])
        seen[key]=c
    out=list(seen.values())
    for c in out:
        c['entropy']=entropy(c['output'])
        c['ascii_ratio']=_ascii_ratio(c['output'])
        c['patterns']=classify(c['output'])
        c['confidence']=round(min(0.99,c['confidence'] + 0.05*len(c['patterns']) + 0.05*(c['ascii_ratio']>0.85)),4)
    out.sort(key=lambda x:x['confidence'], reverse=True)
    return {'input':raw,'candidates':out,'best':out[0] if out else None}

def pattern_library(payloads):
    rows=[]
    for p in payloads:
        d=chain(p)
        best=d['best'] or {'output':str(p),'patterns':[],'confidence':0}
        rows.append({'payload':str(p),'best_type':best.get('type'),'best_confidence':best.get('confidence'),'patterns':[x['name'] for x in best.get('patterns',[])]})
    buckets=defaultdict(list)
    for r in rows:
        key='|'.join(r['patterns']) or 'unclassified'
        buckets[key].append(r['payload'])
    return {'rows':rows,'groups':[{'pattern_set':k,'count':len(v),'examples':v[:5]} for k,v in buckets.items()]}
