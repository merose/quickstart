# Cannot retrieve aggregate parameter from archive

This modification to quickstart is used to send telemetry at a high
rate, in order to show that the realtime archiver cache fills up and
is not flushed, even for segments older than the sortingThreshold.

The manifests in two ways: first, there are warning messages in the
Yamcs log. Second, retrieval of the value using the archive API no
longer works for the parameter, even after a Yamcs restart.

## Environment

Found in Yamcs 5.5.5

## Overview

This modification to the quickstart project replaces the XTCE with a
simpler model that has a single packet with a single parameter inside.

It also adds a Python utility to send packets with varying values for
the single parameter. A command line option allows specifying the
delay between packets. A small delay allows showing the behavior
sooner.

It also updates the Yamcs reference to Yamcs 5.5.5.

## Requirements

The usual requirements for building the Yamcs quickstart project, plus:

- Python 3, available as `python3`
- Yamcs Python client installed via `pip3 install yamcs-client` (or can be installed as `--user`)

## Setup

Clone branch of a copy of the quickstart project:

    $ git clone -b cache-not-flushing git@github.com:merose/quickstart.git

Build the quickstart project normally using mvn.

    $ mvn package

## Running Yamcs

    $ target/bundle-tmp/bin/yamcsd

## Exhibiting the bug

In a terminal window, start the utility that sends packets.

    $ python3 send_packets.py --delay 1

In another terminal window, you can now retrieve values using the
archive API:

~~~
$ curl 'http://localhost:8090/api/archive/myproject/parameters/myproject/value?limit=2'
{
  "parameter": [{
    "id": {
      "name": "value",
      "namespace": "/myproject"
    },
    "rawValue": {
      "type": "UINT32",
      "uint32Value": 1051
    },
    "engValue": {
      "type": "UINT32",
      "uint32Value": 1051
    },
    "generationTime": "2021-10-29T20:45:21.349Z",
    "acquisitionStatus": "ACQUIRED",
    "generationTimeUTC": "2021-10-29T20:45:21.349Z"
  }, {
    "id": {
      "name": "value",
      "namespace": "/myproject"
    },
    "rawValue": {
      "type": "UINT32",
      "uint32Value": 1052
    },
    "engValue": {
      "type": "UINT32",
      "uint32Value": 1052
    },
    "generationTime": "2021-10-29T20:45:21.348Z",
    "acquisitionStatus": "ACQUIRED",
    "generationTimeUTC": "2021-10-29T20:45:21.348Z"
  }],
  "continuationToken": "eyJ0aW1lIjoxNjM1NTQwMzU4MzQ2fQ"
}$
~~~

Now wait about 2 minutes. There will be warnings in the Yamcs log like
this:

~~~
$ egrep 'WARN|ERROR' target/bundle-tmp/log/yamcs-server.log.0 | head -3
Oct 29 13:47:06.829 myproject [19] org.yamcs.parameterarchive.RealtimeArchiveFiller [WARNING] Realtime parameter archive queue full.Consider increasing the writerThreads (if CPUs are available) or using a back filler
Oct 29 13:47:06.830 myproject [19] org.yamcs.parameterarchive.RealtimeArchiveFiller [WARNING] Realtime parameter archive queue full.Consider increasing the writerThreads (if CPUs are available) or using a back filler
Oct 29 13:47:06.832 myproject [19] org.yamcs.parameterarchive.RealtimeArchiveFiller [WARNING] Realtime parameter archive queue full.Consider increasing the writerThreads (if CPUs are available) or using a back filler
$
~~~

After that point, the archive API does not return any results.

~~~
$ curl 'http://localhost:8090/api/archive/myproject/parameters/myproject/value?limit=2'
{
}$
~~~

Even stoping the process that is sending parameters, the archive API
fails to work. It appears that the cache will begin flushing when the
next interval starts (if telemetry is flowing), and the archive API
might start working again.

It also appears that the cache is not flushed when stopping Yamcs,
because the archive API still returns no results.

# Discussion

There appear to be two issues, the second by design.

1. Cache segments are not flushed until a new interval starts, even if
   the segments are older than the current time minus the
   sortingThreshold.

2. Cache segments are never flushed until new telemetry arrives or
   Yamcs is shut down. To avoid data loss due to crashes, it seems
   safer to flush cache segments after a period of idle time, even if
   no new telemetry arrives.
