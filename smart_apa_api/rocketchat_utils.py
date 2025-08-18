import requests

def get_rocketchat_token(login, password):
    url = "http://192.168.10.45:3000/api/v1/login"
    headers = {"Content-Type": "application/json"}
    data = {
        "user": login,
        "password": password
    }

    response = requests.post(url, json=data, headers=headers)
    if response.status_code == 200 and response.json().get("status") == "success":
        #return response.json()["data"]["authToken"]
        return response.json()["data"]["authToken"], response.json()["data"]["userId"]
    else:
        return None, None


def get_last_conversations(user_token, user_id, login):
    #user_token = request.headers.get("X-Auth-Token")
    #user_id = request.headers.get("X-User-Id")
    #
    #if not user_token or not user_id:
    #    return JsonResponse({"error": "Missing auth headers"}, status=400)

    headers = {
        "X-Auth-Token": user_token,
        "X-User-Id": user_id
    }
    url = "http://192.168.10.45:3000/api/v1/dm.list"
    response = requests.get(url, headers=headers)

    if response.status_code != 200:
        #return JsonResponse({"error": "Failed to fetch conversations"}, status=response.status_code)
        return None

    data = response.json()

    # Format for frontend
    _login = login.split('@')[0]
    lst = []
    for conv in data.get("ims", []):
        other_user = next((u for u in conv["usernames"] if u != _login), None)
        if other_user:
            lst.append(other_user)

    return lst