# Labeled-petri-net
This is the implementation of petri net for our assignment.

Visit [here](https://github.com/ptmsk/labeled-petri-net) to get our code in github.

This assignment is separated into 6 files:
- **net.py** contains all neccessary implementation classes to visualize the simple petri net.
- **asm1b_i.py** constructs the Specialist petri net ```s_net``` and visualize desired transition system.
- **asm1b_ii.py** uses ```s_net``` from asm1b_i.py to tackle the problem.
- **asm2.py** constructs the Patient petri net ```p_net```.
- **asm3.py** merges ```s_net``` and ```p_net``` into the superimposed (merge) petri net ```m_net```
- **asm4.py** uses ```m_net``` and find reachable marking by firing one transition once.

Some packages are required for some actions:
* Visualize the petri net: graphviz
    -  Install pydot, pydotplus, pydot, pydot-ng:
    ```pip install pydot```, 
    ```pip install pydotplus```, 
    ```pip install pydot-ng```.
    - Access [this link](https://graphviz.org/download/?fbclid=IwAR0Rjs3pCSDG2Thb-EeJXg5iyJIxalLJRx6kr2s5B0uMnsP9KY4_4pQWTWI) 
    and download the latest 32-bit Windows install package.
    - Add ```C:\Program Files (x86)\Graphviz\bin``` to user environment path. 
    Click [here](https://docs.oracle.com/en/database/oracle/machine-learning/oml4r/1.5.1/oread/creating-and-modifying-environment-variables-on-windows.html?fbclid=IwAR2GjPHqy_IjfskaMmLQOCj1Rx2GUIyUZf9p4DFI9HtRN33lDjepg0kk54Q#GUID-DD6F9982-60D5-48F6-8270-A27EC53807D0)
    to know more about it.
    - Add ```C:\Program Files (x86)\Graphviz\bin\dot.exe``` to system environment path.
    - Install graphviz: ```pip install graphviz```. Restart computer to be enabled to use.
* Organizing graphical files and folders: os, shutil 
    - Install os: ```pip install os```
    - Install shutil: ```pip install shutil```
    


