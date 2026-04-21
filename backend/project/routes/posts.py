from flask import Blueprint, request, jsonify

posts_bp = Blueprint("posts", __name__)

@posts_bp.route("/hello", methods=["POST"])
def hello():
    body = request.get_json()
    text = body.get("text")
    return jsonify(f"Hello {text}!")

@posts_bp.route("/create", methods=["POST"])
def create():
    return "TODO: create post"

@posts_bp.route("/getLatest", methods=["GET"])
def getLatest():
    return "TODO: getLatest post"

