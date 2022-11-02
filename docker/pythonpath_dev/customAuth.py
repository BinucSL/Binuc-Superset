import logging
import os

import jwt
from flask import request, flash, redirect
from flask_admin import expose
from flask_appbuilder.security.views import AuthDBView
from flask_login import login_user

from superset.security.manager import SupersetSecurityManager
logger = logging.getLogger()

class CustomAuthDBView(AuthDBView):
    login_template = 'appbuilder/general/security/login_db.html'

    @expose('/login/', methods=['GET', 'POST'])
    def login(self):
        token = request.args.get('token')
        if not token:
            token = request.cookies.get('access_token')
        if token is not None:
            try:
                jwt_payload = jwt.decode(token, os.environ.get('JWT_SECRET'),
                                         algorithms=['HS256'])
            except:
                flash('Token has expired or is not signed')
                return super(CustomAuthDBView, self).login()
            user_name = jwt_payload.get("user_name")
            user = self.appbuilder.sm.find_user(username=user_name)
            if user:
                login_user(user, remember=False)
                redirect_url = request.args.get('redirect')
                if not redirect_url:
                    redirect_url = self.appbuilder.get_url_for_index
                return redirect(redirect_url)
        else:
            flash('Unable to auto login', 'warning')
            return super(CustomAuthDBView, self).login()


class CustomSecurityManager(SupersetSecurityManager):
    authdbview = CustomAuthDBView
