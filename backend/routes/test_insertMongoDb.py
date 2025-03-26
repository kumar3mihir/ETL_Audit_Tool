import certifi
from pymongo import MongoClient

MONGO_URI = "mongodb+srv://kumarmihir626:SwoNLc8muQslemIX@cluster0.hyejt.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0"
client = MongoClient(MONGO_URI, tlsCAFile=certifi.where())
db = client["etl_metadata"]

print("Connected to MongoDB Atlas successfully!")

# Sample Data
users = [
    {"user_id": 1, "name": "John Doe", "email": "john@example.com", "age": 29, "created_at": "2024-03-26T12:00:00Z"},
    {"user_id": 2, "name": "Jane Smith", "email": "jane@example.com", "age": 35, "created_at": "2024-03-25T10:15:00Z"}
]

orders = [
    {"order_id": "ORD123", "user_id": 1, "product_name": "Laptop", "quantity": 2, "price": 1200.50, "order_date": "2024-03-25T15:30:00Z"},
    {"order_id": "ORD124", "user_id": 2, "product_name": "Smartphone", "quantity": 1, "price": 800.75, "order_date": "2024-03-26T09:45:00Z"}
]

transactions = [
    {"transaction_id": "TXN987", "user_id": 1, "order_id": "ORD123", "amount": 2401.00, "payment_method": "Credit Card", "status": "Completed"},
    {"transaction_id": "TXN988", "user_id": 2, "order_id": "ORD124", "amount": 800.75, "payment_method": "PayPal", "status": "Pending"}
]

# Insert into collections
db.users.insert_many(users)
db.orders.insert_many(orders)
db.transactions.insert_many(transactions)

print("Dummy data inserted successfully!")
