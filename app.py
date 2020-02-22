from flask import Flask
from flask_mail import Mail

app = Flask(__name__)
mail_settings = {
    "MAIL_SERVER": 'smtp.gmail.com',
    "MAIL_PORT": 465,
    "MAIL_USE_TLS": False,
    "MAIL_USE_SSL": True,
    "MAIL_USERNAME": 'ae1276871@gmail.com',
    "MAIL_PASSWORD": 'rdouuhrmnpwmrwhn'
}
app.config.update(mail_settings)
mail = Mail(app)
app.secret_key = 'xxxyyyzzz'
# login_manager = LoginManager(app)
# login_manager.login_view = 'auth.login_get'

from controller.auth import auth
from controller.main import blue
from controller.family import family

app.register_blueprint(blue)
app.register_blueprint(auth)
app.register_blueprint(family)


@app.route('/')
def home_page():
    return 'Home Page!'


if __name__ == '__main__':
    app.run()
