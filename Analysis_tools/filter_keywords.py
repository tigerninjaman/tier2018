import xlrd
from xlutils.copy import copy
from xlwt import easyxf

def save_lists(keyword_lists,xl):
	from xlutils.copy import copy
	from xlwt import easyxf
	rb = xlrd.open_workbook(xl)
	wb = copy(rb)
	w_sheet = wb.get_sheet(2)
	for col in range(len(keyword_lists)):
		colno = 3+col
		w_sheet.write(0,colno,'Filtered category ' + str(col+1))
		for row in range(len(keyword_lists[col])):
			rowno = row + 1
			w_sheet.write(rowno,colno, keyword_lists[col][row])
	wb.save('/Volumes/half_ExFAT//all_files_tier2018/filtering_test.xls')



	# outtext = ""
	# filename = '/Volumes/half_ExFAT/all_files_tier2018/filtering_test.txt'
	# for kl in keyword_lists:
	# 	for w in kl:
	# 		outtext += w + '\n'
	# 	outtext += '\n'
	# with open(filename,'w',encoding='utf-8') as f:
	# 	f.write(outtext)

def filter(keywords,to_filter):
	punc_num = ['0','1','2','3','4','5','6','7','8','9','%','&','*','(',')',',','.',
				'$','|','（','）','？','！','。','，',' ','\n','\t']
	filtered_list = []
	for word in keywords:
		if word == '路':
			print(word)
			print(word in to_filter)
		word = word.strip()
		if word == '' or word == None or word in to_filter or word.find('研華') != -1:
			continue
		check_word = word
		for p in punc_num:
			check_word = check_word.replace(p,'')
		if check_word == '':
			continue
		else:
			filtered_list.append(word)
	print('Original length: ' + str(len(keywords)) + '\nFiltered length: ' + str(len(filtered_list)))
	return filtered_list

def read_keyword_lists(directory):
	book = xlrd.open_workbook(directory)
	sh = book.sheet_by_index(2)
	cat1words = [entry.value for entry in sh.col(0)[1:]]
	cat2words = [entry.value for entry in sh.col(1)[1:]]
	cat3words = [entry.value for entry in sh.col(2)[1:]]
	return [cat1words,cat2words,cat3words]

def read_file(directory):
	with open(directory,'r',encoding='utf-8') as f:
		text = f.read()
	return text.split('\n')

def main():
	filter_words_dir = '/Volumes/half_ExFAT/all_files_tier2018/code/filter_words.txt'
	xl = '/Volumes/half_ExFAT/all_files_tier2018/add_kw_2.xls'
	to_filter = read_file(filter_words_dir)
	print(to_filter)
	word_lists = read_keyword_lists(xl)
	filtered_word_lists = []
	for word_list in word_lists:
		filtered_word_lists.append(filter(word_list,to_filter))
	save_lists(filtered_word_lists,xl)

if __name__ == '__main__':
	main()