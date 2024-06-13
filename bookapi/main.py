from flask import Flask, request
from flask_restful import Resource, Api
import BooksCollection
import RatingsCollection
import requests
from bson.objectid import ObjectId

supported_genre_list = ["Fiction", "Children", "Biography", "Science", "Science Fiction", "Fantasy", "Other"]
book_fields = ["title", "ISBN", "genre", "authors", "publisher", "publishedDate", "id"]
valid_ratings = [1,2,3,4,5]

bookCol = BooksCollection.BooksCollection()
ratingsCol = RatingsCollection.RatingsCollection()

class Books(Resource):
    """
    Books class that handles /books
    """
    def post(self):
        try:
            args = request.get_json()
            book = {"title" : args["title"], "ISBN" : args["ISBN"], "genre" : args["genre"]}
            if book["genre"] not in supported_genre_list:
                return {"error" : "Unprocessable Content"}, 422
            if book["ISBN"] in bookCol.retrieveISBNList() or len(book["ISBN"]) != 13 or not book["ISBN"].isdigit():
                return {"error" : "Unprocessable Content"}, 422
        except KeyError:
            return {"error" : "Unprocessable Content"}, 422
        except:
            return {"error" : "Unsupported media type"}, 415

        try:
            google_books_url = f'https://www.googleapis.com/books/v1/volumes?q=isbn:{book["ISBN"]}' 
            response = requests.get(google_books_url)
        except requests.exceptions.RequestException:
            return {"error": "Internal Server Error: Unable to connect to Google Books"}, 500

        google_books_data = response.json()['items'][0]['volumeInfo']

        book["authors"] = 'and '.join(google_books_data.get("authors"))
        book["publisher"] = google_books_data.get("publisher")
        book["publishedDate"] = google_books_data.get("publishedDate")

        if book["authors"] == "": book["authors"] = "missing"
        if book["publisher"] == "": book["publisher"] = "missing"
        if book["publishedDate"] == "": book["publishedDate"] = "missing"

        id = bookCol.insertBook(book)

        rating = {
            "values": [],
            "average": 0,
            "title": book["title"],
            "_id": ObjectId(id)
        }

        ratingsCol.insertRating(rating)

        return id, 201
    
    def get(self):
        args = request.args
        if args == {}:
            return bookCol.retrieveAllBooks(), 200
        else:
            fields = list(args.keys())
            if [field for field in fields if field not in book_fields] != []:
                return {"error" : "Unprocessable Content"}, 422
            if "genre" in fields:
                if args["genre"] not in supported_genre_list:
                    return {"error" : "Unprocessable Content"}, 422
            if "ISBN" in fields:
                if len(args["ISBN"]) != 13 or not args["ISBN"].isdigit():
                    return {"error" : "Unprocessable Content"}, 422
            return bookCol.retrieveBooksByParameter(args), 200

class BookId(Resource):
    """
    BookId class that handles /books/{id}
    """

    def delete(self, book_id):
        success = bookCol.deleteBook(book_id)
        if success:
            if ratingsCol.deleteRating(book_id):
                return book_id, 200
            else:
                return {"error": "Rating deletion failed"}, 500
        else:
            return 0, 404
    
    def get(self,book_id):
        success, book = bookCol.findBook(book_id)
        if success:
            return book, 200
        else:
            return 0, 404
    
    def put(self, book_id):
        try:
            book = request.get_json()
            keys = list(book.keys())
            missing_fields = [field for field in book_fields if field not in keys]
            if missing_fields != []:
                return {"error" : "Unprocessable Content"}, 422
            if book["genre"] not in supported_genre_list or len(book["ISBN"]) != 13 or not book["ISBN"].isdigit():
                return {"error" : "Unprocessable Content"}, 422
        except KeyError:
            return {"error" : "Unprocessable Content"}, 422
        except:
            return {"error" : "Unsupported media type"}, 415
        success = bookCol.updateBook(book_id, book)
        if success:
            return book_id, 200
        else:
            return 0, 404

class Ratings(Resource):
    """
    Ratings class that handles /ratings
    """
    def get(self):
        args = request.args
        print(args)
        if args == {}:
            return ratingsCol.retrieveAllRatings(), 200
        elif "id" in args.keys():
            return ratingsCol.retrieveRatingsByParameter("id", args["id"]), 200
        else:
            return {"error" : "Unprocessable Content"}, 422

class RatingId(Resource):
    """
    RatingsId class that handles /ratings/{id}
    """
    def get(self, rating_id):
        success, rating = ratingsCol.findRating((rating_id))
        if success:
            return rating, 200
        else:
            return 0, 404
        
class Value(Resource):
    """
    Value class that handles /ratings/{id}/value
    """
    def post(self, rating_id):
        try:
            args = request.get_json()
            if len(args.keys()) != 1:
                return {"error" : "Unprocessable Content"}, 422
            if "value" not in args.keys():
                return {"error" : "Unprocessable Content"}, 422
            if args["value"] not in valid_ratings:
                return {"error" : "Unprocessable Content"}, 422
        except:
            return {"error" : "Unsupported media type"}, 415
        
        success, average = ratingsCol.updateRating(rating_id, args["value"])
        
        if success:
            return average, 200
        else:
            return 0, 404

class Top(Resource):
    """
    Top class that handles /top
    """
    def get(self):
        return ratingsCol.retrieveTop(), 200


app = Flask(__name__)
api = Api(app)

if __name__ == "__main__":
    api.add_resource(Books, '/books')
    api.add_resource(BookId, '/books/<string:book_id>')
    api.add_resource(Ratings, '/ratings')
    api.add_resource(RatingId, '/ratings/<string:rating_id>')
    api.add_resource(Value, '/ratings/<string:rating_id>/values')
    api.add_resource(Top, '/top')
    app.run(host='0.0.0.0', port=8000, debug=True)