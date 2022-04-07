bl_info = {
    'name': 'RenderReminder',
    'category': 'Render',
    'author': 'Spectral Vectors',
    'version': (0, 2, 0),
    'blender': (3, 00, 0),
    'location': 'Addon Preferences',
    'description': 'Send an email and play a sound upon render completion.'
}

import aud, bpy, datetime, pathlib, smtplib, ssl

from bpy.props import (StringProperty,
                       BoolProperty,
                       EnumProperty,
                       )
                       
from bpy.types import (Operator,
                       AddonPreferences,
                       )

from bpy.app.handlers import persistent

from email import encoders
from email.header import Header
from email.mime.base import MIMEBase
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

device = aud.Device()

def coinSound():
    sound = aud.Sound('')
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
def ding():
    sound = aud.Sound('')
    handle = device.play(
                        sound
                        .triangle(3000)
                        .highpass(20)
                        .lowpass(1000)
                        .ADSR(0,0.5,1,0)
                        .fadeout(0,1)
                        .limit(0,1)
                        )


class RenderReminderAddonPreferences(AddonPreferences):
    bl_idname = __name__

    soundselect: EnumProperty(
        name='Sound',
        items={
            ('ding', 'Ding', 'A simple bell sound'),
            ('coin', 'Coin', 'A Mario-like coin sound'),
            ('user', 'User', 'Load a custom sound file')
        },
        default = 'ding',
    )

    usersound: StringProperty(
        name='User',
        description='Load a custom sound from your computer',
        subtype='FILE_PATH',
        default='',
        maxlen=1024,
    )

    includerender: BoolProperty(
        name='Attach Render to Email?',
        default=True,
    )

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
        description="The email address used to send the notification / render",
        default="",
        maxlen=1024,
        )

    receiver_email: StringProperty(
        name="Send To",
        description="The email address(es) you want to receive the notification / render. Multiple emails can be entered, separated by a comma",
        default="",
        maxlen=1024,
        )

    password: StringProperty(
        name="Password",
        description="The password to the sender's email account",
        default="",
        maxlen=1024,
        subtype='PASSWORD',
        )

    def draw(self, context):
        layout = self.layout

        box = layout.box()
        label = box.label(text="Email Settings", icon="URL")
        row = box.row()
        row.prop(self, "sender_email")
        row.prop(self, "password")
        row = box.row()
        row.prop(self, "receiver_email")
        row = box.row()
        row.prop(self, "sendemail")
        row.prop(self, "includerender")
        
        box = layout.box()
        label = box.label(text="Sound Settings", icon="SPEAKER")
        row = box.row()
        row.prop(self, "soundselect")
        row.prop(self, "usersound")
        row = box.row()
        row.prop(self, "playsound")

        row = layout.row()
        row.operator("renderreminder.send_email", text='Test Your Notification Settings', icon='AUTO')

class RR_send_email(Operator):
    """Test your notification settings first to ensure everything works before trusting a long render to it!"""
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

        msg = MIMEMultipart()
        msg['From'] = sender_email
        msg['To'] = receiver_email
        msg['Subject'] = Header(f'{shortfilename} - Render Complete!', 'utf-8').encode()
        msg_content = MIMEText(f'{longfilename} finished rendering at {date_time}', 'plain', 'utf-8')
        # msg.attach(MIMEText(f'<html><body><h1>{shortfilename}</h1>' +
        #     '<p><img src="cid:0"></p>' +
        #     '</body></html>', 'html', 'utf-8'))
        msg.attach(msg_content)
        
        if addon_prefs.includerender:

            renderfile = bpy.context.scene.render.filepath
            render = bpy.path.basename(renderfile)
            file_extension = pathlib.Path(bpy.context.scene.render.filepath).suffix

            with open(renderfile, 'rb') as f:
                mime = MIMEBase('image', file_extension, filename=render)
                mime.add_header('Content-Disposition', 'attachment', filename=render)
                mime.add_header('X-Attachment-Id', '0')
                mime.add_header('Content-ID', '<0>')
                mime.set_payload(f.read())
                encoders.encode_base64(mime)
                msg.attach(mime)
                f.close()

        context = ssl.create_default_context()

        if addon_prefs.sendemail:
            with smtplib.SMTP_SSL(smtp_server, port, context=context) as server:
                server.login(sender_email, password)
                server.sendmail(sender_email, receiver_email.split(','), msg.as_string())

        if addon_prefs.playsound:
            if addon_prefs.soundselect == 'ding':
                ding()
            if addon_prefs.soundselect == 'coin':
                coinSound()
            if addon_prefs.soundselect == 'user':
                file = str(addon_prefs.usersound)
                sound = aud.Sound(file)
                handle = device.play(sound)

        return {'FINISHED'}

@persistent
def sendEmail(dummy):
    bpy.ops.renderreminder.send_email()

@persistent
def writeRender(dummy):
    property = bpy.context.window_manager.operator_properties_last("render.render")
    property.write_still = True

classes = (
    RenderReminderAddonPreferences,
    RR_send_email,
)

def register():
    from bpy.utils import register_class
    for cls in classes:
        register_class(cls)
    bpy.app.handlers.render_complete.append(sendEmail)
    bpy.app.handlers.depsgraph_update_pre.append(writeRender)

def unregister():
    from bpy.utils import unregister_class
    for cls in reversed(classes):
        unregister_class(cls)
    bpy.app.handlers.render_complete.remove(sendEmail)
    bpy.app.handlers.depsgraph_update_pre.remove(writeRender)

if __name__ == "__main__":
    register()