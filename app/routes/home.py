from flask import Blueprint
from app.controller.home import MainController

class MainRoutes:

    def __init__(self):
        self.bp = Blueprint("main", __name__)
        self.controller = MainController()

    def register(self):

        self.bp.route("/")(
            self.controller.home
        )

        return self.bp