from flask import Flask
from app.util import PREFIX
app = Flask(__name__, static_url_path=PREFIX)
app.jinja_options = dict(
    app.jinja_options,
    extensions=['jinja2.ext.do'],
    trim_blocks=True,
    lstrip_blocks=True,
)
