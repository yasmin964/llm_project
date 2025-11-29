import json
import os

FILE = "admins.json"

if not os.path.exists(FILE):
    with open(FILE, "w") as f:
        json.dump({"admins": []}, f)

def get_admins():
    with open(FILE, "r") as f:
        return json.load(f)["admins"]

def save_admins(admins):
    with open(FILE, "w") as f:
        json.dump({"admins": admins}, f)

def add_admin(user_id: int):
    admins = get_admins()
    if user_id not in admins:
        admins.append(user_id)
        save_admins(admins)

def remove_admin(user_id: int):
    admins = get_admins()
    if user_id in admins:
        admins.remove(user_id)
        save_admins(admins)

def is_admin(user_id: int) -> bool:
    return user_id in get_admins()
