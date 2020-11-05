import ctoken
from os import path
import json
import numpy as np
from matplotlib import pyplot as plt
import json_lines

DEFAULT_JSON_PATH = "data.json"

def archive_json_lines(url, token_list, jsonline_path=DEFAULT_JSON_PATH):
    word_freqs = ctoken.computeWordFrequencies(token_list)
    with open(jsonline_path, "a", encoding='utf-8') as f:
        json_record = json.dumps({url: word_freqs}, ensure_ascii=False)
        f.write(json_record + '\n')

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
    with open(DEFAULT_JSON_PATH, 'rb') as f:
        for line in json_lines.reader(f):
            json_dict = line
            for url in json_dict.keys():
                token_counts[url] = compute_token_count(json_dict[url])
    return token_counts


def block_lengths_dict(json_path=DEFAULT_JSON_PATH) -> dict:
    """Computes token counts for entire json file, returns {url: token_count}"""
    block_lengths = {}  # {url: token_count}
    with open(DEFAULT_JSON_PATH, 'rb') as f:
        for line in json_lines.reader(f):
            json_dict = line
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


def compute_optimal_block_maximum(block_counts) -> int:
    """Returns upper threshold for outlier blocks"""
    q1, q3 = compute_quartiles(block_counts)
    iqr = q3 - q1
    high_threshold = q3 + 1.5 * iqr
    return high_threshold


def compute_optimal_token_minimum(token_counts) -> int:
    """Returns lower threshold for outlier tokens"""
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

    if high and low:
        return {url: token_counts[url] for url in token_counts.keys()
                if not low_threshold < token_counts[url] < high_threshold}
    elif high:
        return {url: token_counts[url] for url in token_counts.keys()
                if not token_counts[url] < high_threshold}
    elif low:
        return {url: token_counts[url] for url in token_counts.keys()
                if not low_threshold < token_counts[url]}
    else:
        return {}

def block_outliers(json_path=DEFAULT_JSON_PATH, high=True, low=True) -> dict:
    """Returns a dict containing outlier {url: int} pairs"""
    block_counts = block_lengths_dict(json_path)  # {url: token_count}
    q1, q3 = compute_quartiles(block_counts)
    iqr = q3 - q1
    multi = 1.5
    high_threshold = q3 + multi * iqr
    low_threshold = q1 - multi * iqr
    #print("block outlier thresholds: ", low_threshold, high_threshold)
    if high and low:
        return {url: block_counts[url] for url in block_counts.keys()
                if not low_threshold < block_counts[url] < high_threshold}
    elif high:
        return {url: block_counts[url] for url in block_counts.keys()
                if not block_counts[url] < high_threshold}
    elif low:
        return {url: block_counts[url] for url in block_counts.keys()
                if not low_threshold < block_counts[url]}
    else:
        return {}


if __name__ == "__main__":
    URL_LENGTH_THRESHOLD = 13.5  # in blocks of url , usually around 3-5, 8
    TOKEN_COUNT_THRESHOLD = 359.5 # minimum token count was 204 359

    t_dict = token_count_dict()
    t_dict_threshed = {pair[0]: pair[1] for pair in t_dict.items() if not pair[1] < TOKEN_COUNT_THRESHOLD}
    t_outliers = token_outliers(low=True, high=False)

    b_dict = block_lengths_dict()
    b_dict_threshed = {pair[0]: pair[1] for pair in b_dict.items() if not pair[1] > URL_LENGTH_THRESHOLD}
    b_outliers = block_outliers(low=False, high=True)

    print("token lower threshold:", TOKEN_COUNT_THRESHOLD)
    print("block upper threshold:", URL_LENGTH_THRESHOLD)
    print("original total:", str(len(t_dict)))
    print("Optimals max and min are calculated by outlier equation quartile +/- 1.5 * iqr")
    print("Pre-filter optimal token min: ", compute_optimal_token_minimum(t_dict))
    print("Pre-filter optimal block max: ", compute_optimal_block_maximum(b_dict))
    print("removed via token thresh:", str(len(t_dict) - len(t_dict_threshed)))
    print("removed via blocks thresh:", str(len(b_dict) - len(b_dict_threshed)))

    merge = {key: (b_dict_threshed[key], t_dict_threshed[key]) for key in t_dict_threshed.keys()
                    if key not in b_outliers and key not in t_outliers}
    print("removed via outliers:", str(len(t_outliers) + len(b_outliers)))
    print("new total:", str(len(merge)))


    token_dict_no_outliers = {key: merge[key][1] for key in merge.keys()}
    block_dict_no_outliers = {key: merge[key][0] for key in merge.keys()}
    optimal_t = compute_optimal_token_minimum(token_dict_no_outliers)
    optimal_b = compute_optimal_block_maximum(block_dict_no_outliers)
    print("Post-filter optimal token min: ", optimal_t)
    print("Post-filter optimal block max: ", optimal_b)
    print("original token min: ", min(t_dict.values()))
    print("original block max: ", max(b_dict.values()))
    percent = 1 - len(merge)/len(t_dict)
    print("reduction percentage: ", percent)

    plt.xlabel("tokens")
    plt.boxplot([merge[key][1] for key in sorted(merge.keys())], vert=False)
    plt.savefig("token-boxplot.jpg")
    plt.close()
    plt.xlabel("blocks")
    plt.boxplot([merge[key][0] for key in sorted(merge.keys())],vert=False)
    plt.savefig("blocks-boxplot.jpg")
    plt.close()
    plt.ylabel("token length")
    plt.xlabel("block length")
    x = [merge[key][1] for key in sorted(merge.keys())]
    y = [merge[key][0] for key in sorted(merge.keys())]
    plt.scatter(y, x)
    plt.savefig("token-block-scatter.jpg")
    plt.close()
    plt.xlabel("block length")
    plt.ylabel("count")
    plt.hist(y)
    #plt.xscale("log")
    plt.savefig("token-block-box.jpg")
    plt.close()
