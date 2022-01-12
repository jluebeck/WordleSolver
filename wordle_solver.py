#import json
from math import log
from string import ascii_uppercase

from wordle_data import *

# Jens Luebeck (jluebeck [a] ucsd.edu]

'''
Take list of candidate words and data structures which contain information necessary to apply filters based on letters 
that can't appear, letters which appear in specific places, and the known max/min counts of letters. Returns the set of 
words passing these filters.
'''
# def get_possible_words(words, ignoredLetterSet, reqLetterSet, p2c, lower_counts, upper_counts):
def get_possible_words(data):
    kept = set()
    for w in data.poss_ans:
        wset = set(w)
        # check that the filters are populated and that at minimum no illegal letters appear and that all required
        # letters appear
        if not data.bad_letters.intersection(wset):
            # check if any known letters are in not present
            if data.pos_letters:
                if not all([w[pos] == c for pos, c in data.pos_letters.items()]):
                    continue

            has_illegal = False
            # check that no "yellow" letters are appearing in their previous locations
            for c, nl in data.unpos_req_letters.items():
                if any([w[i] == c for i in nl]):
                    has_illegal = True
                    break

            if has_illegal:
                continue

            # check that the word does not contain fewer than the minimum number appearances for the letters
            for char, lcount in data.lower_counts.items():
                if w.count(char) < lcount:
                    has_illegal = True
                    break

            if has_illegal:
                continue

            # check that the word does not contain more than the maximum number of appearances for the letters
            for char, ucount in data.upper_counts.items():
                if w.count(char) > ucount:
                    has_illegal = True
                    break

            if has_illegal:
                continue

            kept.add(w)

    return kept


def get_check_words(words, ignoredLetterSet):
    return set([w for w in words if not ignoredLetterSet.intersection(set(w))])


# computes the negative log likelihoods for each letter of every word given the set of words
def get_pos_nll_scores(words, k):
    c_d = [{x: 0.00001 for x in ascii_uppercase} for _ in range(k)]
    nwords = float(len(words))
    for w in words:
        for ind, c in enumerate(w):
            c_d[ind][c] += 1

    nll_pos_scores = [{c: -1 * log(v / nwords) for c, v in c_d[ind].items()} for ind in range(5)]
    return nll_pos_scores


def evaluate_guess(ans, guess, k):
    feedback = [0] * k
    ans_letter_counts = defaultdict(int)

    # check for exact matches
    for ind, c in enumerate(ans):
        if guess[ind] == c:
            feedback[ind] = 2

        # if not exact match, increment count in frequency dictionary
        else:
            ans_letter_counts[c] += 1

    # check if guess letter appears in positionally-unmatched answer letters
    for ind, c in enumerate(guess):
        if ans_letter_counts[c] > 0 and not feedback[ind] == 2:
            feedback[ind] = 1
            ans_letter_counts[c] -= 1

    return "".join([str(x) for x in feedback])


def compute_bin_entropy(bins, tot_words):
    probs = [x / tot_words for x in bins.values()]
    # Compute entropy
    return sum([-i * log(i) for i in probs])


def bin_candidates(guess, candidates, k):
    bins = defaultdict(int)
    guess_letters = set(guess)
    tot_words = float(len(candidates))
    for w in candidates:
        w_letters = set(w)
        if not guess_letters.intersection(w_letters):
            bins["00000"] += 1
        else:
            fb = evaluate_guess(w, guess, k)
            bins[fb] += 1

    if len(bins) > 1:
        return bins, compute_bin_entropy(bins, tot_words)

    return bins, 0.


def best_word(candidate_words, check_words, pos_scores, k):
    eps = 0.000000001
    best_score = -1
    best_bins = defaultdict(int)
    cand_set = set(candidate_words)
    bw = ""

    for w in sorted(check_words):
        bins, bin_score = bin_candidates(w, candidate_words, k)
        if bin_score > best_score + eps:
            best_score = bin_score
            best_bins = bins
            bw = w

        elif abs(bin_score - best_score) < eps:
            if bins["00000"] < best_bins["00000"]:
                best_score = bin_score
                best_bins = bins
                bw = w

            elif bins["00000"] == best_bins["00000"]:
                w_letters = set(w)
                if w in cand_set and bw not in cand_set:
                    best_score = bin_score
                    best_bins = bins
                    bw = w

                # break tries by checking for most unique letters
                elif w in cand_set and bw in cand_set:
                    if len(w_letters) > len(set(bw)):
                        best_score = bin_score
                        best_bins = bins
                        bw = w

                    # then try negative log likelihood of letters
                    elif len(w_letters) == len(set(bw)):
                        nll_score = sum([pos_scores[ind][c] for ind, c in enumerate(w)])
                        bw_nll_score = sum([pos_scores[ind][c] for ind, c in enumerate(bw)])
                        if nll_score < bw_nll_score - eps:
                            best_score = bin_score
                            best_bins = bins
                            bw = w

    return bw


# take the feedback from the previous run and add the information to the data structures.
# def add_feedback(guess, colors, bad_letters, unpos_req_letters, pos_letters, lower_counts, upper_counts):
def add_feedback(guess, feedback, data):
    l2count_good = defaultdict(int)
    l2count_bad = defaultdict(int)
    # count the yellows and greens and store
    for ind, (char, col) in enumerate(zip(guess, feedback)):
        if col == "1":
            data.unpos_req_letters[char].add(ind)
            l2count_good[char] += 1

        elif col == "2":
            data.pos_letters[ind] = char
            l2count_good[char] += 1

    # count the greys separately since there may be yellows of the same letter
    for ind, (char, col) in enumerate(zip(guess, feedback)):
        if col == "0":
            if char not in data.unpos_req_letters and char not in data.pos_letters.values():
                data.bad_letters.add(char)

            else:
                l2count_bad[char] += 1

    # use the greys vs yellow/green to improve bounds on how many times a letter can appear
    for char, curr_count in l2count_good.items():
        if curr_count > data.lower_counts[char]:
            data.lower_counts[char] = curr_count
        if l2count_bad[char] > 0:
            data.upper_counts[char] = curr_count


# read flat file of scrabble words, keep only words of size k.
def read_words(k, file):
    words = []
    with open(file) as infile:
        for line in infile:
            w = line.rstrip().upper()
            if len(w) == k:
                if w.isalpha():
                    words.append(w)

    return words


def update_guess(guess, feedback, data):
    add_feedback(guess, feedback, data)
    new_words = get_possible_words(data)

    if feedback == "2" * data.k:
        return True, 1

    nwords = len(new_words)
    if nwords < 1:
        return None, nwords

    else:
        if len(new_words) < 3 or data.gnum >= 5:
            data.to_check = new_words
        else:
            data.to_check = get_check_words(data.to_check, data.bad_letters)

        pos_scores = get_pos_nll_scores(new_words, data.k)
        bw = best_word(new_words, data.to_check, pos_scores, data.k)

    data.poss_ans = new_words
    data.gnum+=1
    return bw, nwords
