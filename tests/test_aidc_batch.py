from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))


def test_output_format_selection_prefers_svg_for_qr():
    from services.aidc_batch import _pick_output_format

    assert _pick_output_format('qr', 'svg') == 'svg'
    assert _pick_output_format('qr', 'png') == 'png'
    assert _pick_output_format('ean13', 'svg') == 'svg'
