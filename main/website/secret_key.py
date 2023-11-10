import requests

def refresh_one_map_token():
    url = "https://www.onemap.gov.sg/api/auth/post/getToken"
    payload = {
        "email": "C220145@e.ntu.edu.sg",
        "password": "Y2ZwBcbv^Nsd2#"
    }

    response = requests.request("POST", url, json=payload)
    
    if response.status_code == 502:
        access_token = "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJzdWIiOiI5M2VhOTMxZWMxYmIxZDJjYjg5MzVlY2FkMjJiZDBlMSIsImlzcyI6Imh0dHA6Ly9pbnRlcm5hbC1hbGItb20tcHJkZXppdC1pdC0xMjIzNjk4OTkyLmFwLXNvdXRoZWFzdC0xLmVsYi5hbWF6b25hd3MuY29tL2FwaS92Mi91c2VyL3Nlc3Npb24iLCJpYXQiOjE2OTg2Njk2MzYsImV4cCI6MTY5ODkyODgzNiwibmJmIjoxNjk4NjY5NjM2LCJqdGkiOiJqUTVWdmRMdjZvejdBMklHIiwidXNlcl9pZCI6MTEyMSwiZm9yZXZlciI6ZmFsc2V9.B2rPgWgk4OZXmvsg5n66-7olY0TxEYUE-sqseGokr-0"
        print("OneMap API is down, using default access token")
        print("Error", response.status_code)
    else:
        access_token = response.json()["access_token"]
        #print(access_token)

    return access_token