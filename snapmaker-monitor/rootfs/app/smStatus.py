#!/usr/bin/env python3
"""Read the status of a Snapmaker 2.0 and send it to Home Assistant.

The status is sent to a Home Assistant webhook, to an MQTT topic, or both.

Based on the original script by NiteCrwlr:
https://github.com/NiteCrwlr/playground/blob/main/SNStatus/SNStatusV2.py
"""

import ipaddress
import json
import logging
import os
import socket
import sys
import time
from datetime import timedelta

import paho.mqtt.client as mqtt
import requests

# ------------------------------------------------------------------------------
# Logging
# ------------------------------------------------------------------------------
# The add-on offers the bashio levels, map the ones Python does not know.
_LEVEL_ALIASES = {"TRACE": "DEBUG", "NOTICE": "INFO", "FATAL": "CRITICAL"}
_log_level = os.environ.get("LOG_LEVEL", "INFO").upper()
_log_level = _LEVEL_ALIASES.get(_log_level, _log_level)
_numeric_level = getattr(logging, _log_level, None)
if not isinstance(_numeric_level, int):
    _numeric_level = logging.INFO
logging.basicConfig(
    level=_numeric_level,
    format="%(asctime)s - %(levelname)s - %(message)s",
)
log = logging.getLogger("snapmaker-monitor")

# ------------------------------------------------------------------------------
# Configuration
# ------------------------------------------------------------------------------
IN_ADDON = os.path.exists("/data/options.json")

DISCOVER_PORT = 20054
BROADCAST_ADDRESS = "255.255.255.255"
UDP_TIMEOUT = 1.0
UDP_RETRIES = 5
BUFFER_SIZE = 1024
HTTP_TIMEOUT = 10  # seconds
POLL_INTERVAL = 60  # seconds
REACHABLE_RETRIES = 5

SM_IP = os.environ.get("SM_IP", "")
SM_PORT = int(os.environ.get("SM_PORT") or 8080)

MQTT_BROKER = os.environ.get("MQTT_BROKER", "")
MQTT_PORT = int(os.environ.get("MQTT_PORT") or 1883)
MQTT_TOPIC = os.environ.get("MQTT_TOPIC") or "snapmaker/status"
MQTT_USER = os.environ.get("MQTT_USER", "")
MQTT_PASSWORD = os.environ.get("MQTT_PASSWORD", "")

SUPERVISOR_TOKEN = os.environ.get("SUPERVISOR_TOKEN", "")
HA_WEBHOOK_ID = os.environ.get("HA_WEBHOOK_ID", "")
if IN_ADDON and HA_WEBHOOK_ID:
    # Go through the Supervisor proxy to Home Assistant Core. The proxy needs
    # the add-on's Supervisor token, and Core sees the request as local, so
    # webhooks with `local_only: true` work as well.
    HA_WEBHOOK_URL = f"http://supervisor/core/api/webhook/{HA_WEBHOOK_ID}"
else:
    HA_WEBHOOK_URL = os.environ.get("HA_WEBHOOK_URL", "")

TOKEN_FILE = (
    os.path.join("/data", "SMtoken.txt") if IN_ADDON else os.path.join(os.getcwd(), "SMtoken.txt")
)

TOOLHEADS = {
    "TOOLHEAD_CNC_1": "CNC",
    "TOOLHEAD_LASER_1": "Laser",
}


# ------------------------------------------------------------------------------
# Helpers
# ------------------------------------------------------------------------------
def mask(secret):
    """Return a shortened version of a secret that is safe to log."""
    if not secret:
        return "<none>"
    return f"{secret[:4]}…" if len(secret) > 8 else "****"


def validate_ip_address(ip_string):
    """Check whether the given string is a valid IP address."""
    try:
        ipaddress.ip_address(ip_string)
    except ValueError:
        return False
    return True


def is_reachable(ip_address, api_port):
    """Check whether the given IP address and port accept TCP connections."""
    try:
        with socket.create_connection((ip_address, int(api_port)), timeout=1):
            return True
    except OSError:
        return False


def udp_discover():
    """Find a Snapmaker 2.0 on the local network via UDP broadcast."""
    for attempt in range(1, UDP_RETRIES + 1):
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as sock:
            sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
            sock.settimeout(UDP_TIMEOUT)
            sock.sendto(b"discover", (BROADCAST_ADDRESS, DISCOVER_PORT))
            try:
                reply, _ = sock.recvfrom(BUFFER_SIZE)
            except TimeoutError:
                log.debug("UDP discovery attempt %d timed out", attempt)
                continue
        return reply.decode(errors="replace").split("|")[0].split("@")[-1]
    log.error("UDP discovery failed")
    sys.exit(1)


# ------------------------------------------------------------------------------
# Snapmaker API
# ------------------------------------------------------------------------------
def _read_saved_token():
    try:
        with open(TOKEN_FILE, encoding="utf-8") as file:
            return file.read().strip()
    except FileNotFoundError:
        return ""


def _save_token(token):
    try:
        with open(TOKEN_FILE, "w", encoding="utf-8") as file:
            file.write(token)
    except OSError as err:
        log.error("Unable to save token to %s: %s", TOKEN_FILE, err)
        sys.exit(1)
    log.info("Token received and saved to %s", TOKEN_FILE)


def get_sm_token(connect_ip):
    """Return a Snapmaker API token, from the token file or a new pairing."""
    sm_url = f"http://{connect_ip}:{SM_PORT}/api/v1/connect"
    headers = {"Content-Type": "application/x-www-form-urlencoded"}

    sm_token = _read_saved_token()
    if sm_token:
        try:
            response = requests.post(
                sm_url,
                data={"token": sm_token},
                headers=headers,
                timeout=HTTP_TIMEOUT,
            )
        except requests.exceptions.RequestException as err:
            log.error("Error connecting to Snapmaker with saved token: %s", err)
            return None
        if response.ok:
            return sm_token
        log.warning(
            "Snapmaker rejected the saved token (HTTP %s), requesting a new one",
            response.status_code,
        )

    log.info("No valid Snapmaker token, requesting a new one")
    while True:
        try:
            response = requests.post(sm_url, timeout=HTTP_TIMEOUT)
            response.raise_for_status()
            if "Failed" in response.text:
                log.error(response.text)
                log.error("Binding failed, please restart the add-on")
                sys.exit(1)

            sm_token = response.json().get("token")
            log.info("Please authorize the connection on the touchscreen.")
            time.sleep(10)

            response = requests.post(
                sm_url,
                data={"token": sm_token},
                headers=headers,
                timeout=HTTP_TIMEOUT,
            )
            response.raise_for_status()
            if sm_token and response.json().get("token") == sm_token:
                _save_token(sm_token)
                return sm_token
            log.warning("Connection was not authorized yet, retrying")
        except requests.exceptions.RequestException as err:
            log.error("Request failed: %s", err)
            time.sleep(20)
        except json.JSONDecodeError as err:
            log.error("Failed to decode JSON from Snapmaker: %s", err)
            sys.exit(1)


def read_status(connect_ip, sm_token):
    """Read the current status from the Snapmaker and normalize it."""
    log.info("Reading Snapmaker status...")
    sm_api = f"http://{connect_ip}:{SM_PORT}/api/v1/status"
    try:
        response = requests.get(sm_api, params={"token": sm_token}, timeout=HTTP_TIMEOUT)
        response.raise_for_status()
        sm_status = response.json()
    except (requests.exceptions.RequestException, ValueError) as err:
        log.error("Reading the status failed: %s", err)
        return {"status": "UNAVAILABLE", "ip": connect_ip, "error": str(err)}

    log.debug("Snapmaker status: %s", sm_status)
    sm_status["ip"] = connect_ip

    tool_head = sm_status.get("toolHead")
    if tool_head == "TOOLHEAD_3DPRINTING_1":
        if sm_status.get("nozzleTemperature") is None:
            sm_status["toolHead"] = "Dual Extruder"
            sm_status["nozzleTemperature"] = sm_status.get("nozzleTemperature1")
            sm_status["nozzleTargetTemperature"] = sm_status.get("nozzleTargetTemperature1")
        else:
            sm_status["toolHead"] = "Extruder"
    elif tool_head in TOOLHEADS:
        sm_status["toolHead"] = TOOLHEADS[tool_head]
    log.debug("Current toolhead: %s", sm_status.get("toolHead"))

    # Keep the formats of earlier versions, existing templates rely on them.
    sm_status["progress"] = "{:0.1f}".format((sm_status.get("progress") or 0) * 100)
    for key in ("estimatedTime", "elapsedTime", "remainingTime"):
        sm_status[key] = str(timedelta(seconds=sm_status.get(key) or 0))

    return sm_status


# ------------------------------------------------------------------------------
# Publishing
# ------------------------------------------------------------------------------
def post_webhook(status):
    """Send the status to the Home Assistant webhook."""
    headers = {}
    if SUPERVISOR_TOKEN and HA_WEBHOOK_URL.startswith("http://supervisor/"):
        headers["Authorization"] = f"Bearer {SUPERVISOR_TOKEN}"
    try:
        response = requests.post(HA_WEBHOOK_URL, json=status, headers=headers, timeout=HTTP_TIMEOUT)
        response.raise_for_status()
    except requests.exceptions.RequestException as err:
        log.error("Could not send the status to the Home Assistant webhook: %s", err)
        return
    log.info("Status sent to the Home Assistant webhook")


def post_mqtt(status):
    """Publish the status to the MQTT broker as a retained message."""
    client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2, client_id="snapmaker-monitor")
    if MQTT_USER:
        client.username_pw_set(MQTT_USER, MQTT_PASSWORD)
    try:
        client.connect(MQTT_BROKER, MQTT_PORT, keepalive=30)
        client.loop_start()
        try:
            info = client.publish(MQTT_TOPIC, json.dumps(status, default=str), qos=1, retain=True)
            info.wait_for_publish(timeout=HTTP_TIMEOUT)
            published = info.is_published()
        finally:
            client.disconnect()
            client.loop_stop()
    except (OSError, ValueError, RuntimeError) as err:
        log.error("Could not publish to MQTT broker %s:%s: %s", MQTT_BROKER, MQTT_PORT, err)
        return
    if not published:
        log.error(
            "MQTT broker %s:%s did not confirm the message, check the address and credentials",
            MQTT_BROKER,
            MQTT_PORT,
        )
        return
    log.info("Status published to MQTT topic %s", MQTT_TOPIC)


def post_status(status):
    """Send the status to every configured target."""
    log.debug("Status: %s", json.dumps(status, default=str, indent=2))
    if HA_WEBHOOK_URL:
        post_webhook(status)
    if MQTT_BROKER:
        post_mqtt(status)
    if not HA_WEBHOOK_URL and not MQTT_BROKER:
        log.warning("No webhook or MQTT broker configured, status not sent")


# ------------------------------------------------------------------------------
# Main
# ------------------------------------------------------------------------------
def check_config():
    """Exit early on configuration that can never work."""
    if HA_WEBHOOK_URL:
        parsed = requests.utils.urlparse(HA_WEBHOOK_URL)
        if not (parsed.scheme and parsed.netloc):
            log.error("Webhook URL %s is not a valid URL", HA_WEBHOOK_URL)
            sys.exit(1)


def main(connect_ip):
    """Read the Snapmaker status once and send it."""
    for retry in range(REACHABLE_RETRIES):
        if is_reachable(connect_ip, SM_PORT):
            break
        log.warning(
            "Snapmaker (%s:%s) not reachable, retrying in %d minute(s)",
            connect_ip,
            SM_PORT,
            retry,
        )
        post_status({"status": "UNAVAILABLE", "ip": connect_ip})
        time.sleep(retry * 60)
    else:
        log.error(
            "Snapmaker (%s:%s) not reachable after %d retries",
            connect_ip,
            SM_PORT,
            REACHABLE_RETRIES,
        )
        post_status({"status": "UNAVAILABLE", "ip": connect_ip})
        sys.exit(1)

    sm_token = get_sm_token(connect_ip)
    if not sm_token:
        post_status({"status": "UNAVAILABLE", "ip": connect_ip})
        return
    log.debug("Connected with token %s", mask(sm_token))
    post_status(read_status(connect_ip, sm_token))


def run():
    """Entry point."""
    check_config()

    connect_ip = SM_IP
    if not connect_ip:
        log.info("No Snapmaker IP set, trying to discover it")
        connect_ip = udp_discover()
    if not validate_ip_address(connect_ip):
        log.error("Snapmaker IP (%s) is not a valid IP address", connect_ip)
        sys.exit(1)

    if not IN_ADDON:
        main(connect_ip)
        return

    log.debug("Running inside a Home Assistant add-on container")
    while True:
        try:
            main(connect_ip)
        except Exception:  # keep the service alive, s6 only restarts on exit
            log.exception("An unexpected error occurred")
        time.sleep(POLL_INTERVAL)


if __name__ == "__main__":
    run()
