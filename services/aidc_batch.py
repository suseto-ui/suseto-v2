import csv, io, zipfile, re
from flask import send_file, jsonify
from .aidc_service import _libraries

MAX_ROWS=250

def _clean(v): return str(v or '').strip()

def _pick_output_format(kind, fmt):
    if fmt in {'svg', 'png'}:
        return fmt
    return 'png' if kind == 'qr' else 'svg'

def preview_csv(upload):
    if not upload or not upload.filename: return {"error":"Nahraj CSV soubor."},400
    try: text=upload.stream.read().decode('utf-8-sig'); upload.stream.seek(0)
    except UnicodeDecodeError: return {"error":"CSV musí být UTF-8."},400
    rows=list(csv.reader(io.StringIO(text)))
    if not rows: return {"error":"CSV je prázdné."},400
    headers=rows[0]; data=rows[1:] if headers else []
    if len(data)>MAX_ROWS: return {"error":f"Maximum je {MAX_ROWS} datových řádků."},400
    return {"headers":headers,"rows":len(data),"sample":data[:5],"max_rows":MAX_ROWS},200

def _validated(value, kind):
    value=_clean(value)
    if not value: return None,'prázdný payload'
    if kind in ('ean13','upca'):
        value=re.sub(r'\D','',value); need=12 if kind=='ean13' else 11
        if len(value)>need:return None,f'{kind.upper()} má příliš mnoho číslic'
        value=value.zfill(need)
    return value,None

def generate_batch(upload, column, kind, fmt):
    qrcode, barcode, ImageWriter, SVGWriter, err=_libraries()
    if err:return jsonify({"error":f"AIDC knihovna není připravena: {err}"}),503
    result,status=preview_csv(upload)
    if status!=200:return jsonify(result),status
    upload.stream.seek(0); rows=list(csv.reader(io.StringIO(upload.stream.read().decode('utf-8-sig')))); headers=rows[0]; data=rows[1:]
    try: idx=int(column)
    except ValueError: return jsonify({"error":"Neplatný sloupec."}),400
    if idx<0 or idx>=len(headers):return jsonify({"error":"Sloupec mimo rozsah."}),400
    buf=io.BytesIO(); manifest=[]; seen=set()
    with zipfile.ZipFile(buf,'w',zipfile.ZIP_DEFLATED) as archive:
        for n,row in enumerate(data,1):
            raw=row[idx] if idx<len(row) else '' ; value,why=_validated(raw,kind)
            if why: manifest.append([n,raw,'skipped',why]); continue
            if value in seen: manifest.append([n,value,'skipped','duplicitní payload']); continue
            seen.add(value); image=io.BytesIO()
            try:
                if kind=='qr':
                    qr=qrcode.QRCode(box_size=8,border=4);qr.add_data(value);qr.make(fit=True);qr.make_image(fill_color='#111827',back_color='white').save(image,format='PNG')
                    ext='png'
                else:
                    output_fmt=_pick_output_format(kind, fmt)
                    code=barcode.get(kind,value,writer=SVGWriter() if output_fmt=='svg' else ImageWriter());code.write(image);ext=output_fmt
                archive.writestr(f'codes/{n:03d}_{re.sub(r"[^A-Za-z0-9._-]","_",value)[:50]}.{ext}',image.getvalue());manifest.append([n,value,'generated',''])
            except Exception as exc: manifest.append([n,value,'skipped',str(exc)])
        report=io.StringIO();w=csv.writer(report);w.writerow(['row','payload','status','note']);w.writerows(manifest);archive.writestr('batch_report.csv',report.getvalue().encode('utf-8-sig'))
    buf.seek(0);return send_file(buf,mimetype='application/zip',as_attachment=True,download_name='suseto-aidc-batch.zip')
