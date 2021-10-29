# Cannot retrieve aggregate parameter from archive

This modification to quickstart sets up a scenario where an aggregate
value is inserted into the parameter archive. The aggregate parameter
can then be retrieved using the processor API. However, the archive
API cannot return the aggregate parameter value. Instead, you must
ask for an aggregate member value. This is much less convenient for
client scripts, of course, and makes them more brittle, since they
have to specify each member of the aggregate that they want to retrieve.

## Environment

Found in Yamcs 5.5.5

## Overview

This modification to the quickstart project replaces the XTCE with a
simpler model that has a single packet, with a single, aggregate
parameter inside.

It also updates the Yamcs reference to Yamcs 5.5.5.

## Requirements

The usual requirements for building the Yamcs quickstart project, plus:

- Python 3, available as `python3`
- Yamcs Python client installed via `pip3 install yamcs-client` (or can be installed as `--user`)

## Setup

Clone branch of a copy of the quickstart project:

    $ git clone -b aggregate-no-history git@github.com:merose/quickstart.git

Build the quickstart project normally using mvn.

    $ mvn package

## Running Yamcs

    $ target/bundle-tmp/bin/yamcsd

## Exhibiting the bug

In a terminal window, send a packet with a value of an aggregate
parameter:

    $ python3 send_packet.py 123

This works, getting the current parameter value:

~~~
$ curl 'http://localhost:8090/api/processors/myproject/realtime/parameters/myproject/structure'
{
  "id": {
    "name": "structure",
    "namespace": "/myproject"
  },
  "rawValue": {
    "type": "AGGREGATE",
    "aggregateValue": {
      "name": ["value"],
      "value": [{
        "type": "UINT32",
        "uint32Value": 123
      }]
    }
  },
  "engValue": {
    "type": "AGGREGATE",
    "aggregateValue": {
      "name": ["value"],
      "value": [{
        "type": "UINT32",
        "uint32Value": 123
      }]
    }
  },
  "acquisitionTime": "2021-10-29T00:02:38.241Z",
  "generationTime": "2021-10-29T00:02:38Z",
  "acquisitionStatus": "ACQUIRED",
  "acquisitionTimeUTC": "2021-10-29T00:02:38.241Z",
  "generationTimeUTC": "2021-10-29T00:02:38.000Z"
  }$
 ~~~

However, retrieving from the archive does not work for the aggregate
parameter:

~~~
$ curl 'http://localhost:8090/api/archive/myproject/parameters/myproject/structure'
{
}$
~~~

while requesting the aggregate member works:

~~~
$ curl 'http://localhost:8090/api/archive/myproject/parameters/myproject/structure.value'
{
  "parameter": [{
    "id": {
      "name": "structure.value",
      "namespace": "/myproject"
    },
    "rawValue": {
      "type": "UINT32",
      "uint32Value": 123
    },
    "engValue": {
      "type": "UINT32",
      "uint32Value": 123
    },
    "generationTime": "2021-10-29T00:02:38Z",
    "acquisitionStatus": "ACQUIRED",
    "generationTimeUTC": "2021-10-29T00:02:38.000Z"
  }]
  }$
~~~

# Discussion

It seems like the processor API and the archive API should be consistent.
