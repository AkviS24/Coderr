# Coderr

Coderr is a developer marketplace application created as part of a Developer Akademie portfolio project.

The project consists of a Django REST Framework backend and a separate frontend application.

The backend in this repository was developed by me as part of the Developer Akademie portfolio project.

## Backend Setup

### 1. Clone the repository

    git clone https://github.com/AkviS24/Coderr.git
    cd coderr/BACKEND

### 2. Create a virtual environment

#### Windows

    python -m venv .venv
    .venv\Scripts\activate

#### Linux / macOS

    python3 -m venv .venv
    source .venv/bin/activate

### 3. Install dependencies

    pip install -r requirements.txt

### 4. Configure environment variables

Create the `.env` file inside the `BACKEND` directory by copying the provided example file.

#### Windows

    copy .env.example .env

#### Linux / macOS

    cp .env.example .env

Open the `.env` file and replace the placeholder with your own Django secret key:

    SECRET_KEY=your-secret-key

The `SECRET_KEY` is loaded from the environment and is not stored directly in the source code.

The `.env` file must never be committed to the repository.

### 5. Apply database migrations

    python manage.py migrate

### 6. Create a superuser

To access the Django admin panel, create a superuser:

    python manage.py createsuperuser

Follow the prompts to enter a username, email address, and password.

The superuser can be used to log in to the Django admin panel and manage the backend data.

### 7. Start the development server

    python manage.py runserver

The backend is then available at:

    http://127.0.0.1:8000/

The API is available below:

    http://127.0.0.1:8000/api/

The Django admin panel is available at:

    http://127.0.0.1:8000/admin/

Log in to the admin panel using the credentials of the superuser you created.

## Technologies

### Backend

- Python 3.14
- Django 6.1
- Django REST Framework 3.18
- SQLite
- Django REST Framework Token Authentication
- python-dotenv
- Pillow

### Frontend

The frontend is provided separately by Developer Akademie.

Frontend repository:

https://github.com/Developer-Akademie-Backendkurs/project.Coderr

The frontend should be copied into the `FRONTEND` directory of this repository.

## Project Structure

    coderr/
    ├── BACKEND/
    │   ├── api_app/
    │   ├── auth_app/
    │   ├── core/
    │   ├── offers_app/
    │   ├── orders_app/
    │   ├── profile_app/
    │   ├── reviews_app/
    │   ├── manage.py
    │   └── ...
    ├── FRONTEND/
    │   └── ...
    └── README.md

## Frontend Setup

The Coderr frontend is available in the Developer Akademie repository:

https://github.com/Developer-Akademie-Backendkurs/project.Coderr

Download or clone the frontend project and copy its contents into the `FRONTEND` directory of this repository.

Follow the setup instructions provided in the frontend repository.

The frontend communicates with the Coderr backend through the REST API.

## Authentication

The API uses Django REST Framework Token Authentication.

Authenticated requests require the following HTTP header:

    Authorization: Token <your-token>

## API

The API is organized into the following areas:

- Authentication and registration
- Customer profiles
- Business profiles
- Offers
- Offer details
- Orders
- Order counts
- Completed order counts
- Reviews
- Base information

The API endpoints are available below the `/api/` path.

## Testing

Run the complete Django test suite from the `BACKEND` directory:

    python manage.py test

For test coverage:

    coverage run manage.py test
    coverage report

To generate an HTML coverage report:

    coverage html

The generated `htmlcov/` directory is excluded from version control.

## Development Principles

The project follows a clear separation of responsibilities:

- **Models** define the database structure.
- **Serializers** handle validation and data transformation.
- **Views** handle API requests and responses.
- **Permissions** handle access control.
- **URLs** handle API routing.

The project follows Clean Code and PEP 8 principles.

Functions and methods should generally remain within 14 lines where practical. The 14-line rule is treated as a guideline and should not lead to artificial or unnecessary helper functions.

Classes and functions are documented where appropriate. Comments are used only when they provide useful additional context.

## Environment and Security

Sensitive configuration is loaded through environment variables.

The following files and directories are excluded from version control:

- `.env`
- virtual environments
- SQLite database files
- uploaded media
- Python cache files
- test and coverage artifacts
- IDE configuration files

Never commit secrets, passwords, tokens, or other sensitive configuration data to the repository.

## Database

The backend uses SQLite for local development.

The local database file is:

    db.sqlite3

Database files are excluded from version control.

## Media Files

Uploaded media files are stored in the local `media/` directory.

The `media/` directory is excluded from version control.

## License

This project was created as part of a Developer Akademie portfolio project.