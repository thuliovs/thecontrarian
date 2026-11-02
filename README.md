# The Contrarian Report

A Django platform that connects clients with professional writers and manages projects, contracts, roles, and PayPal subscription payments.

[Live project](https://thecontrarian.thulio.tech)

## Highlights

- Separate client, writer, and administrator experiences
- Authentication and role-based access
- Project and contract workflows
- PayPal subscription integration
- Responsive Bootstrap 5 interface
- SQLite for local development and optional MySQL migration tooling
- Production configuration for Gunicorn, WhiteNoise, and Vercel

## Technology

- Python and Django
- HTML, CSS, and Bootstrap 5
- SQLite / MySQL
- PayPal REST API
- Gunicorn and WhiteNoise

## Local setup

### Requirements

- Python 3.8+
- Git

```bash
git clone https://github.com/thuliovs/thecontrarian.git
cd thecontrarian

python -m venv .venv
```

Activate the virtual environment:

```bash
# Windows
.venv\Scripts\activate

# macOS / Linux
source .venv/bin/activate
```

Install dependencies and prepare the database:

```bash
pip install -r requirements.txt
cd src
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
```

Open `http://127.0.0.1:8000/`.

## PayPal sandbox

Create a local `.env` file with sandbox credentials:

```env
PAYPAL_CLIENT_ID=your_client_id
PAYPAL_SECRET_ID=your_secret
PAYPAL_AUTH_URL=https://api.sandbox.paypal.com/v1/oauth2/token
PAYPAL_BILLING_SUBSCRIPTIONS_URL=https://api.sandbox.paypal.com/v1/billing/subscriptions
```

Never commit credentials or production secrets.

## Project structure

```text
src/
  account/       authentication and user management
  client/        client workflows
  writer/        writer workflows
  common/        shared templates and utilities
  contrarian/    Django settings and project configuration
  static/        CSS, JavaScript, and images
docs/             project documentation
```

## Production checklist

Before deploying a fork:

- provide a strong `SECRET_KEY`;
- disable Django debug mode;
- configure HTTPS and allowed hosts;
- use production database and PayPal credentials through environment variables;
- review cookie, CSRF, and session settings.

## License

Released under the [MIT License](LICENSE).
