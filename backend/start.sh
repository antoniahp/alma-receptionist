#!/bin/sh
# Arranque del backend en Docker / Render
set -e
python manage.py migrate --noinput
python manage.py ensure_owner
if [ "$DEMO_MODE" = "true" ]; then
  # Demo pública: cada vez que arranca (en Render gratis, tras un rato sin visitas) vuelve a los datos de ejemplo
  python manage.py seed_demo
elif [ "$SEED_DEMO" = "true" ]; then
  python manage.py seed_demo --if-empty
fi
exec gunicorn core.wsgi:application --bind 0.0.0.0:${PORT:-8000} --workers ${WEB_CONCURRENCY:-2} --timeout 120
