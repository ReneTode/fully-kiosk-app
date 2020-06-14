# fully-kiosk-app
an app to control fully kiosk from appdaemon

this app expects that you add a new mqtt plugin (can connect to the same mqtt as you might already have)
the example settings are in the example file.

it creates a group in HA with several sensors for every tablet that you have configured in the yaml.

it also has several functions that you can call from other apps. those functions can be made more general, but can also be used as is)
i did completely rewrite it, because i use it a little different myself, so its possible i made some errors.
