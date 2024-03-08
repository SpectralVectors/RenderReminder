from bpy.props import (
    StringProperty,
    BoolProperty,
    IntProperty,
)

from ..lib import PluginInterface
import bpy, smtplib, ssl, datetime

from email import encoders
from email.header import Header
from email.mime.base import MIMEBase
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart


class EmailPlugin(PluginInterface):
    email_notification: BoolProperty(
        name="Send Email Notification?",
        default=True,
    )  # type: ignore

    include_render_to_mail: BoolProperty(
        name="Attach Render to Email?",
        default=True,
    )  # type: ignore

    email_smtp_server: StringProperty(
        name="SMTP Server",
        description="The SMTP server your email provider uses",
        default="smtp.gmail.com",
        maxlen=1024,
    )  # type: ignore

    email_smtp_port: IntProperty(
        name="Port",
        description="The port number required by the server (commonly 465, 587, 995, 25 or 110)",
        default=465,
    )  # type: ignore

    email_sender_email: StringProperty(
        name="Send From",
        description="The email address used to send the notification / render",
        default="",
        maxlen=1024,
    )  # type: ignore

    email_receivers_email: StringProperty(
        name="Send To",
        description="The email address(es) you want to receive the notification / render. Multiple emails can be entered, separated by a comma",
        default="",
        maxlen=1024,
    )  # type: ignore

    email_password: StringProperty(
        name="Password",
        description="The password to the sender's email account",
        default="",
        maxlen=1024,
        subtype="PASSWORD",
    )  # type: ignore

    @staticmethod
    def execute(vars:list):
        # Get email settings
        email_smtp_server = vars["email_smtp_server"]
        email_smtp_port = vars["email_smtp_port"]
        email_sender_email = vars["email_sender_email"]
        email_receivers_email = vars["email_receivers_email"]
        email_password = vars["email_password"]
        include_render_to_mail = vars["include_render_to_mail"]
        email_notification = vars["email_notification"]


        if not email_notification:
            return

        # Get blend file
        blend_file = bpy.context.blend_data.filepath
        filename = (
            "untitled.blend"
            if blend_file == ""
            else bpy.path.display_name_from_filepath(blend_file)
        )
        long_filename = bpy.path.basename(blend_file)

        renderfile = bpy.context.scene.render.filepath
        render = bpy.path.basename(renderfile)
        file_extension = bpy.context.scene.render.file_extension[1:]

        # Get date
        date_time = datetime.datetime.now().strftime("%H:%M:%S, %m/%d/%Y")

        # Compose email
        msg = MIMEMultipart()
        msg["From"] = email_sender_email
        msg["To"] = email_receivers_email
        msg["Subject"] = Header(f"{filename} - Render Complete!", "utf-8").encode()
        msg_content = MIMEText(
            f"{long_filename} finished rendering {render} at {date_time}",
            "plain",
            "utf-8",
        )
        msg.attach(msg_content)

        # Attach render
        if include_render_to_mail:
            with open("%s.%s" % (renderfile, file_extension), "rb") as f:
                mime = MIMEBase("image", file_extension, filename=render)
                mime.add_header("Content-Disposition", "attachment", filename=render)
                mime.add_header("X-Attachment-Id", "0")
                mime.add_header("Content-ID", "<0>")
                mime.set_payload(f.read())
                encoders.encode_base64(mime)
                msg.attach(mime)
                f.close()

        # Send email
        ssl_context = ssl.create_default_context()
        with smtplib.SMTP_SSL(
            email_smtp_server, email_smtp_port, context=ssl_context
        ) as server:
            server.login(email_sender_email, email_password)
            server.sendmail(
                email_sender_email,
                email_receivers_email.split(","),
                msg.as_string(),
            )
    

    @staticmethod
    def draw(parent, layout):
        box = layout.box()
        box.label(text="Email Settings", icon="URL")
        row = box.row()
        split = row.split(factor=0.8)
        split.prop(parent, f"{EmailPlugin.__name__}.email_smtp_server")
        split.prop(parent, f"{EmailPlugin.__name__}.email_smtp_port")
        row = box.row()
        row.prop(parent, f"{EmailPlugin.__name__}.email_sender_email")
        row.prop(parent, f"{EmailPlugin.__name__}.email_password")
        row = box.row()
        row.prop(parent, f"{EmailPlugin.__name__}.email_receivers_email")
        row = box.row()
        row.prop(parent, f"{EmailPlugin.__name__}.email_notification")
        row.prop(parent, f"{EmailPlugin.__name__}.include_render_to_mail")