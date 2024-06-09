import pandas as pd
STATES = pd.read_csv("states_pops.csv")
MAXLEN = STATES.state.str.len().max()
SOLUTION = ""


def score_answer(answer)
	poss_states = find_states(answer)
	total = 0
	for row in poss_states:
		for li in row:
			for state in li:
				total += STATES.loc[STATES.state==state, "pop"]
	return total

def find_states(answer):
	poss_states_bysq = [[list() for _ in range(5)] for _ in range(5)]
	for i in range(5):
		for j in range(5):
			find_states_bysq(answer, i, j, poss_states_bysq[i][j])
	return poss_states_bysq

def find_states_bysq(answer, i, j, poss_states):
	

def valid_state_path(s, i, j):
	for di, dj in [(-1,1), (0,1), (1,1), (1,0), (1,-1), (0,-1), (-1,-1), (-1,0)]:
		i_new = i + di
		j_new = j + dj
		if i_new >= 0 and i_new < 5:
			if j_new >= 0 and j_new < 5:
				valid_state_string(SOLUTION[i_new, j_new])
				try_path(i_new, j_new)
		else:
			continue

		j += dj

def valid_state_string(s):
	poss = [True]*50
	perf = [True]*50
	for i, ch in enumerate(s):
		valid_state_char(ch, i, poss, perf)
		if not any(poss):
			break
	return poss

def valid_state_char(ch, i, poss, perf):
	for n in range(50):
		if poss[n]:
			if STATES.at[n,"state"][i] != ch:
				if perf[n]:
					perf[n] = False
				else:
					poss[n] = False
