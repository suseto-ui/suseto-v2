_RUNS = []


def save_run(payload):
    run = {'id': str(len(_RUNS) + 1), **payload}
    _RUNS.append(run)
    return run


def list_runs():
    return list(_RUNS)


def get_run(run_id):
    return next((r for r in _RUNS if r['id'] == run_id), None)
