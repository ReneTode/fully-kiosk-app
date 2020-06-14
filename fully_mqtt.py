import appdaemon.plugins.mqtt.mqttapi as mqtt
import json
import datetime
 
class tablet_mqtt(mqtt.Mqtt):

    def initialize(self):
        self.connected_tablets = []
        for id, device in self.args["devices"].items():
            if not self.entity_exists("sensor.tablet_{}".format(device)):
                self.set_state("sensor.tablet_{}".format(device), state = datetime.datetime.now().strftime("%H:%M:%S"))
        self.listen_event(self.message, event="fully", namespace = 'global')

    def message(self, event_name, data, kwargs):
        payload = json.loads(data["payload"])
        if data.get("topic", None) == None:
            return
        topicparts = data["topic"].split("/")
        if topicparts[1] == "deviceInfo":
            deviceID = topicparts[2]
            event = topicparts[1]
        else:
            deviceID = topicparts[3]
            event = topicparts[2]
        tablet_name = self.args["devices"].get(deviceID,"unknown_tablet")

        #self.log("message for {} ({}) came in".format(tablet_name, deviceID))

        if tablet_name == "unknown_tablet":
            self.log("{}: {}".format(topicparts[2],tablet_name))
            return

        if not (tablet_name in self.connected_tablets):
            if event == "deviceInfo":
                self.connect_tablet(tablet_name, json.loads(data["payload"]))
                self.log("connected tablet {}".format(tablet_name))
            else:
                return
                
        if event == "deviceInfo":
            self.set_state("sensor.tablet_{}".format(tablet_name), state = datetime.datetime.now().strftime("%H:%M:%S"), attributes = payload)
            brightness = int(payload["screenBrightness"])
            ha_brightness = int(self.get_state("input_number.tablet_{}_brightness".format(tablet_name)))
            if brightness != ha_brightness:
                self.call_service("input_number/set_value", entity_id = "input_number.tablet_{}_brightness".format(tablet_name), value = brightness)
        elif event == "onMotion":
            entity = "binary_sensor.tablet_{}_motion".format(tablet_name)
            self.set_state(entity, state = "on", attributes = {"device_class": "motion", "friendly_name": "Motion"})
            self.run_in(self.motion_off, 1, entity = entity)
        elif event == "screenOn":
            return
        elif event == "screenOff":
            return
        elif event == "pluggedAC":
            return
        elif event == "pluggedUSB":
            return
        elif event == "pluggedWireless":
            return
        elif event == "unplugged":
            return
        elif event == "networkReconnect":
            return
        elif event == "networkDisconnec":
            return
        elif event == "showKeyboard":
            return
        elif event == "hideKeyboard":
            return
        elif event == "powerOn":
            return
        elif event == "powerOff":
            return
        elif event == "onDarkness":
            return
        elif event == "onMovement":
            return
        elif event == "volumeUp":
            return
        elif event == "volumeDown":
            return
        elif event == "onQrScanCancelled":
            return
        elif event == "onScreensaverStart":
            return
        elif event == "onScreensaverStop":
            return
        elif event == "onDaydreamStart":
            return
        elif event == "onDaydreamStop":
            return
        elif event == "onBatteryLevelChanged":
            entity = "sensor.tablet_{}_battery".format(tablet_name)
            state = int(payload["level"])
            self.set_state(entity, state = state, attributes = {"friendly_name": "Battery"})
        elif event == "mqttDisconnected":
            entity_id = "binary_sensor.tablet_{}_mqtt".format(tablet_name)
            self.set_state(entity_id, state = "off", attributes = {"device_class": "connectivity", "friendly_name": "MQTT"})
        elif event == "mqttConnected":
            entity_id = "binary_sensor.tablet_{}_mqtt".format(tablet_name)
            self.set_state(entity_id, state = "on", attributes = {"device_class": "connectivity", "friendly_name": "MQTT"})
        elif event == "internetDisconnect":
            entity_id = "binary_sensor.tablet_{}_internet".format(tablet_name)
            self.set_state(entity_id, state = "off", attributes = {"device_class": "connectivity", "friendly_name": "Internet"})
        elif event == "internetReconnect":
            entity_id = "binary_sensor.tablet_{}_internet".format(tablet_name)
            self.set_state(entity_id, state = "on", attributes = {"device_class": "connectivity", "friendly_name": "Internet"})
        else:
            self.log("unknown event: {} for tablet: {}".format(event, tablet_name))
        #self.log(data)
        
    def motion_off(self, kwargs):
        self.set_state(kwargs["entity"], state = "off", attributes = {"device_class": "motion", "friendly_name": "Motion"})
        
    def connect_tablet(self, tablet_name, data):
        ip_address = data["ip4"]
        tablet_nr = ip_address.split(".")[3]
        entity_list = []
        
        '''
        ---------------------------------------------------------
        this part can only be used if you got the entities app from Rene Tode working
        ---------------------------------------------------------
        entities_app = "create_entities_tablet_{}".format(tablet_name)
        
        entity_id = "input_number.tablet_{}_volume".format(tablet_name)
        settings = {"platform": "input_number", "initial": 50, "component_type": "tablet_volume", "attributes": {"initial":50, "min": 0, "max": 100, "step": 10, "mode": "slider", "tabletnr": tablet_nr, "friendly_name": "Volume"}} 
        self.get_app(entities_app).build_entity(entity_id, settings)
        entity_list.append(entity_id)
        
        entity_id = "input_number.tablet_{}_brightness".format(tablet_name)
        settings = {"platform": "input_number", "initial": 150, "component_type": "tablet_brightness", "attributes": {"initial":150, "min": 0, "max": 255, "step": 1, "mode": "slider", "tabletnr": tablet_nr, "friendly_name": "Brightness"}} 
        self.get_app(entities_app).build_entity(entity_id, settings)
        entity_list.append(entity_id)

        entity_id = "switch.tablet_{}_deurbel".format(tablet_name)
        settings = {"platform": "switch", "initial": "off", "component_type": "deurbel_fully", "attributes": {"tabletnr": tablet_nr, "friendly_name": "Deurbel"}} 
        self.get_app(entities_app).build_entity(entity_id, settings)
        entity_list.append(entity_id)

        entity_id = "switch.tablet_{}_restart".format(tablet_name)
        settings = {"platform": "switch", "initial": "off", "component_type": "restart_fully", "attributes": {"tabletnr": tablet_nr, "friendly_name": "Restart"}} 
        self.get_app(entities_app).build_entity(entity_id, settings)
        entity_list.append(entity_id)

        entity_id = "switch.tablet_{}_reload".format(tablet_name)
        settings = {"platform": "switch", "initial": "off", "component_type": "reload_fully", "attributes": {"tabletnr": tablet_nr, "friendly_name": "Reload"}} 
        self.get_app(entities_app).build_entity(entity_id, settings)
        entity_list.append(entity_id)

        -----------------------------------------------------------
        '''
        
        entity_id = "binary_sensor.tablet_{}_motion".format(tablet_name)
        self.set_state(entity_id, state = "off", attributes = {"device_class": "motion", "friendly_name": "Motion"})
        entity_list.append(entity_id)

        entity_id = "sensor.tablet_{}_battery".format(tablet_name)
        self.set_state(entity_id, state = 100, attributes = {"friendly_name": "Battery"})
        entity_list.append(entity_id)

        entity_id = "binary_sensor.tablet_{}_mqtt".format(tablet_name)
        self.set_state(entity_id, state = "off", attributes = {"device_class": "connectivity", "friendly_name": "MQTT"})
        entity_list.append(entity_id)

        entity_id = "binary_sensor.tablet_{}_internet".format(tablet_name)
        self.set_state(entity_id, state = "on", attributes = {"device_class": "connectivity", "friendly_name": "Internet"})
        entity_list.append(entity_id)

        entity_list.append("sensor.tablet_{}".format(tablet_name))
        entity_id = "group.tablet_{}".format(tablet_name)
        self.set_state(entity_id, state="off", attributes={"view": False, "hidden": False, "assumed_state": True, "entity_id": entity_list})
        self.log("new tablet connected: {}".format(tablet_name))
        self.connected_tablets.append(tablet_name)

    '''
    ----------------------------------------------------------------
    fuctions below this can be called with get_app from other apps like:
    self.get_app("fully_mqtt").sound_doorbell(tablet_nr = "xxx", ip_group = "xxx.xxx.xxx", tablet_port = "xxx", pw = "")
    self.get_app("fully_mqtt").reload(tablet_nr = "xxx", ip_group = "xxx.xxx.xxx", tablet_port = "xxx", pw = "") (reloads the start page)
    self.get_app("fully_mqtt").restart(tablet_nr = "xxx", ip_group = "xxx.xxx.xxx", tablet_port = "xxx", pw = "") (restarts the fully app)
    self.get_app("fully_mqtt").set_volume(tablet_nr = "xxx", ip_group = "xxx.xxx.xxx", tablet_port = "xxx", pw = "", volume = "xx") 
    self.get_app("fully_mqtt").set_brightness(tablet_nr = "xxx", ip_group = "xxx.xxx.xxx", tablet_port = "xxx", pw = "", brightness = "xx") 
    ----------------------------------------------------------------
    '''

    def sound_doorbell(self, kwargs):
        tabletnr = kwargs["tablet_nr"] # the last number from the IP address
        ipgroup = kwargs["ip_group"]  # the ip range where the tablet is in
        tabletport = kwargs["tablet_port"]
        pw = kwargs["tablet_pw"]
        sound = "" # any valid url to a soundfile (can be put in dashboards web directory)
        cmd = "playSound&url={}&loop=false".format(sound)
        url = "http://{}{}:{}/?password={}&cmd={}".format(ipgroup, tabletnr, tabletport, pw, cmd)
        self.log("doorbell {} triggered".format(tabletnr))
        try:
            response = requests.get(url, timeout=10)
        except requests.exceptions.ReadTimeout:
            self.log("{} commando timeout tablet {}".format(kwargs["cmd"],kwargs["tabletnr"]))
        except requests.exceptions.ConnectionError:
            self.log("i couldnt reach tablet {}".format(kwargs["tabletnr"]))
        except Exception as x:
            self.log("Unknown error: " +  x.__class__.__name__)

    def reload(self, kwargs):
        tabletnr = kwargs["tablet_nr"] # the last number from the IP address
        ipgroup = kwargs["ip_group"]  # the ip range where the tablet is in
        tabletport = kwargs["tablet_port"]
        pw = kwargs["tablet_pw"]
        cmd = "loadStartURL"
        url = "http://{}{}:{}/?password={}&cmd={}".format(ipgroup, tabletnr, tabletport, pw, cmd)
        try:
            response = requests.get(url, timeout=10)
        except requests.exceptions.ReadTimeout:
            self.log("{} commando timeout tablet {}".format(cmd,tabletnr))
        except requests.exceptions.ConnectionError:
            self.log("i couldnt reach tablet {}".format(kwargs["tabletnr"]))
        except Exception as x:
            self.log("Unknown error: " +  x.__class__.__name__)

    def restart(self, kwargs):
        tabletnr = kwargs["tablet_nr"] # the last number from the IP address
        ipgroup = kwargs["ip_group"]  # the ip range where the tablet is in
        tabletport = kwargs["tablet_port"]
        pw = kwargs["tablet_pw"]
        cmd = "restartApp"
        url = "http://{}{}:{}/?password={}&cmd={}".format(ipgroup, tabletnr, tabletport, pw, cmd)
        try:
            response = requests.get(url, timeout=10)
        except requests.exceptions.ReadTimeout:
            self.log("{} commando timeout tablet {}".format(cmd,tabletnr))
        except requests.exceptions.ConnectionError:
            self.log("i couldnt reach tablet {}".format(kwargs["tabletnr"]))
        except Exception as x:
            self.log("Unknown error: " +  x.__class__.__name__)

    def set_volume(self, kwargs):
        tabletnr = kwargs["tablet_nr"] # the last number from the IP address
        ipgroup = kwargs["ip_group"]  # the ip range where the tablet is in
        tabletport = kwargs["tablet_port"]
        pw = kwargs["tablet_pw"]
        volume = kwargs["volume"]
        counter = 1
        while counter < 4:
            cmd = "setAudioVolume&stream={}&level={}".format(counter, volume)
            url = "http://{}{}:{}/?password={}&cmd={}".format(ipgroup, tabletnr, tabletport, pw, cmd)
            try:
                response = requests.get(url, timeout=10)
            except requests.exceptions.ReadTimeout:
                self.log("{} commando timeout tablet {}".format(cmd,tabletnr))
            except requests.exceptions.ConnectionError:
                self.log("i couldnt reach tablet {}".format(kwargs["tabletnr"]))
            except Exception as x:
                self.log("Unknown error: " +  x.__class__.__name__)
                counter += 1

    def set_brightness(self, kwargs):
        tabletnr = kwargs["tablet_nr"] # the last number from the IP address
        ipgroup = kwargs["ip_group"]  # the ip range where the tablet is in
        tabletport = kwargs["tablet_port"]
        pw = kwargs["tablet_pw"]
        brighness = kwargs["brightness"]
        cmd = "setStringSetting&key=screenBrightness&value={}".format(brightness)
        url = "http://{}{}:{}/?password={}&cmd={}".format(ipgroup, tabletnr, tabletport, pw, cmd)
        try:
            response = requests.get(url, timeout=10)
        except requests.exceptions.ReadTimeout:
            self.log("{} commando timeout tablet {}".format(cmd,tabletnr))
        except requests.exceptions.ConnectionError:
            self.log("i couldnt reach tablet {}".format(kwargs["tabletnr"]))
        except Exception as x:
            self.log("Unknown error: " +  x.__class__.__name__)
            counter += 1
