import requests
r = requests.get('http://127.0.0.1:5000/api/media/movie/533535')
print(r.status_code)
print(r.text)
