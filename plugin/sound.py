from bpy.types import AddonPreferences
from bpy.props import (
    StringProperty,
    BoolProperty,
    EnumProperty,
)
import aud

from ..lib import PluginInterface


class SoundPlugin(PluginInterface, AddonPreferences):
    sound_notification: BoolProperty(  # type: ignore
        name="Play Sound Notification?",
        default=True,
    )

    sound_select: EnumProperty(  # type: ignore
        name="Sound",
        items={
            ("ding", "Ding", "A simple bell sound"),
            ("coin", "Coin", "A Mario-like coin sound"),
            ("custom", "Custom", "Load a custom sound file"),
        },
        default="ding",
    )

    user_sound: StringProperty(  # type: ignore
        name="User",
        description="Load a custom sound from your computer",
        subtype="FILE_PATH",
        default="",
        maxlen=1024,
    )

    @staticmethod
    def execute(preferences, context):
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

        if not preferences.sound_notification:
            return

        if preferences.sound_select == "ding":
            play_sound(3000, 1000, 20, 1)
        if preferences.sound_select == "coin":
            play_sound(1500, 2000, 20, 0.2, 0.1)
        if preferences.sound_select == "custom":
            sound_file = str(preferences.user_sound)
            sound = aud.Sound(sound_file)
            device.play(sound)

    @staticmethod
    def draw(parent, layout):
        box = layout.box()
        box.label(text="Sound Settings", icon="SPEAKER")
        row = box.row()
        row.prop(parent, "sound_select")
        row.prop(parent, "user_sound")
        row = box.row()
        row.prop(parent, "sound_notification")
