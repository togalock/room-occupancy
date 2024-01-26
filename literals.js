import { DateTime } from "https://origin.astgov.space/exports/dark-magic/luxon.js";
import { html } from "https://origin.astgov.space/exports/dark-magic/preact/bundle-dev.js";

export function LoadingViewer({ message = "Loading..." }) {
  return html`
    <div class="loading-viewer h-100 flex flex-column justify-center items-center f-mplus bg-washed-red">
      <div class="f3 ma1">${message}</div>
    </div>
  `;
}

export function StatusBar({ status }) {
  return (status === "active")
    ? html`<div class="status-line h1 f-mplus tb bg-green"></div>`
    : html`<div class="status-line pa2 f-mplus tb bg-yellow">Refresh broke!!! (${status})</div>`;
}

export function DutyCard(uid, name, phone, timestamp, status = null) {
  const res = {
    uid: uid,
    name: name,
    phone: phone,
    timestamp: timestamp,
    status: status,
  };
  const self = res;

  self.timestamp_repr = function (timestamp) {
    const dt = DateTime.fromSeconds(timestamp);
    const time_repr = dt.toFormat("HH:mm");
    const duration_repr = dt.diffNow().negate().toFormat("+hh:mm");

    return [time_repr, duration_repr];
  };

  self.render = function (ping_i) {
    if (!ping_i) ping_i = (_1) => undefined;

    const [time_repr, duration_repr] = self.timestamp_repr(self.timestamp);

    return html`
    <div class="duty-card flex flex-row items-center ma2 ph1 bw2 pointer bl b--light-green" onclick=${ping_i}>
      <div class="left">
      <p class="name ma1 f3">${self.name}</p>
      ${!self.status ? null : html`<p class="status ma1 f5">Some status</p>`}
      </div>
      <div class="right ml2 tr">
      <p class="time ma1 f5">${time_repr}</p>
      <p class="duration ma1 f7">${duration_repr}</p>
      </div>
    </div>
    `;
  };

  return self;
}

export function DutyCards(duty_cards = []) {
  const res = { duty_cards: duty_cards };
  const self = res;

  self.render = function(ping_i) {
    return html`
      <div class="duty-cards flex flex-wrap flex-column flex-row-ns">
        ${self.duty_cards.map((card, i) => card.render(() => ping_i(i)))}
      </div>
    `;
  };
}

export function DutyBoard({ children }) {
  return html`
  <div class="duty-board pa2 f-mplus">
    <h5 class="f5 ma0">Now active</h5>
    ${children}
  </div>
  `;
}

export function UserActions({ name, phone, ping_cancel }) {
  return html`
    <div class="user-action fixed pa2 bottom-1 right-1 f-mplus tr fw3 outline">
      <p class="name mv1 fw4">${name}</p>

      <a class="link" href="https://wa.me/${phone}">
        <div class="whatsapp-block mv1">
            <ion-icon class="v-mid" name="logo-whatsapp"></ion-icon>
            <span class="v-mid">Whatsapp</span>
        </div>
      </a>

      <a class="link" href="tel:${phone}">
        <div class="phone-block mv1">
          <ion-icon class="v-mid" name="call-outline"></ion-icon>
          <span class="v-mid">Call ${phone}</span>
        </div>
      </a>

      <div class="cancel-block mv1 pointer shadow" onclick=${ping_cancel}>
        <ion-icon class="v-mid" name="close-outline"></ion-icon>
        <span class="v-mid">Cancel</span>
      </div>
    </div>
  `;
}
