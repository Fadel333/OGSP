from flask import Blueprint, render_template

legal_bp = Blueprint("legal", __name__)

@legal_bp.route("/privacy-policy")
def privacy_policy():
    return render_template("legal/privacy.html")

@legal_bp.route("/terms-and-conditions")
def terms_and_conditions():
    return render_template("legal/terms.html")
