import os
import glob

files = glob.glob('templates/dashboard/*.html')
for f in files:
    # Skip the new base we just made
    if f.endswith('admin_base.html'):
        continue

    # Also skip security_dashboard.html if it's considered an alternative base, 
    # but the user said "server admin is acting like the dashboard" so maybe it's fine.
    # Actually wait, admin_dashboard.html needs special tweaking because I extracted its wrapper into admin_base.html.
    # So I will skip admin_dashboard.html and fix it manually.
    if f.endswith('admin_dashboard.html') or f.endswith('security_dashboard.html'):
        continue

    with open(f, 'r', encoding='utf-8') as file:
        content = file.read()
    
    modified = False
    
    if '{% extends "base.html" %}' in content or "{% extends 'base.html' %}" in content:
        content = content.replace('{% extends "base.html" %}', '{% extends "dashboard/admin_base.html" %}')
        content = content.replace("{% extends 'base.html' %}", '{% extends "dashboard/admin_base.html" %}')
        
        # Replace block names carefully
        content = content.replace('{% block extra_css %}', '{% block admin_css %}')
        content = content.replace('{% block content %}', '{% block admin_content %}')
        content = content.replace('{% block extra_js %}', '{% block admin_js %}')
        
        modified = True

    if modified:
        with open(f, 'w', encoding='utf-8') as file:
            file.write(content)
        print(f"Updated {f}")

print("Done updating list/form templates to use admin_base.html wrapper.")
