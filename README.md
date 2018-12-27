# 🔥 mae [![](https://img.shields.io/pypi/v/mae.svg)](https://pypi.org/project/mae/) [![](https://travis-ci.org/paambaati/mae.svg?branch=master)](https://travis-ci.org/paambaati/mae)

`mae` collects Prometheus metrics from your Mesos apps.

See [Deployment Strategy](#deployment-strategy) to learn how to set up `mae` on your Mesos cluster.

## Requirements

`mae` requires Python (>= 2.7).

## Installation

```
pip install mae
```

## Usage
```
$ mae --help

usage: mae [-h] app_port slave_address slave_port

positional arguments:
  app_port       Port on which this exporter will run on
  slave_address  Mesos slave address
  slave_port     Mesos slave port
```

## Deployment Strategy

`mae` is designed to be run as a daemon on all Mesos slave nodes. This ideally involves 2 steps —

1. [Install `mae`](#installation) as part of your base image/AMI or via [user data](https://docs.aws.amazon.com/AWSEC2/latest/UserGuide/user-data.html).
2. Run `mae` as a daemon. For example, if your distro supports `systemd`, here's a sample script that runs the exporter on port `8888` —
    ```
    # Save this to /etc/systemd/system/mae.service
    [Unit]
    Description=Mesos App Exporter
    After=network.target

    [Service]
    Type=simple
    Restart=on-failure
    ExecStart=/usr/local/bin/mae 8888 localhost 5051 # Assuming the Mesos slave process is running on port 5051

    [Install]
    WantedBy=multi-user.target
    ```
