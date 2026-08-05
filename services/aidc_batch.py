def preview_csv(file_obj):
    return {'rows': [], 'columns': []}, 200


def generate_batch(file_obj, column, kind, fmt):
    return {'ok': True, 'kind': kind, 'format': fmt}
