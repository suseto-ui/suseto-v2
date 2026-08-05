from services.aidc_batch import preview_csv, generate_batch


def test_preview_csv():
    result, status = preview_csv(None)
    assert status == 200
    assert 'rows' in result


def test_generate_batch():
    result = generate_batch(None, '0', 'qr', 'png')
    assert result['ok'] is True
