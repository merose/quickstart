import argparse
import socket
import struct
from datetime import datetime, timezone

from yamcs.client import YamcsClient

def send_packet(millis, sequence_count, value, s, dest):
    packet_data = struct.pack('>Q I I', millis, sequence_count, value)
    s.sendto(packet_data, dest)

now = datetime.now(timezone.utc)

parser = argparse.ArgumentParser(description='Send dummy HGA pan/title state')
parser.add_argument('--host', default='localhost',
                    help='Yamcs hostname (default: localhost)')
parser.add_argument('--port', type=int, default=8090,
                    help='Yamcs web port (default: 8090)')
parser.add_argument('--instance', default='myproject',
                    help='Yamcs instance to access (default: myproject)')
parser.add_argument('--parameter', default='/myproject/value',
                    help='Parameter to show')
parser.add_argument('--page-size', type=int, default=100,
                    help='Page size to use when retrieving values (default 100)')
parser.add_argument('--max-values', type=int, default=50,
                    help='Max no. of values to show (default 50)')

args = parser.parse_args()

client = YamcsClient(f'{args.host}:{args.port}')
archive = client.get_archive(instance=args.instance)

count = 0
for pv in archive.list_parameter_values(args.parameter,
                                        page_size=args.page_size):
    print(f'{pv.generation_time.isoformat()}: value={pv.eng_value}')
    count += 1
    if (count > args.max_values):
        print('Looks like the Python client is in a loop')
        break

print(f'Retrieved {count} values')
