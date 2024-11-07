import os
import asyncio
from flask import Flask, request, jsonify
from sqlalchemy import create_engine, Column, Integer, String, Float
from sqlalchemy.orm import declarative_base, sessionmaker
from werkzeug.utils import secure_filename
import websockets
import json

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

# Create Flask app
app = Flask(__name__)

# File upload configuration
UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'json'}
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Ensure upload directory exists
os.makedirs(UPLOAD_FOLDER, exist_ok=True)


def allowed_file(filename):
    """
    Check if the uploaded file has an allowed extension
    """
    return '.' in filename and \
        filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


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


# Read all books with pagination
@app.route('/books', methods=['GET'])
def get_books():
    session = Session()

    # Get 'offset' and 'limit' query parameters, with defaults if not provided
    offset = request.args.get('offset', default=0, type=int)  # start from the 0th record by default
    limit = request.args.get('limit', default=10, type=int)  # show 10 records by default

    # Query with offset and limit for pagination
    books = session.query(Book).offset(offset).limit(limit).all()
    session.close()

    # Format and return the JSON response
    return jsonify([
        {
            'id': book.id,
            'title': book.title,
            'author': book.author,
            'price': book.price,
            'link': book.link
        } for book in books
    ]), 200


# Read a specific book by query parameter ID
@app.route('/book', methods=['GET'])
def get_book():
    book_id = request.args.get('id')
    session = Session()
    book = session.query(Book).filter(Book.id == book_id).first()
    session.close()
    if book:
        return jsonify(
            {'id': book.id, 'title': book.title, 'author': book.author, 'price': book.price, 'link': book.link}), 200
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


# WebSocket Setup
connected_users = {}


async def chat_handler(websocket, path):
    username = None
    try:
        while True:
            message = await websocket.recv()
            if message.startswith("join_room:"):
                username = message[len("join_room:"):].strip()
                connected_users[username] = websocket
                print(f"{username} has joined the chat.")
                for user, conn in connected_users.items():
                    if user != username:
                        await conn.send(f"{username} has joined the chat.")
                await websocket.send(f"Welcome {username}!")
                break

        async for message in websocket:
            if message == "leave_room":
                connected_users.pop(username, None)
                for user, conn in connected_users.items():
                    await conn.send(f"{username} has left the chat.")
                break
            elif message.startswith("send_msg:"):
                chat_message = message[len("send_msg:"):].strip()
                for user, conn in connected_users.items():
                    if user != username:
                        await conn.send(f"{username}: {chat_message}")
                await websocket.send(f"{username}: {chat_message}")
    except websockets.ConnectionClosed:
        if username:
            connected_users.pop(username, None)


async def start_websocket_server():
    server = await websockets.serve(chat_handler, "localhost", 6789)
    await server.wait_closed()


# New route for file upload
@app.route('/upload', methods=['POST'])
def upload_file():
    # Check if the post request has the file part
    if 'file' not in request.files:
        return jsonify({'message': 'No file part'}), 400

    file = request.files['file']

    # If user does not select file, browser also
    # submit an empty part without filename
    if file.filename == '':
        return jsonify({'message': 'No selected file'}), 400

    # Check if file is allowed
    if file and allowed_file(file.filename):
        # Secure the filename to prevent security risks
        filename = secure_filename(file.filename)

        # Full path to save the file
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)

        # Save the file
        file.save(filepath)

        # Try to parse the JSON file
        try:
            with open(filepath, 'r') as f:
                json_data = json.load(f)

            # Optional: Automatically create books from the uploaded JSON
            session = Session()
            try:
                # Supports both single book and list of books
                if isinstance(json_data, dict):
                    json_data = [json_data]

                for book_data in json_data:
                    new_book = Book(
                        title=book_data['title'],
                        author=book_data['author'],
                        price=book_data['price'],
                        link=book_data['link']
                    )
                    session.add(new_book)

                session.commit()
            except Exception as e:
                session.rollback()
                return jsonify({'message': f'Error creating books: {str(e)}'}), 400
            finally:
                session.close()

            return jsonify({
                'message': 'File uploaded and processed successfully',
                'filename': filename,
                'books_added': len(json_data)
            }), 200

        except json.JSONDecodeError:
            return jsonify({'message': 'Invalid JSON file'}), 400

    return jsonify({'message': 'File type not allowed'}), 400

# Run Flask app with asyncio-compatible server (like Hypercorn or aiohttp)
def run_flask():
    app.run(debug=True, port=5000, use_reloader=False)

async def main():
    await asyncio.gather(
        start_websocket_server(),
        asyncio.to_thread(run_flask)  # Running Flask app in a separate thread
    )

if __name__ == "__main__":
    asyncio.run(main())