from flask import Flask, request, jsonify, render_template, session
from werkzeug.security import generate_password_hash, check_password_hash
from db import app, logins_collection , customers_collection ,shopkeepers_collection , stores_collection, medicines_collection, inventory_collection, orders_collection
from flask import Flask, request, jsonify, render_template, session, redirect, url_for
from bson import ObjectId
from datetime import datetime
import random
import re
import json
from bson import json_util


# Secret key for session management
app.secret_key = 'your_secret_key_here'  

@app.route("/login", methods=['GET'])
def login_page():
    return render_template("login.html")

@app.route("/login", methods=['POST'])
def logins():
    if request.content_type != 'application/json':
        return jsonify({'success': False, 'message': 'Content-Type must be application/json'}), 400

    data = request.get_json()
    action = data.get('action')

    if action == 'signup':
        # Handle signup logic
        username = data.get('username')
        email = data.get('email')
        phone = data.get('phone')
        password = data.get('password')
        user_type = data.get('user_type')
        age = data.get('age')
        gender = data.get('gender')

        existing_user = logins_collection.find_one({'email': email})
        if existing_user:
            return jsonify({'success': False, 'message': 'User already exists'})

        hashed_password = generate_password_hash(password)

        user_data = logins_collection.insert_one({
            'username': username,
            'email': email,
            'phone': phone,
            'password': hashed_password,
            'user_type': user_type,
            'age': age,
            'gender': gender
        })
        result = logins_collection.insert_one({
        'username': username,
        'email': email,
        'phone': phone,
        'password': hashed_password,
        'user_type': user_type,
        'age': age,
        'gender': gender
        })
        
        login_id = result.inserted_id
        # Insert into customer or shopkeeper collection based on user_type
        if user_type == 'customer':
            customers_collection.insert_one({
                'login_id': user_data.inserted_id,
                'name': username,
                'email': email,
                'phone': phone,
                'age': age,
                'gender': gender,
                'address': '',  # Initially empty address or other info
                'order_history': []  # Empty order history at signup
            })
        elif user_type == 'shopkeeper':
            shopkeepers_collection.insert_one({
                'login_id': user_data.inserted_id,
                'name': username,
                'age': age,
                'gender': gender,
                'email': email,
                'shop_name': '',  # Placeholder, can be updated later
                'shop_address': '',  # Placeholder, can be updated later
                'contact_number': phone,  # Phone number
                'shop_inventory': [],  # Empty inventory at signup
            })

        session['user_email'] = email
        session['user_type'] = user_type

        return jsonify({'success': True, 'message': 'Signup successful! Please sign in.'})

    elif action == 'signin':
        # Handle signin logic
        email = data.get('email')
        password = data.get('password')

        user = logins_collection.find_one({'email': email})

        if not user:
            return jsonify({'success': False, 'message': 'User not found'}), 404

        if not check_password_hash(user['password'], password):
            return jsonify({'success': False, 'message': 'Invalid credentials'}), 401

        session['user_email'] = email
        session['user_type'] = user['user_type']
        session['user_id'] = str(user['_id'])  # Store user_id as a string for later use

        return jsonify({'success': True, 'redirect_url': f'/{user["user_type"]}_dashboard'})

    


@app.route("/cust_profile", methods=["GET", "POST"])
def cust_profile():
    if 'user_email' not in session:
        return jsonify({'success': False, 'message': 'Unauthorized access'}), 403

    user_email = session['user_email']
    user = logins_collection.find_one({'email': user_email})

    if not user or user['user_type'] != 'customer':
        return jsonify({'success': False, 'message': 'Customer profile not found'}), 404

    if request.method == 'GET':
       
        profile = customers_collection.find_one({'login_id': user['_id']})
        if profile:
            profile['_id'] = str(profile['_id'])  # Convert ObjectId to string if sending to frontend
            return jsonify({'success': True, 'profile_data': profile})
        else:
            return jsonify({'success': False, 'message': 'Profile not found'}), 404

    elif request.method == 'POST':
        updated_data = request.get_json()

        result = customers_collection.update_one(
            {'login_id': user['_id']},
            {'$set': updated_data}
        )

        if 'email' in updated_data or 'phone' in updated_data or 'username' in updated_data:
            logins_collection.update_one(
                {'_id': user['_id']},
                {'$set': {
                    'email': updated_data.get('email', user['email']),
                    'phone': updated_data.get('phone', user['phone']),
                    'username': updated_data.get('username', user.get('username', ''))
                }}
            )

        if result.modified_count > 0:
            return jsonify({'success': True, 'message': 'Profile updated successfully'})
        else:
            return jsonify({'success': False, 'message': 'No changes made'}), 400





def is_shopkeeper():
    # Check if user_type is 'shopkeeper' in the session
    return session.get('user_type') == 'shopkeeper'


        



def generate_store_id():
    """Generate a custom store ID based on timestamp and random number"""
    timestamp = int(datetime.utcnow().timestamp())
    random_number = random.randint(1000, 9999)
    return f"store_{timestamp}_{random_number}"


@app.route('/create_store', methods=['POST'])
def create_store():
    if 'user_id' not in session or session.get('user_type') != 'shopkeeper':
        return jsonify({'error': 'Unauthorized'}), 403

    data = request.get_json()
    required_fields = ['store_name', 'owner_name', 'shopkeeper_name', 'address', 'contact']

    if not all(field in data for field in required_fields):
        return jsonify({'error': 'Missing required store fields'}), 400

    shopkeeper_id = ObjectId(session['user_id'])  # Taken from session

    store_id = generate_store_id()

    store_data = {
        'store_id': store_id,
        'store_name': data['store_name'],
        'owner_name': data['owner_name'],
        'shopkeeper_name': data['shopkeeper_name'],
        'shopkeeper_id': shopkeeper_id,
        'address': data['address'],
        'contact': data['contact'],
        'created_at': datetime.utcnow()
    }

    stores_collection.insert_one(store_data)

    return jsonify({'message': 'Store created successfully', 'store_id': store_id}), 201


@app.route('/update_store/<store_id>', methods=['POST'])
def update_store(store_id):
    data = request.json
    result = stores_collection.update_one(
        {'_id': ObjectId(store_id)},
        {'$set': {
            'store_name': data.get('store_name'),
            'owner_name': data.get('owner_name'),
            'address': data.get('address'),
            'contact': data.get('contact')
        }}
    )
    if result.modified_count > 0:
        return jsonify({'success': True, 'message': 'Store updated successfully'})
    else:
        return jsonify({'success': False, 'message': 'No changes made or store not found'})


@app.route("/get_my_stores", methods=["GET"])
def get_my_stores():
    if 'user_id' not in session or session.get('user_type') != 'shopkeeper':
        return jsonify({'success': False, 'message': 'Unauthorized'}), 403

    shopkeeper_id = ObjectId(session['user_id'])

    stores = list(stores_collection.find({'shopkeeper_id': shopkeeper_id}))

    for store in stores:
        store['_id'] = str(store['_id'])
        store['shopkeeper_id'] = str(store['shopkeeper_id'])

    return jsonify({'success': True, 'stores': stores})



@app.route('/shop_profile', methods=['GET', 'POST'])
def shop_profile():
    user_id = session.get('user_id')
    if not user_id:
        return jsonify({"success": False, "message": "Unauthorized"}), 403

    if request.method == 'GET':
        # Fetch shopkeeper data
        shopkeeper = shopkeepers_collection.find_one({'login_id': ObjectId(user_id)})
        if not shopkeeper:
            return jsonify({"success": False, "message": "Shopkeeper not found"}), 404

        return jsonify({
            "success": True,
            "profile_data": {
                "name": shopkeeper.get("name", ""),
                "email": shopkeeper.get("email", ""),
                "phone": shopkeeper.get("contact_number", ""),
                "shop_name": shopkeeper.get("shop_name", ""),
                "address": shopkeeper.get("shop_address", "")
            }
        })

    elif request.method == 'POST':
        updated_data = request.json

        # Prepare fields to update in shopkeepers_collection
        update_fields = {
            'name': updated_data.get("name"),
            'email': updated_data.get("email"),
            'contact_number': updated_data.get("phone"),
            'shop_name': updated_data.get("shop_name"),
            'shop_address': updated_data.get("address")
        }

        # Update in shopkeepers_collection
        result = shopkeepers_collection.update_one(
            {'login_id': ObjectId(user_id)},
            {'$set': update_fields}
        )

        # Also update login email/phone if changed
        logins_collection.update_one(
            {'_id': ObjectId(user_id)},
            {'$set': {
                'email': updated_data.get('email'),
                'phone': updated_data.get('phone'),
                'username': updated_data.get('name')
            }}
        )

        if result.modified_count > 0:
            return jsonify({"success": True, "message": "Profile updated successfully"})
        else:
            return jsonify({"success": False, "message": "No changes made"}), 400













@app.route("/shopkeeper_dashboard")
def shopkeeper_dashboard():

    return render_template("shopkeeper_dashboard.html", shopkeeper_id=str(session["user_id"]))

@app.route("/customer_dashboard")
def customer_dashboard():
    return render_template("customer_dashboard.html")

@app.route("/logout")
def logout():
    session.clear()  # Clears the session
    return redirect("/login")  # Redirect to the login page


@app.route('/get_health_news')
def get_health_news():
    import requests
    from datetime import datetime, timedelta

    api_key = "3569183d0fd148ca96a59bb7717a2bd7"
    current_date = datetime.now().date()
    past_date = current_date - timedelta(days=7)

    url = (
        f"https://newsapi.org/v2/everything?"
        f"q=health+fitness+medicine+awareness&"
        f"from={past_date}&to={current_date}&"
        f"sortBy=publishedAt&apiKey={api_key}"
    )

    try:
        res = requests.get(url)
        data = res.json()
        return jsonify({"success": True, "articles": data.get("articles", [])[:4]})
    except Exception as e:
        return jsonify({"success": False, "message": str(e)})



store_id_pattern = r'^store_\d{10}_\d{4}$'

# Function to validate store ID format
def validate_store_id(store_id):
    return bool(re.match(store_id_pattern, store_id))

@app.route("/add_inventory", methods=["POST"])
def add_inventory():
    data = request.json
    store_id = data.get("store_id")
    medicine_name = data.get("medicine_name")
    brand = data.get("brand")
    price = data.get("price")
    quantity = data.get("quantity")
    symptoms = data.get("symptoms", [])

    # Validate required fields
    if not all([store_id, medicine_name, brand, price, quantity]):
        return jsonify({"success": False, "message": "Missing required fields"}), 400

    # Validate custom store ID
    if not validate_store_id(store_id):
        return jsonify({"success": False, "message": "Invalid store_id format"}), 400

    # 1. Insert into inventory
    
    store = stores_collection.find_one({"store_id": store_id})

    if not store:
        return jsonify({"success": False, "message": "Store not found"}), 404
    shop_name = store.get("store_name")
    
    try:
        inventory_doc = {
            "store_id": store_id,
            "shop_name": shop_name,
            "medicine_name": medicine_name,
            "brand": brand,
            "price": price,
            "quantity": quantity,
            "added_at": datetime.utcnow()
        }
        inventory_collection.insert_one(inventory_doc)

        # 2. Insert into medicines collection only if it doesn’t exist
        existing = medicines_collection.find_one({
            "name": medicine_name,
            "brand": brand
        })

        if not existing:
            medicine_doc = {
                "name": medicine_name,
                "brand": brand,
                "price": price,
                "symptoms": symptoms
            }
            medicines_collection.insert_one(medicine_doc)

        return jsonify({"success": True, "message": "Inventory added successfully"}), 201

    except Exception as e:
        return jsonify({"success": False, "message": f"Error: {str(e)}"}), 500


@app.route("/get_inventory/<store_id>", methods=["GET"])
def get_inventory(store_id):
    # Validate store ID format
    if not validate_store_id(store_id):
        return jsonify({"error": "Invalid store_id format"}), 400

    # Fetch all inventory items for this store
    inventory_items = list(inventory_collection.find({"store_id": store_id}))

    # Convert ObjectId to string for JSON response
    for item in inventory_items:
        item["_id"] = str(item["_id"])
        item["store_id"] = str(item["store_id"])
        item["added_at"] = item["added_at"].strftime("%Y-%m-%d %H:%M:%S")

    return jsonify({"inventory": inventory_items}), 200
@app.route("/update_inventory", methods=["POST"])
def update_inventory():
    data = request.json
    store_id = data.get("store_id")  # This should be in the custom store ID format
    medicine_name = data.get("medicine_name")
    brand = data.get("brand")
    price = data.get("price")
    quantity = data.get("quantity")
    symptoms = data.get("symptoms", [])  # Optional, default to an empty list

    # Check for required fields
    if not all([store_id, medicine_name, brand, price, quantity]):
        return jsonify({"error": "Missing required fields"}), 400

    # Validate store ID format
    if not validate_store_id(store_id):
        return jsonify({"error": "Invalid store_id format"}), 400

    # Update inventory based on store_id, medicine_name, and brand
    try:
        # Fetch the existing inventory item
        inventory_item = inventory_collection.find_one({
            "store_id": store_id,
            "medicine_name": medicine_name,
            "brand": brand
        })
        
        if not inventory_item:
            return jsonify({"error": "Inventory item not found"}), 404

        # Prepare the update data
        update_data = {
            "price": price,
            "quantity": quantity,
            "symptoms": symptoms,
            "updated_at": datetime.utcnow()  # Update timestamp
        }

        # Update the inventory item
        inventory_collection.update_one(
            {"_id": inventory_item["_id"]},  # Find the inventory item by its ObjectId
            {"$set": update_data}  # Update the necessary fields
        )

        # Optionally update the `medicines_collection` if needed
        medicines_collection.update_one(
            {"name": medicine_name, "brand": brand},
            {"$set": {"price": price, "symptoms": symptoms}},
            upsert=True  # If the medicine doesn't exist, it will be inserted
        )

        return jsonify({"message": "Inventory updated successfully"}), 200

    except Exception as e:
        return jsonify({"error": f"An error occurred: {str(e)}"}), 500

def validate_store_id(store_id):
    # Accepts formats like store_1744789457_8252
    return bool(re.match(r"^store_\d{10}_\d{4}$", store_id))





if __name__ == '__main__':
    app.run(debug=True)

