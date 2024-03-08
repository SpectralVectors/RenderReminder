from bpy.types import (
    AddonPreferences,
)

from .lib import (
    PluginInterface,
    Injectable,
    extract_vars,
)

from .plugin import *

plugins = PluginInterface.__subclasses__()

class RenderReminderAddonPreferences(AddonPreferences, Injectable):
    bl_idname = __name__

    def __init__(self):
        super().__init__()
        self._auto_inject()

    def _auto_inject(self):
        for plugin in self.plugins:
            vars = extract_vars(plugin)
            for name, value in vars.items():
                self.inject(f"{plugin.__name__}.{name}", value)
            print(f"{plugin.__name__} injected")

    def draw(self, context):
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