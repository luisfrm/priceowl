from flask import Blueprint

bp = Blueprint("product_routes", __name__)

@bp.route("/")
def index():
    return {"status": "ok"}