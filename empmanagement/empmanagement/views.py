from django.shortcuts import render

def csrf_failure_view(request, reason=""):
    return render(request, '403_csrf.html', status=403) 