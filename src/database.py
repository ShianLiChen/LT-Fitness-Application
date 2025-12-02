# src/database.py
from flask_sqlalchemy import SQLAlchemy


# -------------------------
# Database Instance
# -------------------------
"""
SQLAlchemy database instance used throughout the application to interact
with the database. Import `db` in models, routes, and other modules
to perform queries and manage database objects.
"""
db = SQLAlchemy()
