import requests

start_command = {'command': 'start'}
response = requests.post('http://<your_server_ip>:5000/command', json=start_command)
print(response.json())
