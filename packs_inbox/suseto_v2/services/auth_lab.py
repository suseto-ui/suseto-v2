SCENARIOS={
 "rate_limit":{"title":"Rate limit a lockout","owasp":"Authentication","risk":"Automatizované pokusy nejsou omezeny.","mitigation":"Nastav limity, jednotné odpovědi a bezpečný lockout."},
 "enumeration":{"title":"Account enumeration","owasp":"Authentication","risk":"Odlišné odpovědi pro známý a neznámý účet prozrazují existenci identity.","mitigation":"Používej stejnou odpověď a stejnou časovou charakteristiku."},
 "mfa_flow":{"title":"MFA state flow","owasp":"Authentication","risk":"Přechod do autentizovaného stavu před ověřením druhého faktoru.","mitigation":"Vynucuj MFA gate před vydáním relace."},
 "access_matrix":{"title":"Authorization matrix","owasp":"Authorization","risk":"Role může číst zdroj mimo svůj scope.","mitigation":"Kontroluj autorizaci na serveru pro každý objekt."}
}
def simulate(payload):
    key=payload.get("scenario","rate_limit"); spec=SCENARIOS.get(key,SCENARIOS["rate_limit"]); defense=payload.get("defense",{}); limit=max(1,min(int(defense.get("rate_limit",5)),20)); uniform=bool(defense.get("uniform_response",False)); mfa=bool(defense.get("mfa_required",True)); attempts=max(1,min(int(payload.get("attempts",8)),20)); blocked=attempts>limit; findings=[]
    if key=="rate_limit" and not blocked: findings.append("Limit je příliš vysoký pro zvolený simulovaný počet pokusů.")
    if key=="enumeration" and not uniform: findings.append("Simulace rozlišuje identitu podle odpovědi.")
    if key=="mfa_flow" and not mfa: findings.append("MFA gate je vypnutá.")
    if key=="access_matrix": findings.append("Fiktivní matrix vyžaduje explicitní allow/deny pro každý zdroj.")
    risk="low" if not findings else "medium" if len(findings)==1 else "high"
    timeline=[{"step":1,"state":"INPUT","reason":"syntetický scénář načten"},{"step":2,"state":"DEFENSE_POLICY","reason":f"limit={limit}; uniform={uniform}; mfa={mfa}"},{"step":3,"state":"DECISION","reason":"blocked" if blocked else "simulace pokračuje"},{"step":4,"state":"REPORT","reason":risk}]
    return {"sandbox":True,"external_requests":0,"scenario":key,"title":spec["title"],"owasp":spec["owasp"],"risk":risk,"finding":findings or ["Obrana splnila podmínky modelu."],"mitigation":spec["mitigation"],"timeline":timeline,"defense":{"rate_limit":limit,"uniform_response":uniform,"mfa_required":mfa},"blocked":blocked}
