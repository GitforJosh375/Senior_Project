import requests

start_command = {'command': 'start'}
response = requests.post('http://67.43.244.153:5000/command', json=start_command)
print(response.json())
