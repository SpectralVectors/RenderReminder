from bpy.types import AddonPreferences


from .lib import PluginInterface

from .plugin import *

plugins = PluginInterface.__subclasses__()


class RenderReminderAddonPreferences(*plugins, AddonPreferences):  # type: ignore
    bl_idname = __package__

    def draw(self, context):
        layout = self.layout

        # Draw Plugins
        for plugin in plugins:
            plugin.draw(self, layout)

        # Try Sending Notification
        row = layout.row()
        row.operator(
            "renderreminder.notification",
            text="Test Your Notification Settings",
            icon="PLAY",
        )
