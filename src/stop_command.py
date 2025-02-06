import requests

stop_command = {'command': 'stop'}
response = requests.post('http://67.43.244.153:5000/command', json=stop_command)
print(response.json())
