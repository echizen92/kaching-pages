// The Kachingz room, live in a canvas: the app's own art and coordinates (tools/room_assets.py packs
// them), drawn the way the app's MochiRoomView does. A 358-unit square scene; things are drawn back
// to front by where they meet the floor; the cat is tinted by the time of day and casts a shadow.

const BASE = new URL("room/", import.meta.url);
const REDUCE = matchMedia("(prefers-reduced-motion: reduce)");
const images = new Map();
let layoutPromise;

function image(path) {
  if (!images.has(path)) {
    images.set(path, new Promise((resolve, reject) => {
      const im = new Image();
      im.decoding = "async";
      im.onload = () => resolve(im);
      im.onerror = reject;
      im.src = new URL(path, BASE).href;
    }));
  }
  return images.get(path);
}
const layout = () => (layoutPromise ??= fetch(new URL("layout.json", BASE)).then((r) => r.json()));

/** The time of day on the visitor's own clock, as the app works it out. */
export function timeOfDay(date = new Date()) {
  const h = date.getHours() + date.getMinutes() / 60;
  return h >= 5 && h < 8 ? "dawn" : h >= 8 && h < 17 ? "day" : h >= 17 && h < 20 ? "dusk" : "night";
}

const POSES = { idle: "idle", sit: "sitloop", sleep: "sleeploop", joy: "joy" };
const FPS = { idle: 14, sitloop: 14, sleeploop: 14, joy: 12 };
const noise = (n) => { const v = Math.sin(n * 12.9898) * 43758.5453; return v - Math.floor(v); };

export class Room {
  constructor(canvas, state = {}) {
    this.canvas = canvas;
    this.ctx = canvas.getContext("2d");
    this.state = { cat: "tabby", time: "day", weather: "clear", climate: "mild", pose: "idle", furniture: [], ...state };
    this.scratch = document.createElement("canvas");
    this.clock = 0;
    this.clipStart = 0;
    this.effects = [];
    this.visible = false;
    this.img = {};
    this.seq = 0;
    this.ready = this.load(this.state).then(() => {
      this.resize();
      this.draw(0);
      canvas.classList.add("is-ready");
    });
    new ResizeObserver(() => { this.resize(); this.draw(this.clock); }).observe(canvas);
    new IntersectionObserver(([e]) => { this.visible = e.isIntersecting; this.loop(); }, { rootMargin: "120px" }).observe(canvas);
    document.addEventListener("visibilitychange", () => this.loop());
    REDUCE.addEventListener?.("change", () => this.draw(this.clock));
    canvas.addEventListener("click", (e) => this.tap(e));
  }

  /** Changes any of cat, time, weather, climate, pose or furniture. Times and poses cross-fade. */
  async set(next) {
    const seq = ++this.seq;
    this.target = { ...(this.target ?? this.state), ...next };
    const target = this.target;
    await this.ready;
    await this.load(target);
    if (seq !== this.seq) return; // a newer change is on its way
    const prev = this.state;
    if (target.time !== prev.time) this.fade = { from: this.snapshot(), start: this.clock, length: 0.9 };
    if (target.pose !== prev.pose || target.cat !== prev.cat) {
      const frame = this.frameNow(prev);
      this.ghost = { frame, sheet: this.img[`${frame.cat}/${frame.clip}.webp`], start: this.clock };
      this.clipStart = this.clock;
    }
    this.state = { ...target };
    this.draw(this.clock);
  }

  /** A pat: the joy clip once, a few hearts, then back to what the cat was doing. */
  pet() {
    if (this.state.pose === "sleep" || this.state.pose === "joy") return this.hearts();
    const back = this.state.pose;
    this.set({ pose: "joy" });
    this.hearts();
    clearTimeout(this.joyTimer);
    this.joyTimer = setTimeout(() => { if (this.state.pose === "joy") this.set({ pose: back }); },
                               (this.L?.cats[this.state.cat].joy.frames ?? 61) / FPS.joy * 1000 + 250);
  }

  hearts() {
    for (let i = 0; i < 3; i++) this.effects.push({ kind: "heart", start: this.clock + i * 0.18, dx: (i - 1) * 9 });
  }

  // ---------------------------------------------------------------------------------------------

  async load(s) {
    this.L ??= await layout();
    const clip = POSES[s.pose];
    const needs = [`room-${s.time}.webp`, `lamp-${s.time}.webp`, `fishbowl-${s.time}.webp`, "chair.webp",
                   `${s.cat}/${clip}.webp`];
    if (s.weather !== "clear") needs.push(`weather/${s.weather}-${s.time}.webp`, "weather/glass.webp");
    if (s.climate === "hot") needs.push("weather/fan.webp");
    if (s.climate === "cold") needs.push("weather/heater.webp");
    for (const id of s.furniture) needs.push(`furniture/${id}-${s.time}.webp`);
    const loaded = await Promise.all(needs.map(async (n) => [n, await image(n)]));
    this.img = { ...this.img, ...Object.fromEntries(loaded) };
  }

  resize() {
    const r = this.canvas.getBoundingClientRect();
    const side = Math.max(1, Math.round(Math.min(r.width, r.height || r.width) * Math.min(devicePixelRatio || 1, 2)));
    if (this.canvas.width !== side) { this.canvas.width = side; this.canvas.height = side; }
  }

  loop() {
    const run = this.visible && !document.hidden && !REDUCE.matches;
    if (run && !this.raf) {
      let last = performance.now();
      // 30 fps is plenty: the cat animates at 14 and the fan at 12. It saves the battery.
      const tick = (now) => {
        this.raf = requestAnimationFrame(tick);
        if (now - last < 32) return;
        this.clock += Math.min(0.1, (now - last) / 1000);
        last = now;
        this.draw(this.clock);
      };
      this.raf = requestAnimationFrame(tick);
    } else if (!run && this.raf) {
      cancelAnimationFrame(this.raf);
      this.raf = null;
    }
  }

  frameNow(s = this.state) {
    const clip = POSES[s.pose];
    const meta = this.L.cats[s.cat][clip];
    const t = REDUCE.matches ? 0 : this.clock - this.clipStart;
    const i = s.pose === "joy" ? Math.min(meta.frames - 1, Math.floor(t * FPS[clip])) : Math.floor(t * FPS[clip]) % meta.frames;
    return { cat: s.cat, clip, meta, index: i, at: this.catSpot(s) };
  }

  catSpot(s = this.state) {
    const r = this.L.room;
    return s.pose === "sleep" ? { x: r.bed.top[0], y: r.bed.top[1], depth: r.bed.floor[1] } : { x: r.home[0], y: r.home[1], depth: r.home[1] };
  }

  snapshot() {
    const c = document.createElement("canvas");
    c.width = this.canvas.width; c.height = this.canvas.height;
    c.getContext("2d").drawImage(this.canvas, 0, 0);
    return c;
  }

  tap(e) {
    if (!this.L) return;
    const r = this.canvas.getBoundingClientRect();
    const x = (e.clientX - r.left) / r.width * 358, y = (e.clientY - r.top) / r.height * 358;
    const p = this.catSpot();
    const k = this.L.height / 340;
    if (Math.abs(x - p.x) < 34 && y < p.y + 6 && y > p.y - 300 * k) this.pet();
  }

  // ---------------------------------------------------------------------------------------------

  draw(time) {
    if (!this.L || !this.img[`room-${this.state.time}.webp`]) return;
    const { ctx, canvas, L, state: s } = this;
    const u = canvas.width / 358;
    const light = s.time === "day" ? null : L.light[s.time].map((v) => Math.min(1, v));
    const k = L.height / 340;
    ctx.setTransform(1, 0, 0, 1, 0, 0);
    ctx.clearRect(0, 0, canvas.width, canvas.height);

    const p = L.room.image;
    ctx.drawImage(this.img[`room-${s.time}.webp`], p.x * u, p.y * u, p.size * u, p.size * u);
    const win = L.weather.window;
    if (s.weather !== "clear") ctx.drawImage(this.img[`weather/${s.weather}-${s.time}.webp`], win.x * u, win.y * u, win.w * u, win.h * u);
    for (const piece of L.furniture.pieces) {
      if (!s.furniture.includes(piece.id) || piece.x == null) continue;
      ctx.drawImage(this.img[`furniture/${piece.id}-${s.time}.webp`], piece.x * u, piece.y * u, piece.w * u, piece.h * u);
    }

    // Back to front by where each thing meets the floor.
    const items = [];
    const [cx, cy] = L.room.chair;
    items.push([cy, () => this.sprite(this.img["chair.webp"], { ...L.chair, cw: L.chair.w, ch: L.chair.h, cols: 1 }, 0, cx, cy, k, u, light, true)]);
    for (const layer of L.room.layers) {
      items.push([layer.baseY, () => ctx.drawImage(this.img[`${layer.name}-${s.time}.webp`], layer.x * u, layer.y * u, layer.w * u, layer.h * u)]);
    }
    const appliance = s.climate === "hot" ? "fan" : s.climate === "cold" ? "heater" : null;
    if (appliance) {
      const a = L.weather.appliances[appliance];
      const i = a.frames > 1 && !REDUCE.matches ? Math.floor(time * a.fps) % a.frames : 0;
      items.push([a.spot[1], () => this.sprite(this.img[`weather/${appliance}.webp`], a, i, a.spot[0], a.spot[1], a.scale, u, null, true)]);
    }
    const f = this.frameNow();
    items.push([f.at.depth, () => {
      this.sprite(this.img[`${f.cat}/${f.clip}.webp`], f.meta, f.index, f.at.x, f.at.y, k, u, light, true);
      // The outgoing frame fades over the new one, as in the app.
      const ghost = this.ghost;
      if (ghost && time - ghost.start < 0.16 && !REDUCE.matches) {
        ctx.globalAlpha = 1 - (time - ghost.start) / 0.16;
        const g = ghost.frame;
        this.sprite(ghost.sheet, g.meta, g.index, g.at.x, g.at.y, k, u, light, false);
        ctx.globalAlpha = 1;
      }
    }]);
    items.sort((a, b) => a[0] - b[0]).forEach(([, draw]) => draw());

    if (appliance === "heater") this.glow(u, time);
    this.weather(u, time);
    this.drawEffects(u, time, f);

    if (this.fade) {
      const t = (time - this.fade.start) / this.fade.length;
      if (t >= 1 || REDUCE.matches) this.fade = null;
      else {
        ctx.globalAlpha = 1 - t * t * (3 - 2 * t);
        ctx.drawImage(this.fade.from, 0, 0, canvas.width, canvas.height);
        ctx.globalAlpha = 1;
      }
    }
  }

  /** One frame of a sheet, pinned at its feet, tinted, with a cast shadow made from the same frame. */
  sprite(sheet, meta, index, x, y, k, u, tint, shadow) {
    const { ctx } = this;
    const sx = (index % meta.cols) * meta.cw, sy = Math.floor(index / meta.cols) * meta.ch;
    const dw = meta.w * k * u, dh = meta.h * k * u;
    const scratch = this.scratch;
    const sw = Math.ceil(dw), sh = Math.ceil(dh);
    if (scratch.width < sw || scratch.height < sh) { scratch.width = Math.max(scratch.width, sw); scratch.height = Math.max(scratch.height, sh); }
    const sc = scratch.getContext("2d");
    const paint = (fill) => {
      sc.globalCompositeOperation = "source-over";
      sc.clearRect(0, 0, scratch.width, scratch.height);
      sc.drawImage(sheet, sx, sy, meta.cw, meta.ch, 0, 0, dw, dh);
      if (fill) {
        sc.globalCompositeOperation = fill === "black" ? "source-in" : "multiply";
        sc.fillStyle = fill === "black" ? "#000" : `rgb(${fill.map((v) => v * 255).join(",")})`;
        sc.fillRect(0, 0, sw, sh);
        if (fill !== "black") { sc.globalCompositeOperation = "destination-in"; sc.drawImage(sheet, sx, sy, meta.cw, meta.ch, 0, 0, dw, dh); }
        sc.globalCompositeOperation = "source-over";
      }
    };
    if (shadow) {
      paint("black");
      ctx.save();
      ctx.translate(x * u, y * u);
      ctx.transform(1, 0, Math.tan(-50 * Math.PI / 180), 1, 0, 0);
      ctx.scale(1, 0.24);
      ctx.globalAlpha = 0.2;
      if ("filter" in ctx) ctx.filter = `blur(${2.5 * u}px)`;
      ctx.drawImage(scratch, 0, 0, sw, sh, -meta.fx * k * u, -meta.fy * k * u, sw, sh);
      ctx.restore();
    }
    paint(tint);
    ctx.drawImage(scratch, 0, 0, sw, sh, x * u - meta.fx * k * u, y * u - meta.fy * k * u, sw, sh);
  }

  glow(u, time) {
    const { ctx } = this;
    const [x, y] = this.L.weather.appliances.heater.spot;
    const flicker = REDUCE.matches ? 1 : 0.9 + 0.1 * Math.sin(time * 2.1);
    const g = ctx.createRadialGradient(x * u, (y - 14) * u, 0, x * u, (y - 14) * u, 70 * u);
    const night = this.state.time === "night" || this.state.time === "dusk";
    g.addColorStop(0, `rgba(255,140,60,${(night ? 0.32 : 0.18) * flicker})`);
    g.addColorStop(1, "rgba(255,140,60,0)");
    ctx.globalCompositeOperation = "screen";
    ctx.fillStyle = g;
    ctx.fillRect(0, 0, 358 * u, 358 * u);
    ctx.globalCompositeOperation = "source-over";
  }

  /** Grey days dim the room; rain and snow move on the glass; storms flash. (MochiRoomView.drawWeather) */
  weather(u, time) {
    const { ctx, L, state: s } = this;
    if (s.weather === "clear") return;
    let light = L.weather.light[s.weather];
    if (s.time === "night") light = light.map((v) => 1 - (1 - v) * 0.5);
    ctx.globalCompositeOperation = "multiply";
    ctx.fillStyle = `rgb(${light.map((v) => v * 255).join(",")})`;
    ctx.fillRect(0, 0, 358 * u, 358 * u);
    ctx.globalCompositeOperation = "source-over";
    if (s.weather === "cloudy") return;
    const w = L.weather.window;
    const t = REDUCE.matches ? 0 : time;
    const glass = this.glassLayer ??= document.createElement("canvas");
    glass.width = Math.ceil(w.w * u); glass.height = Math.ceil(w.h * u);
    const g = glass.getContext("2d");
    g.clearRect(0, 0, glass.width, glass.height);
    if (s.weather === "snow") {
      g.fillStyle = "rgba(255,255,255,.85)";
      for (let i = 0; i < 26; i++) {
        const speed = 5 + noise(i + 1) * 5;
        const y = (noise(i + 2) * w.h + t * speed) % w.h;
        const x = noise(i) * w.w + Math.sin(t * 0.9 + i) * 2.5;
        g.beginPath(); g.arc(x * u, y * u, (0.7 + noise(i + 3) * 0.8) * u, 0, Math.PI * 2); g.fill();
      }
    } else {
      const heavy = s.weather === "storm";
      g.strokeStyle = `rgba(255,255,255,${heavy ? 0.45 : 0.35})`;
      g.lineWidth = 0.55 * u;
      for (let i = 0; i < (heavy ? 40 : 26); i++) {
        const speed = (heavy ? 70 : 48) + noise(i + 1) * 20;
        const length = (heavy ? 7 : 5) + noise(i + 4) * 3;
        const y = ((noise(i + 2) * w.h + t * speed) % (w.h + length)) - length;
        const x = noise(i) * w.w;
        g.beginPath(); g.moveTo(x * u, y * u); g.lineTo((x - length * 0.18) * u, (y + length) * u); g.stroke();
      }
      if (heavy && !REDUCE.matches) {
        const phase = time % 11;
        const flash = phase < 0.07 ? 1 : phase > 0.16 && phase < 0.24 ? 0.55 : 0;
        if (flash) {
          g.fillStyle = `rgba(255,255,255,${0.75 * flash})`; g.fillRect(0, 0, glass.width, glass.height);
          ctx.fillStyle = `rgba(255,255,255,${0.07 * flash})`; ctx.fillRect(0, 0, 358 * u, 358 * u);
        }
      }
    }
    g.globalCompositeOperation = "destination-in";
    g.drawImage(this.img["weather/glass.webp"], 0, 0, glass.width, glass.height);
    g.globalCompositeOperation = "source-over";
    ctx.drawImage(glass, w.x * u, w.y * u);
  }

  /** Hearts after a pat; Zs while asleep. */
  drawEffects(u, time, f) {
    const { ctx } = this;
    const k = this.L.height / 340;
    const top = f.at.y - (f.meta.fy - 30) * k;
    ctx.textAlign = "center";
    this.effects = this.effects.filter((e) => time - e.start < 1.3);
    for (const e of this.effects) {
      const t = (time - e.start) / 1.3;
      if (t < 0) continue;
      ctx.globalAlpha = Math.max(0, 1 - t * t);
      ctx.fillStyle = "#E8506A";
      ctx.font = `${(9 + 4 * t) * u}px system-ui, sans-serif`;
      ctx.fillText("♥", (f.at.x + e.dx + Math.sin(t * 6 + e.dx) * 3) * u, (top - 34 * t) * u);
    }
    if (this.state.pose === "sleep" && !REDUCE.matches) {
      for (let i = 0; i < 3; i++) {
        const t = ((time + i * 0.9) % 2.7) / 2.7;
        ctx.globalAlpha = Math.sin(t * Math.PI) * 0.9;
        ctx.fillStyle = this.state.time === "night" ? "#E9E6FF" : "#5B4691";
        ctx.font = `600 ${(7 + 5 * t) * u}px Fraunces, Georgia, serif`;
        ctx.fillText("z", (f.at.x + 22 + 12 * t) * u, (f.at.y - 26 - 26 * t) * u);
      }
    }
    ctx.globalAlpha = 1;
  }
}
