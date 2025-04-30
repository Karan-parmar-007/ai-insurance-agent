# agent/api_utils.py
import requests

def get_user_by_email(email):
    try:
        res = requests.get(f"http://localhost:5000/api/user/get_user?email={email}")
        if res.status_code == 200:
            return res.json()
    except Exception as e:
        print("[API] Error:", e)
    return None
