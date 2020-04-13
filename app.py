from daikinapi import Daikin
import argparse
import logging
from prometheus_client import (
    Gauge,
    pushadd_to_gateway,
    start_http_server,
    REGISTRY,
)
from dotenv import load_dotenv
import os, time


"""Parse arguments from command line"""
PARSER = argparse.ArgumentParser(
    description="Export metrics from Daikin airconditioning to prometheus"
)
PARSER.add_argument(
    "-n",
    "--noop",
    help="dont actually post/change anything, just log what would have been posted. "
    "Mostly relevant with --pushgateway",
    action="store_true",
    default=False,
)
PARSER.add_argument(
    "-v", "--verbose", help="set logging to debug", action="store_true", default=False,
)
PARSER.add_argument(
    "-p",
    "--pushgateway",
    help="send metrics prometheus pushgateway and exit. Can also be defined in "
    "PROM_GATEWAY env variable",
    default=False,
)
PARSER.add_argument("hosts", help="list of airconditioning units to query", nargs="*")
ARGS = PARSER.parse_args()

LOGFORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"

if ARGS.verbose:
    logging.basicConfig(level=logging.DEBUG, format=LOGFORMAT)
else:
    logging.basicConfig(level=logging.INFO, format=LOGFORMAT)
    logging.getLogger("requests.packages.urllib3.connectionpool").setLevel(
        logging.WARNING
    )

logging.debug("starting with arguments: %s", ARGS)

load_dotenv()
gauges = {}
hosts = ARGS.hosts if ARGS.hosts else os.environ.get("PROM_HOSTS").split()
for host in hosts:
    API = Daikin(host)
    devicename = API.name if API.name else host
    for attribute in [
        a for a in API.ATTRIBUTES if a not in ["mac", "ver", "name", "rev", "type"]
    ]:
        if attribute == "fan_rate":
            helptext = "Daikin " + attribute + " (0=auto, 1=silent, 3-7 = setting 1-5)"
            valuefunc = (
                lambda a=attribute, A=API: getattr(A, a)
                .replace("A", "0")
                .replace("B", "1")
            )
        else:
            helptext = (
                "Daikin "
                + attribute
                + " ("
                + type(API).__dict__[attribute].__doc__.strip()
                + ")"
            )
            valuefunc = lambda a=attribute, A=API: getattr(A, a)

        if not gauges.get(attribute, False):
            gauges[attribute] = Gauge(
                "daikin_" + attribute, helptext, ["name"], registry=REGISTRY
            )
        gauges[attribute].labels(name=devicename).set_function(valuefunc)

if ARGS.pushgateway or os.environ.get("PROM_GATEWAY", False):
    gateway = ARGS.pushgateway if ARGS.pushgateway else os.environ.get("PROM_GATEWAY")
    if not ARGS.noop:
        pushadd_to_gateway(
            gateway, registry=REGISTRY, job="daikin_exporter"
        )
else:
    start_http_server(os.environ.get("listenport", 8080), registry=REGISTRY)
    while True:
        time.sleep(1)
