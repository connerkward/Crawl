import sys
import re
from collections import defaultdict

STOP_WORDS = ['a', 'about', 'above', 'after', 'again', 'against', 'all', 'am', 'an', 'and', 'any', 'are', "aren't",
              'as', 'at', 'be', 'because', 'been', 'before', 'being', 'below', 'between', 'both', 'but', 'by', "can't",
              'cannot', 'could', "couldn't", 'did', "didn't", 'do', 'does', "doesn't", 'doing', "don't", 'down',
              'during', 'each', 'few', 'for', 'from', 'further', 'had', "hadn't", 'has', "hasn't", 'have', "haven't",
              'having', 'he', "he'd", "he'll", "he's", 'her', 'here', "here's", 'hers', 'herself', 'him', 'himself',
              'his', 'how', "how's", 'i', "i'd", "i'll", "i'm", "i've", 'if', 'in', 'into', 'is', "isn't", 'it', "it's",
              'its', 'itself', "let's", 'me', 'more', 'most', "mustn't", 'my', 'myself', 'no', 'nor', 'not', 'of',
              'off', 'on', 'once', 'only', 'or', 'other', 'ought', 'our', 'ours\tourselves', 'out', 'over', 'own',
              'same', "shan't", 'she', "she'd", "she'll", "she's", 'should', "shouldn't", 'so', 'some', 'such', 'than',
              'that', "that's", 'the', 'their', 'theirs', 'them', 'themselves', 'then', 'there', "there's", 'these',
              'they', "they'd", "they'll", "they're", "they've", 'this', 'those', 'through', 'to', 'too', 'under',
              'until', 'up', 'very', 'was', "wasn't", 'we', "we'd", "we'll", "we're", "we've", 'were', "weren't",
              'what', "what's", 'when', "when's", 'where', "where's", 'which', 'while', 'who', "who's", 'whom', 'why',
              "why's", 'with', "won't", 'would', "wouldn't", 'you', "you'd", "you'll", "you're", "you've", 'your',
              'yours', 'yourself', 'yourselves']

# @ and $ are excluded from TABLE because they add important context to numbers and email addresses, respectively
TABLE2 = str.maketrans('', '', "[]^_`{|}~?<=>*+#%!;[]:\'\",.()_”“‘’")


def tokenize_page(page_text: str, ignore_stop_words: bool = False):
    page_text = page_text.replace('\n', ' ').replace('\t', ' ').replace('/', ' ')
    return tokenize_line(page_text, ignore_stop_words)


def tokenize_line(line: str, ignore_stop_words: bool = False) -> list:
    tokenlist = list()
    for word in line.lower().translate(TABLE2).split():
        # above removes characters that would be inside a token
        # such as the ' in "won't" or periods in "www.google.com"
        # then splits into list of words
        # lower:O(N) + translate:O(N) + split:O(N) + forloop:O(N) = O(4N) = O(N)
        wordlist = re.split('/|-|&', word)  # for splitting archaic dashed and slashed words like "fire-wood"
        if len(wordlist) > 1:
            for w in wordlist:  # O(N)
                if w is not "":
                    try:
                        tokenlist.append(word.encode("ascii").decode())
                    except UnicodeEncodeError:  # for handling bad characters in words
                        pass
        else:
            try:
                tokenlist.append(word.encode("ascii").decode())
            except UnicodeEncodeError:  # for handling bad characters in word
                pass
    if ignore_stop_words:
        # remove_list = list()
        # with open("stopwords.txt") as file:
        #     for word in file:
        #         remove_list.append(word.strip("\n"))
        # print(remove_list)
        tokenlist = [word for word in tokenlist if word not in STOP_WORDS]
    return tokenlist


def tokenize_file(text_file_path) -> list:
    # tokenize() reads characters from ASCII and its superset UTF-8 encoded files only
    # O(N) because despite nested for loops, as there is only N words ever visited
    tokenlist = list()
    try:
        with open(text_file_path, encoding="utf-8-sig") as file:
            for line in file:  # O(N)
                [tokenlist.append(token) for token in tokenize_line(line)]
        return tokenlist
    except UnicodeDecodeError:  # for handling bad file encoding input
        return tokenlist
    except FileNotFoundError:  # for handling bad command line/file input
        return tokenlist


def computeWordFrequencies(tokenlist: list) -> dict:
    # O(N) Time Complexity, because worst case each word in for loop is visited once.
    tokencount = defaultdict(int)  # str: int
    if tokenlist is not None:
        for word in tokenlist:
            tokencount[word] += 1
    return tokencount


def intersection(l1, l2):
    # Pattern from
    # https://www.geeksforgeeks.org/python-intersection-two-lists/
    # O(N) because for each N word, only visited once
    l3 = [value for value in l1 if value in l2]
    return l3


def _print(tokencount: dict):
    # O(n log n) Time Complexity, because worst case for for-loop is O(N), however
    # has 'sorted' which runs at O(n log n), thus O(N LOG N)+ O(N)  = 2N LOG N or N LOG N
    for pair in sorted(tokencount.items(), reverse=True, key=lambda x: x[1]):
        print(f"{pair[0]}-{pair[1]}")


if __name__ == "__main__":
    # start = timeit.default_timer()
    _print(computeWordFrequencies(tokenize_file(str(sys.argv[1]))))
    # stop = timeit.default_timer()
    # print('Time: ', stop - start)
