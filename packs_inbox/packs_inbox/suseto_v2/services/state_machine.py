STATE_DEFINITIONS = {
    'root': {'label':'INIT','parent':None,'score':1.00,'status':'complete','reason':'Inicializace behu a nacteni pravidel.'},
    'profile': {'label':'PROFILE_INPUT','parent':'root','score':0.94,'status':'complete','reason':'Vstup byl profilovan podle formatu a struktury.'},
    'expand': {'label':'GENERATE_CANDIDATES','parent':'profile','score':0.92,'status':'active','reason':'Rozvijeni kandidatu podle prioritnich mutaci.'},
    'filter': {'label':'HEURISTIC_FILTER','parent':'expand','score':0.89,'status':'queued','reason':'Orezani prostoru podle delky, entropy a prefixu.'},
    'validate': {'label':'VALIDATE_RESULT','parent':'filter','score':0.95,'status':'queued','reason':'Kontrolni faze a finalni vyhodnoceni.'},
    'backtrack': {'label':'BACKTRACK','parent':'filter','score':0.43,'status':'standby','reason':'Zalozni navratova vetev pri nizke confidence.'},
}

def build_state_graph(seed):
    nodes=[dict({'id':key,'state':key}, **value) for key,value in STATE_DEFINITIONS.items()]
    edges=[{'from':value['parent'],'to':key} for key,value in STATE_DEFINITIONS.items() if value['parent']]
    frontier=sorted([n for n in nodes if n['status'] in ('active','queued')], key=lambda n:n['score'], reverse=True)
    return {'seed':seed,'nodes':nodes,'edges':edges,'frontier':[{'id':n['id'],'label':n['label'],'score':n['score'],'status':n['status']} for n in frontier]}

def replay_path(path):
    events=[]
    for index,state_id in enumerate(path,1):
        node=STATE_DEFINITIONS.get(state_id, {'label':state_id,'reason':'Externi stav','score':0})
        events.append({'step':index,'state_id':state_id,'label':node['label'],'score':node['score'],'reason':node['reason']})
    return {'path':path,'events':events}

def get_state_detail(state_id):
    node=STATE_DEFINITIONS.get(state_id, STATE_DEFINITIONS['root'])
    children=[key for key,value in STATE_DEFINITIONS.items() if value['parent']==state_id]
    return {'state_id':state_id,'label':node['label'],'score':node['score'],'status':node['status'],'notes':node['reason'],'heuristics':[{'name':'length','weight':0.35},{'name':'entropy','weight':0.30},{'name':'prefix','weight':0.20},{'name':'wrapper','weight':0.15}],'next':children or ['terminate'],'can_backtrack': state_id not in ('root','backtrack')}
