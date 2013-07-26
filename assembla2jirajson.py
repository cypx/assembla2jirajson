#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
import json

data_input = []
data_output = []

file_input = sys.argv[1]
file_output = sys.argv[2]

input_field = ['users, ','spaces, ','milestones, ','ticket_statuses, ','tickets, ','estimate_histories, ','user_tasks, ','ticket_comments, ','ticket_associations, ']
input_dict = {}
multiple_input ={}

for s in input_field:
	input_dict[s] = ''
	multiple_input[s] = False


with open(file_input) as f:

	for line in f:

		for s in input_field:
			if line.startswith(s):
				if multiple_input[s]:
					input_dict[s] += ','+line[len(s):-1]
				else:
					input_dict[s] += line[len(s):-1]
					multiple_input[s] = True


for s in input_field:
	data_input.append(json.loads('{"'+s[:-2]+'": ['+input_dict[s]+']}'))


#data_input.append(json.loads('{"users": ['+input_dict['users, ']+']}'))
#data_input.append(json.loads('{"user_tasks": ['+input_dict['user_tasks, ']+']}'))
#data_input.append(json.loads('{"tickets": ['+input_dict['tickets, ']+']}'))

print len(data_input[0]["users"])

users_output = ''
for i, element in enumerate(data_input[0]["users"]):
	users_output += '{"name":"'+element["login"]+'","fullname": "'+element["fullname"]+'"}'
	if i < len(data_input[0]["users"])-1:
		users_output += ','


#for element in data_input[2]["tickets"]:
#	print element["summary"]


data_output.append(json.loads('{"users": ['+users_output+']}'))





with open(file_output, 'wb') as f:
	f.write(json.dumps(data_output))
