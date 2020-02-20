from werkzeug.security import check_password_hash

from rep.mongo import User


def user_already_exists(username, email):
    for user in User.objects():
        if user.email == email or user.username == username:
            return True
    return False


def find_user(username):
    for user in User.objects():
        if user.username == username:
            return user
    return None


def new_user(username, email, name, password):
    user = User(username=username, email=email, name=name, password=password).save()
    auth_token = user.encode_token(user.username)
    # print(auth_token)
    response_object = {
        'status': 'success',
        'message': 'successfully registered',
        'auth_token': auth_token.decode()
    }
    return response_object


def log_user_in(username, password):
    if user_already_exists(username, 'junk'):
        user = find_user(username)
        if check_password_hash(user.password, password):
            # login_user(user, remember=False)
            auth_token = user.encode_token(user.username)
            response = {
                'status': 'success',
                'message': 'successfully logged in',
                'auth_token': auth_token.decode()
            }
            return response
    return False
