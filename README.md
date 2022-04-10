# RenderReminder
<p align="center">
  <img width="444" height="250" src="/RRGIF.gif">
</p>

<p align="center">
  <img width="660" height="520" src="/RRScreenshot.png">
</p>

## What It Does
Sends an email and plays a sound to notify you when your Blender render is finished!

## How to Install and Use

Click the image below to view the Install Guide on YouTube:

[![Install and Use](https://img.youtube.com/vi/U2bitCl0p8w/0.jpg)](https://youtu.be/U2bitCl0p8w)

## How It Works
This addon uses Python _(smtplib, aud)_ to send an email and play a sound effect once your render is ready.

Blender has a system called App Handlers that run when specific events happen in the application. 

The notification function runs once Blender reports that a render has completed.

The addon will also play a short Blender synthesized sound effect when the render is finished. 

The sound could be one of two internally generated SFX, or you can load your own sound file.

The email and sound notifications can be used separately or in combination, selected via the checkboxes in the addon's preferences.

You can add multiple email addresses to the __'Send To:'__ field, separated by commas.

## Limitations
The addon will automatically name your render after the time the blend file was opened, and save it in your Documents folder if you do not specify another name and location.

It uses Gmail and you will need to make sure that [Allow less secure apps is set to ON](https://myaccount.google.com/lesssecureapps) to send the messages. 

I signed up for a separate Gmail account with lower security settings to use as my 'Send From' account, and that sends notification emails to my main email.

You can fork and customize for your own preferred email service.

It will work for images or animations, however, there may be issues with attachment file size limits if you're dealing with video.

FYI: In order to save the images the addon sets Blender's render option (write_still=True), it is set normally False. The same goes for render caching.
