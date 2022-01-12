#!/usr/bin/env python3
import copy
import multiprocessing
from multiprocessing import Process
import time

import numpy as np

from wordle_solver import *

#Jens Luebeck (jluebeck [a] ucsd.edu]

tries = []
init_guess = "SOARE" # reduced wordle answer set best
# init_guess = "TARES" # full or scrable set
k = 5
max_threads = 15

# with open("precomputes.json") as jfp:
#     precomputed_openings = json.load(jfp)
#
# print("Read " + str(len(precomputed_openings)) + " precomputed openings")


def split(a, n):
    k, m = divmod(len(a), n)
    return (a[i*k+min(i, m):(i+1)*k+min(i+1, m)] for i in range(n))


def evaluate_guess(ans, guess, k):
    feedback = [0]*k
    ans_letter_counts = defaultdict(int)

    # check for exact matches
    for ind, c in enumerate(ans):
        if guess[ind] == c:
            feedback[ind] = 2

        # if not exact match, increment count in frequency dictionary
        else:
            ans_letter_counts[c]+=1

    # check if guess letter appears in positionally-unmatched answer letters
    for ind, (c, v) in enumerate(zip(guess, feedback)):
        if ans_letter_counts[c] > 0 and not feedback[ind] == 2:
            feedback[ind] = 1
            ans_letter_counts[c]-=1

    return "".join([str(x) for x in feedback])


def run_full_test(thread_words, all_guess_words, all_answer_words, k, results, tnum):
    nguesses = [0]*len(thread_words)
    print("Thread-" + str(tnum) + " got " + str(len(thread_words)) + " words")

    correct = "2"*k
    for i, w in enumerate(thread_words):
        if i % 100 == 0 and i > 0:
            print("Thread-" + str(tnum) + " completed " + str(i))

        poss_ans = copy.copy(all_answer_words)
        to_check = copy.copy(all_guess_words)

        data = WordleData(poss_ans, to_check, k, init_guess)
        guess = init_guess
        feedback = evaluate_guess(w, guess, k)
        # print(gnum, guess, feedback, len(words))
        while feedback != correct:
            guess, nwords = update_guess(guess, feedback, data)

            if guess is None:
                print(w, "FAIL")
            feedback = evaluate_guess(w, guess, k)
            # print(gnum, guess, feedback, nwords)

        # print(w + " " + str(gnum) + " solved")
        nguesses[i] = data.gnum

    return_dict[tnum] = nguesses
    print(len(results[tnum]), np.mean(nguesses))


if __name__ == "__main__":
    print("INIT IS " + init_guess)
    start = time.time()
    manager = multiprocessing.Manager()
    words = read_words(k, "resources/full_set.txt") # if using Wordle set
    # words = read_words(k, "resources/sowpods5.txt") # if using scrabble
    guess_words = set(words)
    legal_ans_words = read_words(k,"resources/reduced_set.txt") # if using Worlde "vanilla" behavior
    # legal_ans_words = read_words(k, "resources/full_set.txt") # if using Wordle full set
    # legal_ans_words = read_words(k, "resources/sowpods5.txt") # if using scrabble
    thread_words = legal_ans_words
    nthreads = min(max_threads, len(thread_words))
    word_chunks = list(split(thread_words, nthreads))
    return_dict = manager.dict()
    threadlist = []
    for tnum, x in enumerate(word_chunks):
        threadlist.append(Process(target=run_full_test, args=(x, guess_words, legal_ans_words,  k, return_dict, tnum)))

    for t in threadlist:
        t.start()

    for t in threadlist:
        t.join()

    print("done")
    tot_many_guess = 0.0
    all_guesses = []
    with open("unsolved_words.txt", 'w') as outfile:
        for w_ind, w_chunk in enumerate(word_chunks):
            subguesses = return_dict[w_ind]
            many_guesses = [ind for ind, i in enumerate(subguesses) if i > 6]
            all_guesses.extend(subguesses)
            tot_many_guess+=(len(many_guesses))
            for x in many_guesses:
                outfile.write(w_chunk[x] + "\n")

    print(np.mean(all_guesses))
    print(tot_many_guess/len(words))
    end = time.time()
    print("Elapsed walltime: " + str(end - start))

