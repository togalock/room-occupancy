import {DateTime} from "https://origin.astgov.space/exports/dark-magic/luxon.js";

function zip(...lists) {
  const MIN_LENGTH = Math.min(...lists.map((l) => l.length));
  const res = [];
  for (let i = 0; i < MIN_LENGTH; i++) {
    res.push(lists.map((l) => l[i]));
  }

  return res;
}

export function SummaryManager(status = "unavailable", users = {}, just_left = {}, devices = {}, non_reg = {}) {
  const res = {status: status, users: users, just_left: just_left, devices: devices, non_reg: non_reg};
  const self = res;

  self.timestamp_repr = function (timestamp) {
    const dt = DateTime.fromSeconds(timestamp);
    const time_repr = dt.toFormat("HH:mm");
    const duration_repr = dt.diffNow().negate().toFormat("+hh:mm");

    return [time_repr, duration_repr];
  }

  self.objectify_fields = function(json) {
    const OBJECTIFY_RULES = {
      "users": (l) => l.map((a) => Object.fromEntries(zip(["uid", "name", "phone", "start_time"], a))),
      "just_left": (l) => l.map((a) => Object.fromEntries(zip(["uid", "name", "phone", "stop_time"], a))),
      "devices": (l) => l.map((a) => Object.fromEntries(zip(["mac", "name", "uid", "start_time"], a))),
      "non_reg": (l) => l.map((a) => Object.fromEntries(zip(["mac", "name", "start_time"], a))),
    };

    if (typeof(json) === "string") json = JSON.parse(json);

    const res_json = {};
    for (const [key, object] of Object.entries(json)) {
      res_json[key] = (OBJECTIFY_RULES[key]) ? (OBJECTIFY_RULES[key])(object) : object;
    }

    return res_json;
  }

  self.from_url = async function(url) {
    const req = await fetch(url);
    if (!req.ok) return false;

    let req_json = await req.json();
    req_json = cls.objectify_fields(req_json);

    const {status, users, just_left, devices, non_reg} = req_json;

    return SummaryManager(status, users, just_left, devices, non_reg);
  }

  return self;
}