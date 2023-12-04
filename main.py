from flask import Flask, request, render_template
from config_handler import Config


app = Flask(__name__)
config = Config()


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/importjson')
def import_json():
    return render_template('index.html')


@app.route('/config')
def show_config():
    return render_template('config.html', config=config)


if __name__ == '__main__':
    app.run()