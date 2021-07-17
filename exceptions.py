class InvalidVRF(Exception):
    pass


class NoVRFSpecifiedWithIntInVRF(Exception):
    pass


class InvalidIntf(Exception):
    pass


class InvalidDeviceType(Exception):
    pass


class NoIntfIPSpecified(Exception):
    pass


class NoNXOSIntfIPSpecified(Exception):
    pass


class SubnetTooLarge(Exception):
    pass


class InvalidVlanID(Exception):
    pass


class InvalidNetworkID(Exception):
    pass


class InvalidInterfaceIP(Exception):
    pass


class InterfaceIPAddressNotInNetwork(Exception):
    pass


class VlanNotInVlanDB(Exception):
    pass
