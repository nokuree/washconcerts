from flask import Flask, render_template, request
from requests_html import HTMLSession
from lxml.html.clean import Cleaner


app = Flask(__name__)

def scrape_concerts():
    base_url = "https://www.jambase.com/concerts/us/washington/page/"
    venue_dict = {}

    session = HTMLSession()

    for page in range(1, 16):
        url = base_url + str(page)
        response = session.get(url)
        concert_nodes = response.html.find('.jbshow')

        if not concert_nodes:
            print(f"No concert data found on page {page}.")
            continue

        for node in concert_nodes:
            title_node = node.find('.concert-title a', first=True)
            concert_name = title_node.text.strip() if title_node else "Unknown Concert"

            venue_node = node.find('.venue-name', first=True)
            venue = venue_node.text.strip() if venue_node else "Unknown Venue"

            normalized_venue = venue.lower().strip()

            location_node = node.find('.venue-address-simple span', first=True)
            location = location_node.text.strip() if location_node else "Unknown Location"

            date = node.attrs.get('data-date', 'Unknown Date')
            formatted_date = format_date(date)

            if normalized_venue not in venue_dict:
                venue_dict[normalized_venue] = []

            venue_dict[normalized_venue].append(f"Concert: {concert_name}, Date: {formatted_date}, Location: {venue}")

            print(f"Stored Venue: {normalized_venue}")

        print(f"Finished scraping page {page}.\n\n")

    return venue_dict

def format_date(date):
    if len(date) == 8:
        year = date[2:4]
        month = date[4:6]
        day = date[6:8]
        return f"{month}-{day}-{year}"
    return date

@app.route('/', methods=['GET', 'POST'])
def home():
    venue_dict = scrape_concerts()
    concerts = []

    if request.method == 'POST':
        venue_input = request.form.get('venue', '').lower().strip()
        for venue, concert_list in venue_dict.items():
            if venue_input in venue:
                concerts.extend(concert_list)
    
        if venue_input == "spokane":
            concerts.extend(venue_dict.get("knitting factory concert house", []))
            # concerts.extend(venue_dict.get("spokane", []))

    return render_template('index.html', concerts=concerts)

if __name__ == '__main__':
    app.run(debug=True)
