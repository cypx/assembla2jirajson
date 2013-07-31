#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
import json
import re

data_input = []
data_output = []

file_input = sys.argv[1]
file_output = sys.argv[2]
attachement_url = sys.argv[3]

workflow_conversion = {
	"New":"Open",
	"In progress":"In Progress",
	"Invalid":"Closed",
	"Fixed":"Resolved",
	"To test":"In Progress",
	"Waiting information":"Open",
	"To implement":"Open",
	"Duplicate":"Closed",
	"Test pending":"Open",
	"Waiting subtask treatment":"Open",
	"Waiting deploy":"Open" }

input_field = ['users, ',
	'spaces, ',
	'milestones, ',
	'ticket_statuses, ',
	'tickets, ',
	'estimate_histories, ',
	'user_tasks, ',
	'ticket_comments, ',
	'ticket_associations, ',
	'documents, ']

input_dict = {}

#Assembla export file is not a regular json first we serialize data we want to use

#Initiate a dict key for each input type we want to save
for s in input_field:
	input_dict[s] = ''

#read input file and save wanted line into destination key
with open(file_input) as f:
	for line in f:
		for s in input_field:
			if line.startswith(s):
				if input_dict[s]!='':
					input_dict[s] += ','+line[len(s):-1]
				else:
					input_dict[s] += line[len(s):-1]

#Convert saved line into standard json data
for s in input_field:
	data_input.append(json.loads('{"'+s[:-2]+'": ['+input_dict[s]+']}'))

#Now we can convert JSON data according to JIRA JSON schema

# Some function to return JIRA association and convert value between Assembla and Jira

def reporter_login(id,input_dict):
	name=""
	for element in input_dict[0]["users"]:
		if element["id"] == id:
			name=element["login"]
	return name

def ticket_milestone(id,input_dict):
	milestone=""
	for element in input_dict[2]["milestones"]:
		if element["id"] == id:
			milestone=element["title"]
	return milestone

def space_key (id):
	key=""
	for element in data_input[1]["spaces"]:
		if element["id"] == id:
			key=element["name"]
	return key

# we user "workflow_conversion" parameter for mapping assembla workflow to jira workflow
# if a status is not present in "workflow_conversion" we use internal assembla state
def ticket_status(id,input_dict):
	jira_name=""
	for element in input_dict[3]["ticket_statuses"]:
		if element["id"] == id:
			if element["name"] in workflow_conversion:
				jira_name = workflow_conversion[element["name"]]
			else:
				if element["state"] == 1:
					jira_name = "Open"
				else:
					jira_name = "Closed"
	return jira_name

def ticket_priority(id):
	ticket_priorities={1:"Blocker",2:"Critical",3:"Major",4:"Minor",5:"Trivial"}
	return ticket_priorities[id]

#Convert input string according to JSON encoding

users_output = ''
for i, element in enumerate(data_input[0]["users"]):
	users_output += '{"name":"'+element["login"]+'","fullname": '+json.dumps(element["fullname"])+'}'
	if i < len(data_input[0]["users"])-1:
		users_output += ','

versions_output = {}
for element in data_input[2]["milestones"]:
	space_id=element["space_id"]
	if element["is_completed"]==1:
		released='true'
	else:
		released='false'
	if element["due_date"] is None:
		releaseDate=''
	else:
		releaseDate=str(element["due_date"])+'T00:00:00+00:00'
	if space_id not in versions_output:
		versions_output[space_id] =  '{"name":'+json.dumps(element["title"])+',"released":'+released+',"releaseDate":"'+releaseDate+'"}'
	else:
		versions_output[space_id] +=  ',{"name":'+json.dumps(element["title"])+',"released":'+released+',"releaseDate":"'+releaseDate+'"}'

comments_output = {}
for element in data_input[7]["ticket_comments"]:
	ticket_id=element["ticket_id"]
	if element["comment"] != '':
		if ticket_id not in comments_output:
			comments_output[ticket_id] = ''
		else:
			comments_output[ticket_id] += ','
		comments_output[ticket_id] += '{"author":'+json.dumps(reporter_login(element["user_id"],data_input))+','
		comments_output[ticket_id] += '"body":'+json.dumps(element["comment"])+','
		comments_output[ticket_id] += '"created":"'+element["created_on"]+'"}'

attachments_output = {}
for element in data_input[9]["documents"]:
	ticket_id=element["ticket_id"]
	if ticket_id not in attachments_output:
		attachments_output[ticket_id] = ''
	else:
		attachments_output[ticket_id] += ','
	attachments_output[ticket_id] += '{"name" :'+json.dumps(element["name"])+','
	attachments_output[ticket_id] += '"attacher":'+json.dumps(reporter_login(element["created_by"],data_input))+','
	attachments_output[ticket_id] += '"created":'+json.dumps(element["created_at"])+','
	if element["description"] is not None:
		attachments_output[ticket_id] += '"description":'+json.dumps(element["description"])+','
	attachments_output[ticket_id] += '"uri":"'+attachement_url+element["id"]+'_1"}'

issues_output = {}
for element in data_input[4]["tickets"]:
	space_id=element["space_id"]
	if space_id not in issues_output:
		issues_output[space_id] = ''
	else:
		issues_output[space_id] += ','
	issues_output[space_id] += '{"summary":'+json.dumps(element["summary"])+','
	issues_output[space_id] += '"description":'+json.dumps(element["description"])+','
	issues_output[space_id] += '"status":'+json.dumps(ticket_status(element["ticket_status_id"],data_input))+','
	issues_output[space_id] += '"reporter":'+json.dumps(reporter_login(element["reporter_id"],data_input))+','
	issues_output[space_id] += '"assignee":'+json.dumps(reporter_login(element["assigned_to_id"],data_input))+','
	issues_output[space_id] += '"created":"'+element["created_on"]+'",'
	if element["milestone_id"] is not None:
		issues_output[space_id] += '"fixedVersions":['+json.dumps(ticket_milestone(element["milestone_id"],data_input))+'],'
	if element["updated_at"] is not None:
		issues_output[space_id] += '"updated":"'+element["updated_at"]+'",'
	if element["completed_date"] is not None:
		issues_output[space_id] += '"resolution":"Resolved",'
		issues_output[space_id] += '"resolutionDate":"'+element["completed_date"]+'",'
	if element["id"] in comments_output:
		issues_output[space_id] += '"comments":['+comments_output[element["id"]]+'],'
	if element["priority"] is not None:
		issues_output[space_id] += '"priority":'+json.dumps(ticket_priority(element["priority"]))+','
	if element["id"] in attachments_output:
		issues_output[space_id] += '"attachments":['+attachments_output[element["id"]]+'],'
	issues_output[space_id] += '"key":"'+space_key(space_id)+'-'+str(element["number"])+'",'
	issues_output[space_id] += '"externalId":"'+str(element["number"])+'"}'

project_output = ''
for i, element in enumerate(data_input[1]["spaces"]):
	project_output += '{"name":'+json.dumps(element["name"])+','
	project_output += '"key":"'+element["name"]+'",'
	if element["description"] != "":
		project_output += '"description":'+json.dumps(element["description"])+','
	project_output += '"versions":['+versions_output[element["id"]]+'],'
	project_output += '"issues":['+issues_output[element["id"]]+'],'
	project_output += '"components": ["Component","AnotherComponent"]}'
	if i < len(data_input[1]["spaces"])-1:
		project_output += ','

#Create JSON data and write it to export file

data_output.append(json.loads('{"users": ['+users_output+'],"projects": ['+project_output+']}'))

with open(file_output, 'wb') as f:
	f.write((json.dumps(data_output))[1:-1])


