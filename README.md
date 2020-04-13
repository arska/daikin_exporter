# Daikin Airconditioner/Air source heat pump metrics prometheus exporter

Uses https://pypi.org/project/daikinapi/ / https://github.com/arska/python-daikinapi/ to get metrics and either serves them as a webserver on port 8080 or sends them to a prometheus pushgateway (command line argument --pushgateway or env variable PROM_GATEWAY)

## Usage
$ python app.py -h
usage: app.py [-h] [-n] [-v] [-p PUSHGATEWAY] [hosts [hosts ...]]

Export metrics from Daikin airconditioning to prometheus

positional arguments:
  hosts                 list of airconditioning units to query

optional arguments:
  -h, --help            show this help message and exit
  -n, --noop            dont actually post/change anything, just log what
                        would have been posted. Mostly relevant with
                        --pushgateway
  -v, --verbose         set logging to debug
  -p PUSHGATEWAY, --pushgateway PUSHGATEWAY
                        send metrics prometheus pushgateway and exit. Can also
                        be defined in PROM_GATEWAY env variable

## Environment variables
* PROM_HOSTS: whitespace separated list of hosts to query and metrics to export
* PROM_GATEWAY: prometheus pushgateway to send metrics to and exit
* listenport: port to listen on for prometheus metrics webserver, default=8080
