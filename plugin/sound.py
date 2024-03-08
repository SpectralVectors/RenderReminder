from bpy.props import (
    StringProperty,
    BoolProperty,
    EnumProperty,
)
import aud

from ..lib import PluginInterface

class SoundPlugin(PluginInterface):
    sound_notification: BoolProperty(
        name="Play Sound Notification?",
        default=True,
    )  # type: ignore

    sound_select: EnumProperty(
        name="Sound",
        items={
            ("ding", "Ding", "A simple bell sound"),
            ("coin", "Coin", "A Mario-like coin sound"),
            ("custom", "Custom", "Load a custom sound file"),
        },
        default="ding",
    )  # type: ignore

    user_sound: StringProperty(
        name="User",
        description="Load a custom sound from your computer",
        subtype="FILE_PATH",
        default="",
        maxlen=1024,
    )  # type: ignore

    @staticmethod
    def execute(vars:list):
        device = aud.Device()

        def play_sound(frequency, lowpass, highpass, fadeout, delay=0):
            sound = aud.Sound("")
            device.play(
                sound.triangle(frequency)
                .highpass(highpass)
                .lowpass(lowpass)
                .ADSR(0, 0.5, 1, 0)
                .fadeout(fadeout, fadeout)
                .delay(delay)
                .limit(0, 1)
            )

        if not vars["sound_notification"]:
            return

        if vars["sound_select"] == "ding":
            play_sound(3000, 1000, 20, 1)
        if vars["sound_select"] == "coin":
            play_sound(1500, 2000, 20, 0.2, 0.1)
        if vars["sound_select"] == "custom":
            sound_file = str(vars["user_sound"])
            sound = aud.Sound(sound_file)
            device.play(sound)

    @staticmethod
    def draw(parent, layout):
        box = layout.box()
        box.label(text="Sound Settings", icon="SPEAKER")
        row = box.row()
        row.prop(parent, f"{SoundPlugin.__name__}.sound_select")
        row.prop(parent, f"{SoundPlugin.__name__}.user_sound")
        row = box.row()
        row.prop(parent, f"{SoundPlugin.__name__}.sound_notification")