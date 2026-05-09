import requests
from bs4 import BeautifulSoup
from sqlmodel import SQLModel, create_engine, Session, select, Field
from typing import Optional, Tuple

class Bass(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str
    pickup: str
    strings: int
    frets: int
    score: int
    price: float
    image: str = ""  # Store image URL

DATABASE_URL = "sqlite:///bass.db"
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})

SQLModel.metadata.create_all(engine)


def parse_specs_text(specs_text: str) -> Tuple[str, int, int]:
    """Parse the combined specs text into pickup, strings, and frets."""
    parts = [part.strip() for part in specs_text.split("|") if part.strip()]

    pickup = parts[0] if parts else ""
    strings = 4
    frets = 20

    for part in parts:
        lower_part = part.lower()
        if "string" in lower_part:
            digits = "".join(char for char in part if char.isdigit())
            if digits:
                strings = int(digits)
        elif "fret" in lower_part:
            digits = "".join(char for char in part if char.isdigit())
            if digits:
                frets = int(digits)

    return pickup, strings, frets


def scrape_basses(url: str):
    """
    Scrape bass guitar data from the specified URL using BeautifulSoup.
    
    Args:
        url: The URL to scrape
        
    Returns:
        List of dictionaries containing bass data
    """
    try:
        print(f"Fetching {url}...")
        
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        
        print("Parsing HTML...")
        soup = BeautifulSoup(response.content, 'html.parser')
        
        basses = []
        
        # Find all card containers
        cards = soup.find_all('div', class_='image-cards')
        print(f"Found {len(cards)} cards")
        
        for card in cards:
            try:
                # Get name from div.image-cards > a > div:nth-child(1)
                name_elem = card.select_one('a > div:nth-child(1)')
                name = name_elem.text.strip() if name_elem else ""
                
                # Get specs (strings, pickup, frets) from div.image-cards > a > div:nth-child(2)
                specs_elem = card.select_one('a > div:nth-child(2)')
                specs_text = specs_elem.text.strip() if specs_elem else ""
                
                pickup, strings, frets = parse_specs_text(specs_text)
                
                # Get score from div.image-cards > div:nth-child(2) > a > div:nth-child(2) > div:nth-child(1)
                score_elem = card.select_one('div:nth-child(2) > a > div:nth-child(2) > div:nth-child(1)')
                score_text = score_elem.text.strip() if score_elem else "0"
                score = int(''.join(filter(str.isdigit, score_text))) if any(c.isdigit() for c in score_text) else 0
                
                # Get price from div.image-cards > div:nth-child(2) > a > div:nth-child(2) > div:nth-child(2)
                price_elem = card.select_one('div:nth-child(2) > a > div:nth-child(2) > div:nth-child(2)')
                price_text = price_elem.text.strip() if price_elem else "0"
                price = float(''.join(filter(lambda x: x.isdigit() or x == '.', price_text))) if any(c.isdigit() for c in price_text) else 0.0
                
                # Get image from div.image-cards > a > img:nth-child(3)
                image_elem = card.select_one('a > img:nth-child(3)')
                image = image_elem.get('src', '') if image_elem else ""
                # Convert relative URLs to absolute if needed
                if image and not image.startswith('http'):
                    image = 'https://findmyguitar.com' + image if image.startswith('/') else 'https://findmyguitar.com/' + image
                
                if name:  # Only add if we got a name
                    bass_data = {
                        "name": name,
                        "pickup": pickup,
                        "strings": strings,
                        "frets": frets,
                        "score": score,
                        "price": price,
                        "image": image
                    }
                    basses.append(bass_data)
                    print(f"Scraped: {name} | {strings} strings | {frets} frets | Score: {score} | Price: ${price} | Image: {image[:50]}...")
            except Exception as e:
                print(f"Error parsing card: {e}")
                continue
        
        return basses
    
    except requests.RequestException as e:
        print(f"Error fetching URL: {e}")
        raise

def insert_basses(basses: list):
    """
    Insert scraped bass data into the database using SQLModel.
    
    Args:
        basses: List of dictionaries containing bass data
    """
    with Session(engine) as session:
        for bass_data in basses:
            statement = select(Bass).where(Bass.name == bass_data["name"])
            existing = session.exec(statement).first()
            
            if existing:
                existing.pickup = bass_data["pickup"]
                existing.strings = bass_data["strings"]
                existing.frets = bass_data["frets"]
                existing.score = bass_data["score"]
                existing.price = bass_data["price"]
                existing.image = bass_data["image"]
                print(f"Updated database row: {bass_data['name']}")
            else:
                bass = Bass(**bass_data)
                session.add(bass)
                print(f"Added to database: {bass_data['name']}")
        
        session.commit()

def main():
    """Main function to scrape and populate database."""
    url = "https://findmyguitar.com/electric-basses/explorer.php"
    
    print("Starting bass scraper...")
    basses = scrape_basses(url)
    
    if basses:
        print(f"\nScraped {len(basses)} basses. Inserting into database...")
        insert_basses(basses)
        print("Database population complete!")
    else:
        print("No basses were scraped. Check the website structure and CSS selectors.")

if __name__ == "__main__":
    main()
