import json
import os
import uuid
from http.cookies import SimpleCookie
from google.cloud import firestore
from firebase_admin import auth, initialize_app

from flask import request, jsonify, make_response
import functions_framework

initialize_app()
db = firestore.Client(database="carts-db")
table_name = "carts-db"

@functions_framework.http
def checkout_cart(request):

    if request.method == "OPTIONS":
        # Allows GET requests from any origin with the Content-Type
        # header and caches preflight response for an 3600s
        headers = {
            "Access-Control-Allow-Origin": "http://localhost:4200",
            "Access-Control-Allow-Headers": "Content-Type",
            "Access-Control-Allow-Methods": "OPTIONS,POST,GET",
            "Access-Control-Allow-Credentials": "true",
        }

        return ("", 204, headers)


    claims = auth.verify_id_token(request.args.get('authtoken'))
    # claims['region']

    cookie = SimpleCookie()
    cart_id = ""
    try:
        cookie.load(request.headers.get("cookie", ""))
        cart_id = cookie["cartId"].value
    except KeyError:
        cart_id = str(uuid.uuid4())

    # Set the cookie with the new cart ID
    cookie = SimpleCookie()
    cookie["cartId"] = cart_id
    cookie["cartId"]["max-age"] = (60 * 60) * 24  # 1 day
    cookie["cartId"]["secure"] = True
    cookie["cartId"]["httponly"] = True
    cookie["cartId"]["samesite"] = "None"
    cookie["cartId"]["path"] = "/"

    headers = {
        "Access-Control-Allow-Origin": "http://localhost:4200",
        "Access-Control-Allow-Headers": "Content-Type",
        "Access-Control-Allow-Methods": "OPTIONS,POST,GET",
        "Access-Control-Allow-Credentials": "true",
        "Set-Cookie": cookie["cartId"].OutputString()
    }

    try:
        user_id = claims['uid']
        if not user_id:
            raise KeyError
    except KeyError:
        return make_response(
            jsonify({"message": "Invalid user"}),
            400,
            headers
        )

    # Query Firestore for the cart items using user ID
    cart_ref = db.collection('carts')
    query = cart_ref.where("pk", "==", f"cart#{user_id}")
    cart_items = [doc.to_dict() for doc in query.stream()]

    # Batch delete the cart items
    batch = db.batch()
    for item in cart_items:
        doc_ref = cart_ref.document(item["pk"] + "#" + item["sk"])
        batch.delete(doc_ref)
    batch.commit()

    return make_response(
        jsonify({"products": cart_items}),
        200,
        headers
    )
