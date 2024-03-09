bl_info = {
    "name": "RenderReminder",
    "category": "Render",
    "author": "Spectral Vectors, bonehead-animations, The-EpaG",
    "version": (1, 0, 0),
    "blender": (4, 00, 0),
    "location": "Addon Preferences",
    "description": "Send an email, play a sound and notify you upon render completion.",
    "support": "COMMUNITY",
}



import bpy

from bpy.app.handlers import persistent

from .preferences import RenderReminderAddonPreferences
from .notification import RR_Notification


classes = (
    RenderReminderAddonPreferences,
    RR_Notification,
)

@persistent
def autoNameRender(dummy):
    context = bpy.context
    scene = context.scene
    render = scene.render
    wm = context.window_manager
    render_props = wm.operator_properties_last("render.render")
    render_props.write_still = True
    render.use_render_cache = True

    default_path = "/tmp\\"
    if render.filepath == default_path:
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        documents_path = os.path.expanduser("~/Documents/")
        file_format = render.image_settings.file_format.lower()
        filename = f"{timestamp}.{file_format}"
        render.filepath = os.path.join(documents_path, filename)


@persistent
def sendNotification(dummy):
    bpy.ops.renderreminder.notification()


@persistent
def writeRender(dummy):
    property = bpy.context.window_manager.operator_properties_last("render.render")
    property.write_still = True

def register():
    from bpy.utils import register_class

    for cls in classes:
        register_class(cls)

    bpy.app.handlers.load_post.append(autoNameRender)
    bpy.app.handlers.render_complete.append(sendNotification)
    bpy.app.handlers.depsgraph_update_pre.append(writeRender)


def unregister():
    from bpy.utils import unregister_class

    for cls in reversed(classes):
        unregister_class(cls)

    bpy.app.handlers.load_post.remove(autoNameRender)
    bpy.app.handlers.render_complete.remove(sendNotification)
    bpy.app.handlers.depsgraph_update_pre.remove(writeRender)


if __name__ == "__main__":
    register()
