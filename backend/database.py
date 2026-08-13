from pymongo import MongoClient

from config import MONGODB_URI, MONGODB_DATABASE


client = MongoClient(MONGODB_URI)

db = client[MONGODB_DATABASE]


users = db["users"]
messages = db["messages"]
interactions = db["interactions"]
feedback = db["feedback"]
escalations = db["escalations"]
documents = db["documents"]
insights = db["insights"]
contributors = db["contributors"]
events = db["events"]