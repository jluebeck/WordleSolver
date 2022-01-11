##WordleSolver
This is a maximum-entropy way of solving the "Wordle" problem.
This project stores a build for a Flask web app.

**For a more extensive background and explanation of the tool, [please see this post](https://jluebeck.github.io/posts/WordleSolver)**.

WordleSolver requires python3 and the Flask library. Once cloned, the web app can be run locally by simply running `flask app` from inside the repo directory.

There is also a multithreaded script `run_tests.py` which computes the proportion of words that can't be solved given 
an initial guess and  a collection of  different word/answer sets.




