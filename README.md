# ZeisMicroscopeControl
Control Interface for a Zeiss Microscopy microscope. Current available functionality includes changing the objective lens, controling a motorized XY stage, and adjusting a motorized focus.

## Required Packages:
You will need:
-tkinter
-threading

Additionaly, Zeiss's micro toolbox ([mtb](https://portal.zeiss.com/download-center/softwares/mic/software/13098/368510[P]/file/20221212_002)) will be required to interface with the microscope. You will need both the MTBConfig application (installed through the Zeiss Microscopy Installer or from the RDK zipped file) and the SDK.

After you have extracted the SDK, locate the file "MTBRTApi.dll". Update the path in the line `clr.AddReference(r"C:\Path\To\MTBRTApi.dll")`
