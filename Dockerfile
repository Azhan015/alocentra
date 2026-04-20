FROM python:3.11-slim

WORKDIR /app

RUN apt-get update && apt-get install -y \
    build-essential \
    libpq-dev \
    curl \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# APP_ENV controls runtime behaviour: "development" or "production"
ARG APP_ENV=production
ENV APP_ENV=${APP_ENV}

EXPOSE 8000

CMD ["/bin/sh", "-c", "\
  if [ \"$APP_ENV\" = 'development' ]; then \
    python manage.py runserver 0.0.0.0:8000; \
  else \
    python manage.py collectstatic --noinput && \
    gunicorn alocentra.wsgi:application \
      --bind 0.0.0.0:8000 \
      --workers 3 \
      --timeout 120 \
      --access-logfile - \
      --error-logfile -; \
  fi"]