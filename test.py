import requests
import urllib.request
import time
from datetime import datetime
from datetime import timedelta
import tkinter
from bs4 import BeautifulSoup
from google_drive_downloader import GoogleDriveDownloader as gdd
import json

# %DATERANGE%: The span of the current week of workshops (e.g. October 14th - October 18th)
# %CONTENTSTART%
# %IMAGE%

# Read all template files and store them in variables as strings
topFile = open("top.html", "r")
top = topFile.read()
topFile.close()

bottomFile = open("bottom.html", "r")
bottom = bottomFile.read()
bottomFile.close()

imageTemplateFile = open("Image Template.html", "r")
imageTemplate = imageTemplateFile.read()
imageTemplateFile.close()

textTemplateFile = open("Text Template.html", "r")
textTemplate = textTemplateFile.read()
textTemplateFile.close()

buttonTemplateFile = open("Button Template.html", "r")
buttonTemplate = buttonTemplateFile.read()
buttonTemplateFile.close()

lineSpacerFile = open("Line Spacer.html")
lineSpacer = lineSpacerFile.read()
lineSpacerFile.close()

# Take input from the user for how many workshops they want in a given week
# TODO: make this part of the window
numWorkshops = int(input("How Many Workshops? "))
startDate = input("What is the date of the Monday of the week? (yyyy-mm-dd) ")
startDate = datetime.strptime(startDate, '%Y-%m-%d').date()
endDate = startDate + timedelta(days=4)
dateRange = datetime.strftime(startDate, '%B %-d') + " - " + datetime.strftime(endDate, '%B %-d')
top = top.replace("%DATERANGE%", dateRange)

images  = [imageTemplate]  * numWorkshops
texts   = [textTemplate]   * numWorkshops
buttons = [buttonTemplate] * numWorkshops
spacers = numWorkshops - 1

# Function to move through the frames based on the current frame
def increment(frameNumber):
    frames[frameNumber].pack_forget()


    # Convert string to datetime, then back to a nicely-formatted string (e.g. Thursday, October 17)
    date = datetime.strptime(dateVar.get(), '%Y-%m-%d').date()
    cleanDate = datetime.strftime(date, '%A, %B %-d')

    startTime = datetime.strptime(startVar.get(), '%H:%M')
    cleanStartTime = datetime.strftime(startTime, '%-I:%M %p')

    endTime = datetime.strptime(endVar.get(), '%H:%M')
    cleanEndTime = datetime.strftime(endTime, '%-I:%M %p')

    for i in wsData:
        if i == possibleWorkshops[choiceVar.get()]:

            formLink = formUrl + "?entry." + nameEntry + "=" + i.replace(" ", "+") + "&entry." + dateEntry + "=" + dateVar.get() + "&entry." + timeEntry + "=" + startVar.get()

            images[frameNumber] = images[frameNumber].replace("%IMAGE%", wsData[i]["image"])
            texts[frameNumber] = texts[frameNumber].replace("%TITLE%", possibleWorkshops[choiceVar.get()])
            texts[frameNumber] = texts[frameNumber].replace("%DESC%", wsData[i]["description"]).replace("%DATE%", cleanDate).replace("%TIME1%", cleanStartTime).replace("%TIME2%", cleanEndTime)
            buttons[frameNumber] = buttons[frameNumber].replace("%FORMLINK%", formLink)

    if frameNumber < numWorkshops - 1:
        frames[frameNumber + 1].pack(padx = 20, pady = 20)
    else:

        outputHTML = open("output.html", "w+")
        outputHTML.write(top)
        for i in range(0, numWorkshops):
            outputHTML.write(images[i])
            outputHTML.write(texts[i])
            outputHTML.write(buttons[i])
            outputHTML.write(lineSpacer)
        outputHTML.write(bottom)
        outputHTML.close()


# Init. tkinter window
window = tkinter.Tk()
window.title("GUI")

# Store all frames based on how many workshops are desired
frames = []

# Add all frames to the frames array
for i in range(0, numWorkshops):
    frames.append(tkinter.Frame(window))

# IDs for the Google Form
nameEntry = '156144986' # Replace ' ' with '+'
dateEntry = '263450907' # yyyy-mm-dd
timeEntry = '117690303' # hh:mm
formUrl   = 'https://docs.google.com/forms/d/e/1FAIpQLSfgL6_yMV2PPBxgZUXiFO_rSpyVpGywscx37uDgcMr9b6g7Yw/viewform'

#gdd.download_file_from_google_drive(file_id='1iytA1n2z4go3uVCwE__vIKouTKyIDjEq',
#                                    dest_path='./data/mnist.zip',
#                                    unzip=True)

# Get all spans from the Google Form
response = requests.get(formUrl)
data = BeautifulSoup(response.text, "html.parser")
spans = data.findAll('span')

# Hold all possible works
possibleWorkshops = []

f = open("desc.json", "r")
data = f.read()
f.close()

wsData = json.loads(data)

# Add all workshop options to the possibleWorkshops array
for i in spans:
    if i["class"][0] == "quantumWizMenuPaperselectContent" and i.string != "Choose":
        possibleWorkshops.append(i.string)

choiceVar = tkinter.IntVar()
dateVar   = tkinter.StringVar()
startVar  = tkinter.StringVar()
endVar    = tkinter.StringVar()

# Loop to add all labels, buttons, etc. to each frame
for i in range(0, len(frames)):
    tkinter.Label(frames[i], text = str(i + 1) + " of " + str(numWorkshops)).pack()

    for j in range(0, len(possibleWorkshops)):
        tkinter.Radiobutton(frames[i], text = possibleWorkshops[j], variable = choiceVar, value = j).pack(anchor=tkinter.W, side = tkinter.TOP)

    tkinter.Label(frames[i], text="Date: (yyyy-mm-dd)").pack(anchor = tkinter.W)
    tkinter.Entry(frames[i], textvariable = dateVar).pack(anchor = tkinter.W, pady = 10)

    tkinter.Label(frames[i], text="Start Time: (hh:mm)").pack(anchor = tkinter.W)
    tkinter.Entry(frames[i], textvariable = startVar).pack(anchor = tkinter.W, pady = 10)

    tkinter.Label(frames[i], text="End Time: (hh:mm)").pack(anchor = tkinter.W)
    tkinter.Entry(frames[i], textvariable = endVar).pack(anchor = tkinter.W, pady = 10)

    tkinter.Button(frames[i], text = "Next", command = lambda a=i: increment(a)).pack(side = tkinter.BOTTOM)



# Load first frame
frames[0].pack(padx=20, pady=20)

# Start window loop
window.mainloop()
