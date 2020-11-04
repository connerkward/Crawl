import re
import urllib.parse
from urllib.parse import urlparse
from urllib.parse import urljoin
from bs4 import BeautifulSoup
import json
import tokenizer
import ctoken
import lxml  # required for BS4
from os import path
import json_utils
import threading

# Tokenizer Select
# TOKENIZER = tokenizer.tokenize
TOKENIZER = ctoken.tokenize_page

URL_LENGTH_THRESHOLD = 100  # in blocks of url , usually around 3-5, 8
TOKEN_COUNT_THRESHOLD = 0

def scraper(url, resp) -> set:
    """
    Check for bad url or bad response, text and tokenize, update archive word frequency,
    extract links, log, return links.
    :return: a list of links
    """
    # Check for Bad Response
    if (resp.error is not None) or (400 <= resp.status <= 599) and (resp.raw_response is None): return []
    # Check for Bad URL
    if not is_valid(url): return []

    # Convert to Text-Only
    parsed_html = BeautifulSoup(resp.raw_response.text, features="lxml")

    # Tokenize
    # TODO: Discuss which tokenizer to use
    token_list = TOKENIZER(parsed_html.text, ignore_stop_words=True)
    # Filter Out Min # of Tokens
    # TODO: Discuss if there's a better way to estimate
    if len(token_list) < TOKEN_COUNT_THRESHOLD:
        print(token_list)
    if len(token_list) < TOKEN_COUNT_THRESHOLD: return []

    # Word Frequency
    # TODO: Validate
    threading.Thread(target=json_utils.archive_to_json, args=(url, token_list)).start()

    # Extract Links
    # TODO: Validate
    # with open("./Logs/URL_LOG.txt", "a+") as handle:
    #     handle.write(f"{resp.url} {len(token_list)} {len(tokenizer.compute_word_frequency(token_list))} {len(links)}\n")
    return {link for link in extract_next_links(url, resp, parsed_html) if is_valid(link)}


def extract_next_links(url, resp, parsed_html: BeautifulSoup) -> set:
    """
    Extract links from BeautifulSoup object. (currently doesn't account for dynamic web pages)
    :param parsed_html: BeautifulSoup object
    :return: list of links
    """
    link_set = set()
    # Removed BeautifulSoup object conversion from here, since it already happens in scraper().
    # Instead added BeautifulSoup object as parameter to this function.

    for link in [l.get("href") for l in parsed_html.find_all("a")]:
        # Links are often located in either "href" or "src"
        # link = link.get("href")  # if link.get("href") != None else link.get("src")

        # Not email link, not section link (#link), and is a valid_link()
        if link is not None \
                and '@' not in link \
                and "mailto" not in link \
                and "img" not in link \
                and "image" not in link \
                and "events" not in link \
                and "event" not in link \
                and "pdf" not in link \
                and "calendar" not in link \
                and is_valid(urljoin(resp.url, link)):
            # if url begins with '/', discard the path of the url and add the href path
            # if url does not begin with '/' (e.g. something.html), append it to the end of the url path (urljoin)
            # Defragment the URL
            # Remove the ?query param(s) from url
            link = urljoin(resp.url, link).split("#")[0].split("?")[0]

            """
            filter tips????:
                - Avoid excessively long urls (or maybe just really long queries)
                - Avoid paths containing 4-digits paths (e.g. .../2017/something.html)
                - Avoid path w/ pdf in path (e.g., .../pdf/InformaticsBrochure)
                - Avoid urls w/ parameters
            """

            # Look for a trap in the url (e.g., link to calendar, pdf, etc.)
            is_trap = False
            # check for very long url
            if len(link.split('/')) > URL_LENGTH_THRESHOLD:
                is_trap = True
            else:
                # check for 4 length digit block or sus keywords
                for block in [i for i in link.split('/') if i]:  # removes empty strings
                    # check for 4 length digit block
                    if (len(block) == 4) and (block.isdigit()):
                        is_trap = True
                        break
                    
                    # check for repetitive blocks
                    if link.count(block) > 1:
                        is_trap = True
                        break
                    
                    # check for sus keywords
                    if block in {"calendar", "pdf", "reply", "respond", "comment", "event", "events", "img", "image"}:
                        is_trap = True
                        break
            if is_trap: continue  # move to next for loop iteration

            link_set.add(link)
    return link_set


def is_valid(url):
    try:
        parsed = urlparse(url)

        # scheme check
        if parsed.scheme not in set(["http", "https"]):
            return False

        # valid domain check
        is_valid_domain = False
        for domain in {".ics.uci.edu", ".cs.uci.edu", "informatics.uci.edu", "stat.uci.edu",
                       "today.uci.edu/department/information_computer_sciences/"}:
            if domain in url:
                is_valid_domain = True
        if is_valid_domain == False: return False  # Keep going if in valid domain

        # file extension check
        return not re.match(
            r".*\.(css|js|bmp|gif|jpe?g|ico"
            + r"|png|tiff?|mid|mp2|mp3|mp4"
            + r"|wav|avi|mov|mpeg|ram|m4v|mkv|ogg|ogv|pdf"
            + r"|ps|eps|tex|ppt|pptx|doc|docx|xls|xlsx|names"
            + r"|data|dat|exe|bz2|tar|msi|bin|7z|psd|dmg|iso"
            + r"|epub|dll|cnf|tgz|sha1|mat|thesis"
            + r"|thmx|mso|arff|rtf|jar|csv|apk|war"
            + r"|rm|smil|wmv|swf|wma|zip|rar|gz|img"
            + r"|pdf|js|ppsx|pps)$", parsed.path.lower())
        # added img, war, apk, mat, thesis, pps

    except TypeError:
        print("TypeError for ", parsed)
        raise
