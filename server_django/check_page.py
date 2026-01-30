import urllib.request
from urllib.error import HTTPError

try:
    response = urllib.request.urlopen('http://127.0.0.1:8000/attendance/')
    print("✅ Status: 200 - Page loads successfully!")
except HTTPError as e:
    print(f"❌ Status: {e.code}")
    content = e.read().decode('utf-8')
    
    # Find the error message
    if "Exception Value:" in content:
        start = content.find("Exception Value:") + len("Exception Value:")
        end = content.find("</td>", start)
        error_section = content[start:end]
        # Clean up HTML
        error_section = error_section.replace("<pre>", "").replace("</pre>", "").replace("&#x27;", "'").replace("&quot;", '"')
        print(f"Error: {error_section.strip()}")
    
    # Find the template file
    if "In template" in content:
        start = content.find("In template") 
        end = content.find("</p>", start)
        template_info = content[start:end]
        template_info = template_info.replace("<code>", "").replace("</code>", "").replace("<strong>", "").replace("</strong>", "")
        print(f"\n{template_info.strip()}")
        
except Exception as e:
    print(f"Connection error: {e}")
