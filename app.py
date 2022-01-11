import copy

from flask import Flask, request, render_template, escape

from wordle_solver import *

#Jens Luebeck (jluebeck [a] ucsd.edu]

app = Flask(__name__)
tries = []
gnum = 1
k = 5
init_cbw = "SOARE"
cbw = init_cbw
bad_letters = set()
unpos_req_letters = defaultdict(set)
pos_letters = dict()
lower_counts = defaultdict(int)
upper_counts = defaultdict(int)
init_to_check = read_words(k, "resources/full_set.txt")
init_poss_words = read_words(k, "resources/reduced_set.txt")
to_check = copy.copy(init_to_check)
poss_words = copy.copy(init_poss_words)

@app.route('/', methods=["GET", "POST"])
def index():  # put application's code here
    global gnum
    global k
    global init_cbw
    global cbw
    global bad_letters
    global unpos_req_letters
    global pos_letters
    global lower_counts
    global upper_counts
    global to_check
    global poss_words

    helpstring = "Enter your guesses sequentially. This tool does not yet handle \"hard " \
                 "mode\".\n"

    original_trystring = "As a first guess, I recommend \"" + cbw + "\" since it maximizes the entropy of the Wordle " \
                        "feedback on the reduced Worlde answer set."
    while request.method == "POST":
        if request.form.get('reset') == 'Reset':
            tries.clear()
            gnum=1
            cbw = init_cbw
            trystring = original_trystring
            to_check = copy.copy(init_to_check)
            poss_words = copy.copy(init_poss_words)
            bad_letters = set()
            unpos_req_letters = defaultdict(set)
            pos_letters = dict()
            lower_counts = defaultdict(int)
            upper_counts = defaultdict(int)
            return render_template("index.html", message=helpstring, trystring=trystring, bw=cbw, tries=tries)

        guess = str(escape(request.form.get("guess"))).strip()
        resp = str(escape(request.form.get("resp"))).strip()
        if not guess:
            guess = cbw

        # check the text
        if len(guess) != 5 or not guess.isalpha():
            em = "Your guess must be five letters, and no special characters/numbers"
            return render_template("index.html", message=helpstring, error_message=em, tries=tries)

        # check color validity
        elif not set(resp).issubset({"0", "1", "2"}) or len(resp) != 5:
            em = "The color specification must be the five numbers of 0, 1, or 2 for grey, yellow, green " \
                 "respectively, provided as feedback by Wordle"
            return render_template("index.html", message=helpstring, error_message=em, tries=tries)

        else:
            retval, ncands, to_check, poss_words = update_guess(guess, resp, poss_words, bad_letters, unpos_req_letters,
                                                        pos_letters, lower_counts, upper_counts, gnum, k, to_check)

            tries.append((guess, resp, str(ncands) + " remaining possible words"))
            gnum+=1

            if retval is True:
                # celebrate victory
                victory="Awesome! :-)"
                return render_template("index.html", message=helpstring, victory=victory, tries=tries)

            elif retval is None:
                em = "There were no candidate words from this sequence. Is it a valid candidate? Try resetting and " \
                     "double checking?"
                return render_template("index.html", message=helpstring, error_message=em, tries=tries)

            else:
                cbw = retval

            trystring = "Try: " + cbw
            return render_template("index.html", message=helpstring, trystring=trystring, bw=cbw, tries=tries)

    return render_template("index.html", message=helpstring, trystring=original_trystring, bw=cbw, tries=tries)


if __name__ == '__main__':
    app.run()
