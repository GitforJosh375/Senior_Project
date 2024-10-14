import requests

stop_command = {'command': 'shutdown'}
response = requests.post('http://<your_server_ip>:5000/command', json=stop_command)
print(response.json())
