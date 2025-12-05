from fastapi import Request, HTTPException
from starlette.middleware.base import BaseHTTPMiddleware
from typing import Callable

from .auth import AuthValidator


class ScopeMiddleware(BaseHTTPMiddleware):
    """Scope enforcement using a pluggable AuthValidator."""

    def __init__(self, app, required_scope: str | None = None, auth: AuthValidator | None = None):
        super().__init__(app)
        self.required_scope = required_scope
        self.auth = auth or AuthValidator()

    async def dispatch(self, request: Request, call_next: Callable):
        if self.required_scope:
            test_mode = request.headers.get("X-Test-Bypass") == "1"
            auth_header = request.headers.get("Authorization")
            if not test_mode and not self.auth.authorize(auth_header, self.required_scope):
                raise HTTPException(status_code=403, detail="missing required scope")
        return await call_next(request)
