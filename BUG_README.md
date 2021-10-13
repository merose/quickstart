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

    $ ./show-values-loop

## Discussion

It appears that the out-of-order packet causes the backfiller to put
values into the wrong segment, based on their timestamp. This breaks
the invariant that segments should not overlap in time, for the same
parameter set. After that database corruption, when retrieving values,
the retrieval API can send a continuation token with a timestamp
that causes the retrieval to loop, infinitely.
