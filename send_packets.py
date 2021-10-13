import argparse
import socket
import struct
import time
from datetime import datetime, timezone

def send_packet(millis, sequence_count, value, s, dest):
    packet_data = struct.pack('>Q I I', millis, sequence_count, value)
    s.sendto(packet_data, dest)

now = datetime.now(timezone.utc)

parser = argparse.ArgumentParser(description='Send dummy HGA pan/title state')
parser.add_argument('--host', default='localhost',
                    help='Yamcs hostname (default: localhost)')
parser.add_argument('--port', type=int, default=10015,
                    help='UDP port to use for sending packets (default: 1235)')
parser.add_argument('--apid', type=int, default=100,
                    help='packet APID to use (default: 100)')
parser.add_argument('--sequence-count', type=int, default=0,
                    help='Sequence count for first packet (default: 0)')
parser.add_argument('--second-packet-offset', type=int, default=100,
                    help='Time offset for 2nd packet (default: 100 millis)')
parser.add_argument('--delay', type=int, default=100,
                    help='Delay before sending 2nd packet (default: 100 millis')
parser.add_argument('value1', type=int, help='Value to send in 1st packet')
parser.add_argument('value2', type=int, help='Value to send in 2nd packet')

args = parser.parse_args()

s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
dest = (args.host, args.port)
packet_time = datetime.now(timezone.utc)
millis = int(packet_time.timestamp() * 1000)

send_packet(millis, args.sequence_count, args.value1, s, dest)
time.sleep(args.delay / 1000.0)
send_packet(millis+args.second_packet_offset, args.sequence_count+1,
            args.value2, s, dest)

print('Sent two packets with times 1) {} 2) offset by {} milliseconds'.format(
    packet_time, args.second_packet_offset))
