#!/bin/sh
# 컨테이너 시작 시 DB 마이그레이션(+선택적 관리자 생성) 후 본 명령 실행.
set -e

echo "[entrypoint] migrate..."
python manage.py migrate --noinput

# DJANGO_SUPERUSER_USERNAME/PASSWORD 지정 시 관리자 계정 생성(없을 때만).
if [ -n "$DJANGO_SUPERUSER_USERNAME" ] && [ -n "$DJANGO_SUPERUSER_PASSWORD" ]; then
  echo "[entrypoint] ensure superuser '$DJANGO_SUPERUSER_USERNAME'..."
  python manage.py createsuperuser --noinput \
    --username "$DJANGO_SUPERUSER_USERNAME" \
    --email "${DJANGO_SUPERUSER_EMAIL:-admin@example.com}" 2>/dev/null \
    || echo "[entrypoint] superuser already exists, skip."
fi

exec "$@"
