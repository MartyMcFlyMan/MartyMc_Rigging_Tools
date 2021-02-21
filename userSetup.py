import maya.cmds as cmds
import sys

scripts_path = cmds.internalVar(usd=True)
sys.path.append(scripts_path.rpartition('scripts')[0] + 'prefs/scripts/MM_tools/')
sys.path.append(scripts_path.rpartition('scripts')[0] + 'prefs/scripts/other_tools/')
