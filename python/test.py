import ncs

with ncs.maapi.single_read_trans("", "system", db=ncs.RUNNING) as th:
        try:
            root = ncs.maagic.get_root(th)
            device = root.ncs__devices.device['Node-1']
            # Check whether loopback0 exists
            loopback0 = device.config.cisco_ios_xr__interface.Loopback['1']
            loopback0_ipv4_address = loopback0.ipv4.address.ip
            print(loopback0_ipv4_address)
        except Exception as e:
            print('loopback0 does not exist')