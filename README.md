## Instructions

<!--TOC-->

- [Instructions](#instructions)
  - [Summary](#summary)
  - [Important](#important)
  - [Windows](#windows)
    - [Report](#report)
    - [Notes](#notes)
  - [Mac](#mac)
    - [Report](#report-1)
    - [Notes](#notes-1)
  - [Linux](#linux)
    - [Report](#report-2)
- [Post-install](#post-install)
- [Other](#other)

<!--TOC-->

### Summary

*Open the readme.html file with a web browser for better reading.*

There are just a few steps to run the script:

1. you need Python, at least version 3.11
2. you will setup a Python virtual environment
3. you will install dependencies in the Python virtual environment
4. you will run the script

If you follow all the instructions below, depending on your operating system,  
the process should require just a few minutes. Take your time. I'm available   
for questions and clarifications on this: just ask.

See also [https://docs.python.org/3/library/venv.html#how-venvs-work](https://docs.python.org/3/library/venv.html#how-venvs-work)

**This video is just here for reference, to give you an idea of how it works.
Please follow the instructions i written below.**

<iframe width="560" height="315" src="https://www.youtube-nocookie.com/embed/Y21OR1OPC9A?si=dG3y68A5kAZE5Gg2" title="YouTube video player" frameborder="0" allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture; web-share" referrerpolicy="strict-origin-when-cross-origin" allowfullscreen></iframe>

### Important

**All the commands you see are to be executed one by one. Don't copy the whole command block,
but execute only one command at a time!**

### Windows

1. install Python 3.11 from the [**Windows store**](https://apps.microsoft.com/detail/9nrwmjp3717k?hl=en-us&gl=EN) which works out of the box. **Don't use the releases from the Python website**.
2. open the Powershell **as administrator**, then set the execution policy to `Unrestricted`.
   This needs to be done only once, not every time you create a virtual
   environment. See also
   [https://go.microsoft.com/fwlink/?LinkID=135170](https://go.microsoft.com/fwlink/?LinkID=135170)

   ```shell
   Set-ExecutionPolicy -ExecutionPolicy Unrestricted
   ```
 
3. close the **administrator** Powershell
4. open a normal Powershell
5. go into the project directory and proceed to create the virtual environment

   ```shell
   python3 -m venv .venv
   . .\.venv\Scripts\activate
   pip install -r requirements.txt
   ```

6. install npm from the [website](https://nodejs.org/en)
7. compile the frontend

   ```shell
   cd frontend
   npm install
   npm run build
   cd ..
   ```

8. run the script

   ```shell
   python app.py
   ```

9. to exit the Python virtual environment run

   ```shell
   deactivate
   ```

10. to run the script again run

    ```shell
    . .\.venv\Scripts\activate
    ```

    then start at step 6

11. open another Powershell and run the populate script and the continuous
    readings script

    ```shell
    . .\.venv\Scripts\activate
    cd scripts
    python -m populate
    cd 40_plant_module_system_sensor_reading
    python -m continuous_new_sensor_readings
    deactivate
    ```

12. to start the error simulation, replace the previous step with this one. You
    don't need to call the `continuous_new_sensor_readings` in this case

    ```shell
    . .\.venv\Scripts\activate
    cd scripts
    python -m error_populate
    deactivate
    ```

#### Report

See Linux instructions.

#### Notes

**Note: for security reasons I suggest putting the execution policy back to its   
original state when the script will not be needed anymore.**

These are not 1 to 1 instructions of what you just read but they should help you
undrestand better.

<iframe width="560" height="315" src="https://www.youtube-nocookie.com/embed/Z9Vm9Uxk5pA?si=pNmk-scCCmsu8bWE" title="YouTube video player" frameborder="0" allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture; web-share" referrerpolicy="strict-origin-when-cross-origin" allowfullscreen></iframe>

### Mac

1. open a terminal and go into the project directory
2. if not already installed, install Python

   ```shell
   brew install python
   ```

3. now create the virtual environment

   ```shell
   python3 -m venv .venv
   source .venv/bin/activate
   pip install -r requirements.txt
   ```

4. install npm from the [website](https://nodejs.org/en)
5. compile the frontend

   ```shell
   cd frontend
   npm install
   npm run build
   cd ..
   ```

6. run the script

   ```shell
   python app.py
   ```

7. to exit the Python virtual environment run

   ```shell
   deactivate
   ```

8. to run the script again run

   ```shell
   source .venv/bin/activate
   ```

   then start at step 6

9. see Linux for the populate scripts

#### Report

See Linux instructions.

#### Notes

*Neither the script nor these instructions have been tested on macOS.
At the moment I can test on various Linux distros and on a Windows 10 virtual
machine. As of this moment I don't have a method to test scripts on a Mac OS
system.*

*Everything should work because the steps are similar to Linux, but please keep
this in mind.*    

*You have accepted this as part of the project requirements (see gig FAQs)*

### Linux

1. open a terminal and go into the project directory
2. if you are on a new Debian-based system and never created a Python virtual
   environment before, most probably you need to install this package

   ```shell
   sudo apt install python3-venv
   ```

3. create the virtual environment

   ```shell
   python3 -m venv .venv
   . .venv/bin/activate
   pip install -r requirements.txt
   ```

4. install npm

   ```shell
   sudo apt install npm
   ```

5. compile the frontend

   ```shell
   cd frontend
   npm install
   npm run build
   ```

6. run the script

   ```shell
   python app.py
   ```

7. to exit the Python virtual environment run

   ```shell
   deactivate
   ```

8. to run the script again run

   ```shell
   . .venv/bin/activate
   ```

   then start at step 6

9. open another terminal and run the populate script and the continuous
   readings script

   ```shell
   . .venv/bin/activate
   cd scripts
   python -m populate
   cd 40_plant_module_system_sensor_reading
   python -m continuous_new_sensor_readings
   deactivate
   ```

10. to start the error simulation, replace the previous step with this one. You
    don't need to call the `continuous_new_sensor_readings` in this case

    ```shell
    . .venv/bin/activate
    cd scripts
    python -m error_populate
    deactivate
    ```

#### Report

These steps have only been tested on Debian GNU/Linux.

1. install Pandoc and textlive-extra

   ```shell
   sudo apt install pandoc texlive-latex-extra texlive-science imagemagick
   ```

2. move to the report directory

   ```shell
   cd report/report_finale
   ```

3. activate the Python virtual environment and install the requirements
4. compile the PDF


   ```shell
   ./compile.sh
   ```

## Post-install

**Once the server is running connect to [http://localhost:8080](http://localhost:8080)**

Credentials:
- `admin0`
- `password0`

## Other

To regenerate this HTML doc run:
   
```shell
pandoc -f markdown -t html -o readme.html README.md
```


