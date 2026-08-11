import re
def analyze_payload(payload):
 p=(payload or '').strip(); out={'input':p,'classifications':[],'tree':[],'recommendations':[]}
 if not p: return {'input':'','classifications':[{'type':'empty','confidence':1.0}],'tree':[{'id':'root','label':'empty'}],'recommendations':['vloz data']}
 out['tree'].append({'id':'root','label':'Input','value':p[:120],'score':1.0})
 if p.startswith('WIFI:'): out['classifications'].append({'type':'wifi_payload','confidence':0.99})
 if p.startswith('HOTP:'): out['classifications'].append({'type':'hotp_payload','confidence':0.97})
 if p.startswith('XOR:'): out['classifications'].append({'type':'xor_wrapped_payload','confidence':0.98})
 if re.fullmatch(r'[A-Za-z0-9+/=]{8,}', p or ''): out['classifications'].append({'type':'base64_candidate','confidence':0.8})
 if '.' in p and len(p.split('.'))==3: out['classifications'].append({'type':'jwt_candidate','confidence':0.96})
 if not out['classifications']: out['classifications'].append({'type':'unknown','confidence':0.55})
 out['recommendations'].append('porovnat vetve a udrzet heuristiky')
 return out
