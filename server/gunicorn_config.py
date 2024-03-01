workers = 4  # Number of worker processes
bind = "0.0.0.0:8000"  # Bind to this address and port
threads = 2
chdir = "server"  # Change to your project directory
module = "managr.wsgi:application"  # WSGI module for your Django application
timeout = 60
# Logging settings
accesslog = "-"  # Log to stdout
errorlog = "-"  # Log to stderr
loglevel = "info"  # Logging level: debug, info, warning, error, critical

# Set the maximum number of requests a worker will process before restarting
max_requests = 1000

# Set the maximum number of connections a worker will handle before restarting
max_requests_jitter = 100
