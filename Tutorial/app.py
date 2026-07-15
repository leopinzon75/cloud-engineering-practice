from flask import Flask, render_template
from datetime import datetime
import requests

app = Flask(__name__)

@app.route("/")
def index():
    return render_template("index.html", c=c)

@app.template_filter("date_only")
def date_only_filter(s):
    date_object = datetime.strptime(s, "%Y-%m-%dT%H:%M:%S.%fZ")
    return date_object.date()

def a():
    url = "https://api.spacexdata.com/v4/launches"
    response = requests.get(url)
    if response.status_code == 200:
        return response.json()
    else:
        return []


def b(c):
    successful = list(filter(lambda x: x["success"] and not x["upcoming"], c))
    failed = list(filter(lambda x: not x["success"] and not x["upcoming"], c))
    upcoming = list(filter(lambda x: x["upcoming"], c))

    return {
        "successful": successful,
        "failed": failed,
        "upcoming": upcoming
    }

c = b(a())

if __name__ == "__main__":
    app.run(debug=True)