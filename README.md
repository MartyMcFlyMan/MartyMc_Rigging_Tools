# Marty's Rigging Tools
## The project
Since I started rigging last year, I have wrote a couple of scripts to make the process faster and more enjoyable.

I made a UI that holds all the tools I made and makes them even more easy to use, but also to share.

mySKEL, the third tab of the ToolBox, is my first WIP autorigger. It currently does all the lower body (fk/ik legs and reverse foot setups) and allows for any number of legs.


## To use:

**1. Extract the folder 'MM_tools in :**

Drive:/Users/User/Documents/maya/version/prefs/scripts/

**2. Paste userSetup.py in :**

Drive:/Users/User/Documents/maya/version/scripts/
 
*If you already have a userSetup.py file, just copy and paste the code in your own file.*

 
**3. Make yourself a shelf button with this code :**

```
import rig_tools_ui
reload(rig_tools_ui)

rig_tools_ui.ui()
```
