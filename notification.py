from bpy.types import (
    Operator,
)

from .preferences import RenderReminderAddonPreferences
from .lib import (
    PluginInterface,
    extract_vars,
)

class RR_Notification(Operator):
    """Test your notification settings first to ensure everything works before trusting a long render to it!"""

    bl_idname = "renderreminder.notification"
    bl_label = "Send Notification"
    bl_options = {"REGISTER", "UNDO"}

    @staticmethod
    def _filter_vars(addon_prefs, plugin:str):
        vars = dict(
                filter(
                    lambda var: var[0].startswith(plugin),
                    extract_vars(addon_prefs).items(),
                )
            )
        return dict(
                map(lambda var: (var[0].replace(f"{plugin}.", ""), var[1]), vars.items())
            )

    def execute(self, context):
        # Get preferences
        prefs = context.preferences
        addon_prefs: RenderReminderAddonPreferences = prefs.addons[__name__].preferences

        for plugin in self.plugins:
            if not issubclass(plugin, PluginInterface):
                continue

            plugin.execute(self._filter_vars(addon_prefs, plugin.__name__))

        return {"FINISHED"}
