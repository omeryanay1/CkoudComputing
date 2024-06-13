from flask import Flask, request
from flask_restful import Resource, Api
import requests
import LoansCollection

loanCol = LoansCollection.LoansCollection()

BOOKS_SERVICE_URL = 'http://bookapi:8000/books'

class Loans(Resource):
    """
    Loans class that handles /loans
    """
    def post(self):
        try:
            args = request.get_json()
            memberName = args["memberName"]
            ISBN = args["ISBN"]
            loanDate = args["loanDate"]
            if not memberName or not ISBN or not loanDate:
                return {"error": "Unprocessable Content"}, 422
        except KeyError:
            return {"error": "Unprocessable Content"}, 422
        except:
            return {"error": "Unsupported media type"}, 415

        try:
            response = requests.get(f'{BOOKS_SERVICE_URL}?ISBN={ISBN}')
            if response.status_code != 200:
                return {"error": "Unprocessable Content"}, 422
            book_data = response.json()[0]
        except requests.exceptions.RequestException:
            return {"error": "Internal Server Error: Unable to connect to Books Service"}, 500

        existing_loans = loanCol.retrieveLoansByParameter({"ISBN": ISBN})
        if existing_loans:
            return {"error": "Book already on loan"}, 422

        member_loans = loanCol.retrieveLoansByParameter({"memberName": memberName})
        if len(member_loans) >= 2:
            return {"error": "Member has too many loans"}, 422

        loan = {
            "memberName": memberName,
            "ISBN": ISBN,
            "title": book_data["title"],
            "bookID": book_data["id"],
            "loanDate": loanDate
        }

        loanID = loanCol.insertLoan(loan)
        if not loanID:
            return {"error": "Unable to create loan"}, 422

        return {"loanID": loanID}, 201
    
    def get(self):
        args = request.args
        if args == {}:
            return loanCol.retrieveAllLoans(), 200
        else:
            return loanCol.retrieveLoansByParameter(args), 200

class LoanId(Resource):
    """
    LoanId class that handles /loan/{id}
    """
    def get(self, loan_id):
        success, loan = loanCol.findLoan(loan_id)
        if success:
            return loan, 200
        else:
            return {"error": "Not Found"}, 404
    
    def delete(self, loan_id):
        success = loanCol.deleteLoan(int(loan_id))
        if success:
            return {"loanID": loan_id}, 200
        else:
            return {"error": "Not Found"}, 404

app = Flask(__name__)
api = Api(app)

if __name__ == "__main__":
    api.add_resource(Loans, '/loans')
    api.add_resource(LoanId, '/loan/<string:loan_id>')
    app.run(host='0.0.0.0', port=8001, debug=True)
