import os
import sys

# Ensure project root is in sys.path
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

from flask import Flask, send_from_directory, request, redirect, render_template
from backend.config import Config
from backend.routes.api import api_bp
from backend.services.predictor import PredictorService, FEATURE_NAMES, FEATURE_META


def create_app(config_class=Config) -> Flask:
    """Creates and configures the Flask application."""
    templates_dir = os.path.join(BASE_DIR, "templates")
    app = Flask(
        __name__,
        static_folder=config_class.FRONTEND_DIR,
        static_url_path="",
        template_folder=templates_dir
    )
    app.config.from_object(config_class)

    # Register REST API blueprint
    app.register_blueprint(api_bp)

    # Simple manual CORS headers for API routes
    @app.after_request
    def add_cors_headers(response):
        response.headers["Access-Control-Allow-Origin"] = "*"
        response.headers["Access-Control-Allow-Headers"] = "Content-Type,Authorization"
        response.headers["Access-Control-Allow-Methods"] = "GET,PUT,POST,DELETE,OPTIONS"
        return response

    # Backwards-compatible legacy route for /predict
    @app.route("/predict", methods=["GET", "POST"])
    def legacy_predict():
        if request.method == "GET":
            return redirect("/")

        form_data = request.form
        # Validate fields
        for feat in FEATURE_NAMES:
            if feat not in form_data or not str(form_data[feat]).strip():
                return f"Missing required field: '{feat}'", 400
            try:
                val = float(form_data[feat])
            except ValueError:
                return f"Parameter '{feat}' must be a numeric value", 400
            if not (1.0 <= val <= 10.0):
                return f"Parameter '{feat}' must be between 1 and 10", 400

        predictor = PredictorService.get_instance()
        data_dict = {f: float(form_data[f]) for f in FEATURE_NAMES}
        result = predictor.predict_single(data_dict)

        feature_display = {
            FEATURE_META[f]["label"]: int(data_dict[f]) if data_dict[f].is_integer() else data_dict[f]
            for f in FEATURE_NAMES
        }

        if result["is_malignant"]:
            return render_template("yes.html", features=feature_display), 200
        else:
            return render_template("no.html", features=feature_display), 200

    # Serve decoupled Frontend SPA
    @app.route("/", defaults={"path": ""}, endpoint="home")
    @app.route("/<path:path>")
    def home(path):
        frontend_dir = app.static_folder
        if path != "" and os.path.exists(os.path.join(frontend_dir, path)):
            return send_from_directory(frontend_dir, path)
        return send_from_directory(frontend_dir, "index.html")

    return app


if __name__ == "__main__":
    application = create_app()
    print(f"Starting OncoScreen ML Server on http://{Config.HOST}:{Config.PORT}")
    application.run(host=Config.HOST, port=Config.PORT, debug=Config.DEBUG)
