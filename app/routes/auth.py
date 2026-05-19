
from flask import Blueprint
from app.routes.login import LoginRoutes
from app.routes.register import RegisterRoutes

class AuthRoutes:
    def __init__(self):
        self.login_routes = LoginRoutes()
        self.register_routes = RegisterRoutes()

    def register(self):
        # Return combined blueprints
        blueprints = []
        blueprints.append(self.login_routes.register())
        blueprints.append(self.register_routes.register())
        return blueprints