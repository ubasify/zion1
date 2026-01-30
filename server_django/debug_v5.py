
file_path = r'c:\Users\oladi\sources\rccghgz\server_django\templates\operations\financial_dashboard_v5.html'

with open(file_path, 'rb') as f:
    content = f.read()

print(f"File size: {len(content)} bytes")

# Find working Net Income tag
net_idx = content.find(b'kpi.net_income')
if net_idx != -1:
    print(f"\n--- Working Tag (Net Income) ---")
    chunk = content[net_idx-20:net_idx+40]
    print(chunk)
    print(chunk.hex())

# Find failing Income YTD tag
inc_idx = content.find(b'kpi.income_ytd')
if inc_idx != -1:
    print(f"\n--- Failing Tag (Income YTD) ---")
    chunk = content[inc_idx-20:inc_idx+40]
    print(chunk)
    print(chunk.hex())
    
# Find failing Table tag
cat_idx = content.find(b'item.category')
if cat_idx != -1:
    print(f"\n--- Failing Tag (Item Category) ---")
    chunk = content[cat_idx-20:cat_idx+40]
    print(chunk)
    print(chunk.hex())
