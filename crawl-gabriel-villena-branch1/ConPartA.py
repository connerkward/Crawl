import sys
import re
from collections import defaultdict

# @ and $ are excluded from TABLE because they add important context to numbers and email addresses, respectively
TABLE2 = str.maketrans('', '', "[]^_`{|}~?<=>*+#%!;[]:\'\",.()_”“‘’")


def tokenize(text_file_path) -> list:
    # tokenize() reads characters from ASCII and its superset UTF-8 encoded files only
    # O(N) because despite nested for loops, as there is only N words ever visited
    tokenlist = list()
    try:
        with open(text_file_path, encoding="utf-8-sig") as file:
            for line in file:  # O(N)
                for word in line.lower().translate(TABLE2).split():
                    # translate removes characters that would be inside a token such as "won't" or "www.google.com"
                    # lower:O(N) + translate:O(N) + split:O(N) + forloop:O(N) = O(4N) = O(N)
                    wordlist = re.split('/|-|&', word) # for splitting archaic dashed and slashed words like "fire-wood"
                    if len(wordlist) > 1:
                        for elem in wordlist:  # O(N)
                            if elem is not "":
                                try:
                                    tokenlist.append(elem.encode("ascii").decode())
                                except UnicodeEncodeError:  # for handling bad characters in words
                                    pass
                    else:
                        try:
                            tokenlist.append(word.encode("ascii").decode())
                        except UnicodeEncodeError:  # for handling bad characters in word
                            pass
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


def _print(tokencount: dict):
    # O(n log n) Time Complexity, because worst case for for-loop is O(N), however
    # has 'sorted' which runs at O(n log n), thus O(N LOG N)+ O(N)  = 2N LOG N or N LOG N
    for pair in sorted(tokencount.items(), reverse=True, key=lambda x: x[1]):
        print(f"{pair[0]}-{pair[1]}")


if __name__ == "__main__":
    # start = timeit.default_timer()
    _print(computeWordFrequencies(tokenize(str(sys.argv[1]))))
    # stop = timeit.default_timer()
    # print('Time: ', stop - start)
