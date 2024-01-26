import sqlite3
from config import SQLITE_DICT as SQLITE_DICT 

USERS_QUERY = \
    """
    SELECT Users.UID, Users.Name, Users.Phone, MIN(DeviceLog.StartTime) AS StartTime
    FROM DeviceLog
    JOIN UserDevices ON UserDevices.MAC = DeviceLog.MAC
    JOIN Users ON UserDevices.UID = Users.UID
    WHERE CloseTime IS NULL
    """

DEVICES_QUERY = \
    """
    SELECT TrackedDevices.MAC, TrackedDevices.Name, DeviceLog.StartTime
    FROM DeviceLog
    JOIN TrackedDevices ON DeviceLog.MAC = TrackedDevices.MAC
    WHERE CloseTime IS NULL
    """

NONREG_QUERY = \
    """
    SELECT DeviceLog.MAC, DeviceLog.DeviceName, DeviceLog.StartTime
    FROM DeviceLog
    LEFT JOIN UserDevices ON UserDevices.MAC = DeviceLog.MAC
    LEFT JOIN TrackedDevices ON TrackedDevices.MAC = DeviceLog.MAC
    WHERE CloseTime IS NULL AND (UserDevices.MAC IS NULL AND TrackedDevices.MAC IS NULL)
    """

sqdb = sqlite3.connect(SQLITE_DICT, 500)

def row_to_dict(sqlite_row):
    return dict(zip(sqlite_row.keys(), sqlite_row))

def main():
    with sqdb:
        users = sqdb.execute(USERS_QUERY).fetchall() # TOG, Togalk, 12345678, 16781358913
        devices = sqdb.execute(DEVICES_QUERY).fetchall() # 3D:96:79:D6:F7:C7, TOG Workstation, 16781358913
        non_reg = sqdb.execute(NONREG_QUERY).fetchall() # 3D:96:79:D6:F7:C7, TOG Workstation, 16781358913
    sqdb.close()
    
    print("Users: ")
    print("\n".join([repr(row) for row in users]))

    print("Devices: ")
    print("\n".join([repr(row) for row in devices]))

    print("Non-registered devices: ")
    print("\n".join([repr(row) for row in non_reg]))


main()