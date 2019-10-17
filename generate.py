import requests
import urllib.request
import time
import json
import tkinter
import tkinter.messagebox
from datetime import datetime
from datetime import timedelta
from bs4 import BeautifulSoup
from google_drive_downloader import GoogleDriveDownloader as gdd

# IDs for the Google Form
nameEntry = '156144986' # Replace ' ' with '+'
dateEntry = '263450907' # yyyy-mm-dd
timeEntry = '117690303' # hh:mm
formUrl   = 'https://docs.google.com/forms/d/e/1FAIpQLSfgL6_yMV2PPBxgZUXiFO_rSpyVpGywscx37uDgcMr9b6g7Yw/viewform'

# Store all frames based on how many workshops are desired
frames = []

# Hold all possible workshops (all options in Google Form dropdown)
possibleWorkshops = []

# Read all template files and store them in variables as strings
topFile = open("templates/top.html", "r")
top = topFile.read()
topFile.close()

bottomFile = open("templates/bottom.html", "r")
bottom = bottomFile.read()
bottomFile.close()

imageTemplateFile = open("templates/image.html", "r")
imageTemplate = imageTemplateFile.read()
imageTemplateFile.close()

textTemplateFile = open("templates/text.html", "r")
textTemplate = textTemplateFile.read()
textTemplateFile.close()

buttonTemplateFile = open("templates/button.html", "r")
buttonTemplate = buttonTemplateFile.read()
buttonTemplateFile.close()

lineSpacerFile = open("templates/spacer.html")
lineSpacer = lineSpacerFile.read()
lineSpacerFile.close()



def endProgram():
    exit()

def readJSON(filename):
    # Open the JSON file and read the data
    file = open(filename, "r")
    data = file.read()
    file.close()

    return json.loads(data)

# Ensure the entered workshop quantity and date makes sense before continuing
def checkValues():
    # Ensure the user enters the date in the correct format (yyyy-mm-dd)
    try:
        date = datetime.strptime(startDateVar.get(), '%Y-%m-%d').date()
        dayOfWeek = datetime.strftime(date, '%A')
        daysFromMon = int(datetime.strftime(date, '%w')) - 1
    except:
        tkinter.messagebox.showerror("Invalid Date!", "The date must be of format (yyyy-mm-dd)!")
        return

    # Ensure the user enters an integer for the number of workshops
    try:
        int(numWorkshopsVar.get())
    except:
        tkinter.messagebox.showerror("Invalid Quantity!", "Please enter a whole number for the workshop quantity!")
        return

    # Show an error if the user leaves the workshop field blank or enters a number less than one
    if numWorkshopsVar.get() == "":
        tkinter.messagebox.showerror("Empty Quantity!", "Please enter a workshop quantity!")
        return
    elif int(numWorkshopsVar.get()) <= 0:
        tkinter.messagebox.showerror("Empty Value!", "You need to make at least one workshop!")
        return
    # Warn the user if they try to make more than 5 workshops (to prevent typos)
    elif int(numWorkshopsVar.get()) > 5:
        largeQuantity = tkinter.messagebox.askquestion("Large Quantity", str(numWorkshopsVar.get()) + " workshops is a lot!\nDo you want to continue with this amount?")
        if largeQuantity == "yes":
            pass
        else:
            return

    # Ensure the field is not left blank
    if startDateVar.get() == "":
        tkinter.messagebox.showerror("Empty Date!", "Please enter a date!")
        return

    # Suggest a day that's a monday if the user puts in a day that is not a monday
    if daysFromMon != 0:
        changeDate = tkinter.messagebox.askquestion("Invalid Date!", "The date you entered falls on a " + dayOfWeek + "!\nDid you mean " + str(date - timedelta(days=daysFromMon)) + '?')
        if changeDate == "yes":
            startDateVar.set(str(date - timedelta(days=daysFromMon)))
            print(startDateVar.get())
        else:
            return

    # If everything is okay, destroy the first window and continue with the program
    startupWindow.destroy()

def descPrompt(workshop):
    descAdderWindow = tkinter.Tk()
    descAdderWindow.protocol('WM_DELETE_WINDOW', endProgram)
    descAdderWindow.title("Add a Description")

    linkVar = tkinter.StringVar()

    descAdderFrame = tkinter.Frame(descAdderWindow)
    tkinter.Label(descAdderFrame, text="\"" + workshop + "\" has no description!\nAdd one now or press skip to add one later.").pack(pady=10)
    tkinter.Label(descAdderFrame, text="Description:").pack(anchor=tkinter.W)
    desc = tkinter.Text(descAdderFrame,height=8, width=50)
    desc.pack()
    tkinter.Label(descAdderFrame, text="Use %DATE% as a placeholder for the date of the workshop,\n%TIME1% for the start time, and %TIME2% for the end time.").pack(anchor=tkinter.W, pady=10)
    tkinter.Label(descAdderFrame, text="Image Link:").pack(pady=10)
    tkinter.Entry(descAdderFrame, textvariable=linkVar).pack(fill='x')

    tkinter.Button(descAdderFrame, text="Add", command=lambda: addDesc(descAdderWindow, workshop, desc.get("1.0", tkinter.END), linkVar.get())).pack(padx=10, pady=10)
    tkinter.Button(descAdderFrame, text="Skip", command=lambda: descAdderWindow.destroy()).pack(padx=10, pady=10)

    descAdderFrame.pack(padx=20, pady=20)
    descAdderWindow.mainloop()

def addDesc(window, workshop, desc, link):
    # Remove any carriage returns present in the description
    desc = desc.replace("\n", "")

    oldData = readJSON("desc.json")

    # Format the information about the workshop as JSON
    jsonToAdd = {"description":desc,"image":link}
    # Add this data to the wsData variable
    oldData[workshop] = jsonToAdd

    # Re-write the oldData to the file then close it
    oldDataString = str(oldData).replace("\'", "\"")

    file = open("desc.json", "w+")
    file.write(oldDataString)
    file.close()

    window.destroy()


# Get all spans from the Google Form
response = requests.get(formUrl)
data = BeautifulSoup(response.text, "html.parser")
spans = data.findAll('span')

# Add all workshop options to the possibleWorkshops array
for i in spans:
    if i["class"][0] == "quantumWizMenuPaperselectContent" and i.string != "Choose":
        possibleWorkshops.append(i.string)


# Convert string to JSON object
wsData = readJSON("desc.json")

for i in possibleWorkshops:
    hasDesc = False
    for j in wsData:
        if i == j:
            hasDesc = True
            break
    if hasDesc == False:
        descPrompt(i)


# Create the first window, and hold the program until the user continues
startupWindow = tkinter.Tk()
startupWindow.protocol('WM_DELETE_WINDOW', endProgram)
startupWindow.title("Mailchimp Generator")

# Configure first frame
numWorkshopsVar = tkinter.StringVar()
startDateVar = tkinter.StringVar()

startupFrame = tkinter.Frame(startupWindow)
tkinter.Label(startupFrame, text = "How Many Workshops?").pack()
tkinter.Entry(startupFrame, textvariable = numWorkshopsVar).pack(fill='x', pady = 10)
tkinter.Label(startupFrame, text = "On What Date is Monday of the Week?").pack()
tkinter.Entry(startupFrame, textvariable = startDateVar).pack(fill='x', pady = 10)
tkinter.Button(startupFrame, text = "Next", command = lambda: checkValues()).pack(side = tkinter.BOTTOM)
startupFrame.pack(padx=20, pady=20)

startupWindow.mainloop()

# Init. tkinter window
window = tkinter.Tk()
window.protocol('WM_DELETE_WINDOW', endProgram)
window.title("Mailchimp Generator")

numWorkshops = int(numWorkshopsVar.get())
startDate = startDateVar.get()
startDate = datetime.strptime(startDate, '%Y-%m-%d').date()
endDate = startDate + timedelta(days=4)
dateRange = datetime.strftime(startDate, '%B %-d') + " - " + datetime.strftime(endDate, '%B %-d')
top = top.replace("%DATERANGE%", dateRange)

# Arrays that are generated based on how many workshops are desired
# Holds the strings of HTML for each workshop
images  = [imageTemplate]  * numWorkshops
texts   = [textTemplate]   * numWorkshops
buttons = [buttonTemplate] * numWorkshops


# Add all frames to the frames array
for i in range(0, numWorkshops):
    frames.append(tkinter.Frame(window))

choiceVar = tkinter.IntVar()
dateVar = tkinter.StringVar()
startVar = tkinter.StringVar()
endVar = tkinter.StringVar()

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

#gdd.download_file_from_google_drive(file_id='1iytA1n2z4go3uVCwE__vIKouTKyIDjEq',
#                                    dest_path='./data/mnist.zip',
#                                    unzip=True)

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
        tkinter.messagebox.showinfo("Success!", "HTML file created and saved as \'output.html\'!")
        window.destroy()

# Ensure that wsData contains the latest JSON data before starting
wsData = readJSON("desc.json")

# Load first frame
frames[0].pack(padx=20, pady=20)

# Start window loop
window.mainloop()
