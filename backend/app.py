import json
import asyncio
import aiohttp
from flask import Flask, render_template, request
from requests_html import AsyncHTMLSession

app = Flask(__name__)

venue_dict = {}
base_url = "https://www.jambase.com/concerts/us/washington/page/"


def format_date(date):
    if len(date) == 8:
        year = date[2:4]
        month = date[4:6]
        day = date[6:8]
        return f"{month}-{day}-{year}"
    return date


async def fetch_page(session, url):
    async with session.get(url) as response:
        return await response.text()


async def scrape_concerts():
    async with aiohttp.ClientSession() as session:
        tasks = []
        for page in range(1, 16):
            url = base_url + str(page)
            tasks.append(fetch_page(session, url))

        pages = await asyncio.gather(*tasks)

        for page_content in pages:
            asession = AsyncHTMLSession()
            response = await asession.create_response(page_content)

            concert_nodes = response.html.find('.jbshow')

            if not concert_nodes:
                continue

            for node in concert_nodes:
                title_node = node.find('.concert-title a', first=True)
                concert_name = title_node.text.strip() if title_node else "Unknown Concert"

                venue_node = node.find('.venue-name', first=True)
                venue = venue_node.text.strip() if venue_node else "Unknown Venue"

                locality_script = node.find('script[type="application/ld+json"]', first=True)
                city = "Unknown City"
                if locality_script:
                    event_data = locality_script.text
                    event_json = json.loads(event_data)
                    city = event_json.get('location', {}).get('address', {}).get('addressLocality', 'Unknown City')

                date = node.attrs.get('data-date', 'Unknown Date')
                formatted_date = format_date(date)

                concert_info = f"Concert: {concert_name}, Date: {formatted_date}, Venue: {venue}, City: {city}"
                if city.lower().strip() not in venue_dict:
                    venue_dict[city.lower().strip()] = []

                venue_dict[city.lower().strip()].append(concert_info)

                print(f"Stored Concert: {concert_info} in {city}")

        print("Finished scraping and saving data.\n\n")


@app.route('/', methods=['GET', 'POST'])
def home():
    concerts = []

    if request.method == 'POST':
        city_input = request.form.get('city', '').lower().strip()

        if city_input in venue_dict:
            concerts = venue_dict[city_input]

    return render_template('index.html', concerts=concerts)


if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    loop.run_until_complete(scrape_concerts())
    app.run(debug=True)

