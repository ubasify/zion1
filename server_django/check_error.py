import urllib.request
from urllib.error import HTTPError

try:
    response = urllib.request.urlopen('http://127.0.0.1:8000/attendance/')
    print("Status: 200")
except HTTPError as e:
    print(f"Status: {e.code}")
    content = e.read().decode('utf-8')
    # Extract just the error message
    if "TemplateSyntaxError" in content:
        start = content.find("Could not parse")
        if start > 0:
            end = content.find("</pre>", start)
            print("Error:", content[start:end])
    else:
        print("Error type:", content[content.find("<title>")+7:content.find("</title>")])
except Exception as e:
    print(e)
