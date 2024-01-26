import subprocess
import re
import sqlite3
from time import time as now, sleep
from random import random
from config import SQLITE_DICT as SQLITE_DICT

MAC_ADDRESS_REGEX = "((?:[0-9A-Fa-f]{2}[:-]){5}(?:[0-9A-Fa-f]{2}))"
HOSTNAME_REGEX = "Nmap scan report for (.*?)(?:\s\(|\n)"
IP_ADDRESS_REGEX = "^(\d{1,3}(\.|$)){4}"

NETWORK_PREFIX = "192.168.50.*"
QUERY_PARAMS = ("sudo", "nmap", "-sn", NETWORK_PREFIX)

MINUTES = 60

LAST_POLL = 0
POLLING_INTERVAL, NUMBER_POLLS, BETWEEN_POLLS, SLEEP_INTERVAL = 30, 3, 0, 5

# Longer intervals omits brief room leaves
ENDING_INTERVAL = 10 * MINUTES

connections = dict() # {"59:2A:93:C9:2D:14": ("TOG Workstation", 1652798791)}

def poll():
    output = subprocess.run(QUERY_PARAMS, capture_output=True, text=True).stdout
    mac_output = re.findall(MAC_ADDRESS_REGEX, output)
    hostname_output = re.findall(HOSTNAME_REGEX, output)

    # (1653074173, (('59:2A:93:C9:2D:14', 'TOG Workstation'), )
    return (int(now()), tuple(zip(mac_output, hostname_output)))

def multi_poll(number_polls):
    poll_time, poll_result = None, set()
    for _ in range(number_polls):
        poll_output = poll()
        poll_time = poll_output[0] 
        poll_result = poll_result.union(poll_output[1])
        # Device pongs and random times, use varing poll times to maximize capture
        sleep(random() * BETWEEN_POLLS)
    
    # (1653074173, (('45:04:2E:D7:90:00', 'TOG Workstation'), )
    return (poll_time, tuple(poll_result))

def poll_result(number_polls = NUMBER_POLLS):
    global connections
    time_updated, devices = multi_poll(number_polls)
    new_connections = {"time": time_updated, "new": [], "new_name": [], "lost": []}

    for device_mac, device_name in devices:
        if device_mac in connections:
            connections[device_mac] = (device_name, time_updated)
            if device_name != connections[device_mac][0]:
                new_connections["new_name"].append((device_mac, device_name))
        else:
            new_connections["new"].append((device_mac, device_name))
    
    for device_mac, (device_name, last_seen) in connections.items():
        if last_seen + ENDING_INTERVAL < now():
            new_connections["lost"].append((device_mac, device_name, last_seen))
    
    """
    {"time": 1653074173, 
    "new": [('3D:96:79:D6:F7:C7', 'TOG Workstation'),], 
    "new_name": [], 
    "lost": [('45:04:2E:D7:90:00', 'SPZ Workstation', 1653074122),]}
    """
    
    return new_connections

def recover_state():
    # Re-populate connections dict after service restart
    CONNECTIONS_QUERY = \
        """
        SELECT MAC, DeviceName, StartTime 
        FROM DeviceLog
        WHERE CloseTime IS NULL
        """

    res = dict()

    with sqlite3.connect(SQLITE_DICT, timeout=500) as sqdb:
        connections_result = sqdb.execute(CONNECTIONS_QUERY).fetchall()
        for device_mac, device_name, start_time in connections_result:
            res[device_mac] = (device_name, start_time)
    sqdb.close()

    return res

def commit_ends():
    time_updated = int(now())
    
    END_ALL_DANGLING_QUERY = "UPDATE DeviceLog SET CloseTime = ? WHERE CloseTime IS NULL"

    with sqlite3.connect(SQLITE_DICT, timeout=500) as sqdb:
        sqdb.execute(END_ALL_DANGLING_QUERY, (time_updated, ))
    
    sqdb.close()

def commit_updates(update_result):
    global connections

    INSERT_NEW_QUERY = "INSERT INTO DeviceLog VALUES (?, ?, ?, NULL)"
    UPDATE_NAME_QUERY = "UPDATE DeviceLog SET DeviceName = ? WHERE MAC = ?"
    END_QUERY = "UPDATE DeviceLog SET CloseTime = ? WHERE MAC = ? AND CloseTime IS NULL LIMIT 1"
    update_time = update_result["time"]
    
    with sqlite3.connect(SQLITE_DICT, timeout=500) as sqdb:
        for device_mac, device_name in update_result["new"]:
            connections[device_mac] = (device_name, update_time)
            sqdb.execute(INSERT_NEW_QUERY, (device_mac, device_name, update_time))

        for device_mac, device_name in update_result["new_name"]:
            connections[device_mac] = (device_name, update_time)
            sqdb.execute(UPDATE_NAME_QUERY, (device_name, device_mac))
            
        for device_mac, device_name, last_seen in update_result["lost"]:
            del connections[device_mac]
            sqdb.execute(END_QUERY, (last_seen, device_mac))
    
    sqdb.close()

def main():
    global LAST_POLL, POLLING_INTERVAL, connections
    connections = recover_state()

    while True:
        if LAST_POLL + POLLING_INTERVAL <= now():
            LAST_POLL = now()
            update_result = poll_result()
            commit_updates(update_result)
            sleep(SLEEP_INTERVAL)

main()