import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))


def test_run_store_persists_records(tmp_path, monkeypatch):
    import services.run_store as run_store

    monkeypatch.setattr(run_store, 'STORE', tmp_path / 'runs.json')

    record = run_store.save_run({'name': 'demo'})
    assert record['name'] == 'demo'
    assert run_store.get_run(record['id'])['id'] == record['id']
    assert len(run_store.list_runs()) == 1
