from flask import Flask, jsonify, request
from flask_cors import CORS
from functools import wraps
from marshmallow import Schema, fields, ValidationError, post_load
from typing import List, Dict, Optional, Any, cast
import time

# ----------------- CONFIG -----------------
API_KEY = "podapati@1"

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

# Constants
MAX_BOOKS_PER_PAGE = 20
MIN_BOOKS_PER_PAGE = 1

# ----------------- DATA -----------------
class Book:
    def __init__(self, id: int, title: str, author: str):
        self.id = id
        self.title = title
        self.author = author

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "title": self.title,
            "author": self.author
        }

    @staticmethod
    def from_dict(data: Dict[str, Any]) -> 'Book':
        return Book(
            id=data.get("id", 0),
            title=data["title"],
            author=data["author"]
        )

books: List[Book] = [
    Book(1, "Clean Code", "Robert C. Martin"),
    Book(2, "Deep Learning", "Ian Goodfellow"),
]

# ----------------- SCHEMA -----------------
class BookSchema(Schema):
    id = fields.Int(dump_only=True)     # Auto-generated, not required in input
    title = fields.Str(required=True)   # Must be provided
    author = fields.Str(required=True)  # Must be provided

    @post_load
    def make_book(self, data: Dict[str, Any], **kwargs) -> Dict[str, str]:
        # Ensure we only return title and author
        return {
            "title": str(data["title"]),
            "author": str(data["author"])
        }

book_schema = BookSchema()
books_schema = BookSchema(many=True)

# ----------------- HELPERS -----------------
def require_api_key(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        key = request.headers.get("x-api-key")
        if key and key == API_KEY:
            return f(*args, **kwargs)
        return jsonify({"error": "Unauthorized"}), 401
    return decorated

# ----------------- ROUTES -----------------
@app.route("/")
def home():
    return "<h1>Library Management System API is running!</h1>"

# GET all books (with filtering, sorting, pagination)
@app.route("/books", methods=["GET"])
def get_books():
    page = request.args.get("page", default=1, type=int)
    limit = request.args.get("limit", default=5, type=int)

    # Validate pagination parameters
    if limit < MIN_BOOKS_PER_PAGE or limit > MAX_BOOKS_PER_PAGE:
        return jsonify({"error": f"Limit must be between {MIN_BOOKS_PER_PAGE} and {MAX_BOOKS_PER_PAGE}"}), 400
    if page < 1:
        return jsonify({"error": "Page must be greater than 0"}), 400

    author = request.args.get("author")
    title = request.args.get("title")

    sort_by = request.args.get("sort")
    order = request.args.get("order", "asc")

    # Filtering
    filtered_books = books
    if author:
        filtered_books = [b for b in filtered_books if author.lower() in b.author.lower()]
    if title:
        filtered_books = [b for b in filtered_books if title.lower() in b.title.lower()]

    # Sorting
    if sort_by in ["id", "title", "author"]:
        reverse = (order == "desc")
        filtered_books = sorted(filtered_books, key=lambda x: getattr(x, sort_by), reverse=reverse)

    # Pagination
    start = (page - 1) * limit
    end = start + limit
    paginated_books = filtered_books[start:end]

    return jsonify({
        "page": page,
        "limit": limit,
        "total_books": len(filtered_books),
        "books": [book.to_dict() for book in paginated_books]
    })

# GET single book
@app.route("/books/<int:book_id>", methods=["GET"])
def get_book(book_id):
    book = next((b for b in books if b.id == book_id), None)
    if book:
        return jsonify(book.to_dict())
    return jsonify({"error": "Book not found"}), 404

# SEARCH books
@app.route("/search", methods=["GET"])
def search_books():
    author = request.args.get("author")
    title = request.args.get("title")

    results = books
    if author:
        results = [b for b in results if author.lower() in b.author.lower()]
    if title:
        results = [b for b in results if title.lower() in b.title.lower()]

    return jsonify([book.to_dict() for book in results])

# ADD book
@app.route("/add_book", methods=["POST"])
@require_api_key
def add_book():
    data = request.get_json()
    if not data:
        return jsonify({"error": "No data provided"}), 400

    try:
        validated_data = book_schema.load(data)  # ✅ input validation
        if not isinstance(validated_data, dict):
            return jsonify({"error": "Invalid data format"}), 400

        # Generate new ID using timestamp to avoid collisions
        new_id = int(time.time() * 1000)
        new_book = Book(
            id=new_id,
            title=str(validated_data.get("title", "")),
            author=str(validated_data.get("author", ""))
        )
        books.append(new_book)
        return jsonify(new_book.to_dict()), 201
    except ValidationError as err:
        return jsonify(err.messages), 400
    except (KeyError, TypeError, ValueError) as err:
        return jsonify({"error": f"Invalid data: {str(err)}"}), 400

# UPDATE book
@app.route("/books/<int:book_id>", methods=["PUT"])
@require_api_key
def update_book(book_id):
    data = request.get_json()
    if not data:
        return jsonify({"error": "No data provided"}), 400

    book = next((b for b in books if b.id == book_id), None)
    if not book:
        return jsonify({"error": "Book not found"}), 404

    try:
        validated_data = book_schema.load(data, partial=True)  # ✅ partial update allowed
        if not isinstance(validated_data, dict):
            return jsonify({"error": "Invalid data format"}), 400

        # Update book attributes with type checking
        title = validated_data.get("title")
        if title is not None:
            book.title = str(title)

        author = validated_data.get("author")
        if author is not None:
            book.author = str(author)

        return jsonify(book.to_dict())
    except ValidationError as err:
        return jsonify(err.messages), 400
    except (TypeError, ValueError) as err:
        return jsonify({"error": f"Invalid data: {str(err)}"}), 400

# DELETE book
@app.route("/books/<int:book_id>", methods=["DELETE"])
@require_api_key
def remove_book(book_id):
    book = next((b for b in books if b.id == book_id), None)
    if not book:
        return jsonify({"error": "Book not found"}), 404

    books.remove(book)
    return jsonify({
        "message": "Book deleted successfully",
        "books": [b.to_dict() for b in books]
    })

# ----------------- ERRORS -----------------
@app.errorhandler(400)
def bad_request(error):
    return jsonify({"error": "Bad request", "message": str(error)}), 400

@app.errorhandler(404)
def not_found(error):
    return jsonify({"error": "Resource not found"}), 404

@app.errorhandler(500)
def internal_error(error):
    return jsonify({"error": "Internal server error"}), 500

@app.errorhandler(ValidationError)
def handle_validation_error(error):
    return jsonify({"error": "Validation error", "messages": error.messages}), 400

# ----------------- RUN -----------------
if __name__ == "__main__":
    app.run(debug=True)
