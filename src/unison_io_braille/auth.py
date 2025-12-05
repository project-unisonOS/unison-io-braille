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
        # Placeholder: treat token string as space-separated scopes
        if not token:
            return set()
        return {p for p in token.split() if p}

    def authorize(self, auth_header: str | None, required_scope: str | None) -> bool:
        if not required_scope:
            return True
        token = self.extract_token(auth_header)
        scopes = self.scopes_from_token(token)
        return required_scope in scopes or "*" in scopes
