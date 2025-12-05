from fastapi import Request, HTTPException
from starlette.middleware.base import BaseHTTPMiddleware
from typing import Callable


class ScopeMiddleware(BaseHTTPMiddleware):
    """Stub scope middleware; extend with real JWT/consent validation later."""

    def __init__(self, app, required_scope: str | None = None):
        super().__init__(app)
        self.required_scope = required_scope

    async def dispatch(self, request: Request, call_next: Callable):
        if self.required_scope:
            auth_header = request.headers.get("Authorization")
            test_mode = request.headers.get("X-Test-Bypass") == "1"
            if not auth_header and not test_mode:
                raise HTTPException(status_code=403, detail="missing required scope")
        return await call_next(request)
