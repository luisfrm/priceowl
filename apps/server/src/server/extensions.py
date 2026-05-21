from apscheduler.schedulers.background import BackgroundScheduler
from flask_sqlalchemy import SQLAlchemy

# These instances are created here without being tied to any app.
# They are initialized later inside create_app() via db.init_app(app).
# This pattern avoids circular imports across routes, services, and models.

db = SQLAlchemy()
scheduler = BackgroundScheduler()