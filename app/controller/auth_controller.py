from app.controller.auth_controller import AuthController
from app.controller.login import LoginController
from app.controller.register import RegisterController

class AuthController:
    def __init__(self):
        self.login_controller = LoginController()
        self.register_controller = RegisterController()

    def login(self):
        return self.login_controller.login()

    def register(self):
        return self.register_controller.register()