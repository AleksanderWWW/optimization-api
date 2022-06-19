# optimization-api
### Flask API for choosing optimal proportions of assets for a given investment portfolio

---

## Table of Contents

- [optimization-api](#optimization-api)
 
  - [Overview](#overview)
  - [Tutorial](#tutorial)
  - [Examples](#examples)
  - [Appendix A: Sharpe ratio](#appendix-a-sharpe-ratio)
  - [Appendix B: Efficient frontier](#appendix-b-efficient-frontier)
  - [Appendix C: Simulated Annealing](#appendix-c-simulated-annealing)
  
---

## Overview

Choosing the right asset proportions to the investment portfolio is probably as much a science as an art.
This API takes care of the former. When provided with a list of assets from which to choose, the algorithm
will return a math-based suggestion on how to proportionate those assets in your investment.

In the scope of the project there are 3 optimization algorithms - efficient frontier, simulated annealing 
and tabu search. The API allows you to configure the metaparameters for each of them, but the functions 
come equiped with sensible defaults as well. 

Let's walk through the foundations on how to use *optimization-api* and how you can integrate it
in your financial workflow.

Enjoy!

---

## Tutorial

---

## Examples

---

## Appendix A: Sharpe ratio

---

## Appendix B: Efficient frontier

---

## Appendix C: Simulated Annealing

---

## Appendix D: Tabu Search

Tabu search is another optimization metaheuristic. As it is with simulated annealing, this algorithm is capable
of escaping local minima, by permiting the objective function to temporarily increase its value
from one iter to another.
Here, however, this activity is performed in a deterministic fashion, not a probabilistic one.
To achieve this, certain data structures are utilized for local search.

Tabu search is yet another trajectory-based algorithm.
Starting out from a certain point, an iterative exploration of the design space takes place.
Once a certain stopping criterion is achieved (e.g. a given number of iteration have been performed, or
the objective function decreased below a certain level)
the algorithm terminates and returns the currently stored result.
As it was with simulated annealing, the objective function is $(-1) * (Sharpe-ratio)$.

Upon each iteration, a neighbourhood of the current solution is selected.
Since the problem at hand is a continuous one, the algorithm selects a randomly chosen subset
of the entire (infinite) neighbourhood.
The cardinality of this subset is yet another metaparameter, defined by the user.

From this set a point is chosen, for which the value of the obj. function is minimal.
This point is then compared with the current solution.
If it is 'better' then the algorithm will select it as the new, current solution.
Irrespective of this comparison, however, that point will be the basis for the
neighbourhood selection, in the upcoming iteration.

The next step is the vital point of the tabu search algorithm.
Throughout the execution, a fixed-size FIFO queue data structure is held in the program's memory - the so called
tabu list.
This queue holds the n previously visited points (where n is the size of the queue - user-defined metaparam).
Presence of a given point is such a queue precludes the algorithm from visiting it.
If the number of visited points exceeds n, then the least recent point is removed and the newly visited point
is appended to the end of the queue.
This mechanism decreases the probability of the algorithm getting stuck in a looping sequence of movements.

Another important metaparameter is the so called aspiration criterion.
This one is not user-defined however, although that might change in future releases of the project.
Aspiration criterion is a logical test whoch, if passed, permits the algorithm to visit a certain point
**even though** it is on a tabu list.
This mechanism decreases the probability of the stagnation of the algorithms - e.g. in a situation where it cannot make
any move, because all of the available points are aready on the tabu list.

In this project the aspiration criterion is as follows:
if the value of the objective function for a given point is lower than the value for the current best solution,
then the criterion is met.

---

*Author: Aleksander Wojnarowicz*