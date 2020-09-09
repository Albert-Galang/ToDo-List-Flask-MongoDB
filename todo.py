import pymongo
from flask import Flask, render_template, request, redirect
from bson import ObjectId

# Connecting to the MongoDB Database
client = pymongo.MongoClient("mongodb://localhost:27017/")
database = client["todo-database"]
collection = database["todo"]

app = Flask(__name__)


@app.route("/")
@app.route("/all")
def all_tasks():
    """ Display a list of all tasks, whether complete or uncompleted

    :return:
    """

    todo_list = collection.find()
    heading = "All Tasks"
    return render_template('index.html', heading=heading, todo_list=todo_list)


@app.route("/uncompleted")
def uncompleted():
    """ Display all uncompleted tasks, by filtering by status

    :return:
    """
    todo_list = collection.find({"status": False})
    heading = "Uncompleted Tasks"

    return render_template('index.html', heading=heading, todo_list=todo_list)


@app.route("/completed")
def completed():
    """ Display all completed tasks, by filtering status

    :return:
    """
    todo_list = collection.find({"status": True})
    heading = "Completed Tasks"

    return render_template('index.html', heading=heading, todo_list=todo_list)


@app.route("/toggle_status")
def toggle_status():
    """ Toggle completion status

    :return:
    """
    id = request.values.get("_id")
    task = collection.find({"_id": ObjectId(id)})
    if task[0]["status"] is False:
        collection.update_one({"_id": ObjectId(id)}, {"$set": {"status": True}})
    else:
        collection.update_one({"_id": ObjectId(id)}, {"$set": {"status": False}})

    return redirect("/")


@app.route("/create", methods=['POST'])
def create():
    """ Create new entry and insert into MongoDB Database

    :return:
    """
    name = request.values.get("name")
    description = request.values.get("desc")
    user = request.values.get("user")
    status = False
    collection.insert_one({"name": name, "desc": description, "user": user, "status": status})

    return redirect("/")


@app.route("/remove")
def remove():
    """ Delete entry from MongoDB Database

    :return:
    """
    id = request.values.get("_id")
    collection.delete_one({"_id": ObjectId(id)})

    return redirect("/")


@app.route("/update")
def update():
    """ Display editable task properties on update page

    :return:
    """
    id = request.values.get("_id")
    task = collection.find({"_id": ObjectId(id)})

    return render_template('update.html', tasks=task)


@app.route("/update_task", methods=['POST'])
def update_task():
    """ Edit task properties

    :return:
    """
    name = request.values.get("name")
    description = request.values.get("desc")
    id = request.values.get("_id")
    collection.update_one({"_id": ObjectId(id)}, {'$set': {"name": name, "desc": description}})

    return redirect("/")


@app.route("/search", methods=['GET'])
def search():
    """ Search for a task using both category and search term

    :return:
    """

    search_term = request.values.get("search_term")
    category = request.values.get("category")
    todo_list = collection.find({category: search_term})

    return render_template('search.html', todo_list=todo_list)


if __name__ == "__main__":
    app.run()
