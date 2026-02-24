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
