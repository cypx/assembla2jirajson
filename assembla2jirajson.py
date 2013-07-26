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

users_output = ''
for i, element in enumerate(data_input[0]["users"]):
	users_output += '{"name":"'+element["login"]+'","fullname": "'+element["fullname"]+'"}'
	if i < len(data_input[0]["users"])-1:
		users_output += ','

milestones_output = {}
for element in data_input[2]["milestones"]:
	space_id=element["space_id"]
	print "space_id: "+space_id
	if element["is_completed"]==1:
		released='true'
	else:
		released='false'
	if element["due_date"] is None:
		releaseDate=''
	else:
		releaseDate=str(element["due_date"])+'T00:00:00+00:00'
	if space_id not in milestones_output:
		milestones_output[space_id] =  '{"name":"'+element["title"]+'","released":'+released+',"releaseDate":"'+releaseDate+'"}'
	else:
		milestones_output[space_id] +=  ',{"name":"'+element["title"]+'","released":'+released+',"releaseDate":"'+releaseDate+'"}'


	

project_output = ''
for i, element in enumerate(data_input[1]["spaces"]):
	project_output += '{"name":"'+element["name"]+'",'
	project_output += '"key":"'+element["name"][0:3]+'",'
	if element["description"] != "":
		project_output += '"description":"'+element["description"]+'",'
	project_output += '"versions":['+milestones_output[element["id"]]+'],"components": ["Component","AnotherComponent"]}'
	if i < len(data_input[1]["spaces"])-1:
		project_output += ','

data_output.append(json.loads('{"users": ['+users_output+'],"projects": ['+project_output+']}'))


with open(file_output, 'wb') as f:
	f.write((json.dumps(data_output))[1:-1])


