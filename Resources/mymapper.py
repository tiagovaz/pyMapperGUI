import mapper

class MyMapper:
    def __init__(self):
        self.mon = mapper.monitor()
        self.mon.request_devices()
        self.mon.request_links_by_src_device_name("/*")

    def poll(self, time):
        self.mon.poll(time)

    def setLink(self, source, dest, options={}):
        self.mon.link(source, dest, options)

    def setConnection(self, source, dest, action, options={}):
        self.mon.poll(50)
        if action == "connect":
            self.mon.connect(source, dest, options)
        elif action == "disconnect":
            self.mon.disconnect(source, dest)

    def getConnectionBySignalFullNames(self, src, dest):
        self.mon.poll(50)
        return self.mon.db.get_connection_by_signal_full_names(src, dest)

    def getConnections(self):
        self.mon.poll(50)
        self.connections = [ i for i in self.mon.db.all_connections() ]
        return self.connections

    def getAllDevices(self):
        self.mon.poll(50)
        self.devices = [ i["name"] for i in self.mon.db.all_devices() ]
        return self.devices

    def getInputsFromDevice(self, device_name):
        self.getAllDevices()
        inputs_list = [ i for i in self.mon.db.inputs_by_device_name(device_name) ]
        return inputs_list

    def getOutputsFromDevice(self, device_name):
        self.getAllDevices()
        outputs_list = [ i for i in self.mon.db.outputs_by_device_name(device_name) ]
        return outputs_list

# petit debug
if __name__ == "__main__":
    m = MyMapper()
 #   print m.getAllDevices()
 #   print m.getInputsFromDevice('/om.1')
 #   print m.getOutputsFromDevice('/om.1')
 #   print m.Connect("/om.1", "/om.2")
    print m.getConnections()

