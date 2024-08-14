import json
from typing import Dict
from pudb import set_trace
from googleapi.gmail_SDK_suit import SDK_Suit
from paramiko import SFTPAttributes
from chost.hostconnect import hostconnect
from flask import (Flask, render_template, jsonify, request)

app = Flask(__name__)
app.config['DEBUG'] = True

session:Dict = None
"""
    create the host.json in the directory chost, and
    write in your login credentials using the full
    title such as: username, port, password, host
"""
with open("chost/host.json", 'r') as file:
    session = json.load(file)


@app.route("/")
def quickstart():
    data: list[SFTPAttributes] = None
    with hostconnect(session=session) as host:
        data = host.listdir_attr(path=".")

    return render_template("app.html", data=data)

@app.route("/edit", methods=["POST"])
def edit():
    #set_trace()
    responseJson = request.get_json()
    oldpath = responseJson.get("oldpath")
    newpath = responseJson.get("newpath")

    oldpath = f"./{oldpath}"
    newpath = f"./{newpath}"

    emailDraft = f"""
    <html>
        <head></head>
        <body>
            <p><b style="border: 2px solid #ddd; padding: 5px; color: purple">{oldpath}</b> was changed to <b style="border: 2px solid #ddd; padding: 5px; color: green">{newpath}</b> </p>
        </body>
    </html>
    """

    # me:str="seymour2@pdx.edu"
    # gmail = SDK_Suit()
    # draft = gmail.create_draft(me, me, "CS510-Group2", emailDraft)
    # gmail.send_draft(me, draft["id"])

    with hostconnect(session=session) as host:
        host.rename(oldpath=oldpath, newpath=newpath)

    return jsonify({"status": 202})

if __name__ == "__main__":
    app.run()
