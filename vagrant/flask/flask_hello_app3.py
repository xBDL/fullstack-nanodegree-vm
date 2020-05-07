from flask import Flask
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgres://postgres:password@localhost:5432/postgres'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

class Person(db.Model):
    __tablename__ = 'persons'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(), nullable=False)

    def __repr__(self):
        return f'<Person ID: {self.id}, name: {self.name}>'

db.create_all()

@app.route('/')
def index():
    person = Person.query.first()
    return f'Hello {person.name}'

#Implement a query to filter all users by name 'Bob'.
def all_bobs():
    return Person.query.filter_by(name='Bob').all()

#Implement a LIKE query to filter the users for records with a name that includes the letter "b".
def name_has_b():
    return Person.query.filter(Person.name.like('%b%')).all()

#Return only the first 5 records of the query above.
def five_names_have_b():
    return Person.query.filter(Person.name.like('%b%')).limit(5).all()

#Re-implement the LIKE query using case-insensitive search.
def name_has_b_case_insensitive():
    return Person.query.filter(Person.name.ilike('%b%')).all()

#Return the number of records of users with name 'Bob'.
def number_of_bobs():
    return Person.query.filter_by(name='Bob').count()

if __name__ == '__main__':
    app.run(debug=True)
