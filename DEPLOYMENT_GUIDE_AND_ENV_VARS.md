# AloCentra — Complete Deployment & Environment Guide

> **One file. Zero guesswork.**  
> Follow every section from top to bottom. By the end you will have AloCentra running
> either on your laptop or on a free cloud server — or both.

---

## Table of Contents

1. [Understanding the `.env` File](#1-understanding-the-env-file)
2. [How to Get Every Value — Step by Step](#2-how-to-get-every-value--step-by-step)
3. [Running Locally with Docker](#3-running-locally-with-docker)
4. [Free Cloud Deployment Options](#4-free-cloud-deployment-options)
   - 4A. [Railway (Recommended — Easiest)](#4a-railway-recommended--easiest)
   - 4B. [Render.com](#4b-rendercom)
   - 4C. [Fly.io](#4c-flyio)
   - 4D. [Oracle Cloud Always Free (Most Powerful)](#4d-oracle-cloud-always-free-most-powerful)
5. [Post-Deployment Checklist](#5-post-deployment-checklist)
6. [Troubleshooting](#6-troubleshooting)

---

## 1. Understanding the `.env` File

Your `.env` file lives at the **root of the project** (same folder as `manage.py`).  
It is listed in `.gitignore` — it will **never** be pushed to GitHub. That is intentional.

### Full `.env` Template

Copy this block, paste it into a new file called `.env`, then fill in each value
using Section 2 below.

```env
# ── Environment mode ──────────────────────────────────────────────────────────
# "development"  → Django debug server, debug toolbar, verbose errors
# "production"   → Gunicorn, no debug, strict security headers
APP_ENV=development
DJANGO_SETTINGS_MODULE=alocentra.settings.development

# ── Django core ───────────────────────────────────────────────────────────────
DJANGO_SECRET_KEY=REPLACE_WITH_GENERATED_KEY
DJANGO_DEBUG=True
DJANGO_ALLOWED_HOSTS=localhost,127.0.0.1,0.0.0.0

# ── PostgreSQL (Docker creates this DB automatically from these values) ────────
POSTGRES_DB=alocentra_db
POSTGRES_USER=alocentra_user
POSTGRES_PASSWORD=REPLACE_WITH_STRONG_PASSWORD
DATABASE_URL=postgresql://alocentra_user:REPLACE_WITH_STRONG_PASSWORD@db:5432/alocentra_db

# ── Redis / Celery ────────────────────────────────────────────────────────────
REDIS_URL=redis://redis:6379/0

# ── Email (Gmail App Password) ────────────────────────────────────────────────
EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=yourgmail@gmail.com
EMAIL_HOST_PASSWORD=REPLACE_WITH_16_CHAR_APP_PASSWORD
DEFAULT_FROM_EMAIL=yourgmail@gmail.com

# ── Frontend URL (used in invitation emails) ──────────────────────────────────
FRONTEND_URL=http://localhost:8000

# ── Optional port overrides (local only) ─────────────────────────────────────
DB_PORT=5433
REDIS_PORT=6380
```

### Production differences (change these values when deploying)

| Variable | Local value | Production value |
|---|---|---|
| `APP_ENV` | `development` | `production` |
| `DJANGO_SETTINGS_MODULE` | `alocentra.settings.development` | `alocentra.settings.production` |
| `DJANGO_DEBUG` | `True` | `False` |
| `DJANGO_ALLOWED_HOSTS` | `localhost,127.0.0.1` | `yourdomain.com,www.yourdomain.com` |
| `DATABASE_URL` | points to `@db:5432` | points to cloud DB host |
| `REDIS_URL` | `redis://redis:6379/0` | points to cloud Redis host |
| `FRONTEND_URL` | `http://localhost:8000` | `https://yourdomain.com` |

---

## 2. How to Get Every Value — Step by Step

### 2.1 `DJANGO_SECRET_KEY`

This is a random 50-character string Django uses to sign cookies and tokens.
**Never share it. Never commit it.**

**Step 1:** Open any terminal where Python is available and run:
```bash
python -c "import secrets; print(secrets.token_urlsafe(50))"
```

**Step 2:** Copy the output (looks like `abc123XYZ...`) and paste it as:
```env
DJANGO_SECRET_KEY=abc123XYZ...
```

If you do not have Python locally, use this site: https://djecrety.ir/  
Click "Generate" and copy the result.

---

### 2.2 `POSTGRES_DB`, `POSTGRES_USER`, `POSTGRES_PASSWORD`

When using Docker you **invent these yourself**. Docker reads the values and creates
the database for you automatically on first run.

**Rules for a good password:**
- At least 16 characters
- Mix of upper, lower, numbers, symbols (`@`, `!`, `#`)
- Example: `AloC3ntra@Exam#2026`

**Example block:**
```env
POSTGRES_DB=alocentra_db
POSTGRES_USER=alocentra_user
POSTGRES_PASSWORD=AloC3ntra@Exam#2026
DATABASE_URL=postgresql://alocentra_user:AloC3ntra@Exam#2026@db:5432/alocentra_db
```

> ⚠️ The `@db:5432` part stays exactly as `db:5432`.  
> Inside Docker, the hostname `db` resolves to the Postgres container automatically.

---

### 2.3 `EMAIL_HOST_USER` and `EMAIL_HOST_PASSWORD`

AloCentra sends invitation emails via Gmail SMTP. Follow these exact steps:

**Step 1:** Log into your Google account at https://myaccount.google.com

**Step 2:** Click **Security** in the left sidebar.

**Step 3:** Scroll down to **"How you sign in to Google"** and click **2-Step Verification**.
Enable it if it is not already on (required for App Passwords to work).

**Step 4:** After enabling 2-Step Verification, go back to the Security page
and search for **"App passwords"** in the search bar at the top.

**Step 5:** Click **App passwords**. If you cannot find it, visit directly:
https://myaccount.google.com/apppasswords

**Step 6:** In the dropdown **"Select app"** choose **"Other (Custom name)"**
and type `AloCentra`. Click **Generate**.

**Step 7:** Google shows a 16-character password in a yellow box like:
```
abcd efgh ijkl mnop
```

**Step 8:** **Remove the spaces** and place the 16 letters in your `.env`:
```env
EMAIL_HOST_USER=yourgmail@gmail.com
EMAIL_HOST_PASSWORD=abcdefghijklmnop
DEFAULT_FROM_EMAIL=yourgmail@gmail.com
```

> 💡 If you do not want to use Gmail in development, set:
> ```env
> EMAIL_BACKEND=django.core.mail.backends.console.EmailBackend
> ```
> Invitation emails will print to the terminal instead of actually sending.

---

### 2.4 `DJANGO_ALLOWED_HOSTS`

- **Local:** `localhost,127.0.0.1,0.0.0.0` — no changes needed
- **Cloud server with IP:** `192.168.1.100` — add your server's public IP
- **Custom domain:** `alocentra.mycollege.edu,www.alocentra.mycollege.edu`

Separate multiple values with commas. No spaces.

---

## 3. Running Locally with Docker

### Prerequisites

- Windows 10/11 or macOS or Linux
- Docker Desktop installed (https://www.docker.com/products/docker-desktop/)

### Step-by-Step

**Step 1 — Install Docker Desktop**

1. Go to https://www.docker.com/products/docker-desktop/
2. Download for your OS and run the installer.
3. On Windows, enable **WSL 2 backend** when prompted.
4. Restart your computer if asked.
5. Open Docker Desktop and wait for the green "Engine Running" indicator in the taskbar.

**Step 2 — Clone or open the project**

```bash
# If you are cloning for the first time:
git clone https://github.com/YOURNAME/alocentra.git
cd alocentra

# If the project is already on your machine, just open a terminal inside it.
```

**Step 3 — Create your `.env` file**

1. In the project root, find the file `.env.example`.
2. Copy it and rename the copy to exactly `.env`.
3. Open `.env` and fill every value using Section 2 above.
4. Keep `APP_ENV=development` for local use.

**Step 4 — Build and start all containers**

```bash
docker compose up -d --build
```

- This downloads Postgres, Redis, and Python images (first time only, ~5-10 minutes).
- After completion you will see: `Started alocentra-web-1`, `Started alocentra-db-1`, etc.

**Step 5 — Run database migrations**

```bash
docker compose exec web python manage.py migrate
```

You should see many lines ending in `OK`.

**Step 6 — Open the app**

Navigate to http://localhost:8000 in your browser.
Click **Register** to create the first COE account.

**Step 7 — Stopping the server**

```bash
docker compose down
```

Next time: `docker compose up -d` (no `--build` needed unless you changed Python files).

---

## 4. Free Cloud Deployment Options

All options below are **100% free** at the tier described. You do not need a credit card
for options 4A and 4B. Option 4D requires a credit card for identity verification only —
no charges are made.

---

### 4A. Railway (Recommended — Easiest)

Railway gives you $5 of credit per month on the Hobby plan (free) which is enough
for a small Django app + Postgres + Redis.

**What you get free:** 512 MB RAM, Postgres, Redis, automatic HTTPS, custom domain.

#### Step 1 — Create a Railway account

1. Go to https://railway.app
2. Click **Login** → **Login with GitHub**
3. Authorise Railway to access your GitHub.

#### Step 2 — Push your code to GitHub

```bash
# From inside your alocentra folder:
git init
git add .
git commit -m "initial commit"
git remote add origin https://github.com/YOURNAME/alocentra.git
git push -u origin main
```

#### Step 3 — Create a new Railway project

1. On the Railway dashboard click **New Project**.
2. Select **Deploy from GitHub repo**.
3. Choose your `alocentra` repo.
4. Railway detects it is a Python project and starts building.

#### Step 4 — Add Postgres

1. Inside your Railway project click **+ New**.
2. Select **Database → Add PostgreSQL**.
3. Railway creates a Postgres instance and gives you a `DATABASE_URL`.
4. Click the Postgres service → **Variables** tab → copy `DATABASE_URL`.

#### Step 5 — Add Redis

1. Click **+ New → Database → Add Redis**.
2. Copy the `REDIS_URL` from the Redis service's Variables tab.

#### Step 6 — Set environment variables

Click your **web service** → **Variables** tab → **Raw Editor** and paste:

```env
APP_ENV=production
DJANGO_SETTINGS_MODULE=alocentra.settings.production
DJANGO_SECRET_KEY=<generate one with python -c "import secrets; print(secrets.token_urlsafe(50))">
DJANGO_DEBUG=False
DJANGO_ALLOWED_HOSTS=${{RAILWAY_PUBLIC_DOMAIN}}
DATABASE_URL=${{Postgres.DATABASE_URL}}
REDIS_URL=${{Redis.REDIS_URL}}
EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=yourgmail@gmail.com
EMAIL_HOST_PASSWORD=your16charapppassword
DEFAULT_FROM_EMAIL=yourgmail@gmail.com
FRONTEND_URL=https://${{RAILWAY_PUBLIC_DOMAIN}}
```

> Railway uses `${{ServiceName.VARIABLE}}` syntax to reference other services' variables automatically.

#### Step 7 — Set the start command

In your web service → **Settings** → **Start Command**:
```
python manage.py migrate && gunicorn alocentra.wsgi:application --bind 0.0.0.0:$PORT --workers 3
```

#### Step 8 — Deploy

Click **Deploy**. Railway builds your Docker image and starts the service.
Once it shows **Active**, click the domain link to open your app.

#### Step 9 — Create COE account

Visit `https://your-project.up.railway.app` and click Register.

---

### 4B. Render.com

Render offers a free web service (750 hours/month) and a free PostgreSQL database
(valid for 90 days, then $7/month — use Railway if you need it longer).

#### Step 1 — Create account

1. Go to https://render.com
2. Sign up with GitHub.

#### Step 2 — Create a Web Service

1. Dashboard → **New → Web Service**
2. Connect your GitHub repo `alocentra`.
3. Fill in:
   - **Environment:** Docker
   - **Region:** nearest to you
   - **Instance Type:** Free

#### Step 3 — Set environment variables

In the **Environment** section of your web service add each variable from the
Production list in Section 1. For `DATABASE_URL` use the connection string from
Step 4 below.

#### Step 4 — Create a PostgreSQL database

1. Dashboard → **New → PostgreSQL**
2. Give it a name like `alocentra-db`.
3. **Instance type:** Free
4. After creation, copy the **Internal Database URL** and paste it as `DATABASE_URL`
   in your web service environment variables.

#### Step 5 — Create a Redis instance

1. Dashboard → **New → Redis**
2. Free tier → Create.
3. Copy the **Internal Redis URL** and paste it as `REDIS_URL`.

#### Step 6 — Deploy

Render auto-deploys whenever you push to GitHub. Your first deploy will take 3-5
minutes. After it completes, click the `.onrender.com` URL.

#### Step 7 — Run migrations (one time only)

On the Render dashboard → your web service → **Shell** tab:
```bash
python manage.py migrate
```

---

### 4C. Fly.io

Fly gives you 3 shared-CPU VMs and 3 GB persistent storage free, always.

#### Step 1 — Install Fly CLI

```bash
# macOS / Linux
curl -L https://fly.io/install.sh | sh

# Windows PowerShell (run as Admin)
iwr https://fly.io/install.ps1 -useb | iex
```

#### Step 2 — Sign up and log in

```bash
fly auth signup    # creates a free account
# OR if you already have one:
fly auth login
```

#### Step 3 — Launch the app

Inside your project folder:
```bash
fly launch
```

Answer the prompts:
- App name: `alocentra` (or any name)
- Region: choose the closest one
- PostgreSQL: **yes** (Fly creates a free Postgres cluster)
- Redis: **yes** (Fly creates a free Upstash Redis)
- Deploy now: **no** (we need to set env vars first)

#### Step 4 — Set environment variables

```bash
fly secrets set \
  APP_ENV=production \
  DJANGO_SETTINGS_MODULE=alocentra.settings.production \
  DJANGO_SECRET_KEY="$(python -c 'import secrets; print(secrets.token_urlsafe(50))')" \
  DJANGO_DEBUG=False \
  DJANGO_ALLOWED_HOSTS=alocentra.fly.dev \
  EMAIL_HOST=smtp.gmail.com \
  EMAIL_PORT=587 \
  EMAIL_USE_TLS=True \
  EMAIL_HOST_USER=yourgmail@gmail.com \
  EMAIL_HOST_PASSWORD=your16charapppassword \
  DEFAULT_FROM_EMAIL=yourgmail@gmail.com \
  FRONTEND_URL=https://alocentra.fly.dev
```

The `DATABASE_URL` and `REDIS_URL` are set automatically by Fly when you created
the Postgres and Redis services in Step 3.

#### Step 5 — Deploy

```bash
fly deploy
```

#### Step 6 — Migrate and open

```bash
fly ssh console -C "python manage.py migrate"
fly open
```

---

### 4D. Oracle Cloud Always Free (Most Powerful)

Oracle gives you **2 AMD Compute VMs** with 1 GB RAM each and **200 GB block storage**
**forever** — no expiry, no credit card charges after verification.

This option requires the most setup but gives you the most power and control.

#### Step 1 — Create Oracle Cloud account

1. Go to https://www.oracle.com/cloud/free/
2. Click **Start for free**.
3. Fill in your details. A credit card is required for **identity verification only**.
   You will not be charged if you stay within Always Free resources.
4. Select your home region (cannot be changed later — pick closest to your users).

#### Step 2 — Create a VM instance

1. Dashboard → **Compute → Instances → Create Instance**
2. Shape: **VM.Standard.E2.1.Micro** (Always Free)
3. Image: **Ubuntu 22.04 LTS**
4. Networking: create a new VCN or use default. Enable a public IP.
5. SSH keys: paste your public SSH key (generate with `ssh-keygen -t ed25519`)
6. Click **Create**.
7. Wait 2-3 minutes. Note the **Public IP address**.

#### Step 3 — Open firewall ports

1. In Oracle Cloud → your instance → **Subnet** → **Security List**
2. Add **Ingress Rules**:
   - Source: `0.0.0.0/0`, Protocol: TCP, Port: `80`
   - Source: `0.0.0.0/0`, Protocol: TCP, Port: `443`

Also run this on the VM to open the OS firewall:
```bash
sudo iptables -I INPUT 6 -m state --state NEW -p tcp --dport 80 -j ACCEPT
sudo iptables -I INPUT 6 -m state --state NEW -p tcp --dport 443 -j ACCEPT
sudo netfilter-persistent save
```

#### Step 4 — SSH into your VM and install Docker

```bash
ssh ubuntu@YOUR_PUBLIC_IP

# Once inside the VM:
sudo apt update && sudo apt upgrade -y
sudo apt install -y docker.io docker-compose-v2 git
sudo usermod -aG docker $USER
newgrp docker
```

#### Step 5 — Clone your project

```bash
sudo mkdir -p /opt/alocentra
sudo chown $USER:$USER /opt/alocentra
cd /opt/alocentra
git clone https://github.com/YOURNAME/alocentra.git .
```

#### Step 6 — Create `.env` for production

```bash
nano .env
```

Paste the production template from Section 1, filling in all values.
Change:
- `APP_ENV=production`
- `DJANGO_SETTINGS_MODULE=alocentra.settings.production`
- `DJANGO_DEBUG=False`
- `DJANGO_ALLOWED_HOSTS=YOUR_PUBLIC_IP` (or your domain)
- `DATABASE_URL=postgresql://alocentra_user:PASSWORD@db:5432/alocentra_db`
  (keep `@db:5432` — Docker internal networking)
- `FRONTEND_URL=http://YOUR_PUBLIC_IP` (or `https://yourdomain.com`)

Save with `Ctrl+O`, exit with `Ctrl+X`.

#### Step 7 — Start production stack with Nginx

```bash
docker compose --profile production up -d --build
```

#### Step 8 — Run migrations

```bash
docker compose exec web python manage.py migrate
```

#### Step 9 — Get a free domain and HTTPS (optional but recommended)

**Free domain:** https://www.freenom.com or https://freedns.afraid.org  
Point the domain's A record to your Oracle VM public IP.

**Free HTTPS with Let's Encrypt:**

Edit `nginx/nginx.prod.conf` and replace `your_domain` with your actual domain.
Then run Certbot:
```bash
docker compose --profile ssl run --rm certbot certonly \
  --webroot -w /var/www/certbot \
  -d yourdomain.com -d www.yourdomain.com \
  --email youremail@gmail.com \
  --agree-tos --no-eff-email
```

Uncomment the SSL lines in `nginx/nginx.prod.conf`, then:
```bash
docker compose --profile production restart nginx
```

Your site is now live at `https://yourdomain.com` with auto-renewing certificates.

#### Step 10 — Auto-start on reboot

```bash
sudo crontab -e
# Add this line:
@reboot cd /opt/alocentra && docker compose --profile production up -d
```

---

## 5. Post-Deployment Checklist

After any deployment, verify these in order:

- [ ] Homepage loads without errors
- [ ] Register page appears (first COE registration open)
- [ ] Create first COE account successfully
- [ ] Dashboard shows Rooms, Faculty, Timetable cards
- [ ] Add one test room manually
- [ ] Invite a second user (verify email arrives)
- [ ] Invited user can set password via link
- [ ] Django admin works at `/admin/` (create a superuser first)
- [ ] `DJANGO_DEBUG=False` in production (check no yellow error pages)
- [ ] Static files load (CSS/JS styled correctly — not plain HTML)
- [ ] HTTPS certificate valid (padlock in browser)

**Create a Django superuser for /admin:**
```bash
# Docker:
docker compose exec web python manage.py createsuperuser

# Railway/Render shell:
python manage.py createsuperuser

# Fly.io:
fly ssh console -C "python manage.py createsuperuser"
```

---

## 6. Troubleshooting

| Problem | Likely cause | Fix |
|---|---|---|
| `django.db.OperationalError` on startup | DB not ready yet | Wait 30 s, retry; check `DATABASE_URL` format |
| Static files not loading in prod | `collectstatic` not run | Add `python manage.py collectstatic --noinput` to start command |
| `ALLOWED_HOSTS` error | Domain not in env var | Add exact domain (no `https://`) to `DJANGO_ALLOWED_HOSTS` |
| Celery not sending emails | Redis not reachable | Check `REDIS_URL`; ensure Redis service is running |
| `502 Bad Gateway` from Nginx | Gunicorn not started | Check `docker compose logs web` |
| App password email rejected | 2-Step not enabled | Enable 2-Step Verification first, then regenerate app password |
| `SECRET_KEY` error | Default placeholder still set | Generate and replace `DJANGO_SECRET_KEY` in `.env` |
| Port 8000 already in use | Another service on that port | Change `ports: - "8001:8000"` in compose or kill conflicting process |

### Useful diagnostic commands

```bash
# View live logs from all containers
docker compose logs -f

# View only web logs
docker compose logs -f web

# Access Django shell
docker compose exec web python manage.py shell

# Check which containers are running
docker compose ps

# Restart only one service
docker compose restart web

# Hard reset (deletes all data — local dev only)
docker compose down -v && docker compose up -d --build
```