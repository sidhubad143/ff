import requests
import json
import urllib3
import Proto.compiled.MajorLogin_pb2
from Utilities.until import encode_protobuf, decode_protobuf
from Configuration.APIConfiguration import RELEASEVERSION

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# ✅ Expanded fallback list for OB53–OB54
MAJORLOGIN_ENDPOINTS = [
    "https://loginbpm.ff.blueshark.com/api/MajorLogin",
    "https://loginbpm.ff.blueshark.com/v2/MajorLogin",
    "https://loginbpm.ff.blueshark.com/bpm/MajorLogin",
    "https://loginbpm.ff.blueshark.com/MajorLogin",
    "https://loginbpm.ff.gblueshark.com/MajorLogin",
    "https://loginbpm.ff.blueshark.net/MajorLogin",
]


def get_garena_token(uid, password):
    url = "https://ffmconnect.live.gop.garenanow.com/oauth/guest/token/grant"
    payload = {
        "uid": uid,
        "password": password,
        "response_type": "token",
        "client_type": "2",
        "client_secret": "2ee44819e9b4598845141067b281621874d0d5d7af9d8f7e00c1e54715b7d1e3",
        "client_id": "100067",
    }
    headers = {
        "User-Agent": "GarenaMSDK/4.0.19P9(A063; Android 13; en; IN;)",
        "Connection": "Keep-Alive",
        "Accept-Encoding": "gzip",
    }
    try:
        r = requests.post(url, data=payload, headers=headers, timeout=10)
        r.raise_for_status()
        return r.json()
    except Exception as e:
        print(f"[e] Garena token request failed: {e}")
        return None


def get_major_login(logintoken, openid):
    payload = {
        "openid": openid,
        "logintoken": logintoken,
        "platform": "4",
    }
    encrypted_payload = encode_protobuf(payload, Proto.compiled.MajorLogin_pb2.request())

    headers = {
        "User-Agent": "Dalvik/2.1.0 (Linux; U; Android 13; A063 Build/TKQ1.221220.001)",
        "Connection": "Keep-Alive",
        "Accept-Encoding": "gzip",
        "Content-Type": "application/octet-stream",
        "Authorization": "Bearer",
        "X-Unity-Version": "2018.4.11f1",
        "X-GA": "v1 1",
        "ReleaseVersion": RELEASEVERSION,
    }

    for endpoint in MAJORLOGIN_ENDPOINTS:
        try:
            print(f"[*] Trying MajorLogin endpoint: {endpoint}")
            r = requests.post(endpoint, data=encrypted_payload, headers=headers, timeout=10, verify=False)

            if r.status_code == 200:
                print(f"[+] Success: {endpoint}")
                try:
                    return decode_protobuf(r.content, Proto.compiled.MajorLogin_pb2.response)
                except Exception as e:
                    print(f"[e] Protobuf decode failed: {e}")
                    return False
            else:
                print(f"[e] MajorLogin HTTP {r.status_code}: {r.text[:150]}")

        except Exception as e:
            print(f"[!] Failed to connect to {endpoint}: {e}")

    print("[x] All MajorLogin endpoints failed.")
    return False
