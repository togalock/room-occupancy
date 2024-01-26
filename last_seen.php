<?php

include "config.php";

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

?>