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
                    help=f'UTC time of first packet (default: now)')
parser.add_argument('--second-packet-offset', type=int, default=100,
                    help='Time offset for 2nd packet (default: 100 millis)')
parser.add_argument('--delay', type=int, default=100,
                    help='Delay before sending 2nd packet (default: 100 millis')
parser.add_argument('value1', type=int, help='Value to send in 1st packet')
parser.add_argument('value2', type=int, help='Value to send in 2nd packet')

args = parser.parse_args()

s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
dest = (args.host, args.port)
delta = timedelta(milliseconds=args.second_packet_offset)
pkt1_time = datetime.fromisoformat(args.time).replace(tzinfo=timezone.utc)
pkt2_time = pkt1_time + delta

send_packet(int(pkt1_time.timestamp()*1000), args.sequence_count,
                args.value1, s, dest)
time.sleep(args.delay / 1000.0)
send_packet(int(pkt2_time.timestamp()*1000), args.sequence_count,
                args.value2, s, dest)

print('Sent two packets:')
print('    value={} time={}'.format(args.value1,
                                   pkt1_time.strftime('%Y-%m-%dT%H:%M:%S.%fZ')))
print('    value={} time={}'.format(args.value2,
                                   pkt2_time.strftime('%Y-%m-%dT%H:%M:%S.%fZ')))
