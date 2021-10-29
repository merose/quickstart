import argparse
import socket
import struct
import time
from datetime import datetime, timedelta, timezone

def send_packet(millis, sequence_count, value, s, dest):
    packet_data = struct.pack('>Q I I', millis, sequence_count, value)
    s.sendto(packet_data, dest)

now = datetime.now(timezone.utc)
now_str = now.strftime('%Y-%m-%dT%H:%M:%S')

parser = argparse.ArgumentParser(description='Send dummy HGA pan/title state')
parser.add_argument('--host', default='localhost',
                    help='Yamcs hostname (default: localhost)')
parser.add_argument('--port', type=int, default=10015,
                    help='UDP port to use for sending packets (default: 1235)')
parser.add_argument('--apid', type=int, default=100,
                    help='packet APID to use (default: 100)')
parser.add_argument('--min', type=int, default=0,
                    help='minimum data value in sawtooth (default: 0)')
parser.add_argument('--max', type=int, default=2500,
                    help='maximum data value in sawtooth (default: 2500)')
parser.add_argument('--delay', type=int, default=50,
                    help='inter-packet delay in ms (default: 50)')
parser.add_argument('--verbose', action='store_true',
                    help='if specified, print detailed progress')

args = parser.parse_args()

s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
dest = (args.host, args.port)

sequence_count = 0
value = args.min
delta = 1

while True:
    pkt_time = datetime.now(timezone.utc)
    send_packet(int(pkt_time.timestamp()*1000), sequence_count, value, s, dest)
    if args.verbose:
        print('Sent packet:')
        print('    value={} time={}'.format(value,
                pkt_time.strftime('%Y-%m-%dT%H:%M:%S.%fZ')))

    sequence_count +=1
    if value >= args.max:
        delta = -1
    elif value <= args.min:
        delta = +1
    value += delta
    time.sleep(args.delay / 1000.0)
    if sequence_count % 100 == 0:
        print(f'Sent {sequence_count} packets')

