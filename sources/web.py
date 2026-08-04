import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse


HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (compatible; ScholarshipHub/1.0; "
        "+https://github.com/nobelncc/scholarship-hub)"
    )
}


def fetch_html(url):
    response = requests.get(
        url,
        headers=HEADERS,
        timeout=30,
        allow_redirects=True
    )

    response.raise_for_status()
    return response.text


def html_to_text(html):
    soup = BeautifulSoup(html, "html.parser")

    for element in soup(
        ["script", "style", "noscript", "svg"]
    ):
        element.decompose()

    return soup.get_text(
        "\n",
        strip=True
    )


def fetch_page(url):
    html = fetch_html(url)
    return html_to_text(html)


def extract_links(url):
    """
    Return useful same-domain links from a page.
    """

    html = fetch_html(url)
    soup = BeautifulSoup(html, "html.parser")

    base_domain = urlparse(url).netloc

    links = []

    for a in soup.find_all("a", href=True):

        href = urljoin(url, a["href"])
        text = a.get_text(" ", strip=True)

        parsed = urlparse(href)

        if parsed.netloc != base_domain:
            continue

        if not text:
            continue

        links.append({
            "url": href,
            "text": text
        })

    # Remove duplicates
    unique = {}
    for item in links:
        unique[item["url"]] = item

    return list(unique.values())


def relevant_links(links):
    """
    Keep links likely to lead to scholarship/funding opportunities.
    """

    keywords = [
        "scholarship",
        "scholarships",
        "funding",
        "fellowship",
        "fellowships",
        "grant",
        "grants",
        "award",
        "awards",
        "studentship",
        "studentships",
        "financial aid",
        "funded",
        "funding opportunity"
    ]

    result = []

    for item in links:

        combined = (
            item["text"] + " " + item["url"]
        ).lower()

        if any(
            keyword in combined
            for keyword in keywords
        ):
            result.append(item)

    return result
