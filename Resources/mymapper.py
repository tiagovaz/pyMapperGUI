import mapper

class MyMapper():
    def __init__(self):
        self.mon = mapper.monitor(autosubscribe_flags=mapper.SUB_DEVICE)
        self.initMonitor()
        self.mo_calibrate = mapper.MO_CALIBRATE
        self.mo_expression = mapper.MO_EXPRESSION
        self.mo_reverse = mapper.MO_REVERSE
        self.mo_linear = mapper.MO_LINEAR
        self.mo_bypass = mapper.MO_BYPASS

        self.modes_dict = {'Bypass': mapper.MO_BYPASS, 'Calibrate': mapper.MO_CALIBRATE, 'Reverse': mapper.MO_REVERSE,
                           'Linear': mapper.MO_LINEAR, 'Expression': mapper.MO_EXPRESSION}
        # we often need to fetch reversed info from the dictionay above:
        self.modes_dict_rev = dict((v,k) for k, v in self.modes_dict.iteritems())
        self.OSC_devices = []

    def initMonitor(self):
        self.mon.request_devices()

    def poll(self, time):
        self.mon.poll(time)

    def setNetworkInterface(self, iface):
        self.admin = mapper.admin(iface=iface)
        self.mon = mapper.monitor(self.admin, autorequest=0)
        self.initMonitor()

    def setLink(self, source, dest, options={}):
        self.mon.link(source, dest, options)

    def Connect(self, src, dest, options=None):
        if not options: options = dict(mode=mapper.MO_LINEAR, bound_min=mapper.BA_WRAP,
                                       bound_max=mapper.BA_CLAMP)
        self.mon.poll(20)
        self.mon.connect(src, dest, options)

    def Disconnect(self, src, dest):
        self.mon.disconnect(src, dest)

    def Link(self):
        pass

    def Unlink(self):
        pass

    def getInputOutputDevices(self):
        "This is needed by storage code. Should return {sources: [/dev1, /dev2, /etc], destinations:[/dev3, /dev1]}"
        sources = []
        destinations = []
        devices = self.getAllDevices()
        for d in devices:
            if len(self.getInputsFromDevice(d)) != 0: # if device contains at least one input
                destinations.append(d)
            if len(self.getOutputsFromDevice(d)) != 0: # if device contains at least one output
                sources.append(d)
        in_out_devices = {'sources': sources, 'destinations': destinations}
        print in_out_devices
        return in_out_devices

    def Modify(self, src, dest, options=None):
        self.mon.modify_connection(src, dest, options)
        self.mon.poll(5)

    def getConnectionBySignalFullNames(self, src, dest):
        self.mon.poll(5)
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

    def createDevice(self, device_name):
        self.OSC_dev = mapper.device(device_name)
        self.OSC_dev.add_output("/x", 1, 'f', None, -1000, 1000)
        self.OSC_dev.poll(100)
        self.OSC_devices.append(self.OSC_dev)
        return self.OSC_dev

# petit debug
if __name__ == "__main__":
    m = MyMapper()
    #   print m.getAllDevices()
    #   print m.getInputsFromDevice('/om.1')
    #   print m.getOutputsFromDevice('/om.1')
    #   print m.Connect("/om.1", "/om.2")
    print m.getConnections()
