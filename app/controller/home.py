from flask import render_template

class MainController:

    def home(self):
        return render_template("landing_page.html")