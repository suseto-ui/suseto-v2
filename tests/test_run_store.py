from services.run_store import save_run, list_runs, get_run


def test_save_run_creates_run():
    run = save_run({'kind': 'demo', 'input': {}, 'summary': {}})
    assert run['id']
    assert run['kind'] == 'demo'


def test_list_runs_returns_list():
    runs = list_runs()
    assert isinstance(runs, list)


def test_get_run_returns_saved_run():
    run = save_run({'kind': 'demo2', 'input': {}, 'summary': {}})
    found = get_run(run['id'])
    assert found is not None
    assert found['id'] == run['id']
