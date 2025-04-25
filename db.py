
    # db.py
from flask_pymongo import PyMongo
from flask import Flask
from flask_session import Session

app = Flask(__name__)

app.config["MONGO_URI"] = "mongodb://localhost:27017/medicine_inv"
app.secret_key = 'your_secret_key'

app.config['SESSION_TYPE'] = 'filesystem'

mongo = PyMongo(app)
Session(app)

logins_collection = mongo.db.logins
customers_collection = mongo.db.customers
shopkeepers_collection = mongo.db.shopkeepers
stores_collection = mongo.db.stores
medicines_collection = mongo.db.medicines
inventory_collection = mongo.db.inventory
orders_collection = mongo.db.orders


medicines = [
    {"name": "Paracetamol", "brand": "Crocin", "price": 20, "symptoms_treated": ["fever", "headache"]},
    {"name": "Ibuprofen", "brand": "Brufen", "price": 30, "symptoms_treated": ["fever", "pain"]},
    {"name": "Aspirin", "brand": "Disprin", "price": 15, "symptoms_treated": ["headache", "pain"]},
    {"name": "Amoxicillin", "brand": "Amoxil", "price": 50, "symptoms_treated": ["infection", "fever"]},
    {"name": "Cough Syrup", "brand": "Benadryl", "price": 90, "symptoms_treated": ["cough", "cold"]},
    {"name": "Cetirizine", "brand": "Cetzine", "price": 10, "symptoms_treated": ["allergy", "cold"]},
    {"name": "Loratadine", "brand": "Claritin", "price": 25, "symptoms_treated": ["allergy", "sneezing"]},
    {"name": "Metformin", "brand": "Glycomet", "price": 30, "symptoms_treated": ["diabetes"]},
    {"name": "Atorvastatin", "brand": "Lipvas", "price": 40, "symptoms_treated": ["high cholesterol"]},
    {"name": "Pantoprazole", "brand": "Pantocid", "price": 35, "symptoms_treated": ["acid reflux", "indigestion"]},
    {"name": "Losartan", "brand": "Repace", "price": 40, "symptoms_treated": ["high blood pressure"]},
    {"name": "Ciprofloxacin", "brand": "Ciplox", "price": 50, "symptoms_treated": ["infection"]},
    {"name": "Salbutamol", "brand": "Asthalin", "price": 25, "symptoms_treated": ["asthma", "breathing"]},
    {"name": "Hydrochlorothiazide", "brand": "Aquazide", "price": 30, "symptoms_treated": ["high blood pressure"]},
    {"name": "Paroxetine", "brand": "Pexep", "price": 75, "symptoms_treated": ["depression", "anxiety"]},
    {"name": "Furosemide", "brand": "Lasix", "price": 18, "symptoms_treated": ["edema", "heart failure"]},
    {"name": "Clopidogrel", "brand": "Clopivas", "price": 55, "symptoms_treated": ["blood clot prevention"]},
    {"name": "Diazepam", "brand": "Calmposed", "price": 20, "symptoms_treated": ["anxiety", "muscle spasms"]},
    {"name": "Levothyroxine", "brand": "Thyronorm", "price": 40, "symptoms_treated": ["hypothyroidism"]},
    {"name": "Folic Acid", "brand": "Folvite", "price": 15, "symptoms_treated": ["deficiency", "pregnancy"]},
    {"name": "Lisinopril", "brand": "Zestril", "price": 50, "symptoms_treated": ["high blood pressure", "heart failure"]},
    {"name": "Ranitidine", "brand": "Zinetac", "price": 18, "symptoms_treated": ["stomach acid", "ulcers"]},
    {"name": "Vitamin D3", "brand": "D3 Must", "price": 30, "symptoms_treated": ["bone health"]},
    {"name": "Zinc", "brand": "Zincovit", "price": 20, "symptoms_treated": ["immune support"]},
    {"name": "Calcium", "brand": "Shelcal", "price": 45, "symptoms_treated": ["bone health", "osteoporosis"]},
    {"name": "Magnesium", "brand": "Magnesium Sulphate", "price": 25, "symptoms_treated": ["muscle cramps", "sleep aid"]},
    {"name": "Omega-3", "brand": "Seven Seas", "price": 85, "symptoms_treated": ["heart health", "cholesterol"]},
    {"name": "Multivitamins", "brand": "Revital", "price": 80, "symptoms_treated": ["general health"]},
    {"name": "Codeine", "brand": "Corex", "price": 95, "symptoms_treated": ["pain", "cough"]},
    {"name": "Tramadol", "brand": "Tramazac", "price": 60, "symptoms_treated": ["pain relief"]},
    {"name": "Paracetamol + Caffeine", "brand": "Pacimol Active", "price": 22, "symptoms_treated": ["headache"]}
]

medicines_collection.insert_many(medicines)