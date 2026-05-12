#!/bin/bash
# reload-css.sh
# Run this on the Ubuntu server after editing any CSS/JS/image in vms_project/static/
# No Docker restart needed — WhiteNoise picks up changes automatically.

echo "==> Collecting updated static files..."
docker compose exec web python manage.py collectstatic --noinput

echo ""
echo "✅ Done! Static files updated."
echo "   Hard-refresh your browser with Ctrl+Shift+R to see the changes."
