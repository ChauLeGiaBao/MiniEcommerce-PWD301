from flask import Flask
from shop_routes import shop_bp

app = Flask(__name__)

app.secret_key = "mini-ecommerce-secret-key"

app.register_blueprint(shop_bp)

if __name__ == "__main__":
    app.run(debug=True)