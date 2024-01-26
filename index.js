import {html, render, useState, useEffect} from "https://origin.astgov.space/exports/dark-magic/preact/bundle-dev.js";

import * as ptt from "./protocol.js";
import * as lit from "./literals.js";

const SUMMARY_URL = "./summary.php";

function App(_1) {
  const [SUM_MAN, _SUM_MAN] = useState(null);
  const [ACTING_INDEX, _ACTING_INDEX] = useState(null);
  
  useEffect(() => {
    ptt.SummaryManager.from_url(SUMMARY_URL).then((sum_man) => _SUM_MAN(sum_man));
  }, []);

  if (SUM_MAN === false) return html`<${lit.LoadingViewer} message="Cannot connect to server." />`;
  if (!SUM_MAN) return html`<${lit.LoadingViewer} />`;

  const header_render = html`<h2 class="header ma0 pa2 bg-washed-red f3 f-mplus">Room Occupancy</h2>`;
  const status_bar_render = html`<${lit.StatusBar} status=${SUM_MAN.status} />`;
  
  const duty_cards_list = Object.values(SUM_MAN.users).map((u) => 
    lit.DutyCard(u.uid, u.name, u.phone, u.start_time, u.status));
  const duty_cards_render = lit.DutyCards(duty_cards_list).render(_ACTING_INDEX);
  const duty_board_render = html`
    <${lit.DutyBoard}>
      ${duty_cards_render}
    </${lit.DutyBoard}>`;
  
  const user_actions_render = (ACTING_INDEX === null) ? null : 
    html`<${lit.UserActions} ...${SUM_MAN.users[ACTING_INDEX]} ping_cancel=${() => _ACTING_INDEX(null)} />`;
  
  return html`
    ${header_render}
    ${status_bar_render}
    ${duty_board_render}
    ${user_actions_render}
  `;
}

render(html`<${App} />`, document.getElementById("root"));