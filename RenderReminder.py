bl_info = {
    'name': 'RenderReminder',
    'category': 'Render',
    'author': 'Spectral Vectors',
    'version': (0, 1, 4),
    'blender': (3, 00, 0),
    'location': 'Addon Preferences',
    'description': 'Sends an email upon render completion.'
}

import aud, bpy, smtplib, ssl, datetime

from bpy.props import (StringProperty,
                       BoolProperty,
                       )
                       
from bpy.types import (Operator,
                       AddonPreferences,
                       )

from bpy.app.handlers import persistent

device = aud.Device()
sound = aud.Sound('')

def coinSound():
    handle = device.play(
                        sound
                        .triangle(1000)
                        .highpass(20)
                        .lowpass(2000)
                        .ADSR(0,0.5,1,0)
                        .fadeout(0.1,0.1)
                        .limit(0,1)
                        )

    handle = device.play(
                        sound
                        .triangle(1500)
                        .highpass(20)
                        .lowpass(2000)
                        .ADSR(0,0.5,1,0)
                        .fadeout(0.2,0.2)
                        .delay(0.1)
                        .limit(0,1)
                        )

class RenderReminderAddonPreferences(AddonPreferences):
    bl_idname = __name__

    sendemail: BoolProperty(
        name='Send Email Notification?',
        default=True,
    )

    playsound: BoolProperty(
        name='Play Sound Notification?',
        default=True,
    )

    sender_email: StringProperty(
        name="Send From",
        description=":",
        default="",
        maxlen=1024,
        )

    receiver_email: StringProperty(
        name="Send To",
        description=":",
        default="",
        maxlen=1024,
        )

    password: StringProperty(
        name="Password",
        description=":",
        default="",
        maxlen=1024,
        subtype='PASSWORD',
        )

    def draw(self, context):
        layout = self.layout
        row = layout.row()
        row.prop(self, "sender_email")
        row.prop(self, "password")
        row = layout.row()
        row.prop(self, "receiver_email")
        row.operator("renderreminder.send_email", text='Send Test Email')
        row = layout.row()
        row.prop(self, "sendemail")
        row.prop(self, "playsound")

class RR_send_email(Operator):
    """Display example preferences"""
    bl_idname = "renderreminder.send_email"
    bl_label = "Send Notification Email"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        preferences = context.preferences
        addon_prefs = preferences.addons[__name__].preferences
        sender_email = addon_prefs.sender_email
        receiver_email = addon_prefs.receiver_email
        password = addon_prefs.password

        port = 465  # For SSL
        smtp_server = "smtp.gmail.com"
        shortfilename = bpy.path.display_name_from_filepath(bpy.context.blend_data.filepath)
        longfilename = bpy.path.basename(bpy.context.blend_data.filepath)
        now = datetime.datetime.now()
        date_time = now.strftime("%H:%M:%S, %m/%d/%Y")

        message = f"""\
Subject: {shortfilename} - Render Complete!

{longfilename} finished rendering at {date_time}

- RenderReminder"""

        context = ssl.create_default_context()
        if addon_prefs.sendemail:
            with smtplib.SMTP_SSL(smtp_server, port, context=context) as server:
                server.login(sender_email, password)
                server.sendmail(sender_email, receiver_email, message)
        if addon_prefs.playsound:
            coinSound()
        return {'FINISHED'}


@persistent
def sendEmail(dummy):
    bpy.ops.renderreminder.send_email()


classes = (
    RenderReminderAddonPreferences,
    RR_send_email,
)

def register():
    from bpy.utils import register_class
    for cls in classes:
        register_class(cls)
    bpy.app.handlers.render_complete.append(sendEmail)


def unregister():
    from bpy.utils import unregister_class
    for cls in reversed(classes):
        unregister_class(cls)
    bpy.app.handlers.render_complete.remove(sendEmail)


if __name__ == "__main__":
    register()