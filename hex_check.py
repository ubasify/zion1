file_path = r'c:\Users\oladi\sources\rccghgz\server_django\templates\operations\financial_dashboard_v3.html'

with open(file_path, 'rb') as f:
    content = f.read()

# Find the index of "income_ytd"
idx = content.find(b'income_ytd')
if idx != -1:
    # Print 50 bytes before and after
    start = max(0, idx - 100)
    end = min(len(content), idx + 100)
    chunk = content[start:end]
    print(f"Context surrounding 'income_ytd':")
    print(chunk)
    print("Hex:")
    print(chunk.hex())
else:
    print("Could not find income_ytd string in bytes.")
