## <span style="color:white"><span style="background-color:#c9b458">W</span><span style="background-color:#86888a;">ordle</span><span style="background-color:#6aaa64">Solver</span><span style="background-color:#86888a;"></span></span>

#### [This WordleSolver tool is available online here.](https://wordle-solver.herokuapp.com/)

This is a maximum entropy way of solving the [Wordle](https://www.powerlanguage.co.uk/wordle/) problem.
This repo stores a build for a Flask web app and code for the solver.

**For a more extensive background and explanation of the tool, [please see this post](https://jluebeck.github.io/posts/WordleSolver)**.

WordleSolver requires python3, numpy, the Flask and flask-session libraries. 

`pip install numpy Flask flask-session`

Once cloned, the web app can be run locally by simply running `flask app` from inside the repo directory.

There is also a multithreaded script `run_tests.py` which computes the proportion of words that can't be solved given 
the computed best initial guess, and  a collection of  different word/answer sets to try.





