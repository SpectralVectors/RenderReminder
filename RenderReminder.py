bl_info = {
    'name': 'RenderReminder',
    'category': 'Render',
    'author': 'Spectral Vectors',
    'version': (0, 1, 7),
    'blender': (3, 00, 0),
    'location': 'Addon Preferences',
    'description': 'Sends an email upon render completion.'
}

import aud, bpy, datetime, smtplib, ssl

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
        name='Sound Select',
        items={
            ('ding', 'Ding', 'A simple bell sound'),
            ('coin', 'Coin', 'A Mario-like coin sound'),
            ('user', 'User', 'Load a custom sound file')
        },
        default = 'ding',
    )

    usersound: StringProperty(
        name='User Sound',
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
        row.operator("renderreminder.send_email", text='Demo / Test')
        row = layout.row()
        row.prop(self, "sendemail")
        row.prop(self, "includerender")
        row.prop(self, "playsound")
        row = layout.row()
        row.prop(self, "soundselect")
        row.prop(self, "usersound")

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
            with open(renderfile, 'rb') as f:
                # set attachment mime and file name, the image type is png
                mime = MIMEBase('image', 'png', filename=render)
                # add required header data:
                mime.add_header('Content-Disposition', 'attachment', filename=render)
                mime.add_header('X-Attachment-Id', '0')
                mime.add_header('Content-ID', '<0>')
                # read attachment file content into the MIMEBase object
                mime.set_payload(f.read())
                # encode with base64
                encoders.encode_base64(mime)
                # add MIMEBase object to MIMEMultipart object
                msg.attach(mime)
                f.close()

        context = ssl.create_default_context()

        if addon_prefs.sendemail:
            with smtplib.SMTP_SSL(smtp_server, port, context=context) as server:
                server.login(sender_email, password)
                server.sendmail(sender_email, receiver_email, msg.as_string())

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


classes = (
    RenderReminderAddonPreferences,
    RR_send_email,
)

def register():
    from bpy.utils import register_class
    for cls in classes:
        register_class(cls)
    bpy.app.handlers.render_complete.append(sendEmail)
    property = bpy.context.window_manager.operator_properties_last("render.render")
    property.write_still = True


def unregister():
    from bpy.utils import unregister_class
    for cls in reversed(classes):
        unregister_class(cls)
    bpy.app.handlers.render_complete.remove(sendEmail)
    property = bpy.context.window_manager.operator_properties_last("render.render")
    property.write_still = False

if __name__ == "__main__":
    register()