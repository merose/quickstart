# Algorithm running infinitely

This modification to quickstart sets up a scenario where a custom Java
algorithm continues to run, every 10 seconds, until the current interval
passes.

## Yamcs setup

This modification to quickstart configures Yamcs to use the backfiller
to fill the parameter archive. It uses a `streamUpdateFillFrequency`
of 10 seconds, so that backfiller tasks will be spawned frequently,
and a `warmupTime` of zero.

The XTCE is custom, with only two of interest, one for a `value` in
incoming packets, and one for `computedValue`, which is calculated
by a custom Java algorithm.

In addition, the system parameters service is disabled to reduce the
number of parameters archived.

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

In a new terminal window, look for messages from the custom algorithm
indicating a new algorithm result:

    $ tail -f target/bundle-tmp/log/yamcs-server.log.0 | grep 'Returning one'

In another terminal window, send a packet with an old timestamp:

    $ python3 send_packet.py --time 2021-01-01T00:00:00 1

Expected and actual result: In the terminal window looking at the log,
the algorithm runs twice, once when the packet arrives, and once when
the backfiller task runs for that time period.

In the terminal, send a new packet using the current time:

    $ python3 send_packet.py 3

Expected result: In the terminal window looking at the log, the algorithm
runs twice more, with a result of 6, once when the packet arrives, and
once when the backfiller task runs for that time period.

Actual result: The algorithm runs every 10 seconds from then on, until
the current interval ends.

# Discussion

It seems that the built-in parameter value updates cause the same
interval to be processed over and over again. If the algorithm is
expensive, or if it has side effects (notifying some other system,
say) this could be problematic.

You can show the current few interval boundaries via:

    $ python3 show_interval_boundaries.py
