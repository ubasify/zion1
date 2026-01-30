import urllib.request
from urllib.error import HTTPError

try:
    response = urllib.request.urlopen('http://127.0.0.1:8000/attendance/')
    print("Status: 200")
except HTTPError as e:
    print(f"Status: {e.code}")
    content = e.read().decode('utf-8')
    with open('error_log.html', 'w', encoding='utf-8') as f:
        f.write(content)
except Exception as e:
    print(e)
