from flask import Flask
app = Flask(__name__)


from yourapplication.database import db_session

@app.teardown_request
def shutdown_session(exception=None):
    db_session.remove()

@app.route("/")
def hello():
    return "Planet!"

if __name__ == "__main__":
    app.run()