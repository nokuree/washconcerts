import json
from flask import Flask, render_template, request, jsonify
from requests_html import HTMLSession
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

# This dictionary will store concerts by city
venue_dict = {}

# Define the base URL for scraping
base_url = "https://www.jambase.com/concerts/us/washington/page/"


def format_date(date):
    if len(date) == 8:
        year = date[2:4]
        month = date[4:6]
        day = date[6:8]
        return f"{month}-{day}-{year}"
    return date


for page in range(1, 22):
    url = base_url + str(page)
    session = HTMLSession()
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

        # Extracting the city from the 'addressLocality' field
        locality_script = node.find('script[type="application/ld+json"]', first=True)
        city = "Unknown City"
        if locality_script:
            event_data = locality_script.text
            event_json = json.loads(event_data)
            city = event_json.get('location', {}).get('address', {}).get('addressLocality', 'Unknown City')

        date = node.attrs.get('data-date', 'Unknown Date')
        formatted_date = format_date(date)

        # Save the concert data in a dictionary with the city as the key
        concert_info = f"Concert: {concert_name}, Date: {formatted_date}, Venue: {venue}, City: {city}"
        if city.lower().strip() not in venue_dict:
            venue_dict[city.lower().strip()] = []

        venue_dict[city.lower().strip()].append(concert_info)
        
        print(f"Stored Concert: {concert_info} in {city}")

    print(f"Finished scraping and saving data for page {page}.\n\n")



# Flask route to handle user input and filter concerts by city
@app.route('/api/concerts', methods=['POST'])
def search_concerts():
    city_input = request.json.get('city', '').lower().strip()
    concerts = venue_dict.get(city_input, [])
    return jsonify({'concerts': concerts})


if __name__ == '__main__':
    app.run(debug=True)