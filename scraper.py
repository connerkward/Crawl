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

# Tokenizer Select
# TOKENIZER = tokenizer.tokenize
TOKENIZER = ctoken.tokenize_page


def archive(token_list, json_path="data.json") -> dict:
    """
    Convert token_list to Word Frequency, save to JSON as {word: count}
    :return: returns the word_freqs for this token_list
    """
    # Generate Word Frequencies
    word_freqs = ctoken.computeWordFrequencies(token_list)
    # Write to JSON
    if path.exists(json_path):
        with open(json_path, 'r', encoding='utf-8') as file:
            json_word_freqs = json.load(file)
            for json_key in json_word_freqs.keys():
                if json_key in word_freqs.keys():
                    word_freqs[json_key] += json_word_freqs[json_key]
                else:
                    word_freqs[json_key] = 1
        with open(json_path, 'w', encoding='utf-8') as file:
            json.dump(word_freqs, file, ensure_ascii=True, indent=4)
    else:
        with open(json_path, 'w', encoding='utf-8') as file:
            json.dump(word_freqs, file, ensure_ascii=True, indent=4)
    return word_freqs


def scraper(url, resp) -> list:
    """
    Check for bad url or bad response, text and tokenize, update archive word frequency,
    extract links, log, return links.
    :return: a list of links
    """
    # Check for Bad Response
    if (resp.error is not None) or (400 <= resp.status <= 499) and (resp.raw_response is None): return []
    # Check for Bad URL
    if not is_valid(url): return []

    # Convert to Text-Only
    parsed_html = BeautifulSoup(resp.raw_response.text, features="lxml")
    page_text = parsed_html.text

    # Tokenize
    # TODO: Discuss which tokenizer to use
    token_list = TOKENIZER(page_text, ignore_stop_words=True)

    # Filter Out Min # of Tokens
    # TODO: Discuss if there's a better way to estimate
    if len(token_list) < 200: return []

    # Word Frequency
    # TODO: Validate
    archive(token_list)

    # Extract Links
    # TODO: Validate
    links = extract_next_links(url, resp, parsed_html)

    # Log
    with open("./Logs/URL_LOG.txt", "a+") as handle:
        handle.write(f"{resp.url} {len(token_list)} {len(tokenizer.compute_word_frequency(token_list))} {len(links)}\n")

    return [link for link in links if is_valid(link)]


def extract_next_links(url, resp, parsed_html: BeautifulSoup) -> "list of links":
    """
    Extract links from BeautifulSoup object.
    :param parsed_html: BeautifulSoup object
    :return: list of links
    """
    link_set = set()
    # Removed BeautifulSoup object conversion from here, since it already happens in scraper().
    # Instead added BeautifulSoup object as parameter to this function.
    # CONNER: I have not looked at or changed rest of function

    # (currently doesn't account for dynamic webpages)
    for link in parsed_html.find_all("a"):
        # Links are often located in either "href" or "src"
        link = link.get("href")  # if link.get("href") != None else link.get("src")

        if (link != None) and not (link in ['#', '@']) and ("mailto" not in link):

            ### SET ADDITIONAL CHECKS/FILTERS HERE ###
            # if url begins with '/', discard the path of the url and add the href path
            # if url does not begin with '/' (e.g. something.html), append it to the end of the url path
            link = urljoin(resp.url, link)

            """
            filter tips????:
                - Avoid excessively long urls (or maybe just really long queries)
                - Avoid paths containing 4-digits paths (e.g. .../2017/something.html)
                - Avoid path w/ pdf in path (e.g., .../pdf/InformaticsBrochure)
                - Avoid urls w/ parameters
            
            - Defrag the url (remove the fragment part)
            """

            # Look for a trap in the url (e.g., link to calendar, pdf, etc.)
            is_trap = False
            for block in link.split('/'):
                if ((len(block) == 4) and (block.isdigit()) or (link.split('/').count(block) > 2)):
                    is_trap = True
                    break
                # Look for common words located in url traps
                for trap in {"calendar", "pdf", "reply", "respond", "comment"}:
                    if trap in block:
                        is_trap = True
                        break

            if is_trap: continue

            # print(link.split('/'))

            link = link.split("#")[0]  # Defrag the url

            # Remove the query param(s) from url
            link = link[:link.find('?')]

            # print(url.strip())
            link_set.add(link.lstrip().strip())
    return link_set


def is_valid(url):
    # CONNER: I have not looked at or changed this function
    try:
        parsed = urlparse(url)
        if parsed.scheme not in set(["http", "https"]):
            return False

        # Check against 
        is_valid_domain = False
        for domain in {".ics.uci.edu", ".cs.uci.edu", "informatics.uci.edu", "stat.uci.edu",
                       "today.uci.edu/department/information_computer_sciences/"}:
            if domain in url:
                is_valid_domain = True
        if is_valid_domain == False: return False  # Keep going if in valid domain

        # seed_domain_list = ["ics.uci.edu/", "cs.uci.edu", "informatics.uci.edu","stat.uci.edu/", "today.uci.edu/department/information_computer_sciences/"]
        # if

        return not re.match(
            r".*\.(css|js|bmp|gif|jpe?g|ico"
            + r"|png|tiff?|mid|mp2|mp3|mp4"
            + r"|wav|avi|mov|mpeg|ram|m4v|mkv|ogg|ogv|pdf"
            + r"|ps|eps|tex|ppt|pptx|doc|docx|xls|xlsx|names"
            + r"|data|dat|exe|bz2|tar|msi|bin|7z|psd|dmg|iso"
            + r"|epub|dll|cnf|tgz|sha1"
            + r"|thmx|mso|arff|rtf|jar|csv"
            + r"|rm|smil|wmv|swf|wma|zip|rar|gz"
            + r"|pdf|js|ppsx)$", parsed.path.lower())

    except TypeError:
        print("TypeError for ", parsed)
        raise
