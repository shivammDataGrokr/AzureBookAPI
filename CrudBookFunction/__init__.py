import os
import urllib.parse 
from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_marshmallow import Marshmallow
import logging
import pyodbc


import azure.functions as func

# Configure Database URI: 
params = urllib.parse.quote_plus("Driver={ODBC Driver 17 for SQL Server};Server=tcp:datagrokr.database.windows.net,1433;Database=de-intern-apr;Uid=dgadmin;Pwd=dingding@ding1;Encrypt=yes;TrustServerCertificate=no;Connection Timeout=30;")


# initialization
app = Flask(__name__)
app.config['SECRET_KEY'] = 'keythatissecret'
app.config['SQLALCHEMY_DATABASE_URI'] = "mssql+pyodbc:///?odbc_connect=%s" % params
app.config['SQLALCHEMY_COMMIT_ON_TEARDOWN'] = True

# extensions
db = SQLAlchemy(app)

# Initializing marshmallow
marshy = Marshmallow(app)



#Creating Book Class/Model
class Book(db.Model):
    book_id = db.Column(db.Integer, primary_key = True)
    book_name = db.Column(db.String(100))
    genre = db.Column(db.String(100))
    author = db.Column(db.String(100))

    def __init__(self, book_name, genre, author):
        self.book_name = book_name
        self.genre = genre
        self.author = author

#Creating Book Schema
class BookSchema(marshy.Schema):
    class Meta:
        fields = ('book_id', 'book_name', 'genre' , 'author')


# Init Schema
book_schema = BookSchema()
books_schema = BookSchema(many=True)


#Creating new book 
@app.route('/book', methods=['POST'])
def add_book():
    book_name = request.json['book_name']
    genre = request.json['genre']
    author = request.json['author']

    new_book = Book(book_name, genre, author)
    db.session.add(new_book)
    db.session.commit()
    return book_schema.jsonify(new_book)

#Getting one book details
@app.route('/book/<book_id>', methods=['GET'])
def get_book(book_id):
    book = Book.query.get(book_id)
    return book_schema.jsonify(book)

#Getting all books details
@app.route('/book', methods=['GET'])
def get_all_books():
    books = Book.query.all()
    result = books_schema.dump(books)
    return books_schema.jsonify(result)

#Updating one book details
@app.route('/book/<book_id>', methods=['PUT'])
def update_book(book_id):
    book = Book.query.get(book_id)
    book.book_name = request.json['book_name']
    book.genre = request.json['genre']
    book.author = request.json['author']
    db.session.commit()
    return book_schema.jsonify(book)

#Deleting one book details
@app.route('/book/<book_id>', methods=['DELETE'])
def delete_book(book_id):
    book = Book.query.get(book_id)
    db.session.delete(book)
    db.session.commit()
    return book_schema.jsonify(book)




def main(req: func.HttpRequest) -> func.HttpResponse:
    logging.info('Python HTTP trigger function processed a request.')

    name = req.params.get('name')
    if not name:
        try:
            req_body = req.get_json()
        except ValueError:
            pass
        else:
            name = req_body.get('name')

    if name:
        return func.HttpResponse(f"Hello, {name}. This HTTP triggered function executed successfully.")
    else:
        return func.HttpResponse(
             "This HTTP triggered function executed successfully. Pass a name in the query string or in the request body for a personalized response.",
             status_code=200
        )
