from flask import Flask
from flask_login import LoginManager

app = Flask(__name__)
app.secret_key = 'xxxyyyzzz'
# login_manager = LoginManager(app)
# login_manager.login_view = 'auth.login_get'

from controller.auth import auth
from controller.main import blue

app.register_blueprint(blue)
app.register_blueprint(auth)


@app.route('/')
def home_page():
    return 'Home Page!'


if __name__ == '__main__':
    app.run()
