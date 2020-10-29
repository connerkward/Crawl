import PartA
import sys


def intersection(l1, l2):
    # Pattern from
    # https://www.geeksforgeeks.org/python-intersection-two-lists/
    # O(N) because for each N word, only visited once
    l3 = [value for value in l1 if value in l2]
    return l3

if __name__ == "__main__":
    # O(N) because first tokenize is O(N) + second tokenize O(N) + intersection O(N) = O(3N) or O(N)
    try:
        print(len(set(PartA.tokenize(str(sys.argv[1]))).intersection(set(PartA.tokenize(str(sys.argv[2]))))))
    except IndexError: # for handling bad command line input
        pass