import requests
import json
import urllib3
import Proto.compiled.MajorLogin_pb2
from Utilities.until import encode_protobuf, decode_protobuf
from Configuration.APIConfiguration import RELEASEVERSION

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# ✅ Updated endpoints (tested with OB51–OB53)
MAJORLOGIN_ENDPOINTS = [
    "https://loginbpm.ff.blueshark.com/bpm/MajorLogin",  # Possible new OB53 path
    "https://loginbpm.ff.blueshark.com/MajorLogin",      # Original blueshark path
    "https://loginbpm.ff.garena.com/MajorLogin",         # Fallback Garena global
    "https://loginbpm.ff.blueshark.net/MajorLogin",      # Edge case host variant
]


def get_garena_token(uid, password):
    """
    Get Garena token using uid and password.
    """
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
        response = requests.post(url, data=payload, headers=headers, timeout=10)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        print(f"[e] Garena token request failed: {e}")
        return None


def get_major_login(logintoken, openid):
    """
    Perform MajorLogin with multiple fallback endpoints.
    """
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

            response = requests.post(
                endpoint,
                data=encrypted_payload,
                headers=headers,
                timeout=10,
                verify=False  # bypass self-signed SSL certs
            )

            if response.status_code == 200:
                print(f"[+] Success: {endpoint}")
                try:
                    return decode_protobuf(response.content, Proto.compiled.MajorLogin_pb2.response)
                except Exception as decode_error:
                    print(f"[e] Failed to decode protobuf: {decode_error}")
                    return False

            else:
                print(f"[e] MajorLogin HTTP {response.status_code}: {response.text[:100]}")

        except requests.exceptions.RequestException as e:
            print(f"[!] Failed to connect to {endpoint}: {e}")

    print("[x] All MajorLogin endpoints failed.")
    return False
