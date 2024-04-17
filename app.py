#!/usr/bin/env python3

import os
import sys
import subprocess
import datetime
#vi .env

from flask import Flask, render_template, request, redirect, url_for, make_response

# import logging
import sentry_sdk

# from markupsafe import escape
import pymongo
from pymongo.errors import ConnectionFailure
from bson.objectid import ObjectId
from dotenv import load_dotenv

# load credentials and configuration options from .env file
# if you do not yet have a file named .env, make one based on the template in env.example
load_dotenv(override=True)  # take environment variables from .env.

# instantiate the app using sentry for debugging
app = Flask(__name__)

# # turn on debugging if in development mode
# app.debug = True if os.getenv("FLASK_ENV", "development") == "development" else False

# try to connect to the database, and quit if it doesn't work
try:
    cxn = pymongo.MongoClient(os.getenv("MONGO_URI"))
    db = cxn[os.getenv("MONGO_DBNAME")]  # store a reference to the selected database

    # verify the connection works by pinging the database
    cxn.admin.command("ping")  # The ping command is cheap and does not require auth.
    print(" * Connected to MongoDB!")  # if we get here, the connection worked!
except ConnectionFailure as e:
    # catch any database errors
    # the ping command failed, so the connection is not available.
    print(" * MongoDB connection error:", e)  # debug
    sys.exit(1)  # this is a catastrophic error, so no reason to continue to live


# set up the routes
@app.route("/")
def home():
    """
    Route for the home page.
    Simply returns to the browser the content of the index.html file located in the templates folder.
    """
    return render_template("index.html")

@app.route("/newaccount")
def newaccount():
    """
    Route for GET requests to the new_account creation page.
    Displays a form users can fill out to create a new account.
    """
    return render_template("newaccount.html")

@app.route("/addmoney")
def addmoney():
    """
    Route for GET request to the acknowledgement page.
    Display some information about the acknowledged transaction
    """
    return render_template("addmoney.html")

@app.route("/create")
def create():
    """
    Route for GET requests to the create page.
    Displays a form users can fill out to create a new document.
    """
    return render_template("create.html")  # render the create template

@app.route("/updatewindow")
def updatewindow():
    """
    Route for GET request to the acknowledgement page.
    Display some information about the acknowledged transaction
    """
    return render_template("updatewindow.html")

@app.route("/read")
def read():
    """
    Route for GET requests to the read page.
    Displays some information for the user with links to other pages.
    """
    docs = db.exampleapp.find({}).sort(
        "created_at", -1
    )  # sort in descending order of created_at timestamp
    return render_template("read.html", docs=docs)  # render the read template

@app.route("/acknowledgement")
def acknowledgement():
    """
    Route for GET request to the acknowledgement page.
    Display some information about the acknowledged transaction
    """
    return render_template("acknowledgement.html")

@app.route("/successfullyupdated")
def successfullyupdated():
    """
    Route for GET request to the acknowledgement page.
    Display some information about the acknowledged account creation
    """
    return render_template("successfullyupdated.html")

@app.route("/successfullydeleted")
def successfullydeleted():
    """
    Route for GET request to the acknowledgement page.
    Display some information about the acknowledged account creation
    """
    return render_template("successfullydeleted.html")

@app.route("/accountack")
def accountack():
    """
    Route for GET request to the acknowledgement page.
    Display some information about the acknowledged account creation
    """
    return render_template("accountack.html")

@app.route("/updatepage")
def updatepage():
    """
    Route for GET requests to the read page.
    Displays some information for the user with links to other pages.
    """
    docs = db.exampleapp.find({}).sort(
        "created_at", -1
    )  # sort in descending order of created_at timestamp
    return render_template("updatepage.html", docs=docs)  # render the read template

@app.route("/preexisting")
def preexisting():
    """
    Route for GET requests to the "account number already exists"page.
    """
    return render_template("preexisting.html")

@app.route("/nonexistingaccount")
def nonexistingaccount():
    """
    Route for GET request to the error page if there was no object with the entered DBN number.
    Displays a message and an option to go back and try again
    """
    return render_template("nonexistingaccount.html")

@app.route("/invalidreceiver")
def invalidreceiver():
    """
    Route for GET request to the acknowledgement page.
    Display some information about the acknowledged account creation
    """
    return render_template("invalidreceiver.html")

@app.route("/nosufficientfunds")
def nosufficientfunds():
    """
    Route for GET requests to the create page.
    Displays a form users can fill out to create a new document.
    """
    return render_template("nosufficientfunds.html")  # render the no_sufficient_funds template

@app.route("/edit/<mongoid>")
def edit(mongoid):
    """
    Route for GET requests to the edit page.
    Displays a form users can fill out to edit an existing record.

    Parameters:
    mongoid (str): The MongoDB ObjectId of the record to be edited.
    """
    doc = db.exampleapp.find_one({"_id": ObjectId(mongoid)})
    return render_template(
        "edit.html", mongoid=mongoid, doc=doc
    )  # render the edit template

@app.route("/initiate/<mongoid>")
def initiate(mongoid):
    """
    Route for GET request to the acknowledgement page.
    Display some information about the acknowledged account creation
    """
    docs = db.useraccount.find_one({"_id": ObjectId(mongoid)})
    return render_template("initiate.html", docs=docs)

@app.route("/successful/<mongoid>")
def successful(mongoid):
    """
    Route for GET request to the acknowledgement page.
    Display some information about the acknowledged account creation
    """
    docs = db.useraccount.find_one({"_id": ObjectId(mongoid)})
    return render_template("successful.html", docs=docs)

@app.route("/newaccount", methods=["POST"])
def newaccount_post():
    id = request.form["fnumber"]
    if db.useraccount.find({"dbnnumber": {"$eq": id}}).sort("created_at", -1).count() == 0:
        name = request.form["fname"]
        age = request.form["fage"]
        address = request.form["faddress"]
        email = request.form["femail"]
        dbnnumber = request.form["fnumber"]
        amount = request.form["famount"]
        bname = request.form["fbank"]
        accnumber= request.form["faccnumber"]
        message = request.form["fmessage"]

        # create a new document with the data the user entered
        if bname != "" and accnumber != "" and amount == "":
            doc1= {"dbnnumber":dbnnumber, "amount": amount, "message": message}
            db.trasactiondetail.insert_one(doc1)  #insert a new document
               
        doc = { "name": name, "age": age, "address": address, "email": email, "dbnnumber": dbnnumber,"amount": amount, "created_at": datetime.datetime.utcnow()}
        db.useraccount.insert_one(doc)  # insert a new document
        return redirect(url_for("accountack"))
    else:
       return redirect(url_for('preexisting'))
   
@app.route("/initiate/<mongoid>", methods=["POST"])
def initiate_post(mongoid):
    dbnnumber=db.useraccount.find_one({"_id":{"$eq": ObjectId(mongoid)}})["dbnnumber"]
    amount= request.form["famount"]
    message= request.form["fmessage"]
    
    doc= {"dbnnumber":dbnnumber, "amount": amount, "message": message}
    db.trasactiondetail.insert_one(doc)  #insert a new document
    
    testsender = db.useraccount.find_one({"dbnnumber":{"$eq": dbnnumber}},{"amount":1})["amount"]
    b= int(testsender) + int(amount)
    db.useraccount.update({"dbnnumber":{"$eq": dbnnumber}}, {"$set":{"amount": str(b)}})
    return redirect(url_for('successful', mongoid=mongoid))
    
@app.route("/create", methods=["POST"])
def create_post():
    """
    Route for POST requests to the create page.
    Accepts the form submission data for a new document and saves the document to the database.
    """
    id = request.form["fnumber"]
    if db.useraccount.find({"dbnnumber": {"$eq": id}}).count() == 1:
        a = request.form["famount"]
        if db.useraccount.find({"dbnnumber":{"$eq": id},"amount": {"$gte": a}}).count() == 1:
            aa = request.form["raccnumber"]
            if db.useraccount.find({"dbnnumber": {"$eq": aa}}).count() == 1:
                testsender = db.useraccount.find_one({"dbnnumber":{"$eq": id}},{"amount":1})["amount"]
                testreceiver= db.useraccount.find_one({"dbnnumber":{"$eq": aa}},{"amount":1})["amount"]
                dbnnumber = request.form["fnumber"]
                name = request.form["fname"]
                rname = request.form["rname"]
                raccnumber = request.form["raccnumber"]
                amount = request.form["famount"]
                message = request.form["fmessage"]

                # create a new document with the data the user entered
                doc = {"dbnnumber": dbnnumber, "name": name, "rname": rname, "raccnumber": raccnumber,"amount": amount, "message": message, "created_at": datetime.datetime.utcnow()}
                db.exampleapp.insert_one(doc)  # insert a new document
                b = int(testsender) - int(a)
                c = int(testreceiver) + int(a)
                db.useraccount.update({"dbnnumber":{"$eq": id}}, {"$set":{"amount": str(b)}})
                db.useraccount.update({"dbnnumber":{"$eq": aa}}, {"$set":{"amount": str(c)}})
    
                return redirect(
                url_for("acknowledgement")  # here i have to redirect it to a new page that acknowledges the transaction!
                )  # tell the browser to make a request for the /read route
            else:
                return redirect(url_for("invalidreceiver"))
        else:
            return redirect(url_for("nosufficientfunds"))
    else:
        return redirect(url_for("nonexistingaccount"))

@app.route("/updatewindow", methods=["POST"])
def update_record():
    id = request.form["dbnnumber"]
    docu = db.exampleapp.find({"dbnnumber": {"$eq": id}}).sort("created_at", -1)
    if db.exampleapp.find({"dbnnumber": {"$eq": id}}).sort("created_at", -1).count() == 0:
        return redirect(url_for('nonexistingaccount'))
    else:
        return render_template('updatepage.html', docs=docu)

@app.route("/addmoney", methods=["POST"])
def addmoney_post():
    id = request.form["fnumber"]
    if db.useraccount.find({"dbnnumber": {"$eq": id}}).count() == 1:
        ss = db.useraccount.find_one({"dbnnumber": {"$eq": id}})["_id"]
        return redirect(url_for('initiate', mongoid= ss))
    else:
        return redirect(url_for('nonexistingaccount'))
    
@app.route("/edit/<mongoid>", methods=["POST"])
def edit_post(mongoid):
    """
    Route for POST requests to the edit page.
    Accepts the form submission data for the specified document and updates the document in the database.

    Parameters:
    mongoid (str): The MongoDB ObjectId of the record to be edited.
    """
    recname = request.form["rname"]
    message = request.form["fmessage"]
    

    doc = {
        # "_id": ObjectId(mongoid),
        "rname": recname,
        "message": message,
        "created_at": datetime.datetime.utcnow(),
    }

    db.exampleapp.update_one(
        {"_id": ObjectId(mongoid)}, {"$set": doc}  # match criteria
    )

    return redirect(
        url_for("successfullyupdated")
    )  # tell the browser to make a request for the /read route


@app.route("/delete/<mongoid>")
def delete(mongoid):
    """
    Route for GET requests to the delete page.
    Deletes the specified record from the database, and then redirects the browser to the read page.

    Parameters:
    mongoid (str): The MongoDB ObjectId of the record to be deleted.
    """
    db.exampleapp.delete_one({"_id": ObjectId(mongoid)})
    return redirect(
        url_for("successfullydeleted")
    )  # tell the web browser to make a request for the /read route.


@app.route("/webhook", methods=["POST"])
def webhook():
    """
    GitHub can be configured such that each time a push is made to a repository, GitHub will make a request to a particular web URL... this is called a webhook.
    This function is set up such that if the /webhook route is requested, Python will execute a git pull command from the command line to update this app's codebase.
    You will need to configure your own repository to have a webhook that requests this route in GitHub's settings.
    Note that this webhook does do any verification that the request is coming from GitHub... this should be added in a production environment.
    """
    # run a git pull command
    process = subprocess.Popen(["git", "pull"], stdout=subprocess.PIPE)
    pull_output = process.communicate()[0]
    # pull_output = str(pull_output).strip() # remove whitespace
    process = subprocess.Popen(["chmod", "a+x", "flask.cgi"], stdout=subprocess.PIPE)
    chmod_output = process.communicate()[0]
    # send a success response
    response = make_response(f"output: {pull_output}", 200)
    response.mimetype = "text/plain"
    return response


@app.errorhandler(Exception)
def handle_error(e):
    """
    Output any errors - good for debugging.
    """
    return render_template("error.html", error=e)  # render the edit template


# run the app
if __name__ == "__main__":
    # logging.basicConfig(filename="./flask_error.log", level=logging.DEBUG)
    app.run(load_dotenv=True)
