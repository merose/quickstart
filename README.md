# Yamcs QuickStart project source for CCSDS/cFS projects

This is a variation on the Yamcs quickstart project that is customized
to projects that use CCSDS packets for telemetry and commanding, as is
typical when using NASA cFS as the flight software framework.


## Prerequisites

* Java 11
* Maven 3.1+
* Linux x64 or macOS


## Configuration

See src/main/yamcs/README.md for information about configuring the
running system.


## Customization

There are two supplied Java classes to customize the Yamcs
behavior. One, MyCommandPostProcessor.java, is identical to that
provided by the Yamcs quickstart in the master branch. It is not used
in the supplied configuration here.

The other file, MyPacketPreprocessor.java, is customized from that in
the base Yamcs quickstart project. It allows configuration of the time
format in the CCSDS secondary header, in order to fill in the packet
generation time. See the documentation in src/main/yamcs/README.md for
configuration information, or the source code for more details.


## Running Yamcs

Here are some commands to get things started:

Compile this project:

    mvn compile

Start Yamcs on localhost:

    mvn yamcs:run

Same as yamcs:run, but allows a debugger to attach at port 7896:

    mvn yamcs:debug
    
Delete all generated outputs and start over:

    mvn clean

This will also delete Yamcs data. Change the `dataDir` property in `yamcs.yaml` to another location on your file system if you don't want that.


## Bundling

Running through Maven is useful during development, but it is not recommended for production environments. Instead bundle up your Yamcs application in a tar.gz file:

    mvn package
