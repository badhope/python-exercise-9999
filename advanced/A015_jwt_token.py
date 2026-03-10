# -----------------------------
# 题目：JSON Web Token (JWT) 实现。
# -----------------------------

import base64
import json
import hmac
import hashlib
import time

class JWT:
    def __init__(self, secret):
        self.secret = secret
    
    def encode(self, payload):
        header = {"alg": "HS256", "typ": "JWT"}
        header_encoded = self._base64url_encode(json.dumps(header))
        payload_encoded = self._base64url_encode(json.dumps(payload))
        signature = self._sign(f"{header_encoded}.{payload_encoded}")
        return f"{header_encoded}.{payload_encoded}.{signature}"
    
    def decode(self, token):
        parts = token.split(".")
        if len(parts) != 3:
            return None
        header_encoded, payload_encoded, signature = parts
        expected_signature = self._sign(f"{header_encoded}.{payload_encoded}")
        if not hmac.compare_digest(signature, expected_signature):
            return None
        return json.loads(self._base64url_decode(payload_encoded))
    
    def _base64url_encode(self, data):
        return base64.urlsafe_b64encode(data.encode()).decode().rstrip("=")
    
    def _base64url_decode(self, data):
        padding = 4 - len(data) % 4
        if padding != 4:
            data += "=" * padding
        return base64.urlsafe_b64decode(data).decode()
    
    def _sign(self, data):
        return self._base64url_encode(
            hmac.new(self.secret.encode(), data.encode(), hashlib.sha256).digest()
        )

def main():
    jwt = JWT("my_secret_key")
    payload = {"user_id": 123, "exp": int(time.time()) + 3600}
    token = jwt.encode(payload)
    print(f"JWT Token: {token[:50]}...")
    decoded = jwt.decode(token)
    print(f"解码后: {decoded}")


if __name__ == "__main__":
    main()
