from flask import Flask, request, jsonify
from sqlalchemy import create_engine, Column, Integer, String, Float
from sqlalchemy.orm import declarative_base, sessionmaker

# Create the base class for declarative models
Base = declarative_base()

# Define the Book model
class Book(Base):
    __tablename__ = 'books'

    id = Column(Integer, primary_key=True)
    title = Column(String, nullable=False)
    author = Column(String, nullable=False)
    price = Column(Float, nullable=False)
    link = Column(String, nullable=False)

# Setup the database and session
engine = create_engine('sqlite:///bookstore.db')
Base.metadata.create_all(engine)
Session = sessionmaker(bind=engine)

app = Flask(__name__)

# Create a new book
@app.route('/books', methods=['POST'])
def create_book():
    session = Session()
    data = request.json
    new_book = Book(
        title=data['title'],
        author=data['author'],
        price=data['price'],
        link=data['link']
    )
    session.add(new_book)
    session.commit()
    session.close()
    return jsonify({'message': 'Book created successfully!'}), 201

# Read all books
@app.route('/books', methods=['GET'])
def get_books():
    session = Session()
    books = session.query(Book).all()
    session.close()
    return jsonify([{'id': book.id, 'title': book.title, 'author': book.author, 'price': book.price, 'link': book.link} for book in books]), 200

# Read a specific book by query parameter ID
@app.route('/book', methods=['GET'])
def get_book():
    book_id = request.args.get('id')
    session = Session()
    book = session.query(Book).filter(Book.id == book_id).first()
    session.close()
    if book:
        return jsonify({'id': book.id, 'title': book.title, 'author': book.author, 'price': book.price, 'link': book.link}), 200
    return jsonify({'message': 'Book not found!'}), 404

# Update a specific book by query parameter ID
@app.route('/book', methods=['PUT'])
def update_book():
    book_id = request.args.get('id')
    session = Session()
    data = request.json
    book = session.query(Book).filter(Book.id == book_id).first()
    if book:
        book.title = data.get('title', book.title)
        book.author = data.get('author', book.author)
        book.price = data.get('price', book.price)
        book.link = data.get('link', book.link)
        session.commit()
        session.close()
        return jsonify({'message': 'Book updated successfully!'}), 200
    session.close()
    return jsonify({'message': 'Book not found!'}), 404

# Delete a specific book by query parameter ID
@app.route('/book', methods=['DELETE'])
def delete_book():
    book_id = request.args.get('id')
    session = Session()
    book = session.query(Book).filter(Book.id == book_id).first()
    if book:
        session.delete(book)
        session.commit()
        session.close()
        return jsonify({'message': 'Book deleted successfully!'}), 200
    session.close()
    return jsonify({'message': 'Book not found!'}), 404

if __name__ == "__main__":
    app.run(debug=True)
