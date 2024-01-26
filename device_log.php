<?php

include 'config.php';

$sqdb = new SQLite3($SQLITE_DICT, SQLITE3_OPEN_READONLY);
$sqdb->busyTimeout(5000);

function fetch_rows($query_result, $max_rows = false) {
    if ($query_result == false) return [];
    $res = []; $rows_fetched = 0;

    while ($row = $query_result->fetchArray(SQLITE3_NUM)) {
      if ($query_result->columnType(0) == SQLITE3_NULL) break;
      if ($max_rows !== false && $rows_fetched >= $max_rows) break;
      array_push($res, $row); $rows_fetched++;
    }
    
    return $res;
}

function fetch_all_rows($query_result) {
    return fetch_rows($query_result, false);
}

$LOG_QUERY = <<<QUERY
SELECT DeviceLog.MAC, DeviceLog.DeviceName, DeviceLog.StartTime, DeviceLog.CloseTime,
TrackedDevices.Name, Users.UID, Users.Name
FROM DeviceLog
LEFT OUTER JOIN TrackedDevices ON DeviceLog.MAC = TrackedDevices.MAC
LEFT OUTER JOIN UserDevices ON DeviceLog.MAC = UserDevices.MAC
LEFT OUTER JOIN Users ON UserDevices.UID = Users.UID
ORDER BY DeviceLog.ROWID DESC
QUERY;

$max_rows = (isset($_REQUEST['n'])) ? $_REQUEST['n'] : false;

$device_logs = fetch_rows($sqdb->query($LOG_QUERY), $max_rows);
$sqdb->close();

echo(json_encode($device_logs));
?>