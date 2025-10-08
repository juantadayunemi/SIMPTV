# TrafiSmart Development Server with Auto-Reload
# Watches for changes in Python files and restarts automatically

Write-Host "🚀 Starting TrafiSmart Backend with Auto-Reload..." -ForegroundColor Green
Write-Host "📂 Watching: *.py files" -ForegroundColor Cyan
Write-Host "🔄 Server will restart automatically on code changes" -ForegroundColor Yellow
Write-Host "⏹️  Press Ctrl+C to stop" -ForegroundColor Red
Write-Host ""

# Use Django's built-in runserver with auto-reload
# Compatible with Python 3.13
python manage.py runserver

# Note: runserver_plus requires watchdog which has compatibility issues with Python 3.13
# Use runserver instead - it has built-in auto-reload
