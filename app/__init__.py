from flask import Flask
from app.routes import customer, orders
from config import Config
from app.database import close_db


def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    from app.routes.main import main
    app.register_blueprint(main)

    from app.routes.auth import auth
    app.register_blueprint(auth)

    from app.routes.products import products
    app.register_blueprint(products)

    from app.routes.orders import orders
    app.register_blueprint(orders)

    from app.routes.customer import customer
    app.register_blueprint(customer)

    app.teardown_appcontext(close_db)

    return app

