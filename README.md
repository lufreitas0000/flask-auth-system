# Flask Authentication System

A production-oriented authentication system built with Flask. This project serves as a practical implementation of modern web development techniques and software architecture principles.

## Core Techniques Demonstrated

* **Modular Monolith Architecture:** Code is organized by business domain (Bounded Contexts) rather than technical layers, allowing for future microservice extraction.
* **Application Factory Pattern:** The application is instantiated dynamically, preventing circular imports and enabling flexible testing and environment configurations.
* **Object-Relational Mapping (ORM):** Uses SQLAlchemy for database interactions, keeping the domain model in Python while allowing underlying SQL engines to be swapped easily.
* **Object-Oriented Configuration:** Utilizes class inheritance for secure and strict separation of Development and Production states.
* **Security Best Practices:** * Server-side form validation and CSRF protection via Flask-WTF.
  * Secure password hashing utilizing Werkzeug.
  * Session management controlled by Flask-Login.

## Project Structure

* `config.py`: Environment-aware application configuration.
* `run.py`: The WSGI entry point for the development server.
* `src/`: The application package.
  * `__init__.py`: The Application Factory.
  * `extensions.py`: Unbound extension declarations.
  * `auth/`: The isolated authentication module (Models, Forms, Routes).

## Phase 2 Architecture

* **Database Migrations (Alembic):** The schema is version-controlled via `Flask-Migrate`.
  * To generate a migration: `python -m flask db migrate -m "message"`
  * To apply a migration: `python -m flask db upgrade`
* **Infrastructure Monitoring:** A liveness probe is available at `/status` to verify database connectivity and measure latency.
* **Security Auditing:** (In Progress) Implementation of a relational `AuditLog` to track historical authentication events and IP addresses.

## Testing
The application uses `pytest` with an isolated, in-memory SQLite database (`os.environ['DATABASE_URL'] = "sqlite://"`).
