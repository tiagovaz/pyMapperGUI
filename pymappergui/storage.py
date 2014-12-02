import json
import mapper

class Storage:

    def __init__(self):
        pass

    # This code is based on webmapper code (https://github.com/radarsat1/webmapper)
    def serialise(self, monitor, devices_list):
        sources = {}
        destinations = {}
        connections = {}
        new_connections = []
        next_src = 0
        next_dest = 0
        next_connection = 0
        modeStr = {mapper.MO_BYPASS: 'bypass',
                   mapper.MO_LINEAR: 'linear',
                   mapper.MO_CALIBRATE: 'calibrate',
                   mapper.MO_EXPRESSION: 'expression'}
        boundStr = {mapper.BA_NONE: 'none',
                   mapper.BA_MUTE: 'mute',
                   mapper.BA_CLAMP: 'clamp',
                   mapper.BA_FOLD: 'fold',
                   mapper.BA_WRAP: 'wrap'}

        for device in devices_list:
            for c in monitor.db.connections_by_device_name(device):
                this_connection = {
                  'src': [ c['src_name'] ],
                  'dest': [ c['dest_name'] ],
                  'mute': c['muted'],
                  'mode': modeStr[c['mode']],
                  'srcMin': c['src_min'],
                  'srcMax': c['src_max'],
                  'destMin': c['dest_min'],
                  'destMax': c['dest_max'],
                  'expression': c['expression'],
                  'boundMin': boundStr[c['bound_min']],
                  'boundMax': boundStr[c['bound_max']]
                }
                # To get proper expression nomenclature
                # dest[0] = src[0] NOT y = x
                this_connection['expression'] = this_connection['expression'].replace('y', 'dest[0]').replace('x', 'src[0]')
                new_connections.append(this_connection);

        contents = {"fileversion": "2.1", "mapping": {
                            "connections": new_connections
                            }
                    }
        return json.dumps(contents, indent=4)

    def deserialise(self, monitor, mapping_json, devices):
        js = json.loads(mapping_json)

        #The version we're currently working with
        version = '';
        if 'fileversion' in js:
            version = js['fileversion']
        elif 'mapping' in js and 'fileversion' in js['mapping']:
            version = js['mapping']['fileversion']

        modeIdx = {'bypass': mapper.MO_BYPASS,
                   'linear': mapper.MO_LINEAR,
                   'calibrate': mapper.MO_CALIBRATE,
                   'expression': mapper.MO_EXPRESSION}
        boundIdx = {'none': mapper.BA_NONE,
                    'mute': mapper.BA_MUTE,
                    'clamp': mapper.BA_CLAMP,
                    'fold': mapper.BA_FOLD,
                    'wrap': mapper.BA_WRAP}

        m = js['mapping']

        # sources and destinations are lists, devices are split from the second '/' character
        srcdevs = devices['sources']
        destdevs = devices['destinations']
        links = [( str(x), str(y) ) for x in srcdevs for y in destdevs]
        for l in links:
            monitor.link(l[0], l[1], {})
            monitor.poll(10)
        for c in m['connections']:
            #The name of the source signal (without device, assuming 1 to 1 for now)
            srcsig = str(c['src'][0]).split('/')[2]
            #And the destination
            destsig = str(c['dest'][0]).split('/')[2]

            args = (str(c['src'][0]),
                    str(c['dest'][0]),
                    {})
            if 'mode' in c:
                args[2]['mode'] = modeIdx[c['mode']]
            if 'expression' in c:
                args[2]['expression'] = str(c['expression']
                                            .replace('src[0]', 'x')
                                            .replace('dest[0]', 'y'))
            if 'srcMin' in c:
                args[2]['src_min'] = c['srcMin']
            if 'srcMax' in c:
                args[2]['src_max'] = c['srcMax']
            if 'destMin' in c:
                args[2]['dest_min'] = c['destMin']
            if 'destMax' in c:
                args[2]['dest_max'] = c['destMax']
            if 'boundMin' in c:
                args[2]['bound_min'] = boundIdx[c['boundMin']]
            if 'boundMax' in c:
                args[2]['bound_max'] = boundIdx[c['boundMax']]
            if 'mute' in c:
                args[2]['muted'] = c['mute']

            # If connection already exists, use 'modify', otherwise 'connect'.
            # Assumes 1 to 1, again
            cs = list(monitor.db.connections_by_device_and_signal_names(
                (l[0]).split('/')[1], srcsig,
                (l[1]).split('/')[1], destsig) )
            if len(cs) > 0:
                monitor.modify_connection(args[0], args[1], args[2])
            else:
                monitor.connect(*args)

if __name__ == "__main__":
    m = mapper.monitor(autosubscribe_flags=mapper.SUB_DEVICE)
    m.request_devices()
    m.poll(100)
    devices = [i["name"] for i in m.db.all_devices()]

    s = Storage()

    for d in devices:
        print s.serialise(m, d)

