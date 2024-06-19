import pymongo
from bson.objectid import ObjectId

class RatingsCollection:
    """
    This class represents a collection of ratings. It provides methods
    to insert, delete, find, update, retrieve all, retrieve by parameter,
    and retrieve the top-rated ratings.
    """

    def __init__(self):
        """
        Initializes a new RatingsCollection object.
        """
        self.client = pymongo.MongoClient("mongodb://mongo:27017/")
        self.db = self.client["library"]
        self.collection = self.db["ratings"]
    
    def insertRating(self, rating):
        """
        Inserts a new rating into the collection.

        Args:
            rating (dict): A dictionary containing the rating information.
                Expected keys: "id", "title", "values" (list of values), and "average".

        Returns:
            str: The ID of the inserted rating as a string, or None if it already exists.
        """
        if self.collection.find_one({"title": rating["title"]}):
            print("RatingsCollection: rating already inserted")
            return None
        
        result = self.collection.insert_one(rating)
        rating_id = str(result.inserted_id)
        print(f'RatingsCollection: inserted rating: {rating["title"]} with ID: {rating_id}')
        return rating_id
    
    def deleteRating(self, id):
        """
        Deletes a rating from the collection by its ID.

        Args:
            id (str): The ID of the rating to delete.

        Returns:
            bool: True if the rating was deleted, False otherwise.
        """
        result = self.collection.delete_one({"_id": ObjectId(id)})
        if result.deleted_count > 0:
            print(f'RatingsCollection: deleted rating with ID: {id}')
            return True
        else:
            print("RatingsCollection: rating not in collection")
            return False
        
    def findRating(self, id):
        """
        Finds a rating by its ID.

        Args:
            id (str): The ID of the rating to find.

        Returns:
            tuple: A tuple containing (bool, rating).
                - bool: True if the rating was found, False otherwise.
                - rating (dict): The rating itself if found, None otherwise.
        """
        rating = self.collection.find_one({"_id": ObjectId(id)})
        if rating:
            rating["id"] = str(rating["_id"])
            del rating["_id"]
            print(f'RatingsCollection: found rating: {rating["title"]} with ID: {id}')
            return True, rating
        else:
            print("RatingsCollection: rating not in collection")
            return False, None
        
    def updateRating(self, id, value):
        """
        Updates a rating's value (adds a new value).

        Args:
            id (str): The ID of the rating to update.
            value (int): The new value to add to the rating's values list.

        Returns:
            tuple: A tuple containing (bool, float).
                - bool: True if the rating was updated, False otherwise.
                - float: The new average rating after update, None if update failed.
        """
        rating = self.collection.find_one({"_id": ObjectId(id)})
        if not rating:
            print("RatingsCollection: rating not in collection")
            return False, None
        
        values = rating["values"]
        values.append(value)
        average = round(sum(values) / len(values), 2)
        update_result = self.collection.update_one(
            {"_id": ObjectId(id)},
            {"$set": {"values": values, "average": average}}
        )
        
        if update_result.modified_count > 0:
            print(f'RatingsCollection: updated rating: {rating["title"]} with ID: {id}')
            return True, average
        else:
            print("RatingsCollection: failed to update rating")
            return False, None
    
    def retrieveAllRatings(self):
        """
        Retrieves all ratings in the collection.

        Returns:
            list: A list of all the ratings.
        """
        ratings = list(self.collection.find())
        for rating in ratings:
            rating["id"] = str(rating["_id"])
            del rating["_id"]
        return ratings
        
    def retrieveTop(self):
        """
        Retrieves the top three rated ratings from the collection.

        Returns:
            list: A list of ratings with the top 3 averages in descending order.
        """
        pipeLine = [
            {"$match": {"$expr": {"$gte": [{"$size": "$values"}, 3]}}},  
            {"$sort": {"average": pymongo.DESCENDING}}, 
            {"$limit": 3},  
            {"$group": { 
                "_id": None,
                "thirdHighestAvg": {"$min": "$average"}
            }},
            {"$addFields": {  
                "minAvg": "$thirdHighestAvg"
            }},
            {"$lookup": {  
                "from": "ratings",  
                "let": {"minAvg": "$minAvg"},
                "pipeline": [
                    {"$match": {
                        "$expr": {
                            "$and": [
                                {"$gte": ["$average", "$$minAvg"]},
                                {"$gte": [{"$size": "$values"}, 3]}
                            ]
                        }
                    }}
                ],
                "as": "eligibleRatings"
            }},
            {"$unwind": "$eligibleRatings"},
            {"$replaceRoot": {"newRoot": "$eligibleRatings"}}
        ]
                    
        top_ratings = list(self.collection.aggregate(pipeLine))

        for rating in top_ratings:
            rating["id"] = str(rating["_id"])
            del rating["_id"]
        return top_ratings
