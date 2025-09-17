import tkinter as tk
from tkinter import ttk
import threading
from threading import Thread, Lock

import time
# import the the common language runtime
# it is needed to use the MTB API dll
# in order to import clr, it is required to install python for .Net (pip install pythonnet) under windows
# running under linux has not been tested yet
import clr

bMovingAxis = False

# IMPORTANT: the reference to the current MTB dll needs to be set (possibly to the GAC)
# the version of the dll must be compatible to the MTB version
clr.AddReference(r"C:\Users\cvetk\Downloads\MTBSDK\MTBAPI\MTBRTApi.dll")

# import the MTB
from ZEISS import MTB
device_busy = threading.Event()

################################### 
# define changer position changed event
def onChangerPositionChanged(position):
    # in case, the changer position has changed, the current position is printed
    # a position of "0" indicates an invalid state
    print("Changer moved, current position: " + str(position))

# define changer position settled event
def onChangerPositionSettled(position):
    # in case, the changer position is settled, its current position is printed
    print("Changer settled on position: " + str(position))

# define continual position changed event
def onContinualPositionChanged(positions):
    # in case, the continual (servo/axis) position has changed, the current position is printed
    if bMovingAxis:
        print("Axis moved, current position: " + str(positions["µm"]) + " µm")
    else:
        # (info: a position of "0" indicates an invalid state only for servos, not for axes)
        print("Servo moved, current position: " + str(positions["%"]) + "%")

# define continual position settled event
def onContinualPositionSettled(positions):
    # in case, the continual (servo/axis) position is settled, its current position is printed
    if bMovingAxis:
        print("Axis settled on position: " + str(positions["µm"]) + " µm")
    else:
        print("Servo settled on position: " + str(positions["%"]) + "%")
###############################################


# Move a changer (objective changer or reflector changer)
def setChangerPosition(strID, position):
    changer = MTB.Api.IMTBChanger (mtbroot.GetComponent(strID))
    if position > changer.MaxPosition or position < 1:
        position = (position - 1) % (changer.MaxPosition) + 1
    device_busy.set()
    changerEvents.Advise(changer)
    print("Changing " + strID + " to position " + str(position))
    changer.SetPosition(mtbid, position, MTB.Api.MTBCmdSetModes.Synchronous)
    changerEvents.Unadvise(changer)
    device_busy.clear()

def startMove(strID, speed):
    axis = MTB.Api.IMTBAxis (mtbroot.GetComponent(strID))
    global bMovingAxis
    bMovingAxis = True
    device_busy.set()
    continualEvents.Advise(axis)
    print("Moving axis " + strID + " with speed " + str(speed))
    try:
        axis.Move(speed,"µm/s")
    except:
        print("move failed")


def stopMove(strID):
    axis = MTB.Api.IMTBAxis (mtbroot.GetComponent(strID))
    axis.Stop()
    continualEvents.Unadvise(axis)
    device_busy.clear()
    print("Stopping axis " + strID + " move.")


class CollapsibleSection(ttk.Frame):
    def __init__(self, parent, title="", *args, **kwargs):
        super().__init__(parent, *args, **kwargs)

        self.columnconfigure(0, weight=1)
        self._expanded = tk.BooleanVar(value=True)

        # Toggle button with title
        self.toggle = ttk.Checkbutton(
            self, text=title, style="Toolbutton",
            variable=self._expanded, command=self._toggle
        )
        self.toggle.grid(row=0, column=0, sticky="ew")

        # Container for child widgets
        self.container = ttk.Frame(self)
        self.container.grid(row=1, column=0, sticky="nsew")

    def _toggle(self):
        if self._expanded.get():
            self.container.grid(row=1, column=0, sticky="nsew")
        else:
            self.container.grid_remove()



def create_gui():
    root = tk.Tk()
    root.title("Microscope Control Program")
    root.geometry("500x600")

    # --- Objective Control ---
    if "MTBObjectiveChanger" in componentList:
        # Get the component as a changer so we can get its position information
        changer = MTB.Api.IMTBChanger (componentList["MTBObjectiveChanger"])
        obj_section = CollapsibleSection(root, "Objective Control")
        obj_section.pack(fill="x", pady=5, padx=5)
        obj_frame = obj_section.container

        # Objective buttons
        for i in range(1, changer.MaxPosition + 1):
            ttk.Button(obj_frame, text=f"Obj {i}", command=lambda pos=i: setChangerPosition("MTBObjectiveChanger",pos)).grid(row=0, column=i-1, padx=3, pady=3)

        # Prev / Next
        ttk.Button(obj_frame, text="Prev",command=lambda: setChangerPosition("MTBObjectiveChanger",changer.Position-1)).grid(row=1, column=0, padx=3, pady=3)
        ttk.Button(obj_frame, text="Next",command=lambda: setChangerPosition("MTBObjectiveChanger",changer.Position+1)).grid(row=1, column=1, padx=3, pady=3)


        # Binding keyboard controls for "prev" and "next"
        root.bind("<KeyPress-q>",lambda event: setChangerPosition("MTBObjectiveChanger",changer.Position-1))
        root.bind("<KeyPress-e>",lambda event: setChangerPosition("MTBObjectiveChanger",changer.Position+1))


    # --- Light Control ---
    if False: # We will focus on the other controls for now
        light_section = CollapsibleSection(root, "Light Control")
        light_section.pack(fill="x", pady=5, padx=5)

        light_frame = light_section.container
        light_var = tk.BooleanVar()
        ttk.Checkbutton(light_frame, text="Light On?", variable=light_var).pack(anchor="w", pady=3)
        ttk.Label(light_frame, text="Light Intensity").pack(anchor="w")
        ttk.Scale(light_frame, from_=0, to=100, orient="horizontal").pack(fill="x", pady=3)

    # --- Stage XY Control ---
    if ("MTBStageAxisY" in componentList and "MTBStageAxisX" in componentList):
        maxXYSpeed = 10000 # 10000 microns = 1 centimeter
        stage_xy_section = CollapsibleSection(root, "Stage XY Control")
        stage_xy_section.pack(fill="x", pady=5, padx=5)
        xyScale = tk.DoubleVar()
        def getXYSpeed():
            return (xyScale.get() * maxXYSpeed) / 100
        def increaseXYSpeed():
            if xyScale.get() >= 50.0:
                xyScale.set(100)
            else:
                xyScale.set(2*xyScale.get())    
        def decreaseXYSpeed():
            if xyScale.get() <= 0.1:
                xyScale.set(0.05)
            else:
                xyScale.set(xyScale.get()/2)
            

        xy_frame = stage_xy_section.container

        # Slider for XY Speed
        xyScale = ttk.Scale(xy_frame, from_=0, to=100, orient="horizontal")
        xyScale.grid(row=3, column=0, columnspan=3, sticky="ew", pady=3)
        xyScale.set(50)
        xy_frame.grid_columnconfigure(2,weight=1)

        # Arrow buttons for XY
        forwardButton = ttk.Button(xy_frame,text="▲")
        forwardButton.grid(row=0, column=1, pady=3, sticky="s")
        forwardButton.bind("<ButtonPress-1>", lambda event: startMove("MTBStageAxisY",getXYSpeed()))
        forwardButton.bind("<ButtonRelease-1>", lambda event: stopMove("MTBStageAxisY"))

        leftButton = ttk.Button(xy_frame, text="◀")
        leftButton.grid(row=1, column=0, padx=3, sticky="e")
        leftButton.bind("<ButtonPress-1>", lambda event: startMove("MTBStageAxisX", -getXYSpeed()))
        leftButton.bind("<ButtonRelease-1>", lambda event: stopMove("MTBStageAxisX"))

        rightButton = ttk.Button(xy_frame, text="▶")
        rightButton.grid(row=1, column=2, padx=3, sticky="w")
        rightButton.bind("<ButtonPress-1>", lambda event: startMove("MTBStageAxisX", getXYSpeed()))
        rightButton.bind("<ButtonRelease-1>", lambda event: stopMove("MTBStageAxisX"))

        backButton = ttk.Button(xy_frame, text="▼")
        backButton.grid(row=2, column=1, pady=3, sticky="n")
        backButton.bind("<ButtonPress-1>", lambda event: startMove("MTBStageAxisY", -getXYSpeed()))
        backButton.bind("<ButtonRelease-1>", lambda event: stopMove("MTBStageAxisY"))


    # Binding keyboard shortcuts
        root.bind("<KeyPress-w>", lambda event: (forwardButton.state(["pressed"]),startMove("MTBStageAxisY",getXYSpeed())))
        root.bind("<KeyRelease-w>", lambda event: (forwardButton.state(["!pressed"]),stopMove("MTBStageAxisY")))

        root.bind("<KeyPress-a>", lambda event: (leftButton.state(["pressed"]),startMove("MTBStageAxisX",-getXYSpeed())))
        root.bind("<KeyRelease-a>", lambda event: (leftButton.state(["!pressed"]),stopMove("MTBStageAxisX")))

        root.bind("<KeyPress-d>", lambda event: (rightButton.state(["pressed"]),startMove("MTBStageAxisX",getXYSpeed())))
        root.bind("<KeyRelease-d>", lambda event: (rightButton.state(["!pressed"]),stopMove("MTBStageAxisX")))
        
        root.bind("<KeyPress-s>", lambda event: (backButton.state(["pressed"]),startMove("MTBStageAxisY",-getXYSpeed())))
        root.bind("<KeyRelease-s>", lambda event: (backButton.state(["!pressed"]),stopMove("MTBStageAxisY")))

        root.bind("<KeyPress-=>", lambda event: increaseXYSpeed())
        root.bind("<KeyPress-hyphen>", lambda event: decreaseXYSpeed())
        

    # --- Stage Z Control ---
    if "MTBFocus" in componentList:
        maxZSpeed = 5000 # 5000 microns = 1/2 centimeter
        stage_z_section = CollapsibleSection(root, "Stage Z Control")
        stage_z_section.pack(fill="x", pady=5, padx=5)
        def getZSpeed():
            return (zScale.get() * maxZSpeed) / 100

        z_frame = stage_z_section.container

        # Create the scale and set the default value to 50%
        zScale = ttk.Scale(z_frame, from_=0, to=100, orient="horizontal")
        zScale.set(50)

        upButton = ttk.Button(z_frame, text="▲")
        upButton.pack(pady=3)
        upButton.bind("<ButtonPress-1>", lambda event: startMove("MTBFocus", getZSpeed()))
        upButton.bind("<ButtonRelease-1>", lambda event: stopMove("MTBFocus"))

        downButton = ttk.Button(z_frame, text="▼")
        downButton.pack(pady=3)
        downButton.bind("<ButtonPress-1>", lambda event: startMove("MTBFocus", -getZSpeed()))
        downButton.bind("<ButtonRelease-1>", lambda event: stopMove("MTBFocus"))

        zScale.pack(fill="x", pady=3)

        # Binding keyboard shortcuts for Z
        root.bind("<KeyPress-Up>", lambda event: (upButton.state(["pressed"]),startMove("MTBFocus",getZSpeed())))
        root.bind("<KeyRelease-Up>", lambda event: (upButton.state(["!pressed"]),stopMove("MTBFocus")))

        root.bind("<KeyPress-Down>", lambda event: (downButton.state(["pressed"]),startMove("MTBFocus",-getZSpeed())))
        root.bind("<KeyRelease-Down>", lambda event: (downButton.state(["!pressed"]),stopMove("MTBFocus")))
        
    # Log out of MTB before closing
    def on_closing():
        # log out of the MTB service
        connection.Logout(mtbid)
        connection.Close()
        root.destroy()

    root.protocol("WM_DELETE_WINDOW", on_closing)
    root.mainloop()


# -----------------------------
# main routine
# -----------------------------

# set IPC to zRPC to communicate with MTB 3.10.8 and higher
provider = MTB.Api.IpcTypeProvider
provider.Instance.Init(provider.IpcTypeEnum.Zrpc)

# start connection to MTB
connection = MTB.Api.MTBConnection()

# login to MTB
mtbid = connection.Login("en", "")

# get the mtbroot node
mtbroot = MTB.Api.IMTBRoot (connection.GetRoot(mtbid))

# find out the number of devices that are available on the Microscope
deviceCount = mtbroot.GetDeviceCount()

# create an empty device list and an empty components list
deviceList = []
componentList = {}

# create an event sink for changers
# --> needed to print output of changer events to the command line
changerEvents = MTB.Api.MTBChangerEventSink()

# add the event handlers for changing positions/settled positions of changers
changerEvents.MTBPositionChangedEvent += MTB.Api.MTBChangerPositionChangedHandler(onChangerPositionChanged)
changerEvents.MTBPositionSettledEvent += MTB.Api.MTBChangerPositionSettledHandler(onChangerPositionSettled)

changerEvents.ClientID = mtbid

# create an event sink for continuals (servos and axes)
# --> needed to print output of continual events to the command line
continualEvents = MTB.Api.MTBContinualEventSink()

# add the event handlers for changing positions/settled positions of continuals (servos and axes, axes are continuals, too)
continualEvents.MTBPositionChangedEvent += MTB.Api.MTBContinualPositionChangedHandler(onContinualPositionChanged)
continualEvents.MTBPositionSettledEvent += MTB.Api.MTBContinualPositionSettledHandler(onContinualPositionSettled)

continualEvents.ClientID = mtbid

# a list of available components is available in the MTB documentation
# MTB2011 API.chm - MTB Component IDs
# put all device objects in a device list
print(("Pulling Devices and Components..."))
for i in range(0, deviceCount):
    device = MTB.Api.IMTBDevice (mtbroot.GetDevice(i))
    deviceList.append(device)
    
    print("Device " + str(device))
    componentCount = device.GetComponentCount()
    for a in range(0, componentCount):
        component = MTB.Api.IMTBComponent (device.GetComponent(a))
        componentList.update({component.ID: component})
        print("\tComponent " + component.ID)
        if component.ID == "MTBStage":
            try:
                stage = MTB.Api.IMTBStage (component)
                print(stage.GetConfiguration())
                print(stage.AvailableCmdSetModes())
                print("success")
            except:
                print("oops")
print("Finished Pulling Components")


if __name__ == "__main__":
    create_gui()