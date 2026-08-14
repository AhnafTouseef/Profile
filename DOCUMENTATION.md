# Portfolio Website — Setup & Documentation Guide

## Overview

A dynamic, file-driven academic/research portfolio built with Flask. The site reads its content directly from folders and files — no database required. Adding a new section is as simple as creating a new folder.

---

## Quick Start

### 1. Prerequisites

- Python 3.9 or higher
- pip

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

### 3. Run the App

```bash
python app.py
```

Open your browser at: **http://localhost:5000**

---

## Project Structure

```
portfolio/
├── app.py                   # Flask application (main server)
├── requirements.txt         # Python dependencies
├── tab_order.json           # Controls the order of tabs in the nav bar
│
├── tabs/                    # ← ALL YOUR CONTENT GOES HERE
│   ├── Home/
│   │   ├── images/          # Profile photo (first image found is used)
│   │   └── text/            # Bio text (first .txt file found is used)
│   │
│   ├── Research Interest/
│   │   ├── images/
│   │   └── text/
│   │
│   ├── CV Resume/
│   │   ├── YourCV.docx      # Place your .docx CV file directly here
│   │   └── text/            # Optional fallback if no .docx is found
│   │
│   ├── Contact/
│   │   ├── images/          # Platform logo files (named by platform)
│   │   └── contacts.csv     # Contact data (see format below)
│   │
│   └── [Any New Tab]/       # Create any new tab by adding a folder here
│       ├── images/
│       └── text/
│
├── static/
│   ├── css/main.css         # All styles
│   └── js/main.js           # Scroll animations & interactions
│
└── templates/
    ├── base.html            # Navigation + contact footer (shared layout)
    ├── index.html           # Home page template
    └── tab.html             # All other tab pages template
```

---

## Content Authoring

### Home Tab

The Home tab has a special two-column layout with a large profile photo and animated scroll behavior.

**Folder:** `tabs/Home/`

**Text file** (`tabs/Home/text/profile.txt`):
```
Your Name or Tagline           ← Line 1 becomes the big heading
Rest of your bio text here.   ← Everything after line 1 is body text
You can write multiple lines.
Each non-empty line becomes a paragraph.
```

**Image:** Place your profile photo in `tabs/Home/images/`. Any common image format works (`.jpg`, `.png`, `.webp`). The first image found alphabetically is used.

**Scroll Behavior:**
- On arrival: Big profile photo on the right, your name on the left
- On scroll down: Photo slides and fades away; text transitions to center layout

---

### Regular Tabs (Research, Publications, Achievements, etc.)

Each tab can have multiple content blocks. Each block = one `.txt` file paired with one image.

**Folder:** `tabs/Tab Name/text/` and `tabs/Tab Name/images/`

**Naming convention:** Match the base filename to pair image and text.

```
tabs/Research Interest/
├── text/
│   ├── 01_genomics.txt          # Paired with images/01_genomics.jpg
│   ├── 02_ml.txt                # Paired with images/02_ml.png
│   └── 03_drug_discovery.txt    # No image → text-only block
└── images/
    ├── 01_genomics.jpg
    └── 02_ml.png
```

**Text file format:**
```
Section Heading Here                    ← Line 1 = heading (gold-accented)
Body text starts from line 2 onwards.  ← Shown below the image
Each non-empty line becomes a paragraph.
You can have as many lines as you want.
```

**Layout:** Blocks alternate between image-left and image-right automatically.

**Supported image formats:** `.jpg`, `.jpeg`, `.png`, `.gif`, `.webp`, `.svg`

---

### CV / Resume Tab

Place your Word document directly in the tab folder.

**Folder:** `tabs/CV Resume/`

**Steps:**
1. Place your `.docx` file in `tabs/CV Resume/` (any filename works)
2. The app will automatically convert and render it with original formatting
3. Fonts, headings, tables, bullet points, and links are all preserved

**Fallback:** If no `.docx` is found, the app falls back to `.txt` files in the `text/` subfolder (displayed in preformatted style).

**Requirement:** The `mammoth` Python package handles DOCX conversion (included in `requirements.txt`).

---

### Contact Tab

Contacts are displayed in a responsive grid at the bottom of every page.

**Files needed:**
- `tabs/Contact/contacts.csv` — Contact data
- `tabs/Contact/images/` — Platform logos (optional but recommended)

**contacts.csv format:**

```csv
platform,link,alias
Email,mailto:yourname@university.edu,yourname@university.edu
GitHub,https://github.com/yourusername,@yourusername
LinkedIn,https://linkedin.com/in/yourprofile,Your Name
Twitter,https://twitter.com/yourhandle,@yourhandle
Google Scholar,https://scholar.google.com/yourprofile,Dr. Your Name
ORCID,https://orcid.org/0000-0000-0000-0000,0000-0000-0000-0000
ResearchGate,https://www.researchgate.net/profile/Your-Name,Your Name
```

| Column     | Required | Description                                                    |
|------------|----------|----------------------------------------------------------------|
| `platform` | Yes      | Name shown as the card label; must match logo filename         |
| `link`     | Yes      | Full URL or `mailto:` address                                  |
| `alias`    | No       | Display name shown on the card; if empty, the link is shown    |

**Logo images:** Name each logo file after the platform (case-insensitive, any extension):

```
tabs/Contact/images/
├── Email.png
├── GitHub.svg
├── LinkedIn.png
├── Twitter.png
└── Google Scholar.png
```

The app automatically pairs logo files with CSV rows by matching the `platform` column.

---

## Adding New Tabs

To add a new section (e.g., "Teaching", "Media Coverage", "Blog"):

1. **Create the folder:**
   ```
   tabs/Teaching/
   ├── images/
   └── text/
   ```

2. **Add content:**
   - Create `.txt` files in `text/`
   - Add matching images in `images/`

3. **Update tab order** in `tab_order.json`:
   ```json
   ["Home", "Research Interest", "Publications", "CV Resume",
    "Achievements", "Software Expertise", "Teaching", "Contact"]
   ```

4. The new tab appears automatically in the navigation bar — no code changes needed.

---

## Tab Ordering

Edit `tab_order.json` to control the left-to-right order of tabs in the navigation:

```json
["Home", "Research Interest", "Publications", "CV Resume", "Achievements", "Software Expertise", "Contact"]
```

- Tab names must **exactly match** folder names in `tabs/`
- Tabs not listed will appear at the end (alphabetically sorted)

---

## Special Tab Names

The app recognizes certain tab names and applies special behavior:

| Folder Name(s)                        | Special Behavior                              |
|---------------------------------------|-----------------------------------------------|
| `Home`                                | Hero layout with animated profile photo       |
| `CV Resume`, `CV/Resume`, `Resume`    | Renders `.docx` file as styled web page       |
| `Contact`, `Contact Details`          | Contact grid layout; also pinned to footer    |

These are matched case-insensitively. You can rename the folder and the behavior will still apply as long as the name contains the keywords.

---

## Customization

### Changing Colors & Theme

Edit `static/css/main.css` — all colors are defined as CSS variables at the top:

```css
:root {
  --bg:          #0f0f0e;    /* Main background */
  --gold:        #c9a84c;    /* Accent color */
  --sage:        #4a6741;    /* Secondary accent */
  --text-primary: #f0ead6;  /* Main text */
  /* ... */
}
```

### Changing Fonts

The app uses Google Fonts. To change fonts, edit the `<link>` tag in `templates/base.html` and update the font variables in `main.css`:

```css
--font-display: 'Your Display Font', Georgia, serif;
--font-body:    'Your Body Font', system-ui, sans-serif;
```

### Site Title / Logo Text

Edit `templates/base.html` and find the `.nav-logo` section:

```html
<span class="logo-text">Portfolio</span>
```

Replace `Portfolio` with your name or preferred title.

---

## Production Deployment

### Using Gunicorn (recommended)

```bash
pip install gunicorn
gunicorn -w 4 -b 0.0.0.0:8000 app:app
```

### Using a systemd service

Create `/etc/systemd/system/portfolio.service`:

```ini
[Unit]
Description=Portfolio Flask App
After=network.target

[Service]
User=www-data
WorkingDirectory=/path/to/portfolio
ExecStart=/usr/local/bin/gunicorn -w 4 -b 127.0.0.1:8000 app:app
Restart=always

[Install]
WantedBy=multi-user.target
```

```bash
sudo systemctl enable portfolio
sudo systemctl start portfolio
```

### Nginx reverse proxy config

```nginx
server {
    listen 80;
    server_name yourdomain.com;

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }

    location /static {
        alias /path/to/portfolio/static;
        expires 7d;
    }
}
```

---

## Troubleshooting

| Issue | Solution |
|-------|----------|
| Tab not appearing in nav | Check folder exists in `tabs/` and name is in `tab_order.json` |
| Image not showing | Ensure filename (without extension) matches the `.txt` file stem exactly |
| CV not rendering | Confirm `mammoth` is installed (`pip install mammoth`) and `.docx` is in the tab folder (not in a subfolder) |
| Contact icons missing | Logo filename must match `platform` column in CSV (e.g., platform=`GitHub` → `GitHub.png`) |
| Font not loading | Check internet connection (Google Fonts CDN required); edit `base.html` to use local fonts if needed |

---

## File Naming Tips

- **Text files:** Prefix with numbers to control order: `01_topic.txt`, `02_topic.txt`
- **Images:** Use the same stem as the text file for automatic pairing
- **Tab folders:** Spaces are fine — the app handles URL encoding automatically
- **CSV:** Use UTF-8 encoding; wrap values with commas in double quotes

---

## Dependencies

| Package | Purpose |
|---------|---------|
| Flask   | Web framework |
| mammoth | DOCX → HTML conversion for CV page |
| Werkzeug| URL handling (included with Flask) |

Install all: `pip install -r requirements.txt`
