import tkinter as tk
import json
import time
import keyboard
import mouse
import subprocess as sp

# Wassup man.

class TextDisplay:
  def __init__(self, root, txt, fontSize, BgC, FgC, padX, padY):
    self.text = None
    self.createText(root, txt, fontSize, BgC, FgC, padX, padY)

  def createText(self, r, t, f, B, F, X, Y):
    self.text = tk.Label(
      r,
      text=t,
      font=("Century Gothic", f),
      bg=B,
      fg=F
    )
    self.text.pack(padx=X, pady=Y)

class PButton:
  def __init__(self, guiRef, root, id, txt, x, cmndCallback):
    self.id = id
    self.txt = txt
    self.x = x
    self.btn = None
    self.guiRef = guiRef
    self.isAssigning = False
    self.command = lambda: cmndCallback(self.id)
    if(self.id[0] == 'H'):
      self.CreateButton(root, "#171717", "#ededed", 7, 2, 120)
    if(self.id[0] == 'B'):
      self.CreateButton(root, "#a04040", "#ededed", 7, 3, 160)
    if(self.id[0] == 'P'):
      self.CreateButton(root, "#171717", "#ededed", 7, 5, 215)

  def CreateButton(self, root, _bg, _fg, _width, _height, _y):
    self.btn = tk.Button(
      root,
      command=self.command,
      bd=0,
      bg=_bg,
      fg=_fg,
      font=("Arial", 9, 'bold'),
      text=self.txt,
      width=_width,
      height=_height,
      cursor="hand2"
    )
    self.btn.pack()
    self.btn.place(x=self.x, y=_y)

class GUI:
  def __init__(self, root):
    self.root = root
    self.root.geometry("700x308")
    self.root.resizable(False, False)
    self.BgC = '#242424'
    self.FgC = "#ededed"
    self.root.configure(background=self.BgC)
    self.hotKeys = []
    self.padBtns = []
    self.posKeys = []
    self.appHookCallback = None
    self.appSetTogg = None
    self.appGetTogg = None
    self.createElements()

  # this function creates all the widgets for the application
  def createElements(self):
    self.title = TextDisplay(self.root, "Hot Mode", 24, self.BgC, self.FgC, 0, 15)
    self.author = TextDisplay(self.root, "DDJ-200 Pad Mode Controller v1.0", 10, self.BgC, self.FgC, 0, 0)

    onColor = '#509a42'
    offColor = '#a04040'
    toggColor = ''
    toggText = 'ON'
    def HandleToggle():
      self.appSetTogg('togg', None)
      tgld = self.appGetTogg()
      if(tgld):
        toggColor = onColor
        toggText = 'ON'
      else:
        toggColor = offColor
        toggText = 'OFF'
      self.toggBtn.configure(text=toggText, bg=toggColor)

    self.toggBtn = tk.Button(self.root,text=toggText,font=("Century Gothic", 9, 'bold'),width=5,height=4,bg='#509a42',fg=self.FgC,bd=0,command=HandleToggle,cursor="hand2")
    self.toggBtn.place(relx=0.5, rely=0.6,anchor=tk.CENTER)

    self.setDefaultBtn = tk.Button(self.root, text="Reset",font=("Century Gothic", 9, 'bold'),bg='#363636',fg=self.FgC,bd=0, width=5,cursor="hand2",command=self.setDfltSettings)
    self.setDefaultBtn.place(relx=0.5, rely=0.8, anchor=tk.CENTER)

    self.setHelpBtn = tk.Button(self.root, text="Help",font=("Century Gothic", 9, 'bold'),bg='#363636',fg=self.FgC,bd=0, width=5,cursor="hand2", command=self.openHelp)
    self.setHelpBtn.place(relx=0.5, rely=0.9, anchor=tk.CENTER)

    btnXs = [10, 70, 130, 190, 455, 515, 575, 635]
    btnNames = ['Hot\nCue', 'Beat\nLoop', 'Pad\nFX', 'Sampler']
    btnNames.extend(btnNames)
    for i in range(len(btnXs)):
      self.hotKeys.append(PButton(self, self.root, 'H' + str(i), '', btnXs[i], self.checkCommandID))
      self.padBtns.append(PButton(self, self.root, 'B' + str(i), btnNames[i], btnXs[i], self.checkCommandID))
      self.posKeys.append(PButton(self, self.root, 'P' + str(i), '', btnXs[i], self.checkCommandID))

  def setDfltSettings(self):
    fileNm = 'Hotkeys.json'
    newHtkeys = None
    newPos = None
    for i in range(2):
      with open('./Settings/' + fileNm) as file:
        data = json.load(file)
        dflts = data['DEFAULT']
        if (i == 0):
          data['Hotkeys'] = dflts
          newHtkeys = data
        elif (i > 0):
          data['Positions'] = dflts
          newPos = data
        fileNm = 'Positions.json'
    with open('./Settings/Hotkeys.json', "w") as htkeys:
      json.dump(newHtkeys, htkeys,  indent=4, sort_keys=True)
    with open('./Settings/Positions.json', "w") as pos:
      json.dump(newPos, pos,  indent=4, sort_keys=True)
    self.updateSettingsToGUI()

  def openHelp(self):
    try:
      program = "notepad.exe"
      fileNm = "README.txt"
      sp.Popen([program, fileNm])
    except:
      print('Error: README.txt renamed or not found')

  #this function configures all button hot key text to settings
  def updateSettingsToGUI(self):
    with open('./Settings/Hotkeys.json') as htKeysSettings:
      data = json.load(htKeysSettings)
      hotKeys = data['Hotkeys']
      for i in range(len(hotKeys)):
        self.hotKeys[i].btn.configure(text=hotKeys[i])
    with open('./Settings/Positions.json') as positionSettings:
      data = json.load(positionSettings)
      positions = data['Positions']
      for i in range(len(positions)):
        string = 'Position:\nX: '+str(positions[i]['x'])+'\nY: '+str(positions[i]['y'])
        self.posKeys[i].btn.configure(text=string)

  def resetAllHooks(self):
    keyboard.unhook_all()
    mouse.unhook_all()
    self.appHookCallback()

  def stopAllCurrentAssigningsBut(self, id):
    for i in range(len(self.padBtns)):
      if(self.hotKeys[i].id != id and self.padBtns[i].id != id):
        self.hotKeys[i].isAssigning = False
        self.posKeys[i].isAssigning = False

  # mode 'H' = Hotkeys
  # mode 'P' = Positions
  def dumpToSettings(self, row, value, mode):
    path = ''
    setting = ''
    if(mode == 'H'):
      path = './Settings/Hotkeys.json'
      setting = 'Hotkeys'
    if(mode == 'P'):
      path = './Settings/Positions.json'
      setting = 'Positions'
    data = json.load(open(path))
    data[setting][row] = value
    with open(path, "w") as origData:
      json.dump(data, origData, indent=4, sort_keys=True)

  def assign(self, btnCode, funcID):
    _swtchArr = []
    _idx = 0
    prevTogStatus = self.appGetTogg()

    def executeReset():
      self.resetAllHooks()
      _swtchArr[_idx].isAssigning = False
      self.updateSettingsToGUI()

    def execKeyboard(key):
      self.dumpToSettings(_idx, key.name, 'H')
      executeReset()

    def execMouse():
      x, y = mouse.get_position()
      pos = {
        "x" : x,
        "y" : y
      }
      self.dumpToSettings(_idx, pos, 'P')
      executeReset()

    if(btnCode == 'H'):
      _swtchArr = self.hotKeys
    if(btnCode == 'P'):
      _swtchArr = self.posKeys
    for i in range(len(self.padBtns)):
      if(_swtchArr[i].id[1] == funcID):
        if(_swtchArr[i].isAssigning == False):
          self.stopAllCurrentAssigningsBut(btnCode + funcID)
          self.updateSettingsToGUI()
          _idx = i
          _swtchArr[i].isAssigning = True
          if(btnCode == 'H'):
            _swtchArr[i].btn.configure(text='Press A\nKey...')
            keyboard.on_press(execKeyboard, suppress=False)
          if(btnCode == 'P'):
            _swtchArr[i].btn.configure(text='Right\nClick Pad\nButton in\nRekord\nbox')
            mouse.on_right_click(execMouse)
        else:
          self.resetAllHooks()
          _swtchArr[i].isAssigning = False
          self.updateSettingsToGUI()

  #this function is called when any of the buttons are pressed
  # Extracts the two characters and stores into variables
  def checkCommandID(self, id):
    btnCode = id[0] # Could be 'H' 'B' or 'P' (hot cue, pad mode or position)
    funcID = id[1] # Could be values from 0-7 and represent the identity of the function EG 2 = Deck 1 Pad FX
    if(btnCode == 'H' or btnCode == 'P'): # Hot Key Assign
      self.resetAllHooks()
      self.assign(btnCode, funcID)


class App:
  def __init__(self, gui):
    self.gui = gui
    self.root = gui.root
    self.toggled = True
    self.gui.appHookCallback = self.setKeyEvents
    self.gui.appSetTogg = self.setToggle
    self.gui.appGetTogg = self.getToggle
    self.setKeyEvents()
  
  def setToggle(self, togg, value):
    if(togg == 'togg'):
      self.toggled = not self.toggled
    elif(togg == 'set'):
      self.toggled = value

  def getToggle(self):
    return self.toggled

  def switchPadMode(self, index):
    if(self.toggled): 
      with open('./Settings/Positions.json') as p:
        data = json.load(p)
        positions = data['Positions']
        pX, pY = mouse.get_position()
        x = positions[index]['x']
        y = positions[index]['y']
        mouse.move(x, y)
        mouse.click()
        mouse.move(pX, pY)

  def checkPressEvent(self, key):
    with open('./Settings/Hotkeys.json') as hk:
      data = json.load(hk)
      hotKeys = data['Hotkeys']
      for i in range(len(hotKeys)):
        if(hotKeys[i] == key.name):
          self.switchPadMode(i)

  def setKeyEvents(self):
    keyboard.on_press(self.checkPressEvent)

root = tk.Tk()
root.title('Hot Mode - Created by Cole Mangio')
try:
  root.tk.call('wm', 'iconphoto', root._w, tk.PhotoImage(file='./Settings/icon.png'))
except:
  print('ERROR: No icon detected')
gui = GUI(root)
gui.updateSettingsToGUI()
app = App(gui)

app.root.mainloop()