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
parser.add_argument('--sequence-count', type=int, default=0,
                    help='Sequence count for first packet (default: 0)')
parser.add_argument('--time', default=now_str,
                    help=f'UTC time of packet (default: now)')
parser.add_argument('value', type=int, help='Value to send in packet')

args = parser.parse_args()

s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
dest = (args.host, args.port)
pkt_time = datetime.fromisoformat(args.time).replace(tzinfo=timezone.utc)

send_packet(int(pkt_time.timestamp()*1000), args.sequence_count,
                args.value, s, dest)

print('Sent packet:')
print('    value={} time={}'.format(args.value,
                                   pkt_time.strftime('%Y-%m-%dT%H:%M:%S.%fZ')))
