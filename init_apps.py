import os

apps = ['core', 'accounts', 'rooms', 'faculty', 'duty', 'timetable', 'notifications']
base_path = r'e:\AC\alocentra\apps'

for app in apps:
    app_dir = os.path.join(base_path, app)
    os.makedirs(app_dir, exist_ok=True)
    
    with open(os.path.join(app_dir, '__init__.py'), 'w') as f:
        pass
        
    with open(os.path.join(app_dir, 'apps.py'), 'w') as f:
        f.write(f"""from django.apps import AppConfig\n\nclass {app.capitalize()}Config(AppConfig):\n    default_auto_field = 'django.db.models.BigAutoField'\n    name = 'apps.{app}'\n""")

    with open(os.path.join(app_dir, 'models.py'), 'w') as f:
        f.write("from django.db import models\n\n# Placeholder\n")

    with open(os.path.join(app_dir, 'views.py'), 'w') as f:
        f.write('from django.shortcuts import render\nfrom django.http import HttpResponse\n\ndef placeholder_view(request):\n    return HttpResponse("coming soon")\n')

    with open(os.path.join(app_dir, 'urls.py'), 'w') as f:
        f.write(f"from django.urls import path\nfrom . import views\n\napp_name = '{app}'\n\nurlpatterns = [\n    path('', views.placeholder_view, name='placeholder'),\n]\n")

    # Additional empty files expected
    open(os.path.join(app_dir, 'admin.py'), 'w').close()
    if app != 'core':
        open(os.path.join(app_dir, 'forms.py'), 'w').close()
        
# specific files
open(os.path.join(base_path, 'accounts', 'utils.py'), 'w').close()
open(os.path.join(base_path, 'duty', 'assignment_engine.py'), 'w').close()
open(os.path.join(base_path, 'notifications', 'tasks.py'), 'w').close()

print("Apps created")
