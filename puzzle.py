import pandas as pd
STATES = pd.read_csv("states_pops.csv")
SOLUTION = ""

def score_answer(answer):
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

# def valid_state_path(s, i, j):
# 	for di, dj in [(-1,1), (0,1), (1,1), (1,0), (1,-1), (0,-1), (-1,-1), (-1,0)]:
# 		i_new = i + di
# 		j_new = j + dj
# 		if i_new >= 0 and i_new < 5:
# 			if j_new >= 0 and j_new < 5:
# 				valid_state_string(SOLUTION[i_new, j_new])
# 				try_path(i_new, j_new)
# 		else:
# 			continue

# 		j += dj

# def valid_state_string(s):
# 	poss = [True]*50
# 	perf = [True]*50
# 	for i, ch in enumerate(s):
# 		valid_state_char(ch, i, poss, perf)
# 		if not any(poss):
# 			break
# 	return poss

# def valid_state_char(ch, i, poss, perf):
# 	for n in range(50):
# 		if poss[n]:
# 			if STATES.at[n,"state"][i] != ch:
# 				if perf[n]:
# 					perf[n] = False
# 				else:
# 					poss[n] = False

if __name__ == "__main__":
	answer = "thoaaainaaeslaaaaaaaaaaaa"
	answer = "tho__ain__esl____________"
	score = score_answer(answer)
	print(score)
	print(sum(score.values()))