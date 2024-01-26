<?php
include 'config.php';

$MINUTES = 60;

$sqdb = new SQLite3($SQLITE_DICT, SQLITE3_OPEN_READONLY);
$sqdb->busyTimeout(5000);

function fetch_rows($query_result, $max_rows = false) {
  if ($query_result == false) return [];
  $res = []; $rows_fetched = 0;

  while ($row = $query_result->fetchArray(SQLITE3_NUM)) {
    if ($query_result->columnType(0) === SQLITE3_NULL) break;
    if ($max_rows !== false && $rows_fetched >= $max_rows) break;
    array_push($res, $row); $rows_fetched++;
  }

  return $res;
}

function fetch_all_rows($query_result) {
  return fetch_rows($query_result, false);
}

$USERS_QUERY = <<<QUERY
SELECT Users.UID, Users.Name, Users.Phone, DeviceLog.StartTime
FROM DeviceLog
JOIN UserDevices ON UserDevices.MAC = DeviceLog.MAC
JOIN Users ON UserDevices.UID = Users.UID
WHERE DeviceLog.CloseTime IS NULL
GROUP BY Users.UID ORDER BY StartTime
QUERY;

$JUST_LEFT_TIME = time() - 10 * $MINUTES;

$JUST_LEFT_QUERY = <<<QUERY
SELECT Users.UID, Users.Name, Users.Phone, DeviceLog.CloseTime
FROM DeviceLog
JOIN UserDevices ON UserDevices.MAC = DeviceLog.MAC
JOIN Users ON UserDevices.UID = Users.UID
WHERE DeviceLog.CloseTime >= $JUST_LEFT_TIME
QUERY;

$DEVICES_QUERY = <<<QUERY
SELECT TrackedDevices.MAC, TrackedDevices.Name, TrackedDevices.UID, DeviceLog.StartTime
FROM DeviceLog
JOIN TrackedDevices ON DeviceLog.MAC = TrackedDevices.MAC
WHERE CloseTime IS NULL
QUERY;

$NONREG_QUERY = <<<QUERY
SELECT DeviceLog.MAC, DeviceLog.DeviceName, DeviceLog.StartTime
FROM DeviceLog
LEFT JOIN UserDevices ON UserDevices.MAC = DeviceLog.MAC
LEFT JOIN TrackedDevices ON TrackedDevices.MAC = DeviceLog.MAC
WHERE CloseTime IS NULL AND (UserDevices.MAC IS NULL AND TrackedDevices.MAC IS NULL)
QUERY;

$users = fetch_all_rows($sqdb->query($USERS_QUERY));
$just_left = fetch_all_rows($sqdb->query($JUST_LEFT_QUERY));
$devices = fetch_all_rows($sqdb->query($DEVICES_QUERY));
$non_reg = fetch_all_rows($sqdb->query($NONREG_QUERY));
$sqdb->close();

$status = trim(shell_exec("systemctl is-active $SERVICE_NAME"));

$results = [
  "status" => $status, 
  "users" => $users, 
  "just_left" => $just_left,
  "devices" => $devices, 
  "non_reg" => $non_reg,
];

echo(json_encode($results));

/*
  {"status" : "active",
  "users" : [["TOG", "Togalk", 12345678, 1706277286]],
  "just_left": [["SPZ", "Spasel", 23456789, 1706293026]],
  "devices" : [["E8:3E:5E:9A:64:61","TOG Workstation","TOG",1705582248]]
  "non_reg" : [["3D:96:79:D6:F7:C7","192.168.50.4",1683540107]]}
*/
?>