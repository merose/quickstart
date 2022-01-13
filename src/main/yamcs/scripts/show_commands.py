'''Show commands received via UDP.'''

import argparse
import re
import socket
import struct
import sys
from datetime import datetime, timezone


def print_packet(b):
    for offset in range(0, len(b), 16):
        limit = min(offset+16, len(b))
        bytes = ' '.join([b[i:i+1].hex() for i in range(offset, limit)])
        print(f'{offset:07d}    {bytes}')
    print(f'{len(b):07d}')


parser = argparse.ArgumentParser(description='Show commands received via UDP')
parser.add_argument('--host', default='',
    help='Host to bind to for receiving. Default is all interfaces')
parser.add_argument('--port', type=int, default=1234,
    help='UDP port to listen for commands on (default: 1234)')
parser.add_argument('--not-ccsds', action='store_true',
    help='If specified, commands are not CCSDS packets, so do no decoding')
parser.add_argument('--not-cfs', action='store_true',
    help='If specified, commands are not in cFS-style so no opcode decoding')

args = parser.parse_args()

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
# Listen on all interfaces. Change to 'localhost' if you want to 
sock.bind((args.host, args.port))

while True:
    packet = sock.recv(65536)
    print('Received packet:')
    print_packet(packet)

    # Decode the packet, if it is a CCSDS packet.
    if not args.not_ccsds and len(packet) >= 6:
        (apid_flags, seq_flags, length) = struct.unpack('>H H H', packet[:6])
        actual_length = len(packet) - 6
        if length+1 != actual_length:
            print('Packet length is incorrect, got {} but header has {}'.format(
                actual_length, length+1))
        print(f'    APID: {apid_flags & 0x7FF}')
        print(f'    sequence count: {seq_flags & 0x3FFF}')
        print(f'    packet length: {length}')

        if not args.not_cfs and len(packet) >= 8:
            (opcode_flags, checksum) = struct.unpack('BB', packet[6:8])
            print(f'    opcode: {opcode_flags & 0x7F}')
            print(f'    checksum: {checksum}')
