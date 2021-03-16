cd /opt/managr/client

echo "Removing managr webapp node_modules directory..."
rm -rf node_modules
echo "Done removing node_modules."

echo "Installing managr webapp dependencies..."
npm i

echo "Building the managr VueJS WebApp."
npm run build

cd /opt/managr/server

echo "Collecting static files..."
source /opt/venv/bin/activate && python manage.py collectstatic --noinput

echo "Restarting the Django processes..."
sudo supervisorctl restart all

echo "Removing Cypress cache directory..."
rm -rf /home/ubuntu/.cache/Cypress

echo "All done."
