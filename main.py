from flask import Flask, render_template
from views import *
import os

app = Flask(__name__)
app.register_blueprint(view)


if __name__ == '__main__':
    app.run(debug=True)
