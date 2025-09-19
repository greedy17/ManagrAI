# ---------- FRONTEND BUILD ----------
FROM node:14 AS frontend
WORKDIR /app/client

# Allow npm to run as root
RUN npm config set unsafe-perm true

# Copy package.json + package-lock.json (if exists) first
COPY client/package*.json ./

# Install frontend dependencies
RUN npm install

# Copy frontend source code
COPY client/ ./

# Build frontend
RUN npm run build

# ---------- BACKEND BUILD ----------
FROM python:3.9 AS backend
WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential libpq-dev && \
    rm -rf /var/lib/apt/lists/*

# Copy requirements from root
COPY requirements.txt .

# Install Python dependencies
RUN pip install --upgrade pip && pip install -r requirements.txt

# Copy backend code
COPY . .

# Copy built frontend into Django static folder
COPY --from=frontend /app/client/dist ./client/dist

# Collect static files
RUN python manage.py collectstatic --noinput

# Gunicorn entrypoint
CMD ["gunicorn", "managr.wsgi:application", "--workers=4", "--threads=4", "--bind", "0.0.0.0:$PORT"]
