# Post-Processing for BRT CFD analysis

This python script features an interactive UI to create images of front and side profiles of pressure and velocity. It also integrates a image viewer where the profiles can viewed with a slider. 

## Structure
* `scripts/` - Contains all python scripts. ui.py, fluent_processing.py ect
* `data/` - Contains all data required for the programm to work. excel force sheet, logos, jou sequence ect

## Setup Instructions
### 1. Clone repository
Clone repository by navigating to the preffered location where the programm should live in the terminal
and run:
```bash
git clone https://github.com/LumpiLumper/post_processing.git
```
### 2. Create Virtual enviorment
make a virtual python envirement by running the following command in the same location where you ran -git clone...
```bash
cd post_processing
python -m venv .venv
```
this will create a folder named venv in the same folder where \data and \scripts are. Depending on your python version 
and wheter you are using a powershell or cmd terminal use one of the following commands.
(To figure out which one open the venv folder an look if you have a folder named "Scripts" or "bin")
powershell:
```bash
.venv\Scripts\Activate.ps1
```
or 
```bash
.venv\bin\Activate.ps1
```
cmd:
```bash
.venv\Scripts\activate.bat
```
or
```bash
.venv\bin\activate.bat
```
this will activate the virtual enviorment
### 3. Install python requirements
With the next command we will install all python requirements (all required libaries) for the programm to run.
make sure your venv is activated before you run this command (it will say (venv) at the beginning of the line if it's activated)
```bash
pip install -r data\requirements.txt
```
### 4. Run Programm
Now you can run the program by double clicking the post_processing.bat file