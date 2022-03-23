import requests
import json

def check_offensive(text: str):
    data = {'id': 0, 'comment_txt': text}
    result = requests.post('http://20.124.230.10:8000/predict', json.dumps(data))
    return result.json().get('is_offensive')

