#! /usr/local/bin/python

'''
This python script is a simple tool of query expansion, at first you put query in it, it will give your 10 search result by Bing, then you can assign each to related to the topic or unrelated to your topic, then the script will calculate the query expansion word(each iteration by one), it will repeat this step until the precision reaches what you set.

for simplicity, I didn't implement the existing query modify algorithm.

you can just simply type the following command in the terminal

>> python proj1.py -k "your auth key" -p 0.9 -q "your query"

and all the parameters have their default value, you can just simply run 

>> python proj1.py


Each run the python script will generate a transcript_(random_string) with current experiment result recorded in the current working directory

Created on Feb 3, 2014

@author: Milannic
'''

import argparse 
import base64
import urllib2
import re
import json
import uuid
import math

#global variables
iter_round = 0
accountKey = ''
precision10 = 0
result_list = None
relevant_list = []
irrelevant_list = []
dict_table = {}
query_list = []
query = ""
output_file_desp = None

# weight parameter, beta is the word of weight occurring in a relevant result, gamma is the negative weight of a word occurring in a irrelevant 
beta = 0.85
gamma = 1-beta

#we filter the words in this list for they will never be used in the search expansion
#this list of stop words is generated from nltk python library
non_sense_list = ['i', 'me', 'my', 'myself', 'we', 'our', 'ours', 'ourselves', 'you', 'your', 'yours', 'yourself', 'yourselves', 'he', 'him', 'his', 'himself', 'she', 'her', 'hers', 'herself', 'it', 'its', 'itself', 'they', 'them', 'their', 'theirs', 'themselves', 'what', 'which', 'who', 'whom', 'this', 'that', 'these', 'those', 'am', 'is', 'are', 'was', 'were', 'be', 'been', 'being', 'have', 'has', 'had', 'having', 'do', 'does', 'did', 'doing', 'a', 'an', 'the', 'and', 'but', 'if', 'or', 'because', 'as', 'until', 'while', 'of', 'at', 'by', 'for', 'with', 'about', 'against', 'between', 'into', 'through', 'during', 'before', 'after', 'above', 'below', 'to', 'from', 'up', 'down', 'in', 'out', 'on', 'off', 'over', 'under', 'again', 'further', 'then', 'once', 'here', 'there', 'when', 'where', 'why', 'how', 'all', 'any', 'both', 'each', 'few', 'more', 'most', 'other', 'some', 'such', 'no', 'nor', 'not', 'only', 'own', 'same', 'so', 'than', 'too', 'very', 's', 't', 'can', 'will', 'just', 'don', 'should', 'now','www','https','http','com','net','org']

#and we need to remove all the symbols in a sentence
symbol_list = ["\"",".",",","}","{","]","[",")","(","\'","\'s",":","|","&","*","/","%","^","*","_"]

#preprocessing function, used to remove all the symbol in the bing respond sentence, and transfer all the word to low_case
def pre_processing(origin):
	global non_sense_list
	# at first we need convert all the words to letter case
	dest = origin.lower()
	for symbol in symbol_list:
		dest = dest.replace(symbol," ")
	return dest


# core part of the search expansion
def iteration_result():
	global relevant_list
	global irrelevant_list
	global dic_table
	global query_list
	global query
	global beta
	global gamma

        #dictionary of inverted document index
        inverted_word_table= {}
        #we give every term a index in this list
        inverted_word_list = []
        #the inverted document frequency list(the index it is the same as inverted_word_list)
        idf_list = []
        #generate the inverted document index
        for index,relevant_result in zip(range(len(relevant_list)),relevant_list):
            for relevant_word in relevant_result:
                if inverted_word_table.has_key(relevant_word):
                    if index in inverted_word_table[relevant_word]:
                        pass
                    else:
                        temp = inverted_word_table[relevant_word]
                        temp.append(index)
                        inverted_word_table[relevant_word] = temp
                else:
                    inverted_word_table[relevant_word] = [index]
                    inverted_word_list.append(relevant_word)

        for index,irrelevant_result in zip(range(len(relevant_list),len(irrelevant_list)+len(relevant_list)),irrelevant_list):
            for irrelevant_word in irrelevant_result:
                if inverted_word_table.has_key(irrelevant_word):
                    if index in inverted_word_table[irrelevant_word]:
                        pass
                    else:
                        temp = inverted_word_table[irrelevant_word]
                        temp.append(index)
                        inverted_word_table[irrelevant_word] = temp
                else:
                    inverted_word_table[irrelevant_word] = [index]
                    inverted_word_list.append(irrelevant_word)

        #generate the inverted document frequency list
        for word in inverted_word_list:
            idf_list.append(math.log(10/len(inverted_word_table[word])))



        #we maintain a dictionary to store the total score of each word occurring in our filtered word list.
        
	dic_table = {}
        #for each sentence in the relevant_list
	for relevant_result in relevant_list:
                # the weight of each word in a certain sentence is determined by the length of the sentence
		ratio = len(relevant_result)
		if ratio != 0:
                        #for each sentence in the relevant_list
			for relevant_word in relevant_result:
					#new_value = beta/ratio
					#new_value = beta/ratio
                                        my_index = inverted_word_list.index(relevant_word)
                                        new_value = idf_list[my_index]*beta/len(relevant_list)
                                        #if the word is seen before, we just take out the score and add the value
					if dic_table.has_key(relevant_word):
						dic_table[relevant_word] = dic_table[relevant_word] + new_value 
                                        #else we just set up the key-pair
					else:
						dic_table[relevant_word] = new_value 
        # for each sentence in the irrelevant_list, we do the same thing
        # but all the weight must be negative
	for irrelevant_result in irrelevant_list:
		ratio = len(irrelevant_result)
		if ratio != 0 :
			for irrelevant_word in irrelevant_result:
                                        my_index = inverted_word_list.index(irrelevant_word)
                                        new_value = -1*idf_list[my_index]*gamma/len(irrelevant_list)
					if dic_table.has_key(irrelevant_word):
						dic_table[irrelevant_word] = dic_table[irrelevant_word] + new_value 
					else:
						dic_table[irrelevant_word] = new_value 
        # at last we just sort the dictionary 
	sorted_list = sorted(dic_table.items(), key=lambda x: x[1])
	if len(sorted_list) == 0:
		raise Exception("why there is no new word?")
        # pop the word with largest score
	else :
		new_word = sorted_list.pop()[0]
		query = query + " " + new_word 
		query_list.append(new_word)

#originally we pop two words in each iteration, but it seems that it is less safe
 	#else: 
 	#	new_word = sorted_list.pop()[0]
 	#	query = query + " " + new_word 
 	#	query_list.append(new_word)
 	#	new_word = sorted_list.pop()[0]
 	#	query = query + " " + new_word 
 	#	query_list.append(new_word)


#this function is used after get the original search response, for each result, we mark it either relevant or irrelevant, and store the information in the file and the global variables.
def cal_precision(result_list):
	global relevant_list
	global irrelevant_list
	global iter_round
	global output_file_desp
	
	relevant_list = []
	irrelevant_list = []
	for index,result in zip(range(len(result_list)),result_list):
		print "the number ",index, " result"
		output_file_desp.write("the number "+str(index) + " result\n\n")
		
		result['Description'] = result['Description'].encode('ascii','ignore')
		result['Title'] = result['Title'].encode('ascii','ignore')
		result['Url'] = result['Url'].encode('ascii','ignore')
		
		print "Title : ",result['Title']
		output_file_desp.write("Title : " + result['Title']+'\n\n')
		
		print "Description : ",result['Description']
		output_file_desp.write("Description : " + result['Description']+'\n\n')
		
		print "Url : ",result['Url']
		output_file_desp.write("Url : " + result['Url']+'\n\n')
		
		print "is this result relevant to your query? Yes Or No "
                #preprocess the sentence, we just take the information from Title and the Description

		new_string = pre_processing(result['Url'] + " "+ result['Title'] +" "+result['Description'])
                #print new_string
		#answer = raw_input("new_string")
		new_list = []
		for split_word in new_string.split(" "):
                        # we should discard those words already in the query and in non_sense_list
			if split_word not in non_sense_list and split_word not in query_list and len(split_word) !=0 and len(split_word) !=1 and split_word != '-' :
				new_list.append(split_word)
		answer = raw_input("------>")
                #simple regular expression to recognize the input
                while re.match(".*[yYnN].*",answer) == None:
                    print "cannot recognize the parameter you input,please re-input it again\n"
                    answer = raw_input("------>")
		if re.match(".*[yY].*",answer) != None:
			relevant_list.append(new_list)
			output_file_desp.write("this result is related, yes\n\n")
		elif re.match(".*[nN].*",answer)!=None:
			irrelevant_list.append(new_list)
			output_file_desp.write("this result is not related, no\n\n")
        # calculate the number of relevant results
	rela_num = len(relevant_list)
	output_file_desp.write("in this iteration, the realted number of result is "+str(rela_num)+'\n\n')
	return rela_num
	
			
# main function,parse the parameter and do some pre-work
def main():
	
	global query
	global query_list
	global accountKey
	global precision10
	global iter_round
	global output_file_desp
	
	
	#parse the parameter
	my_parse = argparse.ArgumentParser(description = "this is a test")
	my_parse.add_argument("-k","--key",dest = "my_key",type=str,default = "")
	my_parse.add_argument("-q","--query",dest = "init_query",type=str,default ='steve jobs')
	my_parse.add_argument("-p","--precision",dest = "precision10",type=float,default = 0.9)
	my_para = my_parse.parse_args()
       
	
	
	accountKey = my_para.my_key
	query = my_para.init_query
	precision10 = my_para.precision10
        if precision10 > 1 or precision10 < 0:
            raise Exception("the precision parameter is not valid")

	output_file_desp = open("transcript_"+str(uuid.uuid1())[0:6],'w')
        output_file_desp.write("desired precision10 is "+str(precision10)+"\n")

	query_list = query.lower().split(" ")
        print "desired precision10 is ",precision10
        #iteration loop	
	while True:
		output_file_desp.write("round "+str(iter_round)+'\n\n')
		output_file_desp.write("current query is "+query+'\n\n')
                print "current round is ",iter_round
                print "current search is ",query
		result_list = bing_search(query)
                # if the results are less than 10, end the program
		if(len(result_list) < 10):
			output_file_desp.write("less than 10 records found")
			output_file_desp.close()
			raise Exception("less than 10 records found")
		rela_num=cal_precision(result_list)
                #if we have reached the required precision, end the program
                print "previous precision is ",float(rela_num)/10
		output_file_desp.write("current precision is "+str(float(rela_num)/10))
		if(precision10 <= float(rela_num)/10):
			break
                #if there is no relevant result, end the program
		elif(rela_num == 0):
			output_file_desp.write("no related queries found")
			output_file_desp.close()
			raise Exception("no related queries found")
                #expand the query
		iteration_result()
		iter_round += 1
		
	output_file_desp.write("have reached the required precision10 \n\n")
	output_file_desp.close()
		

#bin search API
def bing_search(query):
	# create credential for authentication
	inner_query = urllib2.quote(query)
	bingUrl = 'https://api.datamarket.azure.com/Bing/Search/Web?Query=%27'+inner_query+'%27&$top=10&$format=json'
	accountKeyEnc = base64.b64encode(accountKey + ':' + accountKey)
	headers = {'Authorization': 'Basic ' + accountKeyEnc}
	req = urllib2.Request(bingUrl, headers = headers)
	response = urllib2.urlopen(req)
	content = response.read()
	#print type(content)
	#content contains the xml/json response from Bing. 
	#then parse it 
	json_result = json.loads(content)
	#just get the field we need for parsing
	# field information : Description, Title,Url
	result_list = json_result['d']['results']
	#return it
	return result_list


if __name__ == "__main__":
	main()

