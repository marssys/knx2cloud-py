# -*- coding: utf-8 -*-

#
# Copyright (c) 2002-2017 WEINZIERL ENGINEERING GmbH
# All rights reserved.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE, TITLE AND NON-INFRINGEMENT. IN NO EVENT
# SHALL THE COPYRIGHT HOLDERS BE LIABLE FOR ANY DAMAGES OR OTHER LIABILITY,
# WHETHER IN CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION
# WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE
#

from ctypes import (
    CDLL, CFUNCTYPE, POINTER,
    c_int, c_void_p, c_char_p,
    c_uint, c_ubyte,
    pointer, create_string_buffer
)

# defined constants from kdrive
# KDRIVE_INVALID_DESCRIPTOR = -1
# KDRIVE_ERROR_NONE = 0
# SERIAL_NUMBER_LENGTH = 6

# load the kdriveExpress
kdrive = CDLL('libkdriveExpress.so')

# Enable to use the kdrive access packet trace
kdrive_packet_trace = False

# IP
knx_ip = "192.168.1.47"

# PORT
knx_port = "3671"

# The KNX Group Address (destination address) we use to send with
address = 0x901

# the error callback pointer to function type
ERROR_CALLBACK = CFUNCTYPE(None, c_int, c_void_p)

# the event callback pointer to function type
EVENT_CALLBACK = CFUNCTYPE(None, c_int, c_uint, c_void_p)

# the telegram callback pointer to function type
TELEGRAM_CALLBACK = CFUNCTYPE(None, POINTER(c_ubyte), c_uint, c_void_p)

# Logging levels (not available from the library)
KDRIVE_LOGGER_FATAL = 1
KDRIVE_LOGGER_INFORMATION = 6

# Conversion IP:PORT to C style
connect_address_s = knx_ip + ":" + knx_port
ca_c = connect_address_s.encode('utf-8')
connect_address = c_char_p(ca_c)


def main():
    # Configure the logging level and console logger
    kdrive.kdrive_logger_set_level(KDRIVE_LOGGER_INFORMATION)
    kdrive.kdrive_logger_console()

    # We register an error callback as a convenience logger function to
    # print out the error message when an error occurs.
    error_callback = ERROR_CALLBACK(on_error_callback)
    kdrive.kdrive_register_error_callback(error_callback, None)

    # We create a Access Port descriptor. This descriptor is then used for
    # all calls to that specific access port.
    ap = kdrive.kdrive_ap_create()

    # We check that we were able to allocate a new descriptor
    # This should always happen, unless a bad_alloc exception is internally thrown
    # which means the memory couldn't be allocated.
    if ap == -1:
        kdrive.kdrive_logger(KDRIVE_LOGGER_FATAL, 'Unable to create access port. This is a terminal failure')
        while 1:
            pass

    # We register an event callback to notify of the Access Port Events
    # For example: KDRIVE_EVENT_TERMINATED
    event_callback = EVENT_CALLBACK(on_event_callback)
    kdrive.kdrive_set_event_callback(ap, event_callback, None)

    # IP Nat connection
    if kdrive.kdrive_ap_open_ip_nat(ap, connect_address) == 0:
        # Connect the Packet Trace logging mechanism
        # to see the Rx and Tx packets
        if kdrive_packet_trace:
            kdrive.kdrive_ap_packet_trace_connect(ap)

        # send a 1-Bit boolean GroupValueWrite telegram: on
        # buffer = (c_ubyte * 1)(1)
        # kdrive.kdrive_ap_group_write(ap, address, buffer, 1)

        # now we simply go into bus monitor mode, and display received telegrams
        key = c_int(0)
        telegram_callback = TELEGRAM_CALLBACK(on_telegram_callback)
        kdrive.kdrive_ap_register_telegram_callback(ap, telegram_callback, None, pointer(key))

        kdrive.kdrive_logger(KDRIVE_LOGGER_INFORMATION, "Entering BusMonitor Mode")
        kdrive.kdrive_logger(KDRIVE_LOGGER_INFORMATION, "Press [Enter] to exit the application ...")
        i = input('')

        # close the access port
        kdrive.kdrive_ap_close(ap)

    # releases the access port
    kdrive.kdrive_ap_release(ap)


def on_error_callback(e, user_data):
    len = 1024
    str = create_string_buffer(len)
    kdrive.kdrive_get_error_message(e, str, len)
    print('kdrive error {0} {1}'.format(hex(e), str.value))


def on_event_callback(ap, e, user_data):
    print('kdrive event {0}'.format(hex(e)))


def on_telegram_callback(telegram, telegram_len, user_data):
    l = list(telegram_len, telegram)
    hex = ' '.join('0x%02x' % b for b in l)
    print(hex)


def list(count, p_items):
    """Returns a python list for the given times represented by a pointer and the number of items"""
    items = []
    for i in range(count):
        items.append(p_items[i])
    return items


if __name__ == '__main__':
    main()
