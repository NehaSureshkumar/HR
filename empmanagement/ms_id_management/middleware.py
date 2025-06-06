from django.http import HttpResponseRedirect
from django.conf import settings

class ForceLocalhostMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Check if the request is using 127.0.0.1
        if request.get_host().startswith('127.0.0.1'):
            # Build the new URL with localhost
            new_url = request.build_absolute_uri().replace('127.0.0.1', 'localhost')
            return HttpResponseRedirect(new_url)
        
        # If using localhost, ensure the protocol is http
        if request.get_host().startswith('localhost'):
            if request.is_secure():
                new_url = request.build_absolute_uri().replace('https://', 'http://')
                return HttpResponseRedirect(new_url)
        
        return self.get_response(request) 