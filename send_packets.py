import argparse
import socket
import struct
import time
from datetime import datetime, timedelta, timezone


def send_packet(t, apid, sequence_count, value, s, dest):
    """Send a CCSDS-formatted packet."""
    packet_data = struct.pack('>Q I I', int(t*1000.0), sequence_count, value)
    apid_flags = apid & ((1 << 11) - 1)
    seq_flags = (sequence_count & (2**14 - 1)) | (3 << 14)
    header = struct.pack('>H H H', apid_flags, seq_flags, len(packet_data)-1)
    s.sendto(header+packet_data, dest)


def parse_iso_time(str):
    return datetime.fromisoformat(str).replace(tzinfo=timezone.utc)


parser = argparse.ArgumentParser(description='Send sample packets')
parser.add_argument('--host', default='localhost',
                    help='Yamcs hostname (default: localhost)')
parser.add_argument('--port', type=int, default=10015,
                    help='UDP port to use for sending packets (default: 1235)')
parser.add_argument('--apid', type=int, default=100,
                    help='packet APID to use (default: 100)')
parser.add_argument('--count', type=int, default=1,
                    help='how many packets to send (default: 1)')
parser.add_argument('--min', type=int, default=0,
                    help='minimum data value in sawtooth (default: 0)')
parser.add_argument('--max', type=int, default=2500,
                    help='maximum data value in sawtooth (default: 2500)')
parser.add_argument('--delay', type=int, default=50,
                    help='inter-packet delay in ms (default: 50)')
parser.add_argument('--start-time', type=parse_iso_time,
                    help='If specified, time for first packet (default: now)')
parser.add_argument('--delta-time', type=int,
                    help='If specified, gen time increment (default: delay)')
parser.add_argument('--verbose', action='store_true',
                    help='if specified, print detailed progress')

args = parser.parse_args()

s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
dest = (args.host, args.port)

value = args.min
delta = 1

if args.start_time:
    pkt_time = args.start_time.timestamp()
else:
    pkt_time = time.time()

for sequence_count in range(args.count):
    send_packet(pkt_time, args.apid, sequence_count, value, s, dest)
    if args.verbose:
        t = datetime.fromtimestamp(pkt_time, timezone.utc)
        print('Sent packet:')
        print('    value={} time={}'.format(value,
                t.strftime('%Y-%m-%dT%H:%M:%S.%fZ')))

    if value >= args.max:
        delta = -1
    elif value <= args.min:
        delta = +1
    value += delta
    time.sleep(args.delay / 1000.0)
    if (sequence_count+1) % 100 == 0:
        print(f'Sent {sequence_count+1} packets')

    if args.delta_time:
        pkt_time += args.delta_time / 1000.0
    else:
        pkt_time += args.delay / 1000.0
