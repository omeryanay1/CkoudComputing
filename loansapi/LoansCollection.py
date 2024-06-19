import pymongo
from bson import ObjectId

class LoansCollection:
    """
    This class represents a collection of loans. It provides methods
    to insert, delete, find, and retrieve all loans.
    """
    def __init__(self):
        """
        Initializes a new LoansCollection object.
        """
        self.client = pymongo.MongoClient("mongodb://mongo:27017/")
        self.db = self.client["library"]
        self.collection = self.db["loans"]
    
    def insertLoan(self, loan):
        """
        Inserts a new loan into the collection.

        Args:
            loan (dict): A dictionary containing loan information.
                Expected keys: "memberName", "ISBN", "title", "bookID", "loanDate".

        Returns:
            str: The ID of the inserted loan as a string, or None if a duplicate ISBN is found.
        """
        if self.collection.find_one({"ISBN": loan["ISBN"]}):
            return None
        
        result = self.collection.insert_one(loan)
        loan_id = str(result.inserted_id)
        return loan_id
    
    def deleteLoan(self, loanID):
        """
        Deletes a loan from the collection by its ID.

        Args:
            loanID (str): The ID of the loan to delete.

        Returns:
            bool: True if the loan is deleted, False otherwise.
        """
        result = self.collection.delete_one({"_id": ObjectId(loanID)})
        return result.deleted_count > 0
        
    def findLoan(self, loanID):
        """
        Finds a loan by its ID.

        Args:
            loanID (str): The ID of the loan to find.

        Returns:
            tuple: A tuple containing (bool, loan).
                - bool: True if the loan is found, False otherwise.
                - loan (dict): The loan if found, None otherwise.
        """
        loan = self.collection.find_one({"_id": ObjectId(loanID)})
        if loan:
            loan["loanID"] = str(loan["_id"]) 
            del loan["_id"]  
            return True, loan
        else:
            return False, None
    
    def retrieveAllLoans(self):
        """
        Retrieves all loans currently in the collection.

        Returns:
            list: A list of loans.
        """
        loans = list(self.collection.find())
        for loan in loans:
            loan["loanID"] = str(loan["_id"])
            del loan["_id"]
        return loans

    def retrieveLoansByParameter(self, args):
        """
        Retrieves loans based on specified parameters.

        Args:
            args (dict): A dictionary where keys represent search fields and values represent parameters.

        Returns:
            list: A list of loans matching the given parameters.
        """
        query = {key: value for key, value in args.items()}
        loans = list(self.collection.find(query))
        for loan in loans:
            loan["loanID"] = str(loan["_id"])
            del loan["_id"]
        return loans
