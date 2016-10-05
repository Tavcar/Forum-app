from google.appengine.api import users
from admins import ADMIN
from functools import wraps


def login_required(f):
    def login(self, *args, **kwargs):
        user = users.get_current_user()
        if user:
            return f(self, *args, **kwargs)
        else:
            return self.redirect_to('home')
    return login


def admin_required(f):
    def admins(self, *args, **kwargs):
        user = users.get_current_user()
        if user.nickname() in ADMIN:
            user.admin = True
            return f(self, *args, **kwargs)
        else:
            user.admin = False
            return self.redirect_to('home')
    return admins


