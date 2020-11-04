import ctoken
from os import path
import json
import numpy as np

DEFAULT_JSON_PATH = "data.json"

def archive_to_json(url, token_list, json_path=DEFAULT_JSON_PATH) -> dict:
    """
    Convert token_list to Word Frequency, save to JSON as {word: count}
    :return: returns the word_freqs for this token_list
    """
    # Generate Word Frequencies
    word_freqs = ctoken.computeWordFrequencies(token_list)
    # Write to JSON
    if path.exists(json_path):
        with open(json_path, 'r', encoding='utf-8') as file:
            json_dict = json.load(file)
            # print(json_dict.keys())
        if json_dict[url]:
            # merge existing
            json_word_freqs = json_dict[url]
            for json_key in json_word_freqs.keys():
                if json_key in word_freqs.keys():
                    word_freqs[json_key] += json_word_freqs[json_key]
        else:  # url not in data
            json_dict[url] = word_freqs
        with open(json_path, 'w', encoding='utf-8') as file:
            json.dump(json_dict, file, ensure_ascii=True, indent=4)
    else:
        with open(json_path, 'w', encoding='utf-8') as file:
            json.dump({url:word_freqs}, file, ensure_ascii=True, indent=4)
    return word_freqs


def compute_token_count(token_dict):
    """Computes token count for single token dict"""
    return sum([token_dict[key] for key in token_dict.keys()])


def compute_all_token_counts(json_path=DEFAULT_JSON_PATH):
    """Computes token counts for entire json file, returns {url: token_count}"""
    token_counts = {}  # {url: token_count}
    with open(json_path, 'r', encoding='utf-8') as file:
        json_dict = json.load(file)
        for url in json_dict.keys():
            token_counts[url] = compute_token_count(json_dict[url])
    return token_counts


def compute_all_block_lengths(json_path=DEFAULT_JSON_PATH):
    """Computes token counts for entire json file, returns {url: token_count}"""
    block_lengths = {}  # {url: token_count}
    with open(json_path, 'r', encoding='utf-8') as file:
        json_dict = json.load(file)
        for url in json_dict.keys():
            block_lengths[url] = len([i for i in url.split('/') if i])
    return block_lengths


def compute_quartiles(counts_dict):
    """Returns Q1 and Q3 from {key:int} dictionary"""
    # from https://www.geeksforgeeks.org/interquartile-range-and-quartile-deviation-using-numpy-and-scipy/
    q1 = np.percentile(counts_dict.values(), 25, interpolation='midpoint')
    # Third quartile (Q3)
    q3 = np.percentile(counts_dict.values(), 75, interpolation='midpoint')
    return q1, q3


def compute_optimal_block_maximum(json_path=DEFAULT_JSON_PATH) -> int:
    """Returns upper threshold for outlier blocks"""
    block_counts = compute_all_block_lengths(json_path)  # {url: block length}
    q1, q3 = compute_quartiles(block_counts)
    iqr = q3 - q1
    high_threshold = q3 + 1.5 * iqr
    return high_threshold


def compute_optimal_token_minimum(json_path=DEFAULT_JSON_PATH) -> int:
    """Returns lower threshold for outlier tokens"""
    token_counts = compute_all_token_counts(json_path)  # {url: token_count}
    q1, q3 = compute_quartiles(token_counts)
    iqr = q3 - q1
    low_threshold = q1 - 1.5 * iqr
    return low_threshold


def outliers(json_path=DEFAULT_JSON_PATH, high=True, low=True) -> dict:
    """Returns a dict containing outlier {url: int} pairs"""
    token_counts = compute_all_token_counts(json_path)  # {url: token_count}
    q1, q3 = compute_quartiles(token_counts)
    iqr = q3 - q1
    high_threshold = q3 + 1.5 * iqr
    low_threshold = q1 - 1.5 * iqr
    if high and low:
        return {url: token_counts[url] for url in token_counts.keys()
                if low_threshold > token_counts[url] > high_threshold}
    elif high:
        return {url: token_counts[url] for url in token_counts.keys()
                if token_counts[url] > high_threshold}
    elif low:
        return {url: token_counts[url] for url in token_counts.keys()
                if token_counts[url] < low_threshold}
    else:
        return {}

if __name__ == "__main__":
    print("block max:", compute_optimal_block_maximum())
    print("token min:", compute_optimal_token_minimum())