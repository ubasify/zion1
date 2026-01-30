import re
import os

file_path = r'c:\Users\oladi\sources\rccghgz\server_django\templates\operations\financial_dashboard_v3.html'

with open(file_path, 'r', encoding='utf-8') as f:
    content = f.read()

# Regex to find {{ ... }} blocks, possibly spanning multiple lines
# We use DOTALL so . matches newlines
# We replace the inside with a version where all whitespace is squashed to usage single space
def squash_whitespace(match):
    inner = match.group(1)
    # Replace all whitespace sequences (newlines, tabs, spaces) with a single space
    clean_inner = ' '.join(inner.split())
    return f"{{{{ {clean_inner} }}}}"

# Apply the regex
new_content = re.sub(r'\{\{(.*?)\}\}', squash_whitespace, content, flags=re.DOTALL)

# Also fix the weird specific split seen in lines 39-40 if regex misses it (it shouldn't)
# But let's verify.

with open(file_path, 'w', encoding='utf-8') as f:
    f.write(new_content)

print("Fixed template tags. Checking for remaining newlines inside tags...")
# Verification
matches = re.findall(r'\{\{.*?\}\}', new_content, flags=re.DOTALL)
for m in matches:
    if '\n' in m:
        print(f"WARNING: Found split tag: {m}")
    else:
        # print(f"OK: {m}")
        pass
print("Done.")
