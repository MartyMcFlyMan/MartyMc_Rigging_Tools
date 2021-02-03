# Marty's Rigging Tools
## The project
Since I started rigging last year, I have wrote a couple of scripts to make the process faster and more enjoyable.

I made a UI that holds all the tools I made and makes them even more easy to use, but also to share.

mySKEL, the third tab of the ToolBox, is my first WIP autorigger. It currently does arms and legs, however many there may be.
It lacks in versatility for now because it was aimed at a project in particular, but in the future I will rework the code to allow for a more modular approach.

There is also a tool to rapidly create controllers and hierarchy on simple FK rigs.
It can be very useful for props or very basic characters.


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
