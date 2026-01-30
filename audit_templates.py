import os
from django.template.loader import get_template
from django.template import TemplateSyntaxError

template_dir = r'c:\Users\oladi\sources\rccghgz\server_django\events\templates\events'
files = [f for f in os.listdir(template_dir) if f.endswith('.html')]

print(f"Checking {len(files)} templates in {template_dir}...")

for filename in files:
    template_name = f"events/{filename}"
    print(f"Checking {template_name}...")
    try:
        get_template(template_name)
        print(f"  OK: {template_name}")
    except TemplateSyntaxError as e:
        print(f"  FAIL: {template_name} -> {e}")
    except Exception as e:
        print(f"  ERROR: {template_name} -> {e}")

print("Done.")
