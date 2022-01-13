# Yamcs QuickStart for CCSDS/cFS projects

This documents how to configure and run the customized quickstart
project. This document should be in the root directory of the
quickstart distribution, or you may be reading it from source in the
src/main/yamcs directory. If you are using the source, you will also
want to consult the main README in the source root directory for more
information about building and running the project.


## Adding your own XTCE

You can add one or more XTCE files into mdb/subsystems/ (or
src/main/yamcs/mdb/subsystems/ in the source tree). Each
SequenceContainer should derive from /Ccsds/TelemetryHeader and each
MetaCommand should derive from /Ccsds/CommandHeader. The APIDs for
each container or command should be added to mdb/ccsds.xml in the
`CCSDS_APID_Type` type definitions in the `<ParameterTypeSet>` or
`<ArgumentTypeSet>` sections. In addition, the opcodes for any
commands must be added to the `cFS_Opcode_Type` definition in the
`<ArgumentTypeSet>` section.


## Running Yamcs

The `yamcsd` program in the bin directory can be used to start
Yamcs. Use Ctrl-C to stop it. Yamcs also distributes, in their source
on GitHub, a sample sysctl script to start and stop Yamcs on Linux
systems.


## Sending telemetry

There is a script in scripts/send_packet.py that allows sending a
single packet of telemetry. Use the "-h" option to get usage
information on that script. As an example, here is a command line that
sends the packet /myproject/sample/telemetry with a value of 3 for the
testValue parameter, and displays the hex of the sent packet.

    $ python3 scripts/send_packet.py --apid 2046 --sequence-count 1 \
        --field 'B:3' --verbose


## Telecommanding

There is a script in scripts/show_commands.py that will echo any
commands it receives over the UDP port. Use the "-h" option to see
usage information for that script. The defaults will work for the
supplied outgoing data link configuration. As an example, this command
line will echo received commands to the console:

    $ python3 scripts/show_commands.py


## Data link configuration

### Telemetry

The incoming telemetry data link is configured to accept UDP packets
on port 1235. You can change this port number, or change to a
different data link class, if you like.

The packet preprocessor is designed to handle a timestamp in the CCSDS
secondary header. The format of the timestamp is configured as
arguments to the packet preprocessor in the data link
configuration. The current configuration in yamcs.myproject.yaml is as
follows:

~~~
    packetPreprocessorClassName: com.example.myproject.MyPacketPreprocessor
    packetPreprocessorArgs:
        timeOffset: 6
    	timeLength: 6
    	fractionLength: 2
    	timeEpoch: UNIX
~~~

This configures a 6-byte timestamp with a 4 byte integral number of
seconds followed by a 2-byte fractional seconds. CCSDS standards
assume the whole timestamp can be interpreted, in binary, by putting a
decimal point after the integral portion. Thus, for a 2-byte fraction,
the units are 1/(2^16) seconds. (Similarly, for a 4-byte fractional
part, the units of the fractional portion are 1/(2^32) seconds.)

The timestamp epoch can be any of the values in
MyPacketPreprocessor.Epoch, currently TAI, UNIX, GPS, or J2000. The
TAI, GPS, and J2000 epochs imply that leap seconds are included in the
timestamp within the secondary header. The UNIX epoch uses UNIX
conventions: leap seconds are not counted, and are not included in the
timestamp.

### Commands

The outgoing command data link sends UDP packets to port 1235 on
localhost. You can change the port or host as you like, or change to a
different outgoing data link class.

The command data link is configured to use the Yamcs standard cFS
command postprocessor class. It fills in the command packet sequence
count and the cFS one-byte checksum. The base XTCE is also configured
to generate cFS-style command packets. You will have to change both if
you are not using cFS-style packets.


## What you may want to change

The base CCSDS definitions and some basic types are in mdb/ccsds.xml
and mdb/xtce.xml. A sample XTCE file for a spacecraft is in
mdb/subsystems/sample.xml. You will want to put your XTCE in the
subsystems/ directory, from which it will be automatically loaded. All
of your telemetry packets should derive from /Ccsds/TelemetryHeader,
and all of your commands should derive form /Ccsds/CommandHeader.

The /Ccsds/TelemetryHeader sequence container is configured to expect
CCSDS packets containing a secondary header with a 6-byte timestamp,
to match the timestamp configured for the packet preprocessor. If you
change  the secondary header format, you must change both the XTCE and
the packet preprocessor configuration.

The /CcsdsCommandHeader metacommand is configured to send a cFS-style
CCSDS packet with a secondary header containing the one-byte opcode
and a one-byte checksum. The checksum is filled in by the command
postprocessor, as mentioned above. If you need a different command
format you will need to change the XTCE and possibly change to a
different packet postprocessor, or write your own.

In addition, the supplied XTCE does not have a provision for setting
the upper bit in the opcode byte, to indicate to a cFS system that
command argument constraint checking should be disabled. If you need
that capability you should modify the XTCE to insert a 1-bit argument
at that position, rather than skipping 1 bit, as the current XTCE does.
