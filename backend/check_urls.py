#!/usr/bin/env python
"""
Script to check all available URL patterns in Django
"""
import os
import sys
import django

# Setup Django
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
django.setup()

from django.urls import get_resolver
from django.urls.resolvers import URLPattern, URLResolver


def show_urls(urlpatterns, indent=0):
    """Recursively show all URL patterns"""
    for pattern in urlpatterns:
        if isinstance(pattern, URLResolver):
            print("  " * indent + f"📁 {pattern.pattern}")
            show_urls(pattern.url_patterns, indent + 1)
        elif isinstance(pattern, URLPattern):
            print("  " * indent + f"📄 {pattern.pattern} -> {pattern.callback}")


if __name__ == "__main__":
    print("=" * 80)
    print("🔍 URLS DISPONIBLES EN EL PROYECTO")
    print("=" * 80)
    print()

    resolver = get_resolver()
    show_urls(resolver.url_patterns)

    print()
    print("=" * 80)
    print("✅ VERIFICACIÓN COMPLETA")
    print("=" * 80)
