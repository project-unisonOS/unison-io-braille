import base64

from jose import jwt

from unison_io_braille.auth import AuthValidator


def _b64url(s: bytes) -> str:
    return base64.urlsafe_b64encode(s).decode().rstrip("=")


def test_auth_validator_jwks_success_and_failure():
    secret = b"supersecret"
    jwks = {
        "keys": [
            {"kty": "oct", "kid": "kid1", "k": _b64url(secret)},
        ]
    }
    validator = AuthValidator(jwks=jwks, jwks_url=None, introspect_url=None)
    good_token = jwt.encode({"scope": "braille.input.read"}, secret, algorithm="HS256", headers={"kid": "kid1"})
    assert validator.authorize(f"Bearer {good_token}", "braille.input.read") is True
    # Wrong scope should fail
    assert validator.authorize(f"Bearer {good_token}", "braille.device.pair") is False
    # Token signed with different key should fail verification
    bad_token = jwt.encode({"scope": "braille.input.read"}, b"wrong", algorithm="HS256", headers={"kid": "kid1"})
    assert validator.authorize(f"Bearer {bad_token}", "braille.input.read") is False

