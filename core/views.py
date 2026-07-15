import os
from django.shortcuts import render
from django.conf import settings


def index(request):
    index_path = settings.FRONTEND_DIR / "index.html"
    if index_path.exists():
        return render(request, "index.html")
    return render(request, "index.html", status=503)
