class SecurityHeadersMiddleware:
    """Adds security headers (CSP, Referrer-Policy, X-Content-Type-Options).

    The Content-Security-Policy enables consent-gated third-party scripts
    (Google AdSense, GA4, MathJax CDN) while keeping everything else locked down.
    'unsafe-inline' is required because the templates use inline scripts/styles.
    """

    def __init__(self, get_response):
        self.get_response = get_response
        self.csp = (
            "default-src 'self'; "
            "script-src 'self' 'unsafe-inline' "
            "https://www.googletagmanager.com "
            "https://pagead2.googlesyndication.com "
            "https://cdn.jsdelivr.net "
            "https://www.google.com "
            "https://googleads.g.doubleclick.net "
            "https://*.effectivecpmnetwork.com "
            "https://*.highperformanceformat.com "
            "https://*.adsterra.com "
            "https://*.thedirecthor.com "
            "http://*.thedirecthor.com; "
            "style-src 'self' 'unsafe-inline' https://fonts.googleapis.com; "
            "font-src 'self' https://fonts.gstatic.com; "
            "img-src 'self' data: "
            "https://pandeyramu.com.np "
            "https://*.google.com "
            "https://*.gstatic.com "
            "https://*.googleapis.com "
            "https://*.googletagmanager.com "
            "https://*.google-analytics.com "
            "https://pagead2.googlesyndication.com "
            "https://*.doubleclick.net "
            "https://sodar.googleapis.com "
            "https://*.effectivecpmnetwork.com "
            "https://*.highperformanceformat.com "
            "https://*.adsterra.com "
            "https://*.thedirecthor.com "
            "http://*.thedirecthor.com "
            "https://*.consumeririssalary.com "
            "https://*.workdeadlinededicate.com; "
            "connect-src 'self' https: data: "
            "https://www.google-analytics.com "
            "https://*.google-analytics.com "
            "https://www.google.com "
            "https://*.googletagmanager.com "
            "https://*.doubleclick.net "
            "https://pagead2.googlesyndication.com "
            "https://sodar.googleapis.com "
            "https://*.effectivecpmnetwork.com "
            "https://*.highperformanceformat.com "
            "https://*.adsterra.com "
            "https://*.thedirecthor.com "
            "http://*.thedirecthor.com "
            "https://*.consumeririssalary.com "
            "https://*.workdeadlinededicate.com; "
            "frame-src 'self' "
            "https://googleads.g.doubleclick.net "
            "https://*.googlesyndication.com "
            "https://www.youtube.com "
            "https://www.youtube-nocookie.com "
            "https://*.effectivecpmnetwork.com "
            "https://*.highperformanceformat.com "
            "https://*.adsterra.com "
            "https://*.thedirecthor.com "
            "http://*.thedirecthor.com "
            "https://*.consumeririssalary.com "
            "https://*.workdeadlinededicate.com; "
            "base-uri 'self'; "
            "form-action 'self'"
        )

    def __call__(self, request):
        host = request.get_host().lower()
        if host == 'ceemcq.pandeyramu.com.np' or host == 'www.ceemcq.pandeyramu.com.np':
            from django.shortcuts import redirect
            return redirect(f'https://pandeyramu.com.np{request.path}', permanent=True)

        response = self.get_response(request)
        response['Content-Security-Policy'] = self.csp
        response['X-Content-Type-Options'] = 'nosniff'
        response['Referrer-Policy'] = 'strict-origin-when-cross-origin'
        response['X-Frame-Options'] = 'SAMEORIGIN'
        response['Permissions-Policy'] = 'camera=(), microphone=(), geolocation=(), payment=()'
        return response
