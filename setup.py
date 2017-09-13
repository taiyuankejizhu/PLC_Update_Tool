import platform
import sys
import usb1

if __name__ == '__main__':
    print(platform.python_version())

    with usb1.USBContext() as context:
        for device in context.getDeviceIterator(skip_on_error=True):
            print('ID %04x:%04x' % (device.getVendorID(), device.getProductID()), '->'.join(str(x) for x in ['Bus %03i' % (device.getBusNumber(), )] + device.getPortNumberList()), 'Device', device.getDeviceAddress())

    handle = context.openByVendorIDAndProductID(
        0x6001,
        0x0403,
        skip_on_error=True,
    )

    if handle is None:
        print('USB device is not online!')
    with handle.claimInterface(0):
        print('Clain interface !')

    sys.exit()
