import pymongo
from bson.objectid import ObjectId

class BooksCollection:
    """
    This class represents a collection of books. It provides methods
    to insert, delete, find, update, retrieve all books, retrieve books
    based on parameters, and retrieve a list of all ISBNs in the collection.
    """
    def __init__(self):
        """
        Initializes a new BooksCollection object.
        """
        self.client = pymongo.MongoClient("mongodb://mongo:27017/")
        self.db = self.client["library"]
        self.collection = self.db["books"]
    
    def insertBook(self, book):
        """
        Inserts a new book into the collection.

        Args:
            book (dict): A dictionary containing book information.
                Expected keys: "ISBN", "title", "authors", "genre", "publisher", "publishedDate".

        Returns:
            str: The ID of the inserted book as a string, or None if a duplicate ISBN is found.
        """
        if self.collection.find_one({"ISBN": book["ISBN"]}):
            print("BookCollection: book already inserted")
            return None
        
        result = self.collection.insert_one(book)
        book_id = str(result.inserted_id)
        print(f'BooksCollection: inserted book: {book["title"]} with ID: {book_id}')
        return book_id
    
    def deleteBook(self, id):
        """
        Deletes a book from the collection by its ID.

        Args:
            id (str): The ID of the book to delete.

        Returns:
            bool: True if the book is deleted, False otherwise.
        """
        result = self.collection.delete_one({"_id": ObjectId(id)})
        if result.deleted_count > 0:
            print(f'BooksCollection: deleted book with ID: {id}')
            return True
        else:
            print("BooksCollection: book not in collection")
            return False
        
    def findBook(self, id):
        """
        Finds a book by its ID.

        Args:
            id (str): The ID of the book to find.

        Returns:
            tuple: A tuple containing (bool, book).
                - bool: True if the book is found, False otherwise.
                - book (dict): The book if found, None otherwise.
        """
        book = self.collection.find_one({"_id": ObjectId(id)})
        if book:
            book["id"] = str(book["_id"])
            del book["_id"]
            print(f'BooksCollection: found book: {book["title"]} with ID: {id}')
            return True, book
        else:
            print("BooksCollection: book not in collection")
            return False, None
        
    def updateBook(self, id, book):
        """
        Updates a book's information.

        Args:
            id (str): The ID of the book to update.
            book (dict): A dictionary containing the updated book information.

        Returns:
            bool: True if the book is updated, False otherwise.
        """
        result = self.collection.update_one({"_id": ObjectId(id)}, {"$set": book})
        if result.modified_count > 0:
            print(f'BooksCollection: updated book with ID: {id}')
            return True
        else:
            print("BooksCollection: book not in collection")
            return False
    
    def retrieveAllBooks(self):
        """
        Retrieves all books currently in the collection.

        Returns:
            list: A list of books.
        """
        books = list(self.collection.find())
        for book in books:
            book["id"] = str(book["_id"])
            del book["_id"]
        return books
    
    def retrieveBooksByParameter(self, args):
        """
        Retrieves books based on specified parameters.

        Args:
            args (dict): A dictionary where keys represent search fields and values represent a parameter.

        Returns:
            list: A list of books matching the given parameters.
        """
        query = {key: value for key, value in args.items()}
        books = list(self.collection.find(query))
        for book in books:
            book["id"] = str(book["_id"])
            del book["_id"]
        return books
    
    def retrieveISBNList(self):
        """
        Retrieves all the books ISBNs.

        Returns:
            list: A list of all the books ISBNs.
        """
        books = self.collection.find({}, {"ISBN": 1})
        return [book["ISBN"] for book in books]
