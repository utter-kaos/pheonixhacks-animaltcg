import requests

def reset_battle_status(user_id):
    url = f"http://127.0.0.1:5000/reset_battle_status/{user_id}"
    try:
        response = requests.post(url)
        if response.status_code == 200:
            print(response.json()["message"])
        else:
            print(f"Error: {response.json().get('error', 'Unknown error')}")
    except requests.RequestException as e:
        print(f"Request failed: {e}")

if __name__ == "__main__":
    user_id = input("Enter the user ID to reset battle status: ")
    reset_battle_status(user_id)
