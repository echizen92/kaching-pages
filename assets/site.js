// The landing page: live rooms (room.js), Mochi's speech, the day that runs as you scroll, the
// playground, and the small demos. Everything works without it; it only adds the motion.
import { Room, timeOfDay } from "./room.js?v=9084d336";

const $ = (s, el = document) => el.querySelector(s);
const $$ = (s, el = document) => [...el.querySelectorAll(s)];
const REDUCE = matchMedia("(prefers-reduced-motion: reduce)").matches;
const TOD = { dawn: "Dawn", day: "Day", dusk: "Dusk", night: "Night" };
const money = (v) => "S$" + v.toLocaleString("en-SG", { minimumFractionDigits: 2, maximumFractionDigits: 2 });

// Header gains a backdrop once the page moves.
const top = $(".top");
const onScroll = () => top.classList.toggle("scrolled", scrollY > 8);
addEventListener("scroll", onScroll, { passive: true });
onScroll();

// Rooms start loading as they come near the screen.
const rooms = new Map();
const roomFor = (canvas) => {
  if (!rooms.has(canvas)) {
    const state = JSON.parse(canvas.dataset.room);
    if (state.time === "auto") state.time = timeOfDay();
    rooms.set(canvas, new Room(canvas, state));
  }
  return rooms.get(canvas);
};
const near = new IntersectionObserver((entries) => {
  for (const e of entries) if (e.isIntersecting) { roomFor(e.target); near.unobserve(e.target); }
}, { rootMargin: "600px 0px" });
$$("canvas[data-room]").forEach((c) => near.observe(c));

// Hero: the room follows the visitor's clock; Mochi talks.
const heroCanvas = $("canvas[data-hero]");
const hero = roomFor(heroCanvas);
const chip = $("[data-tod-chip]");
chip.textContent = `${TOD[hero.state.time]} · your time`;
const speech = $("[data-speech]");
const lines = $$("[data-lines] li").map((li) => li.textContent);
// October: the room's dressed for Halloween, and Mochi's in a witch hat.
if (hero.state.season === "halloween") lines.unshift("It's Halloween month! Do you like my hat? The budgets aren't scary, I promise.");
let line = 0, typing;
function say(text) {
  clearInterval(typing);
  if (REDUCE) { speech.textContent = text; return; }
  let i = 0;
  speech.textContent = "";
  const caret = document.createElement("span");
  caret.className = "caret";
  typing = setInterval(() => {
    i += 1;
    speech.textContent = text.slice(0, i);
    speech.append(caret);
    if (i >= text.length) { clearInterval(typing); setTimeout(() => caret.remove(), 1200); }
  }, 26);
}
let talk = setInterval(next, 6500);
function next() { line = (line + 1) % lines.length; say(lines[line]); }
heroCanvas.addEventListener("click", () => {
  say(["Purr… that's the spot.", "Hehe, again!", "You're my favourite human."][Math.floor(Math.random() * 3)]);
  clearInterval(talk); talk = setInterval(next, 6500);
});
say(lines[0]);

// Reveals and count-ups.
function count(el) {
  const to = parseFloat(el.dataset.count);
  if (REDUCE || el.dataset.done) { el.textContent = money(to); return; }
  el.dataset.done = 1;
  const start = performance.now(), length = 1300;
  const step = (now) => {
    const t = Math.min(1, (now - start) / length), e = 1 - Math.pow(1 - t, 3);
    el.textContent = money(to * e);
    if (t < 1) requestAnimationFrame(step);
  };
  requestAnimationFrame(step);
}
const reveal = new IntersectionObserver((entries) => {
  for (const e of entries) if (e.isIntersecting) { e.target.classList.add("in"); reveal.unobserve(e.target); }
}, { rootMargin: "0px 0px -12% 0px" });
$$("[data-reveal]").forEach((el) => reveal.observe(el));

// A day with Mochi: whichever chapter holds the middle of the screen sets the time.
const day = $(".day");
const storyCanvas = $("canvas[data-story]");
const storyChip = $("[data-story-chip]");
const chapters = $$("[data-chapter]");
const active = new IntersectionObserver((entries) => {
  for (const e of entries) {
    if (!e.isIntersecting) continue;
    const ch = e.target;
    ch.classList.add("in");
    $$("[data-count]", ch).forEach(count);
    const state = JSON.parse(ch.dataset.chapter);
    day.dataset.time = state.time;
    storyChip.textContent = TOD[state.time];
    roomFor(storyCanvas).set(state);
  }
}, { rootMargin: "-45% 0px -45% 0px" });
chapters.forEach((c) => active.observe(c));

// Make it yours.
const playCanvas = $("canvas[data-play]");
const playChip = $("[data-play-chip]");
const caption = $("[data-caption]");
const CAPTIONS = {
  cat: { tabby: "An orange tabby in a green jumper.", tuxedo: "A tuxedo in a cranberry sweater. Switching keeps your friendship, paws and furniture." },
  time: { dawn: "Dawn, day, dusk and night follow your clock.", day: "Dawn, day, dusk and night follow your clock.", dusk: "The lamp comes on at dusk.", night: "At night the room glows and Mochi gets sleepy." },
  weather: { clear: "With weather on, the window shows the sky outside your real one.", cloudy: "A grey day dims the room a little.", rain: "Rain runs down the glass, and Mochi naps more on wet days.", storm: "Storms flash. Mochi is brave about it. Mostly.", snow: "Snow drifts past the window." },
  climate: { mild: "Mild out. Nothing to plug in.", hot: "Hot day? Out comes the fan, and it oscillates.", cold: "Cold day? The heater comes out and glows." },
  furniture: "Earn paws by logging purchases and finishing goals, then spend them on the room. Paws have no cash value.",
};
const pose = (s) => (s.time === "night" ? "sleep" : "sit");
const playState = { cat: "tabby", time: "day", weather: "clear", climate: "mild", furniture: [] };
function applyPlay(key) {
  playChip.textContent = `${TOD[playState.time]} · ${playState.weather}`;
  caption.textContent = key === "furniture" ? CAPTIONS.furniture : CAPTIONS[key][playState[key]];
  roomFor(playCanvas).set({ ...playState, pose: pose(playState) });
}
for (const group of $$("[data-set]")) {
  group.addEventListener("click", (e) => {
    const b = e.target.closest("button");
    if (!b) return;
    $$("button", group).forEach((x) => x.setAttribute("aria-pressed", String(x === b)));
    playState[group.dataset.set] = b.value;
    applyPlay(group.dataset.set);
  });
}
$("[data-toggle=furniture]").addEventListener("click", (e) => {
  const b = e.target.closest("button");
  if (!b) return;
  const on = b.getAttribute("aria-pressed") !== "true";
  b.setAttribute("aria-pressed", String(on));
  // One piece per slot, as in the app: the cushion and the armchair's slot are both seats, but the
  // armchair is always there, so pieces never clash here.
  playState.furniture = on ? [...playState.furniture, b.value] : playState.furniture.filter((f) => f !== b.value);
  applyPlay("furniture");
});

// Travel: currencies flip over.
const FX = [["MYR 42.50", "S$13.30"], ["¥1,200", "S$10.84"], ["฿350.00", "S$13.12"], ["€18.00", "S$25.31"], ["US$9.99", "S$12.95"]];
const fxFrom = $("[data-fx-from]"), fxTo = $("[data-fx-to]");
let fx = 0;
if (!REDUCE) setInterval(() => {
  fx = (fx + 1) % FX.length;
  [fxFrom, fxTo].forEach((el) => el.classList.add("out"));
  setTimeout(() => {
    fxFrom.textContent = FX[fx][0]; fxTo.textContent = FX[fx][1];
    [fxFrom, fxTo].forEach((el) => el.classList.remove("out"));
  }, 450);
}, 2600);

// Hide amounts.
const maskButton = $("[data-mask]"), maskVal = $("[data-mask-val]");
maskButton.addEventListener("click", () => {
  const hidden = maskButton.getAttribute("aria-pressed") !== "true";
  maskButton.setAttribute("aria-pressed", String(hidden));
  maskButton.setAttribute("aria-label", hidden ? "Show amounts" : "Hide amounts");
  maskButton.textContent = hidden ? "🙈" : "👁";
  maskVal.textContent = hidden ? "••••••" : "S$5,234.24";
});
