import os
import csv
import json
import re
from pathlib import Path
import requests
from flask import Flask, render_template, jsonify, send_from_directory, abort, url_for, request
from datetime import datetime
                
 
app = Flask(__name__)

TABS_DIR = Path("tabs")
TAB_ORDER_FILE = Path("tab_order.json")
LOG_FILE = "visitor_log.csv"
MY_HOME_IP = [' 103.147.183.17']

SPECIAL_TABS = {
    "home": ["home"],
    "cv": ["cv resume", "cv/resume", "resume", "cv", "profile"],
    "contact": ["contact", "contact details"]
}


def get_geo_info(ip):
    """Translates an IP address into Location and Organization info."""
    try:
        # Use ip-api.com (Free for 45 requests per minute)
        # We ask for: country, city, isp, and org (org usually shows Universities)
        url = f"http://ip-api.com/json/{ip}?fields=status,country,city,isp,org,mobile"
        response = requests.get(url, timeout=5)
        data = response.json()

        if data.get('status') == 'success':
            # Identify if it's a University/Corporate or just Home ISP
            # We combine ISP and ORG to get the best 'Who' info
            who = data.get('org') if data.get('org') else data.get('isp')
            location = f"{data.get('city')}, {data.get('country')}"
            is_mobile = "Yes" if data.get('mobile') else "No"
            return location, who, is_mobile
    except:
        pass
    return "Unknown", "Unknown", "Unknown"

def get_user_name():
    tab_path = TABS_DIR / "Home"
    text_dir = tab_path / "text"

    if text_dir.exists():
        for txt_file in sorted(text_dir.iterdir()):
            if txt_file.suffix.lower() in ['.txt', '.md']:
                lines = txt_file.read_text(encoding='utf-8', errors='replace').splitlines()
                user_name = lines[0] if lines else ""
                return user_name

user_name = get_user_name() or "User"

@app.before_request
def track_everything():

    # 1. THE FILTER: List of extensions to IGNORE
    ignored_extensions = [
        '.css', '.js', '.jpg', '.png', '.gif',
        '.svg', '.ico', '.woff', '.woff2', '.ttf'
    ]

    # Get the lowercase path (e.g., /static/img/logo.PNG -> .png)
    path = request.path.lower()

    # Check if the path ends with any of the ignored extensions
    if any(path.endswith(ext) for ext in ignored_extensions):
        return # Exit the function; don't log this!

    # 2. ALSO ignore the common "static" folder prefix
    if path.startswith('/static/'):
        return

    # 3. ALSO ignore your secret stats route (otherwise you'll log yourself)
    if 'get_secret_stats_99' in path:
        return

    ip = request.headers.get('X-Forwarded-For', request.remote_addr)
    if ip in MY_HOME_IP:
        return

    # 2. Get the 'Deep' info
    location, organization, is_mobile = get_geo_info(ip)

    # 3. Save to CSV
    file_exists = os.path.isfile(LOG_FILE)
    with open(LOG_FILE, mode='a', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        if not file_exists:
            writer.writerow(['Time', 'IP', 'Location', 'Entity (Uni/Home)', 'Mobile?'])

        else:
            writer.writerow([
                datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                ip,
                location,
                organization,       # This is where 'University of...' shows up
                is_mobile
            ])





@app.route('/get_secret_stats_99') # Use a name only you know
def get_stats():
    # Only allow access if it's you (optional: add a password check here)
    if not os.path.exists(LOG_FILE):
        return json.dumps({"error": "No data yet"})

    with open(LOG_FILE, mode='r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        # Return the last 20 visitors
        rows = list(reader)[-20:]
        return json.dumps(rows)


def get_tab_slug(name):
    return re.sub(r'[^a-z0-9]+', '-', name.lower()).strip('-')

def get_all_tabs():
    if not TABS_DIR.exists():
        return []
    tabs = []
    for d in sorted(TABS_DIR.iterdir()):
        if d.is_dir():
            tabs.append({"name": d.name, "slug": get_tab_slug(d.name), "path": str(d)})
    # Sort by tab_order.json if exists
    if TAB_ORDER_FILE.exists():
        try:
            order = json.loads(TAB_ORDER_FILE.read_text())
            name_to_tab = {t["name"]: t for t in tabs}
            ordered = [name_to_tab[n] for n in order if n in name_to_tab]
            remaining = [t for t in tabs if t["name"] not in order]
            tabs = ordered + remaining
        except Exception:
            pass
    return tabs

def is_special(tab_name, kind):
    return tab_name.lower() in SPECIAL_TABS.get(kind, [])

def get_tab_content(tab_name):
    tab_path = TABS_DIR / tab_name
    if not tab_path.exists():
        return []

    text_dir = tab_path / "text"
    images_dir = tab_path / "images"

    if not text_dir.exists():
        return []

    items = []
    for txt_file in sorted(text_dir.iterdir()):
        if txt_file.suffix.lower() not in ['.txt', '.md']:
            continue
        stem = txt_file.stem
        lines = txt_file.read_text(encoding='utf-8', errors='replace').splitlines()
        heading = lines[0] if lines else stem
        body = "\n".join(lines[1:]).strip() if len(lines) > 1 else ""

        # Find matching image
        image_url = None
        if images_dir.exists():
            for ext in ['.jpg', '.jpeg', '.png', '.gif', '.webp', '.svg']:
                img = images_dir / (stem + ext)
                if img.exists():
                    image_url = url_for('serve_tab_image', tab_name=tab_name, filename=img.name)
                    break

        items.append({"heading": heading, "body": body, "image": image_url, "stem": stem})
    return items

def get_contact_data(tab_name):
    tab_path = TABS_DIR / tab_name
    images_dir = tab_path / "images"
    csv_path = tab_path / "contacts.csv"

    contacts = []
    if not csv_path.exists():
        return contacts

    with open(csv_path, newline='', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            platform = row.get('platform', '').strip()
            link = row.get('link', '').strip()
            alias = row.get('alias', '').strip()
            display = alias if alias else link

            icon_url = None
            if images_dir.exists():
                for ext in ['.png', '.jpg', '.jpeg', '.svg', '.webp']:
                    icon = images_dir / (platform + ext)
                    if icon.exists():
                        icon_url = url_for('serve_tab_image', tab_name=tab_name, filename=icon.name)
                        break

            contacts.append({"platform": platform, "link": link, "display": display, "icon": icon_url})
    return contacts

def get_home_data(tab_name):
    tab_path = TABS_DIR / tab_name
    text_dir = tab_path / "text"
    images_dir = tab_path / "images"

    heading, body, image_url = "", "", None

    if text_dir.exists():
        for txt_file in sorted(text_dir.iterdir()):
            if txt_file.suffix.lower() in ['.txt', '.md']:
                lines = txt_file.read_text(encoding='utf-8', errors='replace').splitlines()
                heading = lines[0] if lines else ""
                body = "\n".join(lines[1:]).strip() if len(lines) > 1 else ""
                break

    if images_dir.exists():
        for img in sorted(images_dir.iterdir()):
            if img.suffix.lower() in ['.jpg', '.jpeg', '.png', '.webp', '.gif']:
                image_url = url_for('serve_tab_image', tab_name=tab_name, filename=img.name)
                break

    return {"heading": heading, "body": body, "image": image_url}

@app.route('/')
def index():
    tabs = get_all_tabs()
    home_tab = None
    for t in tabs:
        if is_special(t['name'], 'home'):
            home_tab = t
            break
    home_data = get_home_data(home_tab['name']) if home_tab else {"heading": "Welcome", "body": "", "image": None}
    contact_tab = next((t for t in tabs if is_special(t['name'], 'contact')), None)
    contact_data = get_contact_data(contact_tab['name']) if contact_tab else []
    return render_template('index.html',user_name=user_name, tabs=tabs, home_data=home_data, contact_data=contact_data, active_slug='home')

@app.route('/tab/<slug>')
def tab_view(slug):
    tabs = get_all_tabs()
    tab = next((t for t in tabs if t['slug'] == slug), None)
    if not tab:
        abort(404)

    contact_tab = next((t for t in tabs if is_special(t['name'], 'contact')), None)
    contact_data = get_contact_data(contact_tab['name']) if contact_tab else []

    if is_special(tab['name'], 'home'):
        home_data = get_home_data(tab['name'])
        return render_template('index.html',user_name=user_name, tabs=tabs, home_data=home_data, contact_data=contact_data, active_slug=slug)

    if is_special(tab['name'], 'contact'):
        return render_template('tab.html',user_name=user_name, tabs=tabs, tab=tab, content=[], is_contact=True, contact_data=contact_data, active_slug=slug)

    if is_special(tab['name'], 'cv'):
        cv_html = get_cv_html(tab['name'])
        return render_template('tab.html',user_name=user_name, tabs=tabs, tab=tab, content=[], is_cv=True, cv_html=cv_html, contact_data=contact_data, active_slug=slug)

    content = get_tab_content(tab['name'])
    return render_template('tab.html',user_name=user_name, tabs=tabs, tab=tab, content=content, contact_data=contact_data, active_slug=slug)

custom_style_map = """
p[style-name='Title'] => h1.cv-title:fresh
p[style-name='Subtitle'] => h1.cv-subtitle:fresh
p[style-name='Heading 1'] => h2.cv-h1:fresh
p[style-name='Heading 2'] => h3.cv-h2:fresh
p[style-name='Normal'] => p.cv-normal:fresh
p[style-name='Quote'] => p.cv-reference1:fresh
p[style-name='Intense Quote'] => p.cv-reference2:fresh

# Explicitly handle inline formatting styles
b => strong
i => em
u => span.cv-underline
"""


def get_cv_html(tab_name):
    tab_path = TABS_DIR / tab_name
    # Look for .docx file
    for f in tab_path.iterdir():
        if f.suffix.lower() == '.docx':
            try:
                import mammoth
                with open(f, 'rb') as docx:
                    result = mammoth.convert_to_html(docx, style_map=custom_style_map)
                    return result.value
            except ImportError:
                return "<p><em>Please install <code>mammoth</code> to render DOCX files: <code>pip install mammoth</code></em></p>"
            except Exception as e:
                return f"<p>Error reading CV: {e}</p>"
    # Look for .txt or .md fallback
    text_dir = tab_path / "text"
    if text_dir.exists():
        for f in sorted(text_dir.iterdir()):
            if f.suffix.lower() in ['.txt', '.md']:
                content = f.read_text(encoding='utf-8', errors='replace')
                return f"<pre style='white-space:pre-wrap'>{content}</pre>"
    return "<p>No CV file found. Place a .docx file in the CV Resume tab folder.</p>"

@app.route('/tab-image/<tab_name>/<filename>')
def serve_tab_image(tab_name, filename):
    img_dir = TABS_DIR / tab_name / "images"
    return send_from_directory(str(img_dir.resolve()), filename)

@app.route('/api/tabs')
def api_tabs():
    return jsonify(get_all_tabs())

if __name__ == '__main__':
    app.run(debug=True, port=5000)
