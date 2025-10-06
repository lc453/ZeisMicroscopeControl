
# ZeisMicroscopeControl

Control interface for a Zeiss Axio Imager microscope.  
Current functionality includes:

- Switching objective lenses  
- Controlling a motorized XY stage  
- Adjusting a motorized focus (Z-axis)  

---

## Requirements

### Python Packages
- `tkinter`  
- `threading`  
- `pythonnet`  
- `time`  

### Zeiss Micro Toolbox (MTB)

To interface with the microscope you need Zeiss’s **Micro Toolbox (MTB)**:

* Download: [Zeiss MTB](https://portal.zeiss.com/download-center/softwares/mic/software/13098/368510[P]/file/20221212_002)
* Install **MTBConfig** (via the Zeiss Microscopy Installer or from the RDK zip file)
* Extract the SDK and locate the file:

```
MTBRTApi.dll
```

Update the reference in your code to point to its location:

```python
clr.AddReference(r"C:\Path\To\MTBRTApi.dll")
```

---

## Notes

* Ensure the MTB SDK and configuration file (`*.mtb`) are correctly set up before running the interface.
* This repository currently provides a GUI template (built with `tkinter`) for microscope control.

