from flask import Flask
from .routes import dng_bp

app = Flask(__name__)
app.register_blueprint(dng_bp)

if __name__ == '__main__':
    # Note: Debug mode should be OFF in production
    # Port and host can be configured as needed
    app.run(debug=True, host='0.0.0.0', port=5000)
