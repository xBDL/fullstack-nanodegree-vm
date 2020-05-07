from flask import Flask, abort, jsonify, redirect, render_template, request, url_for
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
import sys

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgres://postgres:password@localhost:5432/todoapp'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

migrate = Migrate(app, db)

class Todo(db.Model):
  __tablename__ = 'todos'
  id = db.Column(db.Integer, primary_key=True)
  description = db.Column(db.String(), nullable=False)
  completed = db.Column(db.Boolean, nullable=False, default=False)
  list_id = db.Column(db.Integer, db.ForeignKey('todolists.id'), nullable=False)

  def __repr__(self):
    return f'<Todo {self.id} {self.description}>'

class TodoList(db.Model):
  __tablename__ = 'todolists'
  id = db.Column(db.Integer, primary_key=True)
  name = db.Column(db.String(), nullable=False)
  todos = db.relationship('Todo', backref='list', lazy=True, cascade='all,delete-orphan')

  def __repr__(self):
    return f'<TodoList {self.id} {self.name}>'

@app.route('/todos/create', methods=['POST'])
def create_todo():
  error = False
  body = {}
  try:
    description = request.get_json()['description']
    list_id = request.get_json()['list_id']
    todo = Todo(description=description, list_id=list_id)
    db.session.add(todo)
    db.session.commit()
    body['description'] = todo.description
  except:
    error = True
    db.session.rollback()
    print(sys.exc_info())
  finally:
    db.session.close()
  if error:
    abort(400)
  else:
    print(body, flush=True)
    return jsonify(body)

@app.route('/todos/<todo_id>/set-completed', methods=['POST'])
def set_completed_todo(todo_id):
  try:
    completed = request.get_json()['completed']
    todo = Todo.query.get(todo_id)
    todo.completed = completed
    db.session.commit()
  except:
    db.session.rollback()
  finally:
    db.session.close()
  return redirect(url_for('index'))

@app.route('/todos/<todo_id>', methods=['DELETE'])
def delete_todo(todo_id):
  try:
    Todo.query.filter_by(id=todo_id).delete()
    db.session.commit()
  except:
    db.session.rollback()
  finally:
    db.session.close()
  return jsonify({ 'success': True })

@app.route('/lists/<list_id>')
def get_list(list_id):
  if db.session.query(TodoList.id).filter_by(id=list_id).scalar() is None:
    return redirect(url_for('get_list', list_id=1))
  else:
    return render_template('index.html', 
      active_list=TodoList.query.get(list_id),
      lists=TodoList.query.all(), 
      todos=Todo.query.filter_by(list_id=list_id).order_by('id').all())

@app.route('/lists/create', methods=['POST'])
def create_todo_list():
  error = False
  body = {}
  try:
    name = request.get_json()['name']
    todo_list = TodoList(name=name)
    db.session.add(todo_list)
    db.session.commit()
    body['name'] = todo_list.name
  except:
    error = True
    db.session.rollback()
    print(sys.exc_info())
  finally:
    db.session.close()
  if error:
    abort(400)
  else:
    print(body, flush=True)
    return jsonify(body)

@app.route('/lists/<list_id>/set-completed', methods=['POST'])
def set_completed_list(list_id):
  try:
    completed = request.get_json()['completed']
    todo_list = TodoList.query.get(list_id)
    for todo in todo_list.todos:
      todo.completed = completed
    db.session.commit()
  except:
    db.session.rollback()
  finally:
    db.session.close()
  return redirect(url_for('index'))

@app.route('/lists/<list_id>', methods=['DELETE'])
def delete_list(list_id):
  try:
    todo_list = TodoList.query.filter_by(id=list_id).one()
    db.session.delete(todo_list)
    db.session.commit()
  except:
    db.session.rollback()
  finally:
    db.session.close()
  return jsonify({ 'success': True })

@app.route('/')
def index():
  return redirect(url_for('get_list', list_id=1))

if __name__ == '__main__':
  app.run(debug=True)
