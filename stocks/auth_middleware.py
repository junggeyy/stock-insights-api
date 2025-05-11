# stocks/auth_middleware.py
import os
from urllib.parse import parse_qs
from asgiref.sync import sync_to_async
from channels.middleware import BaseMiddleware
from django.db import close_old_connections


@sync_to_async
def get_user_from_token(token_key):
    from django.contrib.auth.models import AnonymousUser
    from rest_framework.authentication import TokenAuthentication
    from django.db import close_old_connections

    close_old_connections()

    if not token_key:
        print("[Middleware] No token provided.")
        return AnonymousUser()

    try:
        user_auth_tuple = TokenAuthentication().authenticate_credentials(token_key)
        if user_auth_tuple:
            user, _ = user_auth_tuple
            print(f"[Middleware] Authenticated user: {user.username}")
            return user
    except Exception as e:
        print(f"[Middleware] Invalid token: {e}")
        return AnonymousUser()

    return AnonymousUser()


class TokenAuthMiddleware(BaseMiddleware):
    async def __call__(self, scope, receive, send):
        query_string = scope.get("query_string", b"").decode()
        query_params = parse_qs(query_string)
        token_key = query_params.get("token", [None])[0]

        close_old_connections()
        scope["user"] = await get_user_from_token(token_key)

        return await super().__call__(scope, receive, send)
