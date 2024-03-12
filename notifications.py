from bpy.types import (
    Operator,
)

from .lib import PluginInterface

from .plugin import *

plugins = PluginInterface.__subclasses__()


class RR_Notification(Operator):
    """Test your notification settings first to ensure everything works before trusting a long render to it!"""

    bl_idname = "renderreminder.notification"
    bl_label = "Send Notification"
    bl_options = {"REGISTER", "UNDO"}

    def execute(self, context):
        # Get preferences
        prefs = context.preferences
        addon_prefs = prefs.addons["RenderReminder"].preferences

        # Execute Plugins
        for plugin in plugins:
            plugin.execute(addon_prefs, context)

        return {"FINISHED"}
