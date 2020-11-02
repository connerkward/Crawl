import re
import urllib.parse
from urllib.parse import urlparse
from urllib.parse import urljoin

from bs4 import BeautifulSoup
import json
import requests
import tokenizer



def scraper(url, resp):
    links = extract_next_links(url, resp)
    return [link for link in links if is_valid(link)]

def extract_next_links(url, resp):
    # Implementation requred.

    link_set = set()


    if (resp.raw_response == None) and (resp.error != None) or (400 <= resp.status <= 499): return link_set

    #page = requests.get(url)
    #print(resp.raw_response.text)
    if not resp.raw_response: return link_set
    soup = BeautifulSoup(resp.raw_response.text, features="lxml")
    page_text = soup.text   # html doc stripped of html tags


    # Tokenize page_text and if len(token_list) does not reach a certain threshold, skip page
    token_list = tokenizer.tokenize(page_text)
    if len(token_list) < 200: return link_set
    #print(len(token_list))

    ### FIND A WAY TO STRIP HTML DOC OF HTML MARKUPS AND TOKENIZE WORDS GATHERED IN DICT W/ WORD COUNT IN DOC ###
    ### WILL EVENTUALLY ENCOMPASS TOKENS/WORDS FROM ENTIRE SET OF PAGES ###

    #with open("./Logs/URL_LOG.txt", "a") as log:
        
    # get all urls (currently doesn't account for dynamic webpages)
    for link in soup.find_all("a"):
        # Links are often located in either "href" or "src"
        link = link.get("href")# if link.get("href") != None else link.get("src")

        if (link != None) and not(link in ['#', '@']) and ("mailto" not in link):

            ### SET ADDITIONAL CHECKS/FILTERS HERE ###
            #if url begins with '/', discard the path of the url and add the href path
            #if url does not begin with '/' (e.g. something.html), append it to the end of the url path
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
            
            #print(link.split('/'))

            link = link.split("#")[0]  # Defrag the url

            # If url query is more than 50 characters, skip it
            #if url.rsplit('/'.)

            #print(url.strip())
            link_set.add(link.lstrip().strip())

    with open("./Logs/URL_LOG.txt", "a+") as handle:
        handle.write(f"{resp.url} {len(token_list)} {len(tokenizer.compute_word_frequency(token_list))} {len(link_set)}\n")

    return link_set

def is_valid(url):
    try:
        parsed = urlparse(url)
        if parsed.scheme not in set(["http", "https"]):
            return False

        # Check against 
        is_valid_domain = False
        for domain in {".ics.uci.edu", ".cs.uci.edu", "informatics.uci.edu","stat.uci.edu", "today.uci.edu/department/information_computer_sciences/"}:
            if domain in url:
                is_valid_domain = True
        if is_valid_domain == False: return False   # Keep going if in valid domain

        #seed_domain_list = ["ics.uci.edu/", "cs.uci.edu", "informatics.uci.edu","stat.uci.edu/", "today.uci.edu/department/information_computer_sciences/"]
        #if 

        return not re.match(
            r".*\.(css|js|bmp|gif|jpe?g|ico"
            + r"|png|tiff?|mid|mp2|mp3|mp4"
            + r"|wav|avi|mov|mpeg|ram|m4v|mkv|ogg|ogv|pdf"
            + r"|ps|eps|tex|ppt|pptx|doc|docx|xls|xlsx|names"
            + r"|data|dat|exe|bz2|tar|msi|bin|7z|psd|dmg|iso"
            + r"|epub|dll|cnf|tgz|sha1"
            + r"|thmx|mso|arff|rtf|jar|csv"
            + r"|rm|smil|wmv|swf|wma|zip|rar|gz"
            + r"|pdf|js)$", parsed.path.lower())

    except TypeError:
        print ("TypeError for ", parsed)
        raise