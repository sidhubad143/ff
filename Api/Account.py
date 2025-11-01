import requests
import json
import urllib3
import Proto.compiled.MajorLogin_pb2
from Utilities.until import encode_protobuf, decode_protobuf
from Configuration.APIConfiguration import RELEASEVERSION

# Suppress SSL warnings for self-signed cert (only for Blueshark host)
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


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
    except requests.exceptions.RequestException as e:
        print(f"[e] Garena token request failed: {e}")
        return None
    except json.JSONDecodeError:
        print("[e] Garena token JSON parse failed")
        return None


def get_major_login(logintoken, openid):
    """
    Perform MajorLogin with the provided credentials.
    """
    try:
        payload = {
            "openid": openid,
            "logintoken": logintoken,
            "platform": "4",
        }
        encrypted_payload = encode_protobuf(payload, Proto.compiled.MajorLogin_pb2.request())

        # ✅ Updated OB52+ endpoint
        url = "https://loginbpm.ff.blueshark.com/MajorLogin"

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

        try:
            # ✅ SSL verify disabled ONLY for this domain
            response = requests.post(
                url,
                data=encrypted_payload,
                headers=headers,
                timeout=10,
                verify=False,  # bypass self-signed cert error
            )
        except requests.exceptions.SSLError as ssl_error:
            print(f"[!] SSL verification failed, retrying with verify=False: {ssl_error}")
            response = requests.post(
                url,
                data=encrypted_payload,
                headers=headers,
                timeout=10,
                verify=False
            )

        # Handle bad HTTP status codes
        if response.status_code != 200:
            print(f"[e] MajorLogin HTTP {response.status_code}: {response.text[:200]}")
            return False

        # Decode protobuf safely
        try:
            message = decode_protobuf(response.content, Proto.compiled.MajorLogin_pb2.response)
            return message
        except Exception as decode_error:
            print(f"[e] Failed to decode MajorLogin response: {decode_error}")
            return False

    except Exception as e:
        print(f"[e] get_major_login() failed: {e}")
        return False
