import base64
import json
from typing import Set


class AuthValidator:
    """
    Minimal auth/scope validator.
    In production, replace with JWT/consent introspection.
    """

    def __init__(self) -> None:
        pass

    def extract_token(self, auth_header: str | None) -> str | None:
        if not auth_header:
            return None
        if auth_header.lower().startswith("bearer "):
            return auth_header.split(" ", 1)[1].strip()
        return None

    def scopes_from_token(self, token: str | None) -> Set[str]:
        if not token:
            return set()
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

    def authorize(self, auth_header: str | None, required_scope: str | None) -> bool:
        if not required_scope:
            return True
        token = self.extract_token(auth_header)
        scopes = self.scopes_from_token(token)
        return required_scope in scopes or "*" in scopes
