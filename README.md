# UFC Pick'em

A backend service for predicting UFC fight outcomes. Users create an account, submit picks for upcoming fights before a lock deadline, and get scored automatically once results are in.

## What it does

- Register and log in with a real authentication system — passwords are hashed, never stored in plain text
- Submit a pick for any upcoming fight, as long as it's before the event's lock time
- Once a fight result is recorded, check who picked correctly

## How it works

**Authentication:** Passwords are hashed with bcrypt before being stored. Login issues a JWT that has to be included on every protected request. A dependency (`get_current_user`) verifies that token and identifies the requesting user before any protected endpoint runs.

**Data model:** Four related tables — `users`, `events`, `fights`, and `picks`. `picks` is a many-to-many junction table connecting users and fights, since one user can pick many fights and one fight can be picked by many users. A unique constraint on `(user_id, fight_id)` prevents a user from picking the same fight twice.

**Concurrency safety:** Rather than checking "does this pick already exist?" before inserting — which has a race condition if two identical requests arrive close together — the app relies on the database's unique constraint to reject duplicates. The insert is attempted directly, and a caught `IntegrityError` handles the duplicate case cleanly instead of crashing.

**Lock-time enforcement:** Each event has a `lock_time`. Submitting a pick after that time is rejected, checked by traversing the relationship from a pick's fight to its event.

**Scoring:** Once an admin records a fight's real winner, an endpoint compares every submitted pick against that result and reports who was correct.

## Tech stack

Python, FastAPI, PostgreSQL, SQLAlchemy, python-jose (JWT), passlib + bcrypt (password hashing), deployed on Railway.

## Running it locally

1. Clone the repo and create a virtual environment

python -m venv venv
.\venv\Scripts\Activate.ps1
pip install -r requirements.txt

2. Create a `.env` file with:
DATABASE_URL=postgresql://user:password@localhost:5432/ufcpickem
JWT_SECRET_KEY=your_generated_secret_key

3. Create the tables:
python create_tables.py

4. Run the server:uvicorn main:app --reload

5. Visit `http://127.0.0.1:8000/docs` to view the API (note: protected routes require a bearer token in the Authorization header, since this project's login doesn't use Swagger's default OAuth2 form flow)

## Upcoming additions

- A real UFC event data source instead of manually entered fights
- A simpler way to authenticate through the Swagger docs UI
- Tests specifically simulating concurrent pick submissions