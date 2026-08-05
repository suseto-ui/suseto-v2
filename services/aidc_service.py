def generate_qr(data, fmt='png'):
    return {'kind': 'qr', 'data': data, 'format': fmt}


def generate_barcode(data, kind='code128', fmt='png'):
    return {'kind': kind, 'data': data, 'format': fmt}


def scan_analysis(payload):
    return {'payload': payload, 'classification': 'unknown', 'length': len(payload or '')}
