# Bass Guitar Database Project

A FastAPI application that scrapes bass guitar data using Selenium and stores it in a SQLite database using SQLModel.

## Project Structure

- `main.py` - FastAPI application with REST API endpoints
- `scraper.py` - Selenium web scraper (manual ChromeDriver setup)
- `scraper_auto.py` - Selenium web scraper (auto-managed ChromeDriver with webdriver-manager)
- `createdb.py` - Database initialization script
- `data.py` - Contains the target URL for scraping
- `requirements.txt` - Python dependencies
- `static/` - HTML, CSS, and JavaScript files for frontend

## Setup Instructions

### 1. Install Dependencies

```bash
# Install Python dependencies
pip install -r requirements.txt
```

### 2. Choose Your Scraper

**Option A: Auto-managed ChromeDriver (Recommended)**
```bash
python scraper_auto.py
```

**Option B: Manual ChromeDriver Installation**
```bash
# Install Chromium and ChromeDriver
apt-get update
apt-get install -y chromium-browser chromium-chromedriver

# Run scraper
python scraper.py
```

### 3. Initialize Database

The database is automatically created when the scraper runs. To manually initialize:
```bash
python createdb.py
```

### 4. Run the FastAPI Server

```bash
python main.py
```

The API will be available at `http://localhost:8000`

## API Endpoints

- `GET /basses` - Get all basses from the database
- `GET /basses/{bass_id}` - Get a specific bass by ID
- `GET /basses/name/{name}` - Search for basses by name

## Database Schema

The `bass` table contains:
- `id` (INTEGER, Primary Key)
- `name` (TEXT)
- `pickup` (TEXT)
- `strings` (INTEGER)
- `frets` (INTEGER)
- `score` (INTEGER)
- `price` (REAL)

## Configuration

The target URL is defined in `data.py`:
```python
url = "https://findmyguitar.com/electric-basses/explorer.php"
```

## Troubleshooting

### ChromeDriver Issues
If you encounter ChromeDriver errors, use `scraper_auto.py` instead, which automatically manages the driver.

### CSS Selector Issues
If the scraper doesn't extract data correctly, you may need to inspect the website and update the selectors in the scraper:
- Modify the table selector
- Update row/column selectors to match the actual HTML structure

### Database Locked Errors
Ensure no other processes are accessing `bass.db` when running the scraper or API.

## Future Enhancements

- Web UI for viewing and managing bass data
- Advanced filtering and sorting options
- Database migration tools
- API authentication
