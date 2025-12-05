import base64
import json
from typing import Set, Optional, Dict, Any

import httpx
from jose import jwt, jwk
from jose.utils import base64url_decode

from .settings import AUTH_JWKS_URL, AUTH_INTROSPECT_URL, AUTH_CLIENT_ID, AUTH_CLIENT_SECRET


class AuthValidator:
    """
    Minimal auth/scope validator.
    Prefers JWT verification against JWKS if configured, otherwise falls back to
    introspection endpoint or scope string parsing.
    """

    def __init__(self) -> None:
        self.jwks: Optional[Dict[str, Any]] = None
        if AUTH_JWKS_URL:
            try:
                resp = httpx.get(AUTH_JWKS_URL, timeout=2.0)
                resp.raise_for_status()
                self.jwks = resp.json()
            except Exception:
                self.jwks = None

    def extract_token(self, auth_header: str | None) -> str | None:
        if not auth_header:
            return None
        if auth_header.lower().startswith("bearer "):
            return auth_header.split(" ", 1)[1].strip()
        return None

    def scopes_from_token(self, token: str | None) -> Set[str]:
        if not token:
            return set()
        verified_claims = self._verify_jwt(token)
        if verified_claims:
            scopes_claim = verified_claims.get("scope") or verified_claims.get("scp") or verified_claims.get("scopes")
            if isinstance(scopes_claim, str):
                return {p for p in scopes_claim.split() if p}
            if isinstance(scopes_claim, (list, tuple)):
                return {str(p) for p in scopes_claim}
        if AUTH_INTROSPECT_URL:
            scopes = self._introspect(token)
            if scopes:
                return scopes
        # If token looks like JWT, read unverified payload for scope/scope-like claims
        if token.count(".") == 2:
            try:
                _, body, _ = token.split(".")
                padding = "=" * ((4 - len(body) % 4) % 4)
                payload_bytes = base64.urlsafe_b64decode(body + padding)
                payload = json.loads(payload_bytes.decode("utf-8"))
                scopes_claim = payload.get("scope") or payload.get("scp") or payload.get("scopes")
                if isinstance(scopes_claim, str):
                    return {p for p in scopes_claim.split() if p}
                if isinstance(scopes_claim, (list, tuple)):
                    return {str(p) for p in scopes_claim}
            except Exception:
                pass
        # Fallback: treat token string as space-separated scopes
        return {p for p in token.split() if p}

    def _verify_jwt(self, token: str) -> Optional[Dict[str, Any]]:
        if not self.jwks:
            return None
        try:
            header = jwt.get_unverified_header(token)
            kid = header.get("kid")
            key_data = next((k for k in self.jwks.get("keys", []) if k.get("kid") == kid), None)
            if not key_data:
                return None
            public_key = jwk.construct(key_data)
            message, encoded_sig = token.rsplit(".", 1)
            decoded_sig = base64url_decode(encoded_sig.encode("utf-8"))
            if not public_key.verify(message.encode("utf-8"), decoded_sig):
                return None
            return jwt.get_unverified_claims(token)
        except Exception:
            return None

    def _introspect(self, token: str) -> Optional[Set[str]]:
        data = {"token": token}
        if AUTH_CLIENT_ID and AUTH_CLIENT_SECRET:
            data["client_id"] = AUTH_CLIENT_ID
            data["client_secret"] = AUTH_CLIENT_SECRET
        try:
            resp = httpx.post(AUTH_INTROSPECT_URL, data=data, timeout=2.0)
            if resp.status_code >= 200 and resp.status_code < 300:
                body = resp.json()
                scopes_claim = body.get("scope") or body.get("scp") or body.get("scopes")
                if isinstance(scopes_claim, str):
                    return {p for p in scopes_claim.split() if p}
                if isinstance(scopes_claim, (list, tuple)):
                    return {str(p) for p in scopes_claim}
        except Exception:
            return None
        return None

    def authorize(self, auth_header: str | None, required_scope: str | None) -> bool:
        if not required_scope:
            return True
        token = self.extract_token(auth_header)
        scopes = self.scopes_from_token(token)
        return required_scope in scopes or "*" in scopes
