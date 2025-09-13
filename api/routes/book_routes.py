"""Route handlers for book-related endpoints."""
from flask import Blueprint, request, jsonify
from typing import List
import time

from api.models.book import Book
from api.schemas.book_schema import book_schema
from api.middleware.auth import require_api_key
from api.config.config import Config

# Create blueprint
book_bp = Blueprint('books', __name__)

# In-memory storage (replace with database in production)
books: List[Book] = [
    Book(1, "Clean Code", "Robert C. Martin"),
    Book(2, "Deep Learning", "Ian Goodfellow"),
]

@book_bp.route("/books", methods=["GET"])
def get_books():
    """Get list of books with filtering, sorting, and pagination."""
    page = request.args.get("page", default=1, type=int)
    limit = request.args.get("limit", default=5, type=int)

    # Validate pagination parameters
    if limit < Config.MIN_BOOKS_PER_PAGE or limit > Config.MAX_BOOKS_PER_PAGE:
        return jsonify({
            "error": f"Limit must be between {Config.MIN_BOOKS_PER_PAGE} and {Config.MAX_BOOKS_PER_PAGE}"
        }), 400
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

@book_bp.route("/books/<int:book_id>", methods=["GET"])
def get_book(book_id):
    """Get a single book by ID."""
    book = next((b for b in books if b.id == book_id), None)
    if book:
        return jsonify(book.to_dict())
    return jsonify({"error": "Book not found"}), 404

@book_bp.route("/search", methods=["GET"])
def search_books():
    """Search books by title or author."""
    author = request.args.get("author")
    title = request.args.get("title")

    results = books
    if author:
        results = [b for b in results if author.lower() in b.author.lower()]
    if title:
        results = [b for b in results if title.lower() in b.title.lower()]

    return jsonify([book.to_dict() for book in results])

@book_bp.route("/books", methods=["POST"])
@require_api_key
def add_book():
    """Add a new book."""
    data = request.get_json()
    if not data:
        return jsonify({"error": "No data provided"}), 400

    try:
        validated_data = book_schema.load(data)
        if not isinstance(validated_data, dict):
            return jsonify({"error": "Invalid data format"}), 400

        new_id = int(time.time() * 1000)
        new_book = Book(
            id=new_id,
            title=str(validated_data.get("title", "")),
            author=str(validated_data.get("author", ""))
        )
        books.append(new_book)
        return jsonify(new_book.to_dict()), 201
        
    except Exception as e:
        return jsonify({"error": str(e)}), 400

@book_bp.route("/books/<int:book_id>", methods=["PUT"])
@require_api_key
def update_book(book_id):
    """Update a book."""
    data = request.get_json()
    if not data:
        return jsonify({"error": "No data provided"}), 400

    book = next((b for b in books if b.id == book_id), None)
    if not book:
        return jsonify({"error": "Book not found"}), 404

    try:
        validated_data = book_schema.load(data, partial=True)
        if not isinstance(validated_data, dict):
            return jsonify({"error": "Invalid data format"}), 400

        title = validated_data.get("title")
        if title is not None:
            book.title = str(title)

        author = validated_data.get("author")
        if author is not None:
            book.author = str(author)

        return jsonify(book.to_dict())
        
    except Exception as e:
        return jsonify({"error": str(e)}), 400

@book_bp.route("/books/<int:book_id>", methods=["DELETE"])
@require_api_key
def remove_book(book_id):
    """Delete a book."""
    book = next((b for b in books if b.id == book_id), None)
    if not book:
        return jsonify({"error": "Book not found"}), 404

    books.remove(book)
    return jsonify({
        "message": "Book deleted successfully",
        "books": [b.to_dict() for b in books]
    })
