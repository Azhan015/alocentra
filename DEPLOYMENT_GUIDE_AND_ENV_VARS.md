# AloCentra: Deep-Dive Deployment & Environment Guide

This guide contains everything you need to know about setting up and running **AloCentra** on your local machine and in a production host environment.

---

## 1. Environment Variables (`.env`) & The Database Connection

The entire application relies on environment variables defined in a `.env` file at the root of the project. This prevents sensitive information (like passwords) from being pushed to source control (GitHub/GitLab).

### Database Configuration (PostgreSQL)

When running the project via Docker, the `docker-compose.yml` file uses the official `postgres` image to automatically spin up a database server. 

Here are the critical keys and how they correlate:

- `POSTGRES_DB`: The name of the database that will be created.
- `POSTGRES_USER`: The superuser username for Postgres.
- `POSTGRES_PASSWORD`: The password for the `POSTGRES_USER`.
- `DATABASE_URL`: The full connection string mapped for Django to use.

**Example Local `.env` DB Vars:**
```env
POSTGRES_DB=alocentra_db
POSTGRES_USER=alocentra_user
POSTGRES_PASSWORD=supersecurepassword123

# The connection string syntax is: postgresql://[USER]:[PASSWORD]@[HOST]:[PORT]/[DB_NAME]
# "db" is the host because inside the Docker Network, services can resolve each other by their container names.
DATABASE_URL=postgresql://alocentra_user:supersecurepassword123@db:5432/alocentra_db
```

### Django Configuration
- `DJANGO_SECRET_KEY`: A random string used for cryptographic signing.
- `DJANGO_DEBUG`: Set to `True` for Local development and `False` for Production!
- `DJANGO_ALLOWED_HOSTS`: Comma-separated domains where your app will live (e.g. `localhost,127.0.0.1,api.mycollege.edu`).
- `DJANGO_SETTINGS_MODULE`: Use `alocentra.settings.development` for local or `alocentra.settings.production` for LIVE.

### Email & Celery Configuration
- `REDIS_URL=redis://redis:6379/0`: Points Celery to the Redis broker.
- Email backend uses standard SMTP (e.g., Gmail with App Passwords).

---

## 1.5 Where to Get These Values (Step-by-Step)

If you're wondering *how* to generate, find, or create these specific `.env` values so your project runs perfectly, here is a detailed breakdown for each:

### 1. DJANGO_SECRET_KEY
The Secret Key is used to cryptographically sign sessions and password resets. **Never share this value.**
- **How to get it:** You can generate a truly random secret key by opening your terminal or command prompt (if Python is installed) and running:
  ```bash
  python -c "import secrets; print(secrets.token_urlsafe(50))"
  ```
  Copy the generated string and paste it into your `.env` file as your `DJANGO_SECRET_KEY`.

### 2. Database Credentials (POSTGRES_DB, USER, PASSWORD)
If you are running the project using Docker, you get to **make these up yourself!**
- **How to get it:** Simply invent a strong password, a username, and a database name. Enter them into the `.env` file. When you launch docker, the system will automatically read these variables and create a brand-new PostgreSQL database right on your machine matching the exact credentials you provided. You don't need to install Postgres locally or configure anything else.
- **Example Creation:**
  `POSTGRES_DB=alocentradb`
  `POSTGRES_USER=myadmin`
  `POSTGRES_PASSWORD=P@ssw0rd2026`
  Then, your `DATABASE_URL` becomes: `postgresql://myadmin:P@ssw0rd2026@db:5432/alocentradb`. 
  *(Note: The `@db:5432` part stays exactly as "db:5432" because Docker uses "db" as the internal network name to link the web app to the database container).*

### 3. EMAIL_HOST_USER and EMAIL_HOST_PASSWORD
For the application to send "Invite User" emails, it needs to log into an email account on your behalf. We recommend using a standard Gmail account.
- **How to get it:** 
  1. Log into your Google Account and go to **Account Settings -> Security**.
  2. Enable **2-Step Verification** (if not already enabled).
  3. Search for **App passwords** in the top settings search bar (or go inside 2-Step Verification settings and scroll down to "App passwords").
  4. Create a new App Password (select "Other (Custom name)" and type "AloCentra Exam App").
  5. Google will generate a 16-character password in a yellow box (e.g., `abcd efgh ijkl mnop`).
  6. **Remove all the spaces** and paste that 16-letter code into `EMAIL_HOST_PASSWORD`. Finally, put your normal Gmail address into `EMAIL_HOST_USER` and `DEFAULT_FROM_EMAIL`.

### 4. DJANGO_ALLOWED_HOSTS and FRONTEND_URL
- **Local Development (Testing on your laptop):** 
  - `DJANGO_ALLOWED_HOSTS=localhost,127.0.0.1,0.0.0.0`
  - `FRONTEND_URL=http://localhost:8000`
- **When Hosting on a Server/Cloud (DigitalOcean, AWS, etc.):** 
  - Replace these with your server's Public IP address or the actual domain name you bought (e.g., `DJANGO_ALLOWED_HOSTS=192.168.1.100,alocentra.mycollege.edu` and `FRONTEND_URL=https://alocentra.mycollege.edu`).

---

## 2. Running Locally with Docker (Step-by-Step for Beginners)

Docker simplifies everything by encapsulating PostgreSQL, Redis, Celery (background tasks), and the Django App into separate containers so you don't have to install them individually on your computer.

If you have never used Docker before, read these steps carefully from start to finish.

### Step 1: Install Docker Desktop
Before you can run any Docker commands, your computer needs the Docker Engine installed.
1. Go to [https://www.docker.com/products/docker-desktop/](https://www.docker.com/products/docker-desktop/) in your web browser.
2. Click the **Download for Windows** (or Mac) button.
3. Run the installer you downloaded. Keep all the default settings checked (especially WSL 2 backend if you are on Windows).
4. Restart your computer if it asks you to.
5. After your computer restarts, **open the Docker Desktop application** from your Start Menu. 
6. Wait for the icon in your system tray (bottom right corner) to turn green or say "Engine Running". Keep this application open in the background.

### Step 2: Open Your Terminal
You need a place to type commands.
1. Open **VS Code** (or your preferred editor) and open the `alocentra` project folder.
2. Go to the top menu, click **Terminal**, then **New Terminal**.
3. *Make sure the terminal path shows that you are inside the `alocentra` folder (e.g., `E:\AC\alocentra>`).*

### Step 3: Create your `.env` File
Docker needs the environment variables to build the database.
1. Look at the files in your project folder. You will see a file named `.env.example`.
2. Right-click that file, select **Copy**, then right-click in the empty space and select **Paste**.
3. Rename the newly pasted file to exactly `.env` (with the dot at the front).
4. Open your new `.env` file and verify that the values inside look exactly like the ones discussed in Section 1.5 above. (You can leave the default passwords if you are just testing it on your laptop).

### Step 4: Build and Start the Containers
Now we tell Docker to read the `docker-compose.yml` file, download all the necessary software, and link it together.
1. In your VS Code terminal, type the following command exactly:
   ```bash
   docker compose up -d --build
   ```
2. Press **Enter**.
3. You will see Docker downloading various "layers" and fetching Python, Postgres, and Redis. This might take 5-10 minutes the very first time depending on your internet speed.
4. When it finishes, it will print messages saying things like `Started alocentra-db-1`, `Started alocentra-web-1`.

### Step 5: Migrate the Database (Tell Django to create the tables)
Even though the database server is running, Django needs to create its specific tables (like Users, Faculty, Rooms) inside that database.
1. In the exact same terminal, type:
   ```bash
   docker compose exec web python manage.py migrate
   ```
2. Press **Enter**. You will see a long list of green text saying `Applying accounts.0001_initial... OK`.

### Step 6: Access Your Live Application!
Your server is now actively running in the background.
1. Open your web browser (Chrome, Edge, Safari).
2. In the address bar at the top, type `http://localhost:8000` and hit Enter.
3. You will see the gorgeous AloCentra landing page! Click "Register" to create the very first Controller of Examinations (COE) account, which will have full admin privileges.

### How to Stop the Project Later
When you are done testing for the day and want to turn off the server so it doesn't use your computer's RAM:
1. In your terminal, type:
   ```bash
   docker compose down
   ```
2. Next time you want to start it back up, just open Docker Desktop, open your terminal, and type `docker compose up -d` (you don't need `--build` or `migrate` again unless you changed the Python code!).

---

## 3. Hosting in Production (Real Server)

If you are deploying this to a real server (like an AWS EC2 instance, DigitalOcean Droplet, Linode, etc.), follow these steps:

### A. Server Setup
1. **Provision a Linux Server** (Ubuntu 22.04 LTS is standard).
2. **Install Docker and Docker Compose**.
   ```bash
   sudo apt update
   sudo apt install docker.io docker-compose-v2 -y
   ```
3. **Clone your repository** to the server (e.g., inside `/opt/alocentra`).

### B. Production `.env`
Create a `.env` in the server project root. **CRITICAL DIFFERENCES:**
```env
DJANGO_DEBUG=False
DJANGO_ALLOWED_HOSTS=192.168.1.100,yourcustomdomain.com
DJANGO_SETTINGS_MODULE=alocentra.settings.production
DJANGO_SECRET_KEY=MakeThisAVeryLongRandomString12345!

POSTGRES_DB=alocentra_prod
POSTGRES_USER=prod_user
POSTGRES_PASSWORD=generate_a_strong_password_here
DATABASE_URL=postgresql://prod_user:generate_a_strong_password_here@db:5432/alocentra_prod
```

### C. Run the Production Compose config
Instead of the standard `docker-compose.yml`, which uses `runserver`, use the production compose file that uses `Gunicorn` (a battle-tested production web server).

```bash
docker compose -f docker-compose.prod.yml up -d --build
```

### D. Setup a Reverse Proxy (Nginx)
The Django app will run on port `8000`. You want users to access it on port `80` (HTTP) or `443` (HTTPS). Install Nginx to proxy passes the requests to Docker.

```bash
sudo apt install nginx -y
sudo nano /etc/nginx/sites-available/alocentra
```
Add the following configuration:
```nginx
server {
    listen 80;
    server_name yourcustomdomain.com;

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    # Static files routing
    location /static/ {
        alias /opt/alocentra/staticfiles/;
    }
}
```
Enable the site and restart Nginx:
```bash
sudo ln -s /etc/nginx/sites-available/alocentra /etc/nginx/sites-enabled/
sudo systemctl restart nginx
```

### E. Collect Static and Migrate (In Production)
```bash
# Apply Database Migrations
docker compose -f docker-compose.prod.yml exec web python manage.py migrate

# Gather all CSS/JS files into the staticfiles directory for Nginx to serve
docker compose -f docker-compose.prod.yml exec web python manage.py collectstatic --noinput
```

You are now successfully hosted! Secure the site with an SSL certificate using `certbot` and you are good to go.
