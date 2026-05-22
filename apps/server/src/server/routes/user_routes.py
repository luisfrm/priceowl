from flask import Blueprint

bp = Blueprint("user_routes", __name__)

@bp.route("/")
def index():
    return {"status": "ok"}