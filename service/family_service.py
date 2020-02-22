from service.service import find_user
from rep.mongo import Family, User, Spend
from flask_mail import Message
from app import mail
from mongoengine import Q
import random
import string


def random_string_digits(string_length=6):
    """Generate a random string of letters and digits """
    letters_and_digits = string.ascii_letters + string.digits
    return ''.join(random.choice(letters_and_digits) for i in range(string_length))


def create_new_family(username):
    user = find_user(username)
    try:
        token = random_string_digits(8)
        family = Family(token=token, name=str(username)).save()
        user.role_in_family = 4
        user.family = family
        user.save()
        return family
    except Exception as e:
        print(e)
        return False


def invited_to_family(username, token):
    families = Family.objects(token=token)
    if len(families) is not 0:
        family = families[0]
    else:
        return False
    flag = False
    for pend in family.pending:
        if pend == username:
            flag = True
            break
    if flag:
        family.pending.remove(username)
        family.save()
        user = find_user(username)
        user.role_in_family = 1
        user.family = family
        user.save()
        return True
    else:
        return False


def send_invitation(username, invited_user):
    user = find_user(username)
    family = user.family
    family.pending.append(invited_user)
    family_token = user.family.token
    link = 'http://127.0.0.1:5000/family/invited/' + str(family_token)
    msg = Message(subject='Invitation to family', sender='ae1276871@gmail.com',
                  recipients=[find_user(invited_user).email],
                  body='Hi, You have been invited to ' + str(family.name) + "'s family by " + str(
                      username) + '. you can accept the invitation via clicking on the link below : ' + str(link))
    mail.send(msg)
    family.save()
    return True


def family_spends(username, page, per_page):
    if page is None:
        page = 1
    if per_page is None:
        per_page = 5
    page = int(page)
    items_per_page = int(per_page)
    offset = (page - 1) * items_per_page

    user = find_user(username)
    if user.role_in_family == 0 or user.role_in_family == 1:
        return False
    family = user.family
    users = []
    for user in User.objects(family=family):
        users.append(user)
    spends = []
    for spend in Spend.objects().skip(offset).limit(items_per_page):
        if spend.owner in users:
            spends.append(spend)

    return spends
