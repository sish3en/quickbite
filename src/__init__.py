import os
from pathlib import Path

from dotenv import load_dotenv
from flask import Flask

from .database import init_db, seed_database


def create_app(test_config=None):
    load_dotenv()
    # The templates and static folders are located one level above src/.
    app = Flask(
        __name__,
        instance_relative_config=True,
        template_folder="../templates",
        static_folder="../static",
    )
    app.config.from_mapping(
        SECRET_KEY=os.getenv("SECRET_KEY", "development-key"),
        DATABASE_PATH=os.getenv("DATABASE_PATH", str(Path(app.instance_path) / "quickbite.db")),
        MEALDB_BASE_URL=os.getenv("MEALDB_BASE_URL", "https://www.themealdb.com/api/json/v1/1"),
        MEALDB_TIMEOUT=float(os.getenv("MEALDB_TIMEOUT", "5")),
    )
    if test_config:
        app.config.update(test_config)

    Path(app.instance_path).mkdir(parents=True, exist_ok=True)
    init_db(app)
    seed_database(app)

    from .routes import main_bp
    app.register_blueprint(main_bp)
    return app
