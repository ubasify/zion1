import os
import django
from django.conf import settings
from django.template import Template, Context, TemplateSyntaxError

# Configure minimal Django settings
if not settings.configured:
    settings.configure(
        TEMPLATES=[{
            'BACKEND': 'django.template.backends.django.DjangoTemplates',
            'DIRS': [os.path.join(os.getcwd(), 'server_django', 'templates')],
            'APP_DIRS': True,
             'OPTIONS': {
                'libraries': {
                    'custom_filters': 'core.templatetags.custom_filters',
                },
            },
        }],
        INSTALLED_APPS=[
            'django.contrib.contenttypes',
            'core', # containing the templatetags
        ]
    )
    django.setup()

def validate_template(path):
    with open(path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    try:
        t = Template(content)
        print(f"SUCCESS: {path} is valid.")
    except TemplateSyntaxError as e:
        print(f"ERROR: {path} has syntax error:")
        print(e)
    except Exception as e:
        print(f"ERROR: {path} has other error:")
        print(e)

if __name__ == "__main__":
    path = os.path.join(os.getcwd(), 'server_django', 'templates', 'operations', 'attendance_list_v4.html')
    print(f"Validating {path}...")
    validate_template(path)
