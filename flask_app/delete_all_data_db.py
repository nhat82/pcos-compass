from pymongo import MongoClient
MONGO_URI = 'mongodb+srv://nhattmng_db_user:GnrkpBCzhbNtv49L@pcoscluster.fgqx8ux.mongodb.net/?retryWrites=true&w=majority&appName=PCOSCluster'
client = MongoClient(MONGO_URI) 

db_name = "test"
db = client[db_name]

user_input_collection_name = input("collection name: ")
collection = db[user_input_collection_name]
collection.delete_many({})
print(f"Deleted all documents from collection: {user_input_collection_name}")
