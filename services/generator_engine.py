import base64, datetime, hmac, hashlib
SECRET_KEY='suseto-v2-dev'
def unix_ts(): return str(int(datetime.datetime.now().timestamp()))
def unix_ts_ms(): return str(int(datetime.datetime.now().timestamp()*1000))
def wifi_payload(ssid,password,security='WPA'): return f"WIFI:S:{ssid};T:{security};P:{password};;"
def hotp_payload(counter=1): return f"HOTP:{counter}:{hmac.new(SECRET_KEY.encode(),str(counter).encode(),hashlib.sha256).hexdigest()[:6].upper()}"
def base64_wrap(text): return base64.b64encode(text.encode()).decode()
def profile_bundle(seed): return {'seed':seed,'unix_ts':unix_ts(),'unix_ts_ms':unix_ts_ms(),'base64':base64_wrap(seed),'hotp_like':hotp_payload(1),'wifi_like':wifi_payload(seed,'demo')}
