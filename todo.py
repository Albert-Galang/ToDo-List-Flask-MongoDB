import pymongo
from flask import Flask, render_template, request, redirect
from bson import ObjectId
import bcrypt
from flask_login import LoginManager, logout_user, current_user, login_user, login_required

# Connecting to the MongoDB Database

client = pymongo.MongoClient("mongodb://localhost:27017/")
database = client["todo-database"]
collection = database["todo"]
users = database["users"]

app = Flask(__name__)
login_manager = LoginManager(app)
login_manager.login_view = 'login'

# TODO: Create a Login system using Flask-Login and make tasks by default private, where visibility is a toggleable true/false like completion


class User:
    def __init__(self, username):
        self.username = username

    @staticmethod
    def is_authenticated():
        return True

    @staticmethod
    def is_active():
        return True

    @staticmethod
    def is_anonymous():
        return False

    def get_id(self):
        return self.username


@login_manager.user_loader
def load_user(username):
    u = users.find_one({"name": username})
    if not u:
        return None
    return User(username=u['name'])


@app.route('/logout')
def logout():
    """ Simple logout function that redirects to index

    :return:
    """
    logout_user()
    return redirect('/')


@app.route("/")
def index():
    """ Checks if current user exists and is authenticated, if not redirects to login/registration pages

    :return:
    """
    if current_user.is_authenticated:
        return redirect('/all')
    return render_template('index.html')


@app.route('/login', methods=['POST'])
def login():
    """ Gets login details, hashes the password and compares to stored password. If both are equal then user is logged in, else is directed to try again.

    :return:
    """
    login = users.find_one({'name': request.form['username']})
    if login:
        if bcrypt.hashpw(request.form['pass'].encode('utf-8'), login['password']) == login['password']:
            user_obj = User(username=login['name'])
            login_user(user_obj)
            return redirect("/all")

    return 'Invalid username/password combination, please return to login'


@app.route('/register', methods=['POST', 'GET'])
def register():
    """ Checks if username is already taken, if not then creates a new user document

    :return:
    """
    if request.method == 'POST':
        users = database["users"]
        existing_user = users.find_one({'name': request.form['username']})

        if existing_user is None:
            hashpass = bcrypt.hashpw(request.form['pass'].encode('utf-8'), bcrypt.gensalt())
            users.insert_one({'name': request.form['username'], 'password': hashpass})
            user_obj = User(username=request.form['username'])
            login_user(user_obj)
            return redirect("/all")

        return 'That username already exists, please try again'

    return render_template('register.html')


@app.route("/all")
@login_required
def all_tasks():
    """ Display a list of all_tasks tasks, whether complete or uncompleted

    :return:
    """

    username = current_user.username
    todo_list = collection.find()
    heading = "All Tasks"
    return render_template('tasklist.html', heading=heading, todo_list=todo_list, username=username)


@app.route("/uncompleted")
@login_required
def uncompleted():
    """ Display all_tasks uncompleted tasks, by filtering by status

    :return:
    """
    username = current_user.username
    todo_list = collection.find({"status": False})
    heading = "Uncompleted Tasks"

    return render_template('tasklist.html', heading=heading, todo_list=todo_list, username=username)


@app.route("/completed")
@login_required
def completed():
    """ Display all_tasks completed tasks, by filtering status

    :return:
    """
    username = current_user.username
    todo_list = collection.find({"status": True})
    heading = "Completed Tasks"

    return render_template('tasklist.html', heading=heading, todo_list=todo_list, username=username)


@app.route("/toggle_status")
@login_required
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
@login_required
def create():
    """ Create new entry and insert into MongoDB Database

    :return:
    """
    username = current_user.username
    name = request.values.get("name")
    description = request.values.get("desc")
    status = False
    collection.insert_one({"name": name, "desc": description, "user": username, "status": status})

    return redirect("/")


@app.route("/remove")
@login_required
def remove():
    """ Delete entry from MongoDB Database

    :return:
    """
    id = request.values.get("_id")
    collection.delete_one({"_id": ObjectId(id)})

    return redirect("/")


@app.route("/update")
@login_required
def update():
    """ Display editable task properties on update page

    :return:
    """
    username = current_user.username
    id = request.values.get("_id")
    task = collection.find({"_id": ObjectId(id)})

    return render_template('update.html', tasks=task)


@app.route("/update_task", methods=['POST'])
@login_required
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
@login_required
def search():
    """ Search for a task using both category and search term

    :return:
    """

    search_term = request.values.get("search_term")
    category = request.values.get("category")
    todo_list = collection.find({category: search_term})

    return render_template('search.html', todo_list=todo_list)


if __name__ == "__main__":
    app.secret_key = 'mysecret'
    app.run()
