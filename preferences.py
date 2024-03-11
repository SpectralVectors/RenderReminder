from bpy.types import AddonPreferences


from .lib import PluginInterface

from .plugin import *

plugins = PluginInterface.__subclasses__()


class RenderReminderAddonPreferences(*plugins, AddonPreferences):  # type: ignore
    bl_idname = __package__

    def draw(self, context):
        print(f"[{__package__}]Draw Preferences")
        layout = self.layout

        # Draw Plugins
        for plugin in plugins:
            if not issubclass(plugin, PluginInterface):
                continue

            plugin.draw(self, layout)

        # Try Sending Notification
        row = layout.row()
        row.operator(
            "renderreminder.notification",
            text="Test Your Notification Settings",
            icon="PLAY",
        )
