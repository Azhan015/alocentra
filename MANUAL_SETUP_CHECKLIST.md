# Manual Setup Checklist

- [x] Create Virtual Environment and install packages inside `e:\AC\alocentra`
- [x] Configure Postgres DB string in `.env`
- [x] Run `python manage.py migrate`
- [x] Create the `.env` file from the example structure provided
- [ ] Run Redis Server (e.g. via WSL, Docker, or Windows binary)
- [ ] Run Celery Worker locally to send dynamic email invites (`pip install eventlet; celery -A alocentra worker -P eventlet -l info`)
- [ ] Load staticfiles (`python manage.py collectstatic`) (For Production)

If all items above look good, you can proceed to use `python manage.py runserver` to load AloCentra securely on `localhost`!
