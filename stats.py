import collections
from collections import defaultdict
import json
from urllib.parse import urlparse

data = defaultdict(set)


if __name__ == '__main__':

	total_url = set()
	target_url = set()

	with open("Logs/data_17723.json", 'r') as f:
		for line in f:
			json_line = json.loads(line)
			for url in json_line.keys():
				if ".ics.uci.edu" in url: # "www.ics.uci.edu" not in url:
					target_url.add(url)
				total_url.add(url)

	for url in target_url:
		parse = urlparse(url)
		data[parse.netloc].add(url)
	tempD = collections.OrderedDict(sorted(data.items()))
	with open("subdomain_count.txt", 'w+') as handle:
		for key, value in tempD.items():
			print(key, len(value))
			handle.write(f"{key} {len(value)}\n")
