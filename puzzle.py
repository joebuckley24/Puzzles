import numpy as np
import pandas as pd
STATES = pd.read_csv("states_pops.csv")
SOLUTION = ""

def score(answer):
	poss_states = find_states(answer)
	score = {}
	for row in poss_states:
		for li in row:
			for state in li:
				if state not in score:
					score[state] = STATES.loc[STATES.state==state, "pop"].values[0]
	return score

def find_states(answer):
	board = [answer[5*n:5*(n+1)] for n in range(5)]
	poss_states_bysq = [[list() for _ in range(5)] for _ in range(5)]
	for i in range(5):
		for j in range(5):
			find_states_bysq(board, i, j, "", [True]*50, [True]*50, poss_states_bysq[i][j], str(i)+str(j)+" ")
	return poss_states_bysq

def find_states_bysq(board, i, j, s, poss, perf, ansr_ij, ij_path):
	poss_ = poss[:]
	perf_ = perf[:]
	# print(f"ansr_ij={ansr_ij}")
	# print(f"i={i}")
	# print(f"j={j}")
	# print(f"ij_path={ij_path}")
	# print(f"s={s}")
	# print(f"s + board[i][j]={s+board[i][j]}")
	# print("poss=")
	# print(STATES.loc[poss,"state"])
	# print("perf=")
	# print(STATES.loc[perf,"state"])
	# print("")
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
	if any(poss_):
		for di, dj in [(-1,1), (0,1), (1,1), (1,0), (1,-1), (0,-1), (-1,-1), (-1,0)]:
			i_ = i + di
			j_ = j + dj
			if i_ >= 0 and i_ < 5 and j_ >= 0 and j_ < 5:
				find_states_bysq(board, i_, j_, s+board[i][j], poss_, perf_, ansr_ij, ij_path+str(i_)+str(j_)+" ")

def def_distr():
	counts = {}
	for stt in STATES.state:
		for ch in stt:
			if ch in counts:
				counts[ch] += 1
			else:
				counts[ch] = 1
	letters = np.fromiter(counts.keys(), dtype=object)
	probs = np.fromiter(counts.values(), dtype=float) / sum(counts.values())
	return letters, probs

def gen_cand(letters, probs):
	return "".join(np.random.choice(letters, 25, p=probs))

def print_board(s25):
	for n in range(5):
		print("    " + s25[5*n:5*(n+1)])

def print_scores(dic):
	for k,v in dic.items():
		print(f"{k}: {v}")

if __name__ == "__main__":
	answer = \
	"tho__" + \
	"ain__" + \
	"esl__" + \
	"_____" + \
	"_____"
	# scr = score(answer)
	# print(scr)
	# print(sum(scr.values()))

	letters, probs = def_distr()
	pos_scores = []
	for i in range(100_000):
		cand = gen_cand(letters, probs)
		scrs = score(cand)
		scr = sum(scrs.values())
		if scr > 0:
			pos_scores.append((cand,scrs,scr))

	top5 = sorted(pos_scores, key=lambda t: t[2], reverse=True)[:5]
	for i in range(5):
		print_board(top5[i][0])
		print_scores(top5[i][1])
		print(top5[i][2])
		print("")