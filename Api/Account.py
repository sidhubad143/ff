import requests
import json
import Proto.compiled.MajorLogin_pb2
from Utilities.until import encode_protobuf, decode_protobuf
from Configuration.APIConfiguration import RELEASEVERSION


def get_garena_token(uid, password):
    """
    Get Garena token using uid and password

    Args:
        uid (str): User ID
        password (str): Password

    Returns:
        dict: JSON response from the API
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
    except json.JSONDecodeError as e:
        print(f"[e] Garena token JSON parse failed: {e}")
        return None


def get_major_login(logintoken, openid):
    """
    Perform major login with the provided credentials

    Args:
        logintoken (str): The login token
        openid (str): The open ID

    Returns:
        dict | bool: Decoded response message or False on error
    """
    try:
        # Encrypt protobuf payload
        payload = {
            "openid": openid,
            "logintoken": logintoken,
            "platform": "4",
        }
        encrypted_payload = encode_protobuf(payload, Proto.compiled.MajorLogin_pb2.request())

        # ✅ Updated OB52+ endpoint
        url = "https://loginbpm.ff.garena.com/MajorLogin"

        # ✅ Clean and corrected headers
        headers = {
            "User-Agent": "Dalvik/2.1.0 (Linux; U; Android 13; A063 Build/TKQ1.221220.001)",
            "Connection": "Keep-Alive",
            "Accept-Encoding": "gzip",
            "Content-Type": "application/octet-stream",
            "Authorization": "Bearer",
            "X-Unity-Version": "2018.4.11f1",
            "X-GA": "v1 1",
            "ReleaseVersion": RELEASEVERSION,  # should be OB52 or OB53
        }

        # Send the login request
        response = requests.post(url, data=encrypted_payload, headers=headers, timeout=10)

        # Handle 401 / invalid responses gracefully
        if response.status_code != 200:
            print(f"[e] MajorLogin HTTP {response.status_code} - {response.text}")
            return False

        # Decode protobuf response
        message = decode_protobuf(response.content, Proto.compiled.MajorLogin_pb2.response)
        return message

    except Exception as e:
        print(f"[e] get_major_login() failed: {e}")
        return False
