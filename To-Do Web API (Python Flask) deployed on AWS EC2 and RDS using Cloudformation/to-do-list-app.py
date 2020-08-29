# Import Flask modules
from flask import Flask, jsonify, abort, request
from flask_sqlalchemy import SQLAlchemy
# Create an object named app
app = Flask(__name__)
# Configure mysql database
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://admin:password@database-3.cgy9ixalilkj.us-east-1.rds.amazonaws.com/task'
db = SQLAlchemy(app)


# Write a function named `init_taskdb` which initializes the tasks db
# Create task table within sqlite db and populate with sample data
# Execute the code below only once.


def init_task_db():
    drop_table = 'DROP TABLE IF EXISTS tasks;'
    tasks_table = """
    CREATE TABLE tasks(
    task_id INTEGER PRIMARY KEY,
    title VARCHAR NOT NULL,
    description VARCHAR,
    is_done BOOLEAN NOT NULL DEFAULT 0 CHECK(is_done IN(0,1)));
    """
    data = """
    INSERT INTO tasks (title, description, is_done)
    VALUES
        ("Grocery Shopping", "Buy weekly meal prep supplies", 1 ),
        ("Haircut", "Haircut Appointment at 5pm", 0),
        ("Project 103", "Finish Project 103", 0);
    """
    db.session.execute(drop_table)
    db.session.execute(tasks_table)
    db.session.execute(data)
    db.session.commit()


# Write a function named `get_all_tasks` which gets all tasks from the tasks table in the db,
# and return result as list of dictionary
# `[{'task_id': 1, 'title':'XXXX', 'description': 'XXXXXX', 'is_done': True or False} ]`.


def get_all_tasks():
    query = """
    SELECT * FROM tasks;
    """

    result = db.session.execute(query)
    tasks = [{'task_id': row[0], 'title':row[1], 'description':row[2],
              'is_done': bool(row[3])} for row in result]
    return tasks


# Write a function named `find_task` which finds tasks using task_id from the tasks table in the db,
# and return result as list of dictionary
# `[{'task_id': 1, 'title':'XXXX', 'description': 'XXXXXX', 'is_sold': 'Yes' or 'No'} ]`.

def find_tasks(id):
    query = f"""
    SELECT * FROM tasks WHERE task_id={id};
    """

    row = db.session.execute(query).first()
    task = None
    if row is not None:
        task = {'task_id': row[0], 'title': row[1], 'description': row[2], 'is_done': bool(row[3])}
    return task

# Write a function named `insert_task` which inserts tasks into the tasks table in the db,
# and return the newly added task as dictionary
# [{'task_id': 1, 'title':'XXXX', 'description': 'XXXXXX', 'is_sold': 'Yes' or 'No'} ]`.


def insert_task(title, description):
    insert = f"""
    INSERT INTO tasks (title, description)
    VALUES ('{title}', '{description}');
    """
    result = db.session.execute(insert)
    db.session.commit()

    query = f"""
    SELECT * FROM tasks WHERE task_id={result.lastrowid};
    """
    row = db.session.execute(query).first()

    return {'task_id': row[0], 'title': row[1], 'description': row[2], 'is_done': bool(row[3])}

# Write a function named `change_task` which updates tasks into the task table in the db,
# and return updated added task as dictionary
# {'task_id': 1, 'title':'XXXX', 'description': 'XXXXXX', 'is_sold': 'Yes' or 'No'} ]`.


def change_task(task):
    update = f"""
    UPDATE tasks
    SET title='{task['title']}', author = '{task['description']}', is_done = {task['is_done']}
    WHERE task_id= {task['task_id']};
    """

    result = db.session.execute(update)
    db.session.commit()

    query = f"""
    SELECT * FROM tasks WHERE task_id={task['task_id']};
    """
    row = db.session.execute(query).first()
    return {'task_id': row[0], 'title': row[1], 'description': row[2], 'is_done': bool(row[3])}

# Write a function named `remove_task` which removes task from the tasks table in the db,
# and returns True if successfully completed or False.


def remove_task(task):
    delete = f"""
    DELETE FROM tasks
    WHERE task_id= {task['task_id']};
    """

    result = db.session.execute(delete)
    db.session.commit()

    query = f"""
    SELECT * FROM tasks WHERE task_id={task['task_id']};
    """
    row = db.session.execute(query).first()

    return True if row is None else False

# Write a function named `home` which returns 'Welcome to the Ajay's To Do List API Service',
# and assign to the static route of ('/')


@app.route('/')
def home():
    return "Welcome to the Ajay's To Do List API Service"

# Write a function named `get_tasks` which returns all tasks in JSON format for `GET`,
# and assign to the static route of ('/tasks')

@app.route('/tasks', methods=['GET'])
def get_tasks():
    return jsonify({'tasks': get_all_tasks()})


# Write a function named `get_task` which returns the task with given task_id in JSON format for `GET`,
# and assign to the static route of ('/task/<int:task_id>')
@app.route('/tasks/<int:task_id>', methods=['GET'])
def get_task(task_id):
    task = find_tasks(task_id)
    if task == None:
        abort(404)
    return jsonify({'task found': task})

# Write a function named `add_task` which adds new task using `POST` methods,
# and assign to the static route of ('/tasks')


@app.route('/tasks', methods=['POST'])
def add_task():
    if not request.json or not 'title' in request.json:
        abort(400)
    return jsonify({'newly added task': insert_task(request.json['title'], request.json.get('description', ''))}), 201

# Write a function named `update_task` which updates an existing task using `PUT` method,
# and assign to the static route of ('/tasks/<int:task_id>')


@app.route('/tasks/<int:task_id>', methods=['PUT'])
def update_task(task_id):
    task = find_tasks(task_id)
    if task == None:
        abort(404)
    if not request.json:
        abort(400)
    task['title'] = request.json.get('title', task['title'])
    task['description'] = request.json.get('description', task['description'])
    task['is_done'] = int(request.json.get('is_done', int(task['is_sold'])))
    return jsonify({'updated task': change_task(task)})


# Write a function named `delete_task` which updates an existing task using `DELETE` method,
# and assign to the static route of ('/tasks/<int:task_id>')
@app.route('/tasks/<int:task_id>', methods=['DELETE'])
def delete_task(task_id):
    task = find_tasks(task_id)
    if task == None:
        abort(404)
    return jsonify({'result': remove_task(task)})


# Add a statement to run the Flask application which can be reached from any host on port 5000.
if __name__ == "__main__":
    init_task_db()
    #app.run(debug=True)
    app.run(host='0.0.0.0', port=80)


# db_endpoint = open("/home/ec2-user/dbserver.endpoint", 'r', encoding='UTF-8')
# db_endpoint.readline().strip()
# db_endpoint.close()


# 10: 13
# echo "{MyRDSInstance}" > /home/ec2-user/dbserver.endpoint

