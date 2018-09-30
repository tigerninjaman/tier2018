import numpy as np
import math
import datetime, xlrd, os
import burst_detection as bd


# file = "C:\\Users\\windows\\Desktop\\google Microsoft and BMW.xlsx"
# book = xlrd.open_workbook(file)
# sh = book.sheet_by_index(0)
# appl_date = sh.col(0)[1:]
# companies = sh.col(8)[1:]
# abstracts = sh.col(20)[1:]
# keyword = 'Artificial intelligence'
# grouped_by_date = {}

# for i,a in enumerate(abstracts):
# 	abstract = a.value
# 	if abstract == 0:
# 		continue
# 	date = appl_date[i].value
# 	date_list = date.split('/')
# 	orddate = datetime.date(int(date_list[2]),int(date_list[0]),int(date_list[1])).toordinal()
# 	company = companies[i].value
# 	if not orddate in grouped_by_date:
# 		grouped_by_date[orddate] = []
# 	grouped_by_date[orddate].append((company,abstract))

# r = []
# d = []
# for date in sorted(grouped_by_date.keys()):
# 	d.append(len(grouped_by_date[date]))
# 	target_events = 0
# 	for co_abs in grouped_by_date[date]:
# 		abstract = co_abs[1]
# 		if abstract.lower().find(keyword.lower()) != -1:
# 			target_events += 1
# 	r.append(target_events)

# n = len(r)

# q,d,r,p = bd.burst_detection(r,d,n,s=2,gamma=1,smooth_win=1)
# bursts = bd.enumerate_bursts(q,'burstLabel')
# weighted_bursts = bd.burst_weights(bursts,r,d,p)
# print('weighted bursts:')
# print(weighted_bursts)


def read_keywords():
	with open('keywords.txt','r') as f:
		keywords = f.read()
	keywords_list = keywords.split('\n\n')
	topics_list = []
	for k in keywords_list:
		topics_list.append(k.split('\n'))
	return topics_list

def read_abstracts():	
	grouped_by_company = {}
	folder = 'C:\\Users\\windows\\Desktop\\patent_data'
	for file in os.listdir(folder):
		print(file)
		filepath = os.path.join(folder,file)
		book = xlrd.open_workbook(filepath)
		sh = book.sheet_by_index(0)
		appl_date = sh.col(0)[1:]
		companies = sh.col(3)[1:]
		abstracts = sh.col(20)[1:]
		for i,a in enumerate(abstracts):
			abstract = a.value
			if abstract == 0:
				continue
			date = appl_date[i].value
			date_list = date.split('/')
			orddate = datetime.date(int(date_list[2]),int(date_list[0]),int(date_list[1])).toordinal()
			company = companies[i].value.lower()
			if not company in grouped_by_company:
				grouped_by_company[company] = {}
			if str(orddate) not in grouped_by_company[company]:
				grouped_by_company[company][str(orddate)] = []
			grouped_by_company[company][str(orddate)].append(abstract)
	for co in grouped_by_company.keys():
		grouped_by_company[co] = sorted(grouped_by_company[co].items())
	return grouped_by_company

def main():
	topics_list = read_keywords()
	company_date_abstract = read_abstracts()
	for company in company_date_abstract:
		co_list = company_date_abstract[company]
		for topic in topics_list:
			for keyword in topic:
				r = []
				d = []
				for date_abs in co_list:
					abs_list = date_abs[1]
					d.append(len(abs_list))
					target_events = 0
					for ab in abs_list:
						if ab.lower().find(keyword.lower()) != -1:
							target_events += 1
					r.append(target_events)
				n = len(r)

				if all(elem == 0 for elem in r):
					continue
				try:
					q,d,r,p = bd.burst_detection(r,d,n,s=2,gamma=1,smooth_win=1)
				except:
					print(d)
					print(r)
					continue
				bursts = bd.enumerate_bursts(q,'burstLabel')
				weighted_bursts = bd.burst_weights(bursts,r,d,p)
				if weighted_bursts.empty:
					continue
				print('-------------------------')
				print('  ' + company.upper())
				print('-------------------------')
				print('weighted bursts for ' + keyword + ':')
				print(weighted_bursts)
		print('\n')
if __name__ == '__main__':
	main()


# contains_index_list = []
# for i,a in enumerate(abstracts):
# 	if a.value != 0.0 and a.value.find(keyword) != -1:
# 		contains_index_list.append(i)

 
# def kleinberg(offsets, s=2, gamma=1):
 
# 	if s <= 1:
# 		raise ValueError("s must be greater than 1!")
# 	if gamma <= 0:
# 		raise ValueError("gamma must be positive!")
# 	if len(offsets) < 1:
# 		raise ValueError("offsets must be non-empty!")
 
# 	offsets = np.array(offsets, dtype=object)
	
# 	if offsets.size == 1:
# 		bursts = np.array([0, offsets[0], offsets[0]], ndmin=2, dtype=object)
# 		return bursts
 
# 	offsets = np.sort(offsets)
# 	gaps = np.diff(offsets)
 
# 	if not np.all(gaps):
# 		raise ValueError("Input cannot contain events with zero time between!")
 
# 	T = np.sum(gaps)
# 	n = np.size(gaps)
# 	g_hat = T / n
 
# 	k = int(math.ceil(float(1 + math.log(T, s) + math.log(1 / np.amin(gaps), s))))
 
# 	gamma_log_n = gamma * math.log(n)
 
# 	def tau(i, j):
# 		if i >= j:
# 			return 0
# 		else:
# 			return (j - i) * gamma_log_n
	
# 	alpha_function = np.vectorize(lambda x: s ** x / g_hat)
# 	alpha = alpha_function(np.arange(k))
 
# 	def f(j, x):
# 		return alpha[j] * math.exp(-alpha[j] * x)
 
# 	C = np.repeat(float("inf"), k)
# 	C[0] = 0
 
# 	q = np.empty((k, 0))
# 	for t in range(n):
# 		C_prime = np.repeat(float("inf"), k)
# 		q_prime = np.empty((k, t+1))
# 		q_prime.fill(np.nan)
 
# 		for j in range(k):
# 			cost_function = np.vectorize(lambda x: C[x] + tau(x, j))
# 			cost = cost_function(np.arange(0, k))
 
# 			el = np.argmin(cost)
 
# 			if f(j, gaps[t]) > 0:
# 				C_prime[j] = cost[el] - math.log(f(j, gaps[t]))
			
# 			if t > 0:
# 				q_prime[j,:t] = q[el,:]
 
# 			q_prime[j, t] = j + 1
 
# 		C = C_prime
# 		q = q_prime
 
# 	j = np.argmin(C)
# 	q = q[j,:]
 
# 	prev_q = 0
	
# 	N = 0
# 	for t in range(n):
# 		if q[t] > prev_q:
# 			N = N + q[t] - prev_q
# 		prev_q = q[t]
 
# 	bursts = np.array([np.repeat(np.nan, N), np.repeat(offsets[0],N),np.repeat(offsets[0], N)], ndmin=2, dtype=object).transpose()
 
# 	burst_counter = -1
# 	prev_q = 0
# 	stack = np.repeat(np.nan, N)
# 	stack_counter = -1
# 	for t in range(n):
# 		if q[t] > prev_q:
# 			num_levels_opened = q[t] - prev_q
# 			for i in range(int(num_levels_opened)):
# 				burst_counter += 1
# 				bursts[burst_counter, 0] = prev_q + i
# 				bursts[burst_counter, 1] = offsets[t]
# 				stack_counter += 1
# 				stack[stack_counter] = burst_counter
# 		elif q[t] < prev_q:
# 			num_levels_closed = prev_q - q[t]
# 			for i in range(int(num_levels_closed)):
# 				# print(offsets[t])
# 				# print(stack_counter)
# 				# print(stack[stack_counter])
# 				bursts[int(stack[stack_counter]), 2] = offsets[t]
# 				stack_counter -= 1
# 		prev_q = q[t] 
 
# 	while stack_counter >= 0:
# 		bursts[int(stack[stack_counter]), 2] = offsets[n]
# 		stack_counter -= 1
 
# 	return bursts

# print(kleinberg(contains_index_list))
