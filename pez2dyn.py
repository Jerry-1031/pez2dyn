'''
Unzip .pez file, get .json file and .wav/.mp3/.ogg file;
Put .json, .wav/.mp3/.ogg and this pez2dyn.py file in a same directory;
Change input_file_name and output_file_name;
Choose which judgeline you want to convert;
Execute this Python file and get output;
Open the output with Dynode, press F5 to export .xml file.
'''

# Change it yourself
input_file_name = "1.json"
output_file_name = "1.dyn"

# music_name = "0.ogg"
# Automatic detect music name

# {line1: side1, line2: side2, ...}
# sides: 0 = down, 1 = left, 2 = right
# Example(autoDetect = False): linelist = {0: 0, 24: 1, 25: 2}

linelist = {}
autoDetect = True

DYNODE_VERSION = "v0.1.13.2"

lineNotesCount = {}
def notesCount(lines):
	sum = 0
	i = 0
	for line in lines:
		lineNotesCount[i] = line["numOfNotes"]
		sum += line["numOfNotes"]
		if autoDetect and line["numOfNotes"] != 0:
			linelist[i] = 0
		i += 1
	return sum

import json

file = open(input_file_name, 'r')
content = file.read()

text = json.loads(content)
lines = text["judgeLineList"]

print("Total Notes Count:", notesCount(lines))
print(lineNotesCount)
print(linelist)

BPMList = text["BPMList"]
bpmlist = []
starttimelist = []

BPMListLen = len(BPMList)
BPMList[0]["nowTime"] = 0.
now_time = 0.
for i in range(1, BPMListLen):
	BPMList[i]["nowTime"] = BPMList[i - 1]["nowTime"] + 60000. / BPMList[i - 1]["bpm"] * (BPMList[i]["startTime"][0] - BPMList[i - 1]["startTime"][0])

print(BPMList)

def convertTime(a):
	for i in range(BPMListLen + 1):
		if i == BPMListLen or a < BPMList[i]["startTime"]:
			return BPMList[i - 1]["nowTime"] + 60000. / BPMList[i - 1]["bpm"] * ((a[0] - BPMList[i - 1]["startTime"][0]) + a[1] / a[2])

bpm = text["BPMList"][0]["bpm"]
startTime = convertTime(text["BPMList"][0]["startTime"])
meter = 4

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

timingPoints = []
for b in BPMList:
	timingPoint = {}
	timingPoint["meter"] = meter
	timingPoint["time"] = b["nowTime"]
	timingPoint["beatLength"] = 60000 / b["bpm"]
	timingPoints.append(timingPoint)

res["timingPoints"] = timingPoints

output = open(output_file_name, 'w')
output.write(json.dumps(res, sort_keys = True))

print("Convert Success.")
print("Output File Name:", output_file_name)
