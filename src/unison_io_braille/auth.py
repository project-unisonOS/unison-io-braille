import base64
import json
import time
from typing import Set, Optional, Dict, Any

import httpx
from jose import jwt, jwk
from jose.utils import base64url_decode

from .settings import AUTH_JWKS_URL, AUTH_INTROSPECT_URL, AUTH_CLIENT_ID, AUTH_CLIENT_SECRET


class AuthValidator:
    """
    Minimal auth/scope validator.
    Prefers JWT verification against JWKS if configured, otherwise falls back to
    introspection endpoint or scope string parsing. JWKS is cached with a short TTL.
    """

    def __init__(self, jwks: Optional[Dict[str, Any]] = None, jwks_url: str | None = AUTH_JWKS_URL, introspect_url: str | None = AUTH_INTROSPECT_URL) -> None:
        self.jwks: Optional[Dict[str, Any]] = jwks
        self.jwks_url = jwks_url
        self.introspect_url = introspect_url
        self.jwks_cached_at = 0.0
        self.jwks_ttl = 3600.0
        self.jwks_backoff_seconds = 300.0

    def extract_token(self, auth_header: str | None) -> str | None:
        if not auth_header:
            return None
        if auth_header.lower().startswith("bearer "):
            return auth_header.split(" ", 1)[1].strip()
        return None

    def scopes_from_token(self, token: str | None) -> Set[str]:
        if not token:
            return set()
        self._ensure_jwks()
        verified_claims = self._verify_jwt(token)
        if verified_claims:
            scopes_claim = verified_claims.get("scope") or verified_claims.get("scp") or verified_claims.get("scopes")
            if isinstance(scopes_claim, str):
                return {p for p in scopes_claim.split() if p}
            if isinstance(scopes_claim, (list, tuple)):
                return {str(p) for p in scopes_claim}
        # If JWKS/JWT verification is configured and failed, do not fall back to unverified parsing
        if (self.jwks or self.jwks_url) and not verified_claims:
            return set()
        if self.introspect_url:
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
            alg = header.get("alg") or "RS256"
            key_data = next((k for k in self.jwks.get("keys", []) if k.get("kid") == kid), None)
            if not key_data:
                return None
            if key_data.get("kty") == "oct" and key_data.get("k"):
                secret = base64url_decode(key_data["k"].encode("utf-8"))
                return jwt.decode(token, secret, algorithms=[alg], options={"verify_aud": False, "verify_exp": False})
            public_key = jwk.construct(key_data, algorithm=alg)
            message = ".".join(token.split(".")[0:2])
            encoded_sig = token.split(".")[2]
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
            resp = httpx.post(self.introspect_url, data=data, timeout=2.0)
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

    def _ensure_jwks(self) -> None:
        if not self.jwks_url:
            return
        now = time.time()
        # refresh if never fetched or TTL expired
        if self.jwks and (now - self.jwks_cached_at) < self.jwks_ttl:
            return
        # avoid hammering if last attempt failed recently
        if self.jwks_cached_at and (now - self.jwks_cached_at) < self.jwks_backoff_seconds and not self.jwks:
            return
        try:
            resp = httpx.get(self.jwks_url, timeout=2.0)
            resp.raise_for_status()
            self.jwks = resp.json()
        except Exception:
            self.jwks = None
        finally:
            self.jwks_cached_at = now

    def authorize(self, auth_header: str | None, required_scope: str | None) -> bool:
        if not required_scope:
            return True
        token = self.extract_token(auth_header)
        scopes = self.scopes_from_token(token)
        return required_scope in scopes or "*" in scopes
