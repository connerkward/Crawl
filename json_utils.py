import ctoken
from os import path
import json
import numpy as np
from matplotlib import pyplot as plt

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
        try:
            # merge existing
            json_word_freqs = json_dict[url]
            for json_key in json_word_freqs.keys():
                if json_key in word_freqs.keys():
                    word_freqs[json_key] += json_word_freqs[json_key]
        except KeyError:
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


def token_count_dict(json_path=DEFAULT_JSON_PATH) -> dict:
    """Computes token counts for entire json file, returns {url: token_count}"""
    token_counts = {}  # {url: token_count}
    with open(json_path, 'r', encoding='utf-8') as file:
        json_dict = json.load(file)
        for url in json_dict.keys():
            token_counts[url] = compute_token_count(json_dict[url])
    return token_counts


def block_lengths_dict(json_path=DEFAULT_JSON_PATH) -> dict:
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
    q1 = np.percentile(list(counts_dict.values()), 25, interpolation='midpoint')
    # Third quartile (Q3)
    q3 = np.percentile(list(counts_dict.values()), 75, interpolation='midpoint')
    return q1, q3


def compute_optimal_block_maximum(json_path=DEFAULT_JSON_PATH) -> int:
    """Returns upper threshold for outlier blocks"""
    block_counts = block_lengths_dict(json_path)  # {url: block length}
    q1, q3 = compute_quartiles(block_counts)
    iqr = q3 - q1
    high_threshold = q3 + 1.5 * iqr
    return high_threshold


def compute_optimal_token_minimum(json_path=DEFAULT_JSON_PATH) -> int:
    """Returns lower threshold for outlier tokens"""
    token_counts = token_count_dict(json_path)  # {url: token_count}
    q1, q3 = compute_quartiles(token_counts)
    iqr = q3 - q1
    low_threshold = q1 - 1.5 * iqr
    return low_threshold


def token_outliers(json_path=DEFAULT_JSON_PATH, high=True, low=True) -> dict:
    """Returns a dict containing outlier {url: int} pairs"""
    token_counts = token_count_dict(json_path)  # {url: token_count}
    q1, q3 = compute_quartiles(token_counts)
    iqr = q3 - q1
    high_threshold = q3 + 1.5 * iqr
    low_threshold = q1 - 1.5 * iqr
    #print("token outlier thresholds: ", low_threshold, high_threshold)

    if high and low:
        return {url: token_counts[url] for url in token_counts.keys()
                if not low_threshold < token_counts[url] < high_threshold}
    elif high:
        return {url: token_counts[url] for url in token_counts.keys()
                if not token_counts[url] > high_threshold}
    elif low:
        return {url: token_counts[url] for url in token_counts.keys()
                if not token_counts[url] < low_threshold}
    else:
        return {}

def block_outliers(json_path=DEFAULT_JSON_PATH, high=True, low=True) -> dict:
    """Returns a dict containing outlier {url: int} pairs"""
    block_counts = block_lengths_dict(json_path)  # {url: token_count}
    q1, q3 = compute_quartiles(block_counts)
    iqr = q3 - q1
    high_threshold = q3 + 1.5 * iqr
    low_threshold = q1 - 1.5 * iqr
    #print("block outlier thresholds: ", low_threshold, high_threshold)
    if high and low:
        return {url: block_counts[url] for url in block_counts.keys()
                if not low_threshold < block_counts[url] < high_threshold}
    elif high:
        return {url: block_counts[url] for url in block_counts.keys()
                if not block_counts[url] > high_threshold}
    elif low:
        return {url: block_counts[url] for url in block_counts.keys()
                if not block_counts[url] < low_threshold}
    else:
        return {}


if __name__ == "__main__":
    t_dict = token_count_dict()
    t_outliers = token_outliers()

    b_dict = block_lengths_dict()
    b_outliers = block_outliers()

    print("token quartiles:", compute_quartiles(token_count_dict()))
    print("block quartiles:", compute_quartiles(block_lengths_dict()))

    # token_count_dict with outliers removed
    #x = {key: int(t_dict[key]) for key in t_dict if key not in t_outliers}
    # token_count_dict with outliers removed
    #y = {key: int(b_dict[key]) for key in b_dict if key not in b_outliers}
    # print("token quartiles w/ outliers removed:", compute_quartiles(x))
    # print("block quartiles w/ outliers removed:", compute_quartiles(y))

    x = t_dict
    y = b_dict
    print(len(t_dict))
    print(len(b_dict))
    merge = {key: (y[key], x[key]) for key in x.keys()
                    if key not in block_outliers() and key not in token_outliers()}
    print(merge)
    # token_count_dict with outliers removed
    #x = {key: int(t_dict[key]) for key in t_dict if key not in t_outliers}
    # token_count_dict with outliers removed
    #y = {key: int(b_dict[key]) for key in b_dict if key not in b_outliers}

    # t_mean = np.mean(list(x.values()))
    # b_mean = np.mean(list(y.values()))
    # print(f"token mean: {t_mean}")
    # print(f"block mean: {b_mean}")

    plt.xlabel("tokens")
    plt.boxplot([i[1] for i in merge], vert=False)
    plt.savefig("token-boxplot.jpg")
    plt.close()
    plt.xlabel("blocks")
    plt.boxplot([i[0] for i in merge],vert=False)
    plt.savefig("blocks-boxplot.jpg")
    plt.close()
    #plt.ylabel("token length")
    #plt.xlabel("block length")
    #plt.bar([i[0] for i in merge], [i[1] for i in merge])
    #plt.savefig("token-block-scatter.jpg")
    #plt.close()
