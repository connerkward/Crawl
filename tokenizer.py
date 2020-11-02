'''
@author: Amen Wondwosen
31 October 2020
'''

from bs4 import BeautifulSoup
from collections import defaultdict
import nltk
from nltk.corpus import stopwords
nltk.download('stopwords')
import re
import requests
import time


"""
Token characteristics:
	- Sequence of text between spaces
	- Can contain text blocks w/ multiple periods
	- Text blocks containing special characters not
	  separated by space(s)
"""


def tokenize(page:str) -> "list of tokens":

	token_list = []

	stop_words = stopwords.words()	# Save it here to prevent redundant calling

	compact_page = page.replace('\n', ' ').replace('\t', ' ').replace('/', ' ')

	for block in compact_page.split():
		if (re.match("[a-zA-Z0-9]", block) != None):
			block = block.strip()

			#if len
			
			# If len(alphanumeric)/len(total) is less than 25%, skip it
			if (sum((i.isalpha() or i.isdigit()) for i in block) / len(block) >= 0.25):

				#if block[0].isalpha() == False:
				#	block = block[1:]
				#if block[-1].isalpha() == False:
				#	block = block[:-1]

				if block not in stop_words: token_list.append(block)


	return token_list


def compute_word_frequency(token_list:list) -> dict:
	"""
	Given a list of tokens token_list, iterate through the
	list and add them to the dict word_counter_dict with
	the word as the key and its frequency in token_list.
	If a word exists in word_frequency_dict, increment its
	respective value by one.
	Runs linear time relative to the size of the parameter
	(O^N). Iterating through a list as well as adding to a
	dict both take linear time.
	"""

	word_counter_dict = defaultdict(int)

	### START HERE ###

	for token in token_list:
		word_counter_dict[token] += 1


	return word_counter_dict


def print_frequency(frequency_dict: dict) -> None:
	"""
	Given frequency_dict with a str key and int value,
	iterate through frequency dict and print each
	key/value pair in the format: <key> - <value>.
	Runs O(N log N) relative to the size of the
	parameter.
	"""

	for word, count in sorted(frequency_dict.items(), reverse=True, key=lambda x: x[1]):
		print(f"{word} - {count}")

	pass


#def remove_tags(text):
#    ''.join(xml.etree.ElementTree.fromstring(text).itertext())


#if __name__ == '__main__':
#
#	url = "https://www.ics.uci.edu"
#
#	print_frequency(compute_word_frequency(tokenize(url)))
