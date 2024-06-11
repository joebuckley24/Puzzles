import numpy as np
import pandas as pd
import random
import copy
import pickle
STATES = pd.read_csv("states_pops.csv")
SOLUTION = ""

def score(answer):
	poss_states, sqs_used = find_states(answer)
	score = {}
	for row in poss_states:
		for li in row:
			for state in li:
				if state not in score:
					score[state] = STATES.loc[STATES.state==state, "pop"].values[0]
	return score, sqs_used

def ansr2brd(ansr):
	return [ansr[5*n:5*(n+1)] for n in range(5)]

def find_states(answer):
	board = ansr2brd(answer)
	poss_states_bysq = [[list() for _ in range(5)] for _ in range(5)]
	sqs_used = {}
	for i in range(5):
		for j in range(5):
			find_states_bysq(board, i, j, "", [True]*50, [True]*50, poss_states_bysq[i][j], str(i)+str(j)+" ", sqs_used)
	return poss_states_bysq, sqs_used

def find_states_bysq(board, i, j, s, poss, perf, ansr_ij, ij_path, sqs_used):
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

def def_cond_distr():
	counts = {}
	for stt in STATES.state:
		for i, ch in enumerate(stt):
			if ch not in counts:
				counts[ch] = {}
			if i > 0:
				left = stt[i-1]
				if left not in counts[ch]:
					counts[ch][left] = 1
				else:
					counts[ch][left] += 1
			if i < len(stt)-1:
				right = stt[i+1]
				if right not in counts[ch]:
					counts[ch][right] = 1
				else:
					counts[ch][right] += 1
	# for el in counts:
	# 	counts[el] = (
	# 		np.fromiter(counts[el].keys(), dytpe=object),
	# 		np.fromiter(counts[el].values(), dtype=float)
	# 	)
	return counts

def gen_cand(letters, probs):
	return "".join(np.random.choice(letters, 25, p=probs))

def gen_muttn(letters, probs):
	return "".join(np.random.choice(letters, 1, p=probs))

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
			# print(cond_cnts)
			# print(cond_cnts[neighb])
			for ltr, cnt in cond_cnts[neighb].items():
				if ltr not in cnts:
					cnts[ltr] = cnt
				else:
					cnts[ltr] += cnt
	letters = np.fromiter(cnts.keys(), dtype=object)
	probs = np.fromiter(cnts.values(), dtype=float) / sum(cnts.values())
	mut = "".join(np.random.choice(letters, 1, p=probs))
	return cand[:idx] + mut + cand[idx+1:]

def crossover(cand1, cand2):
	split = random.randrange(23)
	cand1_ = cand1[:split+1] + cand2[split+1:]
	cand2_ = cand2[:split+1] + cand1[split+1:]
	return cand1_, cand2_

def print_board(s25):
	s25 = s25.upper()
	for n in range(5):
		print("    " + s25[5*n:5*(n+1)])

def print_scores(dic):
	for k,v in dic.items():
		print(f"{k}: {v}")

def print_output(tup):
	print_board(tup[0])
	print_scores(tup[1])
	print(f"total={tup[2]}")

# if __name__ == "__main__":
if False:
	# answer = \
	# "tho__" + \
	# "ain__" + \
	# "esl__" + \
	# "_____" + \
	# "_____"
	# scr = score(answer)
	# print(scr)
	# print(sum(scr.values()))

	letters, probs = def_distr()
	cond_counts = def_cond_distr()

	try:
		with(open("pos_scores.pickle","rb")) as f:
			pos_scores = pickle.load(f)
	except FileNotFoundError:
		pos_scores = []
		for i in range(10_000): #originally 100k
			cand = gen_cand(letters, probs)
			scrs, _ = score(cand)
			scr = sum(scrs.values())
			if scr > 0:
				pos_scores.append((cand,scrs,scr))

	top5 = sorted(pos_scores, key=lambda t: t[2], reverse=True)[:5]
	# for i in range(5):
	# 	print_board(top5[i][0])
	# 	print_scores(top5[i][1])
	# 	print(top5[i][2])
	# 	print("")

	# print_board(mutate(top5[-1][0], cond_counts))
	# print("")
	# c1, c2 = crossover(top5[-2][0], top5[-1][0])
	# print_board(c1)
	# print_board("")
	# print_board(c2)

	rounds = 8
	top_n = 5000
	top = sorted(pos_scores, key=lambda t: t[2], reverse=True)[:top_n]
	for i in range(rounds):
		idxs = list(range(top_n))
		random.shuffle(idxs)
		for i, j in zip(idxs[:top_n//2], idxs[top_n//2:]):
			c1, c2 = crossover(top[i][0], top[j][0])
			c1 = mutate(c1, cond_counts)
			c2 = mutate(c2, cond_counts)
			c1_scores, c1_sqs = score(c1)
			c1_score = sum(c1_scores.values())
			c2_scores, c2_sqs = score(c2)
			c2_score = sum(c2_scores.values())
			top += [(c1,c1_scores,c1_score), (c2,c2_scores,c2_score)]
		top = sorted(top, key=lambda t: t[2], reverse=True)[:top_n]

	top5 = sorted(top, key=lambda t: t[2], reverse=True)[:5]
	for i in range(5):
		print_board(top5[i][0])
		print_scores(top5[i][1])
		print(top5[i][2])
		print("")

if __name__ == "__main__":

	letters, probs = def_distr()
	cond_counts = def_cond_distr()

	with(open("top1000.pickle","rb")) as f:
		top1000 = pickle.load(f)
	# c1, c2 = crossover(top1000[0][0], top1000[1][0])
	# c1_scores, c1_sqs = score(top1000[0][0])
	# c1_score = sum(c1_scores.values())
	# c2_scores, c2_sqs = score(top1000[1][0])
	# c2_score = sum(c2_scores.values())

	for i in range(5):
		c1_scores, c1_sqs = score(top1000[i][0])
		for k, v in sorted(c1_sqs.items()):
			print(k + ": " + str(len(v)))
		print("")

	for i in range(5):
		c1_scores, c1_sqs = score(top1000[i][0])
		print(len(c1_sqs))

	print_output(top1000[4])

	bstr = "wtimkensvfkoalircsrodnain"
	best = sum(score(bstr)[0].values())
	for i in range(25):
		instr = "".join([bstr[:i] + "_" + bstr[i+1:]])
		print_board(instr)
		best - sum(score(instr)[0].values())

	for i in [4, 20]:
		print("")
		print(i)
		for num in range(ord('a'),ord('z')+1):
			ltr = chr(num)
			instr = bstr[:i] + ltr + bstr[i+1:]
			new_scr = sum(score(instr)[0].values())
			print(ltr + ": " + str(new_scr))

	new_bstr = "wtimaensvfkoalircsroenain"
	new_best = sum(score(new_bstr)[0].values())

