'''Send a CCSDS packet to Yamcs with specified contents.'''

import argparse
import re
import socket
import struct
import sys
import time
from datetime import datetime, timezone


def ensure_room(b, desired_length):
    if len(b) >= desired_length:
        return b
    else:
        return b + bytearray(desired_length - len(b))


def print_packet(b):
    for offset in range(0, len(b), 16):
        limit = min(offset+16, len(b))
        bytes = ' '.join([b[i:i+1].hex() for i in range(offset, limit)])
        print(f'{offset:07d}    {bytes}')
    print(f'{len(b):07d}')


now_str = datetime.utcnow().isoformat(timespec='milliseconds')
parser = argparse.ArgumentParser(
    description='Send a packet with given APID and data',
    epilog=f'''\
The --length argument is the desired packet data length after any CCSDS
headers; the program will pad the packet with zero bytes, if necessary,
and calculate the correct packet length value to store in the primary
header.

You can specify the packet data bytes using --data, or you can fill in
packet fields individually using the --field (or -f) option. Each field
value optionally contains an offset, in bytes, from the prior field,
a Python struct format for the field, and a value.

The default timestamp for the secondary header is the current time. You
can override the packet time using the --time argument, which takes a
time in ISO 8601 format. Do not specify the time zone; UTC is assumed.

Examples:
    %(prog)s --apid 2047 --no-secondary-header
        Sends a CCSDS idle packet of minimal size (1 byte of data)
    %(prog)s --apid 100 --length 100
        Sends a packet with a secondary header and 100 zero bytes of payload
    %(prog)s --apid 100 --sequence-count 123 --data 010203
        Sends a packet with sequence count 123 and three bytes of data
    %(prog)s --apid 100 --time 2021-01-10T16:28:32 --length 10
        Sends a packet with a specified timestamp and length
    %(prog)s --apid 100 --field '>I:12345' --field 'B:10' --field '2:B:12'
        Sends a packet with three fields, and a gap of 2 bytes between the
        second and third field. The total payload size is 4+1+2+1=8.
''',
    formatter_class=argparse.RawDescriptionHelpFormatter)
parser.add_argument('--host', default='localhost',
    help='Hostname of Yamcs server')
parser.add_argument('--port', type=int, default=1235,
    help='UDP port to send telemetry to Yamcs data link')
parser.add_argument('--apid', type=int, required=True,
    help='CCSDS APID for the packet')
parser.add_argument('--sequence-count', '-n', type=int, default=0,
    help='The sequence count for the packet (default: 0)')
parser.add_argument('--no-secondary-header', action='store_true',
    help='If specified, no secondary header will be added')
parser.add_argument('--data', help='Packet data (hexadecimal), if specified')
parser.add_argument('--length', type=int, default=-1,
    help='Packet data length, if specified')
parser.add_argument('--field', '-f', dest='fields',
    metavar='[offset:]format:value', action='append',
    help='Packet field value')
parser.add_argument('--time', default=now_str,
    help='Timestamp to use in the secondary header')
parser.add_argument('--time-length', type=int, default=6,
    help='Length of time in secondary header (default: 6)')
parser.add_argument('--time-fraction-length', type=int, default=2,
    help='Length of fractional time within time field (default: 2)')
parser.add_argument('--verbose', '-v', action='store_true',
    help='Echo the packet to the console as well')
parser.add_argument('--dry-run', action='store_true',
    help='If specified, display the packet data but do not send to Yamcs')

args = parser.parse_args()

packet_time = datetime.fromisoformat(args.time).replace(tzinfo=timezone.utc) \
    .timestamp()

# Start with a zero-length payload.
payload = bytearray(0)

# Create the desired length payload, if specified.
payload = ensure_room(payload, args.length)

# Store the payload data, if specified.
if args.data is not None:
    if len(args.data)%2 != 0:
        print('--data requires a hexadecimal argument of even length')
        sys.exit(1)
    data = bytes.fromhex(args.data)
    payload = ensure_room(payload, len(data))
    payload[:len(data)] = data

# Store fields, if specified.
offset = 0
if args.fields is None:
    args.fields = []
for f in args.fields:
    components = f.split(':')
    if len(components) < 2:
        print('--field requires the form: [offset:]format:value')
        sys.exit(1)
    if len(components) >= 3:
        gap, fmt, value = components[:3]
    else:
        gap = 0
        fmt, value = components[:2]
    if re.search('[bBhHiIlLqQnN]', fmt) is not None:
        field = struct.pack(fmt, int(value))
    elif re.search('[efd]', fmt) is not None:
        field = struct.pack(fmt, float(value))
    else:
        # Else assume a string value
        field = struct.pack(fmt, value)
    offset += int(gap)
    payload = ensure_room(payload, offset + len(field))
    payload[offset:offset+len(field)] = field
    offset += len(field)

header2 = b''
if not args.no_secondary_header:
    seconds = int(packet_time)
    fraction = packet_time - seconds
    seconds_length = args.time_length - args.time_fraction_length
    format = '>'
    if seconds_length == 2:
        format += 'H'
    elif seconds_length == 4:
        format += 'I'
    elif seconds_length == 8:
        format += 'Q'
    else:
        print(f'Length of seconds field must be 2, 4, or 8: {seconds_length}')
        sys.exit(1)
    if args.time_fraction_length == 0:
        pass
    elif args.time_fraction_length == 2:
        format += 'H'
        ticks = round(fraction  * (2 ** 16))
    elif args.time_fraction_length == 4:
        format += 'I'
        ticks = round(fraction  * (2 ** 32))
    else:
        print(f'Length of fraction field must be 0, 2, or 4: {args.time_fraction_length}')
        sys.exit(1)
    if args.time_fraction_length > 0:
        header2 = struct.pack(format, seconds, ticks)
    else:
        header2 = struct.pack(format, seconds)

user_data = header2 + payload
user_data = ensure_room(user_data, 1)

apid_flags = args.apid & ((1 << 11) - 1)
if not args.no_secondary_header:
    apid_flags = apid_flags | (1 << 11)
seq_flags = (args.sequence_count & 0x3FFF) | 0xC000
header1 = struct.pack('>H H H', apid_flags, seq_flags, len(user_data)-1)

packet = header1 + user_data

if args.verbose or args.dry_run:
    print('Sent packet:')
    print_packet(packet)
if not args.dry_run:
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.sendto(packet, (args.host, args.port))
