# My Solution to Jane Street 06/2024 Puzzle, "Altered States 2" ##

Please go to the June 2024 entry in Jane Street's [Puzzle Archive](https://www.janestreet.com/puzzles/altered-states-2-index/ "archive") for the official prompt and other months' puzzles.

![5x5 blank grid and 3x3 example grid](june-2024.png "Example photo")

## Instructions ##

A little while ago we asked solvers to smoosh as many of the 50 U.S. states into a 5-by-5 grid as possible.

Now we’re at it again! Once more, your goal is to score **as many points as possible** by placing **U.S. states** in a 5-by-5 grid.

*   States can be spelled by making **King’s moves** from square to square. (See the example.)
*   This time around, the score for a state is its **population** in the [2020 U.S. Census](https://en.wikipedia.org/wiki/2020_United_States_census#State_rankings "census"). So, for example, CALIFORNIA scores 39,538,223 points.
*   In the true spirit of the puzzle’s title, you may “alter” the name of a state by _at most one letter_. “Altering” a state means replacing a letter with another letter. (So NEW**P**ORK, NEWYOR**F**, and NEWYORK would all score for NEWYORK, but NEWYRK and NEWY**RO**K would not.)
*   If a state appears multiple times in your grid, it only scores once.

The 3-by-3 example above scores **32,913,047 points**, for Illinois (Inlinois), Ohio, Utah (Atah), Iowa (Ioha), and Idaho (Ieaho).

To send in your entry, please render your grid as **one unbroken 25-digit string** by concatenating the rows. (The 3-by-3 grid from the example would be “thoainesl”.)

To qualify for the leaderboard, you entry must score **at least half** of the available points. (So: at least 165,379,868.)

## Solution ##

We need to find an optimal 5x5 arrangement of letters to maximize our score. Since we don't have any training data and can't easily generate any, we'll have to be smarter than just throwing data at a neural net until it spits out the right answer. Instead, we'll have to use an iterative optimization technique to generate, test, and improve our arrangement of letters. This sounds like the perfect job for a **genetic algorithm**. 

The genetic algorithm is inspired by natural selection in the biological world, in which each generation of solutions is iteratively improved via recombination and mutation until an acceptable solution is found. In other words, first we randomly generate solutions. Then, we take pairs of those solutions, split each one in half, and recombine each of the different halves so we have two new child candidates. Next, in the mutation step we inject noise into the process by regenerating one or more of the letters in a candidate solution so as to broaden the set of paths that we search. Now it's time to score each new solution using the evaluation function that we want to maximaize. Finally, using the parent and child population of solutions, we select the top 50% of candidates, thus keeping the same number of potential solutions. Each iteration we will have a top-scoring candidate, and once we breach our threshold of 165 million, we're done!

## Implementation

We represent each candidate as a string of length 25, initally randomly generated based on the distribution of letters across all 50 states. This makes our recombination function basically trivial to implement:

    def crossover(cand1, cand2):
		split = random.randrange(23)
		cand1_ = cand1[:split+1] + cand2[split+1:]
		cand2_ = cand2[:split+1] + cand1[split+1:]
		return cand1_, cand2_

We simply split the two candidate strings into two pieces at some random point such that `XXXXX...XX` and `YYYYY...YY` would be split, for instance, into `XXYYY...YY` and `YYXXX...XX` when our index `split=1` (since our index starts at 0). Our mutation function, shown in full below, is a little more involved:

	def mutate(cand, cond_cnts):
		idx = random.choice(range(25))
		i, j = divmod(idx, 5)
		cnts = {}
		for di, dj in [(-1,1), (0,1), (1,1), (1,0), (1,-1), (0,-1), (-1,-1), (-1,0)]:
			i_ = i + di
			j_ = j + dj
			if i_ >= 0 and i_ < 5 and j_ >= 0 and j_ < 5:
				idx_ = 5*i_ + j_
				neighb = cand[idx_]
				for ltr, cnt in cond_cnts[neighb].items():
					if ltr not in cnts:
						cnts[ltr] = cnt
					else:
						cnts[ltr] += cnt
		letters = np.fromiter(cnts.keys(), dtype=object)
		probs = np.fromiter(cnts.values(), dtype=float) / sum(cnts.values())
		mut = "".join(np.random.choice(letters, 1, p=probs))
		return cand[:idx] + mut + cand[idx+1:]

First, we generate a random index integer, and figure out what its neighboring indices would be if the letters were arranged in a 5x5 grid. Our for loop in the middle of the funtion is going through and getting all the neighbors we find of our chosen random index. For example, if we generated `idx=4`, we'd be in the top right corner of the grid, and only have three neighbors, `{3,8,9}`. We naively form a distribution of letters from which to sample by adding the conditional counts of letters that appear next to `l` for each neighboring letter `l`. Then we replace the sampled letter into our index spot and return the new candidate string.

The most important function will be our evaluation or fitness function, without which we cannot decide if we've solved the problem or rate our candidate solutions. The main engine of our evaluation function is `find_states_bysq(board, i, j, s, poss, perf, ansr_ij, ij_path, sqs_used)`, which allows us to recursively search for states, exploring all possible paths from a given `i` and `j` in a candidate solution `board`. (Note that we represent a solution as a list of 5 strings of length 5 in this function.) The parameter `s` is the string showing the path that we have searched so far (so perhaps we've traveled 3 squares already and landed on the second letter in the second row and have the letters `A`, `L`, `A`, meaning `s=ala`, `i=1`, and `j=1`. ) We have two length 50 boolean variables, `poss` and `perf`, that keep track of which states are still possible given the path travelled thus far (remember we get up to one erroneous letter when constructing the state, hence the need for `perf`). Since all python variables are pointers and we want to update our two lists of booleans, we must copy them, e.g. `poss_ = poss[:]`, in order to prevent false negatives when we backtrack to a new path. Here's the recursive part of the function:

		if any(poss_):
			for di, dj in [(-1,1), (0,1), (1,1), (1,0), (1,-1), (0,-1), (-1,-1), (-1,0)]:
				i_ = i + di
				j_ = j + dj
				if i_ >= 0 and i_ < 5 and j_ >= 0 and j_ < 5:
					find_states_bysq(board, i_, j_, s+board[i][j], poss_, perf_, ansr_ij, ij_path+str(i_)+str(j_)+" ", sqs_used)

Perhaps the most important parameter is `ansr_ij`. This keeps track of all states that have actually been successfully found in our sweep through a candidate solution. We keep this function parameter as a pointer to the list of states found, and append the state to the list upon completion of the path. The other two parameters were used for analysis, to check function accuracy and determine whether there were unused squares on a given board for post-scoring analysis. Here's the function in its entirety.

	def find_states_bysq(board, i, j, s, poss, perf, ansr_ij, ij_path, sqs_used):
		poss_ = poss[:]
		perf_ = perf[:]
		for k in range(50):
			if poss[k]:
				stt = STATES.at[k,"state"]
				if board[i][j] != stt[len(s)]:
					if perf[k]:
						perf_[k] = False
					else:
						poss_[k] = False
				if poss_[k]:
					if len(s) + 1 == len(stt):
						ansr_ij.append(stt)
						poss_[k] = False
						for ij in ij_path.split():
							if ij in sqs_used:
								sqs_used[ij].add(stt)
							else:
								sqs_used[ij] = {stt}
		if any(poss_):
			for di, dj in [(-1,1), (0,1), (1,1), (1,0), (1,-1), (0,-1), (-1,-1), (-1,0)]:
				i_ = i + di
				j_ = j + dj
				if i_ >= 0 and i_ < 5 and j_ >= 0 and j_ < 5:
					find_states_bysq(board, i_, j_, s+board[i][j], poss_, perf_, ansr_ij, ij_path+str(i_)+str(j_)+" ", sqs_used)

After putting everything together and running several generations of the genetic algorithm, our best string was 

> W T I M A
> 
> E N S V F
> 
> K O A L I
> 
> R C S R O
> 
> E N A I N

giving us a score of 188,652,076.