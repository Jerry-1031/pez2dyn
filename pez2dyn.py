'''
Unzip .pez file, get .json file and .wav/.mp3/.ogg file;
Put .json, .wav/.mp3/.ogg and this pez2dyn.py file in a same directory;
Change input_file_name and output_file_name;
Choose which judgeline you want to convert;
Execute this Python file and get output;
Open the output with Dynode, press F5 to export .xml file.
'''

# Change it yourself
input_file_name = "0.json"
output_file_name = "out.dyn"

# music_name = "0.ogg"
# Automatic detect music name

# {line1: side1, line2: side2, ...}
# sides: 0 = down, 1 = left, 2 = right
linelist = {24: 0, 5: 1, 26: 1, 4: 2, 25: 2}

DYNODE_VERSION = "v0.1.13.2"

bpm = 120.
startTime = 0.
meter = 4

def convertTime(a):
	t = 60000 / bpm * (a[0] + a[1] / a[2]) + startTime
	return t

def notesCount(lines):
	sum = 0
	i = 0
	for line in lines:
		sum += line["numOfNotes"]
		print(i, line["numOfNotes"])
		i += 1
	return sum

ds = []
def addLineNotes(l, side = 0):
	minp = 1e9
	maxp = -1e9
	for n in l["notes"]:
		d = {}

		d["side"] = float(side)
		d["width"] = n["size"]
		if side != 0:
			d["width"] *= 2

		type = n["type"]
		if type == 1:
			d["noteType"] = 0.
		if type == 2:
			d["noteType"] = 2.
		if type == 3 or type == 4:
			d["noteType"] = 1.

		d["position"] = n["positionX"] / 200 + 2.5

		if type == 2:
			d["lastTime"] = convertTime(n["endTime"]) - convertTime(n["startTime"])
		else:
			d["lastTime"] = 0.

		d["time"] = convertTime(n["startTime"])

		minp = min(n["positionX"], minp)
		maxp = max(n["positionX"], maxp)

		ds.append(d)
	return [minp, maxp]

import json

file = open(input_file_name, 'r')
content = file.read()

text = json.loads(content)
lines = text["judgeLineList"]

notesCount(lines)

bpm = text["BPMList"][0]["bpm"]
startTime = convertTime(text["BPMList"][0]["startTime"])

for id, s in linelist.items():
	addLineNotes(lines[id], s)

res = {"backgroundPath": "", "chartPath": "", "videoPath": "", "version": DYNODE_VERSION}

# res["musicPath"] = music_name
res["musicPath"] = text["META"]["song"]

charts = {}
charts["notes"] = ds
charts["title"] = text["META"]["name"]
charts["sidetype"] = ["PAD", "PAD"]
charts["difficulty"] = 5
charts["bpm"] = bpm
charts["barpm"] = bpm / meter
res["charts"] = charts

timingPoints = {}
timingPoints["beatLength"] = 60000 / bpm
timingPoints["time"] = startTime
timingPoints["meter"] = meter
res["timingPoints"] = [timingPoints]

output = open(output_file_name, 'w')
output.write(json.dumps(res, sort_keys = True))