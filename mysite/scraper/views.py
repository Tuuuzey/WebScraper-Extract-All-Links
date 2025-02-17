from django.shortcuts import render
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse

def main(request):
    if request.method == 'POST':
        web = request.POST.get('web', '').strip()

        if web.startswith(('https://', 'http://', 'www.')):
            urls_to_try = [web]
        else:
            urls_to_try = [f"https://{web}", f"http://{web}", f"http://www.{web}"]

        page = None
        valid_url = None

        # Try to get a valid page.
        for url in urls_to_try:
            try:
                page = requests.get(url, timeout=5)
                if page.status_code == 200:
                    valid_url = url 
                    break
            except requests.RequestException:
                continue

        if not page or page.status_code != 200:
            return render(request, 'scraper/main.html', {'error': "This page does not exist."})

        # Derive the base domain from the valid URL.
        parsed_url = urlparse(valid_url)
        base_domain = f"{parsed_url.scheme}://{parsed_url.netloc}"

        soup = BeautifulSoup(page.text, 'html.parser')
        links = {}

        # Process each link found on the page.
        for link in soup.find_all('a'):
            href = link.get('href')
            if href:
                # If the link is relative (doesn't start with http:// or https://),
                # fix it by joining with the base domain.
                if not href.startswith(('http://', 'https://')):
                    fixed_href = urljoin(base_domain, href)
                else:
                    fixed_href = href

                # Even if the link does not start with the base, we keep it (fixed if relative).
                links[link.string] = fixed_href

        return render(request, 'scraper/main.html', {'links': links})

    return render(request, 'scraper/main.html')
