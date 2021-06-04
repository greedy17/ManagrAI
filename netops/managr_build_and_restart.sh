cd /opt/managr/server
echo "pulling latest master"
git pull

echo "applying migrations"
source /opt/venv/bin/activate && python manage.py migrate --noinput

echo "Collecting static files..."
source /opt/venv/bin/activate && python manage.py collectstatic --noinput

echo "Restarting the Django processes..."
sudo supervisorctl restart all

echo "Removing Cypress cache directory..."
rm -rf /home/ubuntu/.cache/Cypress

echo "All done."
