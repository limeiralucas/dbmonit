from flask_admin import Admin, expose
from flask_admin.base import AdminIndexView
from flask_admin.contrib import sqla
from flask_simplelogin import login_required
from flask_admin.model import typefmt
from datetime import datetime

from dbmonit.ext.database import db
from dbmonit.models import (
    Operation,
    User,
    Client
)

AdminIndexView._handle_view = login_required(AdminIndexView._handle_view)
sqla.ModelView._handle_view = login_required(sqla.ModelView._handle_view)


class AdminView(sqla.ModelView):
    def __init__(self, *args, **kwargs):
        super(AdminView, self).__init__(*args, **kwargs)

        self.column_formatters = dict(typefmt.BASE_FORMATTERS)
        self.column_formatters.update(
            {type(None): typefmt.null_formatter, datetime: self.date_format}
        )

        self.column_type_formatters = self.column_formatters

    def date_format(self, view, value):
        return value.strftime("%d %b %Y - %I:%M:%p")


class HomeView(AdminIndexView):
    @expose("/")
    def index(self):
        users_count = User.query.count()
        operations_count = Operation.query.count()
        return self.render(
            "admin/home.html", users_count=users_count, operations_count=operations_count,
        )


class UserAdmin(AdminView):
    column_list = ["username"]
    can_edit = False


class OperationView(AdminView):
    page_size = 50

class ClientAdmin(AdminView):
    can_edit = True

def init_app(app):
    admin = Admin(index_view=HomeView())
    admin.name = app.config.TITLE
    admin.template_mode = "bootstrap3"
    admin.base_template = "layout.html"
    admin.init_app(app)
    admin.add_view(OperationView(Operation, db.session))
    admin.add_view(UserAdmin(User, db.session))
    admin.add_views(ClientAdmin(Client, db.session))
