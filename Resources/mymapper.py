import mapper

class MyMapper():  #TODO: refactore this to heritage from mapper library
    def __init__(self):
        self.mon = mapper.monitor()
        self.mon.request_devices()
        self.mon.request_links_by_src_device_name("/*")

    def poll(self, time):
        self.mon.poll(time)

    def setLink(self, source, dest, options={}):
        self.mon.link(source, dest, options)

    def setSignalMin(self, signal, value):
        """receives a signal address and set the new min value from 'value'"""
        self.selectedSignal = self.getSignalObjectBySignalFullName(signal,
                                                                   "output")  #TODO: add a 'selected src/dest signal' attr for this class
        self.selectedSignal.set_max(value)

    # remember: Ranges are stored independently for each connection!
    def setSignalMax(self, signal, value):
        signal.set_max(value)

    def setNewConnection(self, source, dest, action, options=None): #TODO: make config file for default conn setup
        if not options: options = {'mode': mapper.MO_EXPRESSION,
                                   'expression': 'y=x',
                                   'src_min': 1,
                                   'bound_min': mapper.BA_WRAP,
                                   "bound_max": mapper.BA_CLAMP}
        self.mon.poll(20)
        if action == "connect":
            self.mon.connect(source, dest, options)
        elif action == "disconnect":
            self.mon.disconnect(source, dest)

    def getConnectionBySignalFullNames(self, src, dest):
        self.mon.poll(20)
        return self.mon.db.get_connection_by_signal_full_names(src, dest)

    def getSignalObjectBySignalFullName(self, dest, which):
        device = "/" + dest.split("/")[1]
        signal = "/" + "/".join(dest.split("/")[2:])
        if which == "input":
            return self.mon.db.get_input_by_device_and_signal_name(device, signal)
        elif which == "output":
            return self.mon.db.get_output_by_device_and_signal_name(device, signal)

    def getConnections(self):
        self.mon.poll(50)
        self.connections = [i for i in self.mon.db.all_connections()]
        return self.connections

    def getAllDevices(self):
        self.mon.poll(50)
        self.devices = [i["name"] for i in self.mon.db.all_devices()]
        return self.devices

    def getInputsFromDevice(self, device_name):
        self.getAllDevices()
        inputs_list = [i for i in self.mon.db.inputs_by_device_name(device_name)]
        return inputs_list

    def getOutputsFromDevice(self, device_name):
        self.getAllDevices()
        outputs_list = [i for i in self.mon.db.outputs_by_device_name(device_name)]
        return outputs_list

# petit debug
if __name__ == "__main__":
    m = MyMapper()
    #   print m.getAllDevices()
    #   print m.getInputsFromDevice('/om.1')
    #   print m.getOutputsFromDevice('/om.1')
    #   print m.Connect("/om.1", "/om.2")
    print m.getConnections()

