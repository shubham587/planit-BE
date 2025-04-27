from app import db_init

def check_user(email):
    return db_init.User.find_one({"email": email})

def reqister_user(username, email, password):
    return db_init.User.insert_one({"username": username, "email": email, "password": password})

def add_to_blacklist(jti):
    return db_init.BlackList.insert_one({"jti": jti})

def check_token_blacklist(jti):
    return db_init.BlackList.find_one({"jti": jti})