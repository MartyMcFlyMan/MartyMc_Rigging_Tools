# Marty's Rigging Tools
## The project
Since I started rigging last year, I have wrote a bunch of scripts to make the process faster and more enjoyable.

I made a UI that holds all the tools I made and makes them even more easy to use and to share.

*mySKEL*, the third tab of the ToolBox, is my first WIP autorigger.
It currently does arm and leg Fkik setups with a reverse foot setup option available.
The next step for mySKEL will be to give cleanup options and lock controls attributes.

I also plan to implement error handling in the code, as it might be hard for a beginner 
user to understand the errors that will inevitably arise from using my tools.

*Simple Fk Rig*:
There is also a tool to rapidly create controllers and hierarchy on simple FK rigs.
It can be very useful for props or very basic characters.

*Other Tools*:
This folder will contain tools for stuff other than rigging.

It currently contains a tool I wrote that selects random vertices from an object or from a selection of points.
I wrote this tool for a team project where we needed to rapidly create many realistic props that often required
to have their surfaces broken. I made a UI for the tool that allowed my team members to use it easily.




## Installing MM_Tools:

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
