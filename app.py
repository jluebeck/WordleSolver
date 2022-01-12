from flask import Flask, request, render_template, escape, session, redirect
from flask_session import Session

from wordle_solver import *

#Jens Luebeck (jluebeck [a] ucsd.edu]

app = Flask(__name__)
app.secret_key = b'\xb4\xc0m\x90w\xe5`i/\xedl\xc5\xc1B\xd9\xec'
app.config['SESSION_TYPE'] = 'filesystem'

Session(app)

helpstring = "Enter your guess and the feedback info into this tool. Enter guesses sequentially. This tool does" \
             " not yet handle \"hard mode\".\n"
wmap = {"default":"Wordle (default)", "full":"Wordle (expanded)", "scrabble":"Scrabble"}
modes_to_wmap = {"Wordle (default)":"default", "Wordle (expanded)":"full", "Scrabble":"scrabble"}


def initialize(mode="default", k=5):
    if mode == "scrabble":
        init_cbw = "TARES"
        init_to_check = read_words(k, "resources/sowpods5.txt")
        init_poss_words = read_words(k, "resources/sowpods5.txt")

    elif mode == "full":
        init_cbw = "TARES"
        init_to_check = read_words(k, "resources/full_set.txt")
        init_poss_words = read_words(k, "resources/full_set.txt")

    else:
        init_cbw = "SOARE"
        init_to_check = read_words(k, "resources/full_set.txt")
        init_poss_words = read_words(k, "resources/reduced_set.txt")

    session['tries'] = []
    session['k'] = k
    session['cbw'] = init_cbw
    session['poss_ans'] = init_poss_words
    session['to_check'] = init_to_check
    session['bad_letters'] = []
    session['unpos_req_letters'] = defaultdict(set)
    session['pos_letters'] = dict()
    session['lower_counts'] = defaultdict(int)
    session['upper_counts'] = defaultdict(int)
    session['gnum'] = 1


def session_to_data():
    data = WordleData(session['poss_ans'], session['to_check'], cbw=session['cbw'])
    data.k = session['k']
    data.bad_letters = set(session['bad_letters'])
    data.unpos_req_letters = session['unpos_req_letters']
    data.pos_letters = session['pos_letters']
    data.lower_counts = session['lower_counts']
    data.upper_counts = session['upper_counts']
    data.gnum = session['gnum']
    return data


def update_session(data):
    session['cbw'] = data.cbw
    session['poss_ans'] = data.poss_ans
    session['to_check'] = data.to_check
    session['bad_letters'] = list(data.bad_letters)
    session['unpos_req_letters'] = data.unpos_req_letters
    session['pos_letters'] = data.pos_letters
    session['lower_counts'] = data.lower_counts
    session['upper_counts'] = data.upper_counts
    session['gnum'] = data.gnum


@app.route('/play', methods=["GET", "POST"])
def play():
    if request.method == "POST":
        reset = False
        picked_wordset = request.form.get('change_data')
        if picked_wordset in modes_to_wmap:
            reset = True
            session['mode'] = modes_to_wmap[picked_wordset]

        if request.form.get('reset') == 'Reset' or reset:
            session.pop('tries', None)
            session.pop('k', None)
            session.pop('cbw', None)
            session.pop('poss_ans', None)
            session.pop('to_check', None)
            session.pop('bad_letters', None)
            session.pop('unpos_req_letters', None)
            session.pop('pos_letters', None)
            session.pop('lower_counts', None)
            session.pop('upper_counts', None)
            session.pop('gnum', None)
            return redirect('/')

        data = session_to_data()
        session['guess'] = str(escape(request.form.get("guess"))).strip()
        session['resp'] = str(escape(request.form.get("resp"))).strip()
        if not session['guess']:
            session['guess'] = data.cbw

        # check the text
        if len(session['guess']) != 5 or not session['guess'].isalpha():
            em = "Your guess must be five letters, and no special characters/numbers"
            return render_template("index.html", message=helpstring, error_message=em, tries=session['tries'],
                                   dataset_description=session['data_description'])

        # check color validity
        elif not set(session['resp']).issubset({"0", "1", "2"}) or len(session['resp']) != 5:
            em = "The color specification must be the five numbers of 0, 1, or 2 for grey, yellow, green " \
                 "respectively, provided as feedback by Wordle\n Try: " + session['cbw']
            return render_template("index.html", message=helpstring, error_message=em, tries=session['tries'],
                                   bw=session['cbw'],dataset_description=session['data_description'])

        else:
            session['retval'], session['ncands'] = update_guess(session['guess'], session['resp'], data)
            al = session['tries']
            al.append((session['guess'], session['resp'], str(session['ncands']) + " remaining possible words"))
            session['tries'] = al

            if session['retval'] is True:
                # celebrate victory
                victory = "Awesome! :-)"
                update_session(data)
                return render_template("index.html", message=helpstring, victory=victory, tries=session['tries'],
                                       dataset_description=session['data_description'])

            elif session['retval'] is None:
                em = "There were no candidate words from this sequence. Is it a valid candidate? Try resetting and " \
                     "double checking?"
                update_session(data)
                return render_template("index.html", message=helpstring, error_message=em, tries=session['tries'],
                                       dataset_description=session['data_description'])

            else:
                data.cbw = session['retval']

            trystring = "Try: " + data.cbw
            update_session(data)
            return render_template("index.html", message=helpstring, trystring=trystring, bw=data.cbw,
                                   tries=session['tries'],dataset_description=session['data_description'])

    return render_template("index.html", message=helpstring, trystring=session['original_trystring'],
                           bw=session['cbw'], tries=session['tries'],dataset_description=session['data_description'])


@app.route('/', methods=["GET", "POST"])
def index():  # put application's code here
    if 'mode' not in session:
        session['mode'] = "default"

    session['data_description'] = "The current dataset uses the possible answerset from: " + wmap[session['mode']]
    initialize(mode=session['mode'])
    session['original_trystring'] = "As a first guess, I recommend \"" + session['cbw'] + "\" since it maximizes" \
                                    " the entropy of the feedback on the answer set."

    session['trystring'] = session['original_trystring']
    if request.method == "POST":
        return play()

    return render_template("index.html", message=helpstring, trystring=session['original_trystring'], bw=session['cbw'],
                           tries=session['tries'], dataset_description=session['data_description'])


if __name__ == '__main__':
    app.run()
