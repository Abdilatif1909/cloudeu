class SecurityHeadersMiddleware:
    """Adds headers not covered directly by Django's built-in security middleware."""

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)
        response.setdefault("X-XSS-Protection", "1; mode=block")
        response.setdefault("Referrer-Policy", "strict-origin-when-cross-origin")
        response.setdefault("Permissions-Policy", "camera=(), microphone=(), geolocation=()")
        response.setdefault(
            "Content-Security-Policy",
            "default-src 'self'; "
            "script-src 'self' 'unsafe-inline' https://www.youtube.com https://www.youtube-nocookie.com; "
            "style-src 'self' 'unsafe-inline'; "
            "img-src 'self' data: https://img.youtube.com; "
            "frame-src 'self' https://www.youtube.com https://www.youtube-nocookie.com; "
            "connect-src 'self'; "
            "object-src 'none'; "
            "base-uri 'self'; "
            "frame-ancestors 'none'",
        )
        return response
