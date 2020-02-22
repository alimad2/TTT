from service.service import find_user
from rep.mongo import Family

import random
import string


def random_string_digits(string_length=6):
    """Generate a random string of letters and digits """
    letters_and_digits = string.ascii_letters + string.digits
    return ''.join(random.choice(letters_and_digits) for i in range(string_length))


def create_new_family(username):
    user = find_user(username)
    members = [user]
    try:
        token = random_string_digits(8)
        family = Family(token=token, members=members).save()
        user.role_in_family = 4
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
    user = find_user(username)
    user.role_in_family = 1
    user.save()
    family.members.append(user)
    family.save()
    return True
