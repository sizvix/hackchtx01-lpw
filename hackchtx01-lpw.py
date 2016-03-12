from flask import Flask

app = Flask(__name__)


@app.route('/')
def racine():
    return 'I\'m running'


if __name__ == '__main__':
    app.run()
