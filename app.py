from flask import *
from main import calculation_with_metadata
import requests

app = Flask(__name__, template_folder="templates")
app.config["DEBUG"] = True

@app.route("/", methods=["GET", "POST"])
def hello_world():
    #errors = ""
    checker_url = "https://www.youtube.com/oembed?url=http://www.youtube.com/watch?v="
    if request.method == "POST":
        link = str(request.form["link"])
        vid_id = link.removeprefix("https://www.youtube.com/watch?v=")
        if requests.get(checker_url + vid_id).status_code == 200:
            try:
                calculation_with_metadata(link)
                return redirect("/success")
            except:
                return redirect("/failed")
        elif requests.get(checker_url + vid_id).status_code != 200:
            return render_template('home_error.html')
            #errors += "<p>{!r} is not a valid link.</p>\n".format(request.form["link"])
    return render_template('home.html')

@app.route("/success", methods=["GET", "POST"])
def success():
    return render_template('success.html')

@app.route("/failed", methods=["GET", "POST"])
def failed():
    return render_template('failed.html')

if __name__ == "__main__":
    app.run(debug=True)
