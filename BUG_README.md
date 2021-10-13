# Value looping bug description

## Requirements

The usual requirements for building the Yamcs quickstart project, plus:

- Python 3, available as `python3`
- Yamcs Python client installed via `pip3 install yamcs-client` (or can be installed as `--user`)

## Setup

Build the quickstart project normally using mvn.

    $ mvn package

## Running Yamcs

    $ target/bundle-tmp/bin/yamcsd

## Exhibiting the bug

In another terminal window:

    $ ./show-out-of-order

## Discussion

There is a bug in the RealTimeArchiveFiller that ignores _all_ packets
that go back in time. To work around that bug, we set `pastJumpThreshold`
to zero. This allows us to send packets that are in one interval, but
then send a packet for the prior interval. That is supposed to cause
a cache flush in the filler, and the start of a new segment. However,
it appears that it messes up the placement of future values, causing
infinite looping upon retrieval.

Documentation on RealtimeArchiveFiller settings: https://docs.yamcs.org/yamcs-server-manual/services/instance/parameter-archive-service/

Issue filed for this bug: https://github.com/yamcs/yamcs/issues/618

Issue was fixed on 2021-10-09 with commits https://github.com/yamcs/yamcs/commit/9b79844faf7ce5af3bbc7b7f7b12e18447bbad31 and https://github.com/yamcs/yamcs/commit/4f47db782e5e16c4ba280cd661605f233a41c0d6.
