DEFAULT_WEIGHTS = {"length": 0.35, "entropy": 0.30, "prefix": 0.20, "wrapper": 0.15}
STRATEGIES = {"best_first", "beam", "breadth_first"}
def normalize_weights(raw=None):
    raw = raw or DEFAULT_WEIGHTS
    values = {k: max(0.0, float(raw.get(k, DEFAULT_WEIGHTS[k]))) for k in DEFAULT_WEIGHTS}
    total = sum(values.values()) or 1.0
    return {k: round(v / total, 4) for k, v in values.items()}
def build_frontier(seed, strategy="best_first", budget=8, weights=None):
    if strategy not in STRATEGIES: strategy = "best_first"
    budget = max(1, min(int(budget), 30))
    w = normalize_weights(weights)
    base = sum(ord(c) for c in str(seed)) % 31
    candidates=[]
    for i in range(budget):
        components={"length":((base+i*7)%100)/100,"entropy":((base*3+i*11)%100)/100,"prefix":((base*5+i*3)%100)/100,"wrapper":((base*2+i*13)%100)/100}
        score=round(sum(components[k]*w[k] for k in w),4)
        candidates.append({"id":f"candidate-{i+1}","label":f"Candidate {i+1:02}","score":score,"components":components})
    if strategy in ("best_first","beam"): candidates.sort(key=lambda x:x["score"], reverse=True)
    if strategy == "beam": candidates=candidates[:min(5,len(candidates))]
    return {"strategy":strategy,"budget":budget,"weights":w,"frontier":candidates}
