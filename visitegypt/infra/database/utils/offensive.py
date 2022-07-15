import requests
import json

def check_offensive(text: str):
    data = {'id': 0, 'comment_txt': text}
    result = requests.post('http://129.146.97.191/api/predict', json.dumps(data))
    return result.json().get('is_offensive')

