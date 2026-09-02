# Deployment Pipeline

This repo uses GitHub Actions to test every push and pull request, then deploys `main` to the VPS over SSH.

## 1. Local steps before touching the server

1. Commit and push this repository to GitHub.
2. Create an SSH key for GitHub Actions on your local machine:

   ```bash
   ssh-keygen -t ed25519 -C "github-actions-medium-online-store" -f ~/.ssh/medium_online_store_actions
   ```

3. In the GitHub repository, go to `Settings` -> `Secrets and variables` -> `Actions` and add:

   ```text
   VPS_HOST=62.171.172.156
   VPS_USER=root
   VPS_SSH_KEY=<contents of ~/.ssh/medium_online_store_actions>
   PROJECT_PATH=/srv/django/medium_online_store/app
   VENV_PATH=/srv/django/medium_online_store/venv
   SERVICE_NAME=medium-online-store
   ```

## 2. One-time server setup

1. Add the public key to the server:

   ```bash
   mkdir -p ~/.ssh
   chmod 700 ~/.ssh
   echo "<contents of ~/.ssh/medium_online_store_actions.pub>" >> ~/.ssh/authorized_keys
   chmod 600 ~/.ssh/authorized_keys
   ```

2. Create the application directory and virtual environment:

   ```bash
   mkdir -p /srv/django/medium_online_store
   cd /srv/django/medium_online_store
   python3 -m venv venv
   git clone git@github.com:GamalSerag/medium_online_store.git app
   ```

3. Create `/srv/django/medium_online_store/app/.env.production` with production values:

   ```text
   DJANGO_SETTINGS_MODULE=config.settings.production
   SECRET_KEY=<strong-secret-key>
   DEBUG=0
   ALLOWED_HOSTS=<your-domain>,www.<your-domain>,62.171.172.156
   DATABASE_URL=postgres://<user>:<password>@127.0.0.1:5432/<database>
   ```

4. Install dependencies and initialize Django:

   ```bash
   cd /srv/django/medium_online_store/app
   /srv/django/medium_online_store/venv/bin/pip install -r requirements.txt
   ENV_FILE=.env.production DJANGO_SETTINGS_MODULE=config.settings.production /srv/django/medium_online_store/venv/bin/python manage.py migrate
   ENV_FILE=.env.production DJANGO_SETTINGS_MODULE=config.settings.production /srv/django/medium_online_store/venv/bin/python manage.py collectstatic --noinput
   ```

5. Create or confirm the systemd service is named `medium-online-store`.

## 3. Deploy

Push to `main`. GitHub Actions will run tests first, then update the server and restart the service.
