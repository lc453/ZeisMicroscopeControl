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

# Move a changer (objective changer or reflector changer)
def setChangerPosition(strID, position):
    if position > 6 or position < 1:
        position = (position - 1) % (6) + 1
    print("Changing " + strID + " to position " + str(position))
    

def startMove(strID, speed):
    print("Moving axis " + strID + " with speed " + str(speed))


def stopMove(strID):
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
    root.title("Microscope Control Demo")
    root.geometry("500x600")

    # --- Objective Control ---
    if True:
        # Get the component as a changer so we can get its position information
        obj_section = CollapsibleSection(root, "Objective Control")
        obj_section.pack(fill="x", pady=5, padx=5)
        obj_frame = obj_section.container
        

        # Objective buttons
        for i in range(1, 6 + 1):
            ttk.Button(obj_frame, text=f"Obj {i}", command=lambda pos=i: setChangerPosition("MTBObjectiveChanger",pos)).grid(row=0, column=i-1, padx=3, pady=3)

        # Prev / Next
        ttk.Button(obj_frame, text="Prev",command=lambda: setChangerPosition("MTBObjectiveChanger",-1)).grid(row=1, column=0, padx=3, pady=3)
        ttk.Button(obj_frame, text="Next",command=lambda: setChangerPosition("MTBObjectiveChanger",1)).grid(row=1, column=1, padx=3, pady=3)

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
    if (True):
        maxXYSpeed = 10000 # 10000 microns = 1 centimeter
        stage_xy_section = CollapsibleSection(root, "Stage XY Control")
        stage_xy_section.pack(fill="x", pady=5, padx=5)
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

        # Sliders for X and Y
        xyScale = ttk.Scale(xy_frame, from_=0, to=100, orient="horizontal")
        xyScale.set(50)

        xy_frame.grid_columnconfigure(2,weight=1)

        # Arrow buttons for XY
        forwardButton = ttk.Button(xy_frame,text="▲")
        forwardButton.grid(row=0, column=1, sticky="s", pady=3)
        forwardButton.bind("<ButtonPress-1>", lambda event: startMove("MTBStageAxisY",getXYSpeed()))
        forwardButton.bind("<ButtonRelease-1>", lambda event: stopMove("MTBStageAxisY"))

        leftButton = ttk.Button(xy_frame, text="◀")
        leftButton.grid(row=1, column=0, sticky="e", padx=3)
        leftButton.bind("<ButtonPress-1>", lambda event: startMove("MTBStageAxisX", -getXYSpeed()))
        leftButton.bind("<ButtonRelease-1>", lambda event: stopMove("MTBStageAxisX"))

        rightButton = ttk.Button(xy_frame, text="▶")
        rightButton.grid(row=1, column=2, sticky="w", padx=3)
        rightButton.bind("<ButtonPress-1>", lambda event: startMove("MTBStageAxisX", getXYSpeed()))
        rightButton.bind("<ButtonRelease-1>", lambda event: stopMove("MTBStageAxisX"))

        backButton = ttk.Button(xy_frame, text="▼")
        backButton.grid(row=2, column=1, sticky="n", pady=3)
        backButton.bind("<ButtonPress-1>", lambda event: startMove("MTBStageAxisY", -getXYSpeed()))
        backButton.bind("<ButtonRelease-1>", lambda event: stopMove("MTBStageAxisY"))

        
        #xyScale.grid(row=3, column=0, columnspan=3, sticky="ew", pady=3)
        xyScale.grid(row=3, column=0, columnspan=100, sticky="ew", pady=3)

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
        root.bind("<KeyPress-minus>", lambda event: decreaseXYSpeed())
        


    # --- Stage Z Control ---
    if True:
        maxZSpeed = 5000 # 5000 microns = 1/2 centimeter
        stage_z_section = CollapsibleSection(root, "Stage Z Control")
        stage_z_section.pack(fill="x", pady=5, padx=5)
        def getZSpeed():
            return (zScale.get() * maxZSpeed) / 100

        z_frame = stage_z_section.container

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

        root.bind("<KeyPress-Up>", lambda event: (upButton.state(["pressed"]),startMove("MTBFocus",getZSpeed())))
        root.bind("<KeyRelease-Up>", lambda event: (upButton.state(["!pressed"]),stopMove("MTBFocus")))

        root.bind("<KeyPress-Down>", lambda event: (downButton.state(["pressed"]),startMove("MTBFocus",-getZSpeed())))
        root.bind("<KeyRelease-Down>", lambda event: (downButton.state(["!pressed"]),stopMove("MTBFocus")))

        
    # Log out of MTB before closing
    def on_closing():
        root.destroy()

    root.protocol("WM_DELETE_WINDOW", on_closing)
    root.mainloop()


# -----------------------------
# main routine
# -----------------------------





if __name__ == "__main__":
    create_gui()