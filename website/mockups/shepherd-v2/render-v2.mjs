import fs from "node:fs/promises";
import path from "node:path";
import { fileURLToPath } from "node:url";
import { chromium } from "@playwright/test";

const root = path.resolve(path.dirname(fileURLToPath(import.meta.url)), "../../..");
const outputDir = path.join(root, "website", "mockups", "shepherd-v2");
const themeRoot = path.join(root, "website", "mockups", "shepherd-v3");

const colors = {
  navy: "#061220",
  teal: "#0B2B32",
  paper: "#F7F8F5",
  ice: "#EAF2F7",
  cobalt: "#2167F3",
  azure: "#70B8FF",
  amber: "#D69A45",
  hairline: "#C6D5DF",
  ink: "#10212C",
  muted: "#647986",
};

const asset = async (name) =>
  "data:image/png;base64," +
  (await fs.readFile(path.join(outputDir, name))).toString("base64");

const [heroOutcome, heroNight, heroSeal, materialStudy] = await Promise.all([
  asset("hero-direction-01-art.png"),
  asset("hero-direction-02-art.png"),
  asset("hero-direction-03-art.png"),
  asset("section-material-art.png"),
]);

const css = [
  ":root {",
  "  --navy: " + colors.navy + "; --teal: " + colors.teal + "; --paper: " + colors.paper + "; --ice: " + colors.ice + ";",
  "  --cobalt: " + colors.cobalt + "; --azure: " + colors.azure + "; --amber: " + colors.amber + "; --hairline: " + colors.hairline + ";",
  "  --ink: " + colors.ink + "; --muted: " + colors.muted + "; --serif: Georgia, 'Times New Roman', serif;",
  "  --sans: ui-sans-serif, system-ui, -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;",
  "  --mono: 'SFMono-Regular', Consolas, 'Liberation Mono', monospace;",
  "}",
  "* { box-sizing: border-box; }",
  "html, body { margin: 0; padding: 0; background: var(--paper); color: var(--ink); }",
  "body { font-family: var(--sans); font-size: 16px; line-height: 1.45; -webkit-font-smoothing: antialiased; }",
  "main { overflow: hidden; }",
  "h1, h2, h3, p { margin: 0; }",
  "h1, h2, h3 { font-family: var(--serif); font-weight: 400; letter-spacing: -0.06em; }",
  ".shell { width: min(1184px, calc(100% - 112px)); margin: 0 auto; }",
  ".announcement { min-height: 48px; display: flex; align-items: center; justify-content: center; gap: 18px; padding: 8px 20px; background: var(--ice); color: var(--ink); font-size: 12px; }",
  ".announcement strong { font-weight: 650; }",
  ".announcement span { font-family: var(--mono); font-size: 10px; letter-spacing: .04em; }",
  ".announcement .link { border-radius: 999px; padding: 8px 14px; background: var(--navy); color: var(--paper); font-size: 11px; }",
  ".section { position: relative; min-height: 920px; padding: 90px 0; display: flex; align-items: center; }",
  ".section.short { min-height: 700px; }",
  ".section.paper { background: var(--paper); }",
  ".section.ice { background: var(--ice); }",
  ".section.dark { background: var(--navy); color: var(--paper); }",
  ".section.teal { background: var(--teal); color: var(--paper); }",
  ".nav { display: flex; align-items: center; justify-content: space-between; gap: 32px; height: 78px; }",
  ".hero .nav { position: absolute; top: 48px; left: 50%; transform: translateX(-50%); z-index: 5; }",
  ".wordmark { display: flex; align-items: center; gap: 10px; font-size: 18px; font-weight: 700; letter-spacing: -.05em; }",
  ".mark { position: relative; width: 22px; height: 22px; border: 1px solid currentColor; }",
  ".mark::before, .mark::after { content: ''; position: absolute; background: currentColor; }",
  ".mark::before { width: 1px; top: 3px; bottom: 3px; left: 10px; }",
  ".mark::after { height: 1px; left: 3px; right: 3px; top: 10px; }",
  ".nav-links { display: flex; align-items: center; gap: 28px; margin-left: auto; color: inherit; font-size: 12px; }",
  ".nav-links span { opacity: .72; }",
  ".button { min-height: 44px; display: inline-flex; align-items: center; justify-content: center; padding: 0 21px; border: 1px solid transparent; border-radius: 999px; font-size: 12px; font-weight: 700; white-space: nowrap; }",
  ".button.primary { background: var(--cobalt); color: white; }",
  ".button.light { background: var(--paper); color: var(--navy); }",
  ".button.outline { border-color: currentColor; color: inherit; background: transparent; }",
  ".eyebrow, .mono { font-family: var(--mono); font-size: 10px; line-height: 1.2; letter-spacing: .11em; text-transform: uppercase; }",
  ".eyebrow { color: var(--cobalt); }",
  ".dark .eyebrow, .teal .eyebrow { color: var(--azure); }",
  ".boundary { color: var(--azure); font-family: var(--mono); font-size: 10px; letter-spacing: .04em; text-transform: uppercase; }",
  ".hero { min-height: 1050px; padding: 0; display: block; position: relative; background: var(--navy); color: var(--paper); overflow: hidden; }",
  ".hero-copy { position: relative; z-index: 3; max-width: 960px; margin: 0 auto; padding: 170px 20px 0; text-align: center; }",
  ".hero .announcement { position: relative; z-index: 6; }",
  ".hero-copy h1 { max-width: 1100px; margin: 20px auto 22px; font-size: clamp(60px, 5.6vw, 84px); line-height: .92; }",
  ".hero-copy p { max-width: 620px; margin: 0 auto; color: #C6D5DF; font-size: 16px; line-height: 1.55; }",
  ".hero-actions { display: flex; justify-content: center; gap: 12px; margin: 28px 0 15px; }",
  ".hero-scene { position: absolute; z-index: 1; left: 48px; right: 48px; top: 410px; bottom: 0; overflow: hidden; border: 1px solid rgba(198,213,223,.22); }",
  ".hero-scene img { width: 100%; height: 100%; display: block; object-fit: cover; object-position: center; filter: saturate(.82) contrast(1.06); }",
  ".hero-scene::before { content: ''; position: absolute; z-index: 2; inset: 0; background: linear-gradient(180deg, rgba(6,18,32,.95) 0%, rgba(6,18,32,.28) 28%, rgba(6,18,32,.08) 65%, rgba(6,18,32,.66) 100%); }",
  ".hero-scene::after { content: ''; position: absolute; z-index: 2; left: 8%; right: 10%; bottom: 17%; height: 1px; background: var(--azure); opacity: .84; transform: rotate(-5deg); transform-origin: left; }",
  ".hero-route { position: absolute; z-index: 4; left: 8%; right: 10%; bottom: 17%; display: flex; justify-content: space-between; align-items: center; color: var(--paper); transform: translateY(-10px); }",
  ".hero-route span { display: flex; align-items: center; gap: 8px; font-family: var(--mono); font-size: 9px; letter-spacing: .08em; text-transform: uppercase; }",
  ".hero-route i { width: 8px; height: 8px; display: inline-block; border-radius: 50%; background: var(--cobalt); box-shadow: 0 0 0 4px rgba(112,184,255,.18); }",
  ".hero-caption { position: absolute; z-index: 4; left: 28px; bottom: 24px; color: rgba(247,248,245,.76); font-family: var(--mono); font-size: 9px; letter-spacing: .07em; text-transform: uppercase; }",
  ".hero-direction .hero-copy { padding-top: 120px; }",
  ".hero-direction .hero-scene { top: 280px; }",
  ".hero-direction.split .hero-copy { max-width: 1184px; padding-top: 170px; text-align: left; display: grid; grid-template-columns: .9fr 1.1fr; gap: 48px; align-items: end; }",
  ".hero-direction.split .hero-copy h1 { margin-left: 0; }",
  ".hero-direction.split .hero-copy p { margin-left: 0; }",
  ".hero-direction.split .hero-actions { justify-content: flex-start; }",
  ".hero-direction.split .hero-scene { top: 48px; left: 50%; right: 0; bottom: 0; border: 0; }",
  ".hero-direction.split .hero-scene::before { background: linear-gradient(90deg, rgba(6,18,32,.98) 0%, rgba(6,18,32,.56) 42%, rgba(6,18,32,.08) 100%); }",
  ".hero-direction.split .hero-route, .hero-direction.split .hero-caption { display: none; }",
  ".proof { min-height: 300px; display: flex; align-items: center; border-bottom: 1px solid var(--hairline); }",
  ".proof-grid { display: grid; grid-template-columns: 1.15fr repeat(3, 1fr); gap: 34px; align-items: start; }",
  ".proof-intro { max-width: 360px; font-family: var(--serif); font-size: 28px; line-height: 1.02; }",
  ".proof-item { padding-left: 18px; border-left: 1px solid var(--cobalt); }",
  ".proof-item strong { display: block; font-family: var(--mono); font-size: 10px; letter-spacing: .08em; text-transform: uppercase; color: var(--cobalt); }",
  ".proof-item span { display: block; margin-top: 13px; color: var(--muted); font-size: 13px; line-height: 1.4; }",
  ".section-head { display: grid; grid-template-columns: 1fr 1fr; gap: 76px; align-items: end; margin-bottom: 54px; }",
  ".section-head h2 { max-width: 590px; margin-top: 16px; font-size: clamp(52px, 5.2vw, 80px); line-height: .91; }",
  ".section-head p { max-width: 500px; color: var(--muted); font-size: 16px; line-height: 1.55; }",
  ".dark .section-head p, .teal .section-head p { color: #C6D5DF; }",
  ".approach-grid { display: grid; grid-template-columns: repeat(3, 1fr); gap: 0; border-top: 1px solid var(--hairline); }",
  ".approach-item { min-height: 430px; padding: 22px 28px 26px 0; border-right: 1px solid var(--hairline); }",
  ".approach-item + .approach-item { padding-left: 28px; }",
  ".approach-item:last-child { border-right: 0; }",
  ".approach-item h3 { margin: 34px 0 15px; font-size: 34px; line-height: .95; }",
  ".approach-item p { max-width: 260px; color: var(--muted); font-size: 13px; line-height: 1.5; }",
  ".approach-art { height: 132px; margin-top: 26px; overflow: hidden; border: 1px solid var(--hairline); background: white; }",
  ".approach-art img { width: 100%; height: 100%; object-fit: cover; filter: saturate(.68) contrast(.98); }",
  ".mini-record { height: 100%; padding: 16px; background: #FDFDFB; font-family: var(--mono); font-size: 9px; }",
  ".mini-record div { display: flex; justify-content: space-between; padding: 9px 0; border-bottom: 1px solid var(--hairline); }",
  ".mini-record b { color: var(--cobalt); font-weight: 500; }",
  ".event-strip { height: 100%; padding: 16px 18px; background: var(--navy); color: var(--paper); font-family: var(--mono); font-size: 8px; }",
  ".event-strip div { position: relative; padding: 0 0 15px 16px; border-left: 1px solid var(--azure); }",
  ".event-strip div::before { content: ''; position: absolute; left: -4px; top: 1px; width: 7px; height: 7px; border-radius: 50%; background: var(--cobalt); }",
  ".term-strip { height: 100%; padding: 16px; background: rgba(214,154,69,.10); border-left: 3px solid var(--amber); }",
  ".term-strip strong { display: block; font-family: var(--serif); font-size: 27px; font-weight: 400; line-height: .95; }",
  ".term-strip span { display: block; margin-top: 14px; color: var(--muted); font-family: var(--mono); font-size: 8px; line-height: 1.35; text-transform: uppercase; }",
  ".route-section { min-height: 840px; }",
  ".route-section .section-head h2 { max-width: 520px; }",
  ".route-track { position: relative; display: grid; grid-template-columns: repeat(4, 1fr); border-top: 1px solid rgba(198,213,223,.34); border-bottom: 1px solid rgba(198,213,223,.34); }",
  ".route-track::before { content: ''; position: absolute; top: 65px; left: 6%; right: 6%; height: 1px; background: var(--azure); }",
  ".route-step { position: relative; min-height: 390px; padding: 34px 24px 28px 0; border-right: 1px solid rgba(198,213,223,.25); }",
  ".route-step + .route-step { padding-left: 24px; }",
  ".route-step:last-child { border-right: 0; }",
  ".route-step .step-meta { display: flex; align-items: center; gap: 11px; color: var(--azure); font-family: var(--mono); font-size: 10px; }",
  ".route-step .dot { width: 10px; height: 10px; border-radius: 50%; background: var(--cobalt); box-shadow: 0 0 0 5px rgba(112,184,255,.16); }",
  ".route-step h3 { margin: 92px 0 14px; font-size: 34px; line-height: .94; }",
  ".route-step p { max-width: 210px; color: #C6D5DF; font-size: 13px; line-height: 1.45; }",
  ".route-step small { position: absolute; left: 0; bottom: 28px; color: rgba(198,213,223,.66); font-family: var(--mono); font-size: 9px; letter-spacing: .08em; text-transform: uppercase; }",
  ".route-step + .route-step small { left: 24px; }",
  ".records-layout { display: grid; grid-template-columns: .85fr 1.15fr; gap: 52px; align-items: center; }",
  ".records-copy h2 { max-width: 500px; margin-top: 16px; font-size: clamp(54px, 5.6vw, 88px); line-height: .88; }",
  ".records-copy p { max-width: 430px; margin-top: 22px; color: var(--muted); font-size: 16px; line-height: 1.55; }",
  ".record-stage { position: relative; min-height: 560px; overflow: hidden; border: 1px solid rgba(16,33,44,.18); background: var(--navy); }",
  ".record-stage > img { width: 100%; height: 100%; position: absolute; inset: 0; object-fit: cover; opacity: .44; filter: saturate(.68) contrast(1.1); }",
  ".record-stage::after { content: ''; position: absolute; inset: 0; background: linear-gradient(135deg, rgba(6,18,32,.92) 0%, rgba(6,18,32,.32) 55%, rgba(6,18,32,.78) 100%); }",
  ".record-panel { position: absolute; z-index: 2; width: 56%; min-height: 152px; padding: 20px; border: 1px solid rgba(198,213,223,.45); background: rgba(247,248,245,.96); color: var(--ink); }",
  ".record-panel:nth-of-type(1) { top: 10%; left: 8%; transform: rotate(-3deg); }",
  ".record-panel:nth-of-type(2) { top: 33%; right: 7%; transform: rotate(2deg); background: rgba(11,43,50,.94); color: var(--paper); }",
  ".record-panel:nth-of-type(3) { bottom: 10%; left: 14%; transform: rotate(-1deg); }",
  ".record-panel h3 { margin-top: 20px; font-size: 27px; line-height: .95; }",
  ".record-panel p { margin-top: 9px; color: var(--muted); font-family: var(--sans); font-size: 11px; line-height: 1.35; }",
  ".record-panel.dark-panel p { color: #C6D5DF; }",
  ".synthetic { color: var(--cobalt); font-family: var(--mono); font-size: 8px; letter-spacing: .08em; line-height: 1.3; text-transform: uppercase; }",
  ".dark-panel .synthetic { color: var(--azure); }",
  ".comparison { min-height: 820px; }",
  ".comparison-grid { display: grid; grid-template-columns: 1fr 1fr; border-top: 1px solid var(--hairline); }",
  ".comparison-column { padding: 24px 30px 0 0; }",
  ".comparison-column + .comparison-column { padding-left: 30px; border-left: 1px solid var(--hairline); }",
  ".comparison-column h3 { margin-bottom: 22px; font-size: 33px; }",
  ".comparison-row { display: grid; grid-template-columns: 1fr 1.25fr; gap: 18px; min-height: 76px; padding: 17px 0; border-bottom: 1px solid var(--hairline); }",
  ".comparison-row strong { font-family: var(--mono); color: var(--cobalt); font-size: 9px; letter-spacing: .08em; text-transform: uppercase; }",
  ".comparison-row span { color: var(--muted); font-size: 13px; line-height: 1.35; }",
  ".method { min-height: 920px; }",
  ".method-grid { display: grid; grid-template-columns: .92fr 1.08fr; gap: 56px; align-items: start; }",
  ".method-copy h2 { max-width: 540px; margin-top: 16px; font-size: clamp(55px, 5.6vw, 84px); line-height: .88; }",
  ".method-copy p { max-width: 420px; margin-top: 22px; color: var(--muted); font-size: 16px; line-height: 1.55; }",
  ".method-list { border-top: 1px solid var(--hairline); }",
  ".method-row { display: grid; grid-template-columns: 180px 1fr; gap: 24px; min-height: 94px; align-items: center; border-bottom: 1px solid var(--hairline); }",
  ".method-row strong { color: var(--cobalt); font-family: var(--mono); font-size: 9px; letter-spacing: .08em; text-transform: uppercase; }",
  ".method-row span { color: var(--muted); font-size: 14px; }",
  ".faq { margin-top: 70px; }",
  ".faq-title { margin-bottom: 20px; font-family: var(--serif); font-size: 32px; }",
  ".faq-row { display: grid; grid-template-columns: 260px 1fr; gap: 26px; padding: 17px 0; border-top: 1px solid var(--hairline); }",
  ".faq-row:last-child { border-bottom: 1px solid var(--hairline); }",
  ".faq-row strong { font-family: var(--serif); font-size: 22px; font-weight: 400; }",
  ".faq-row span { color: var(--muted); font-size: 13px; line-height: 1.4; }",
  ".measure { min-height: 430px; background: var(--ice); display: flex; align-items: center; text-align: center; }",
  ".measure h2 { max-width: 870px; margin: 18px auto 0; font-size: clamp(58px, 7.5vw, 112px); line-height: .86; }",
  ".measure p { max-width: 480px; margin: 24px auto 0; color: var(--muted); font-size: 15px; }",
  ".closing { min-height: 760px; text-align: center; }",
  ".closing h2 { max-width: 860px; margin: 18px auto 25px; font-size: clamp(64px, 7.8vw, 118px); line-height: .86; }",
  ".closing p { max-width: 480px; margin: 0 auto 27px; color: #C6D5DF; font-size: 16px; }",
  ".form { min-height: 980px; }",
  ".form-layout { display: grid; grid-template-columns: .86fr 1.14fr; gap: 78px; align-items: start; }",
  ".form-copy h2 { max-width: 480px; margin: 18px 0 22px; font-size: clamp(60px, 6.2vw, 94px); line-height: .86; }",
  ".form-copy p { max-width: 410px; color: #C6D5DF; font-size: 16px; line-height: 1.5; }",
  ".form-card { padding: 32px; background: var(--paper); color: var(--ink); }",
  ".form-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 15px; }",
  ".field { display: grid; gap: 7px; }",
  ".field.full { grid-column: 1 / -1; }",
  ".field label { color: var(--muted); font-family: var(--mono); font-size: 9px; letter-spacing: .08em; text-transform: uppercase; }",
  ".field-box { min-height: 47px; padding: 13px; border: 1px solid var(--hairline); background: white; color: #80929B; font-size: 13px; }",
  ".field-box.large { min-height: 112px; }",
  ".consent { display: flex; gap: 10px; align-items: flex-start; margin: 22px 0; color: var(--muted); font-size: 11px; }",
  ".check { width: 15px; height: 15px; flex: none; border: 1px solid var(--cobalt); }",
  ".form-foot { display: flex; justify-content: space-between; align-items: center; gap: 18px; }",
  ".form-foot .boundary { color: var(--cobalt); }",
  ".privacy { margin-top: 20px; color: var(--muted); font-family: var(--mono); font-size: 9px; line-height: 1.5; }",
  ".states { display: grid; gap: 9px; margin-top: 25px; }",
  ".state { padding: 11px 14px; border-left: 3px solid var(--cobalt); background: var(--ice); }",
  ".state.warn { border-left-color: var(--amber); }",
  ".state strong { display: block; color: var(--cobalt); font-family: var(--mono); font-size: 9px; letter-spacing: .08em; }",
  ".state.warn strong { color: #946322; }",
  ".state span { display: block; margin-top: 4px; color: var(--muted); font-size: 11px; }",
  ".doc { min-height: 100vh; padding: 60px; }",
  ".doc.paper { background: var(--paper); } .doc.dark { background: var(--navy); color: var(--paper); }",
  ".doc-head { display: flex; justify-content: space-between; gap: 40px; align-items: end; margin-bottom: 46px; }",
  ".doc-head h1 { max-width: 780px; margin-top: 16px; font-size: 78px; line-height: .86; }",
  ".doc-head p { max-width: 330px; color: var(--muted); font-size: 13px; }",
  ".dark .doc-head p { color: #C6D5DF; }",
  "table { width: 100%; border-collapse: collapse; font-size: 12px; }",
  "th { padding: 11px 12px; border-top: 1px solid currentColor; border-bottom: 1px solid var(--hairline); color: var(--cobalt); font-family: var(--mono); font-size: 9px; letter-spacing: .08em; text-align: left; text-transform: uppercase; }",
  "td { padding: 14px 12px; border-bottom: 1px solid var(--hairline); vertical-align: top; line-height: 1.4; }",
  "td:first-child { width: 17%; font-weight: 700; } td:nth-child(2) { width: 14%; color: var(--cobalt); font-family: var(--mono); font-size: 9px; text-transform: uppercase; }",
  ".thesis-flow { display: grid; grid-template-columns: repeat(5, 1fr); border-top: 1px solid rgba(198,213,223,.34); border-bottom: 1px solid rgba(198,213,223,.34); }",
  ".flow-cell { min-height: 220px; padding: 24px 18px 20px 0; border-right: 1px solid rgba(198,213,223,.25); }",
  ".flow-cell + .flow-cell { padding-left: 18px; } .flow-cell:last-child { border: 0; }",
  ".flow-cell strong { color: var(--azure); font-family: var(--mono); font-size: 9px; letter-spacing: .08em; }",
  ".flow-cell h2 { margin: 58px 0 12px; font-size: 31px; } .flow-cell p { color: #C6D5DF; font-size: 12px; }",
  ".tokens { display: grid; grid-template-columns: repeat(4, 1fr); gap: 12px; margin-top: 26px; }",
  ".token { min-height: 100px; padding: 14px; border: 1px solid rgba(198,213,223,.26); }",
  ".token i { display: block; width: 30px; height: 30px; margin-bottom: 18px; background: var(--paper); }",
  ".token:nth-child(2) i { background: var(--cobalt); } .token:nth-child(3) i { background: var(--azure); } .token:nth-child(4) i { background: var(--amber); }",
  ".token span { color: #C6D5DF; font-family: var(--mono); font-size: 9px; }",
  "@media (max-width: 720px) {",
  "  .shell { width: calc(100% - 40px); }",
  "  .announcement { min-height: 54px; justify-content: space-between; gap: 10px; padding: 7px 14px; font-size: 10px; }",
  "  .announcement span { max-width: 170px; font-size: 8px; line-height: 1.25; } .announcement .link { padding: 7px 10px; font-size: 9px; }",
  "  .nav { height: 62px; } .hero .nav { top: 54px; } .nav-links { display: none; } .nav .button { min-height: 34px; padding: 0 12px; font-size: 9px; }",
  "  .hero { min-height: 880px; } .hero-copy { padding-top: 142px; } .hero-copy h1 { max-width: 360px; margin-top: 17px; font-size: 50px; line-height: .91; } .hero-copy p { max-width: 350px; font-size: 13px; }",
  "  .hero-actions { flex-wrap: wrap; gap: 8px; margin-top: 20px; } .hero-actions .button { min-height: 38px; padding: 0 14px; font-size: 10px; }",
  "  .hero-scene { left: 20px; right: 20px; top: 495px; } .hero-route { left: 7%; right: 7%; bottom: 18%; display: grid; grid-template-columns: repeat(2, 1fr); gap: 12px; transform: translateY(-9px); } .hero-route span { font-size: 7px; } .hero-caption { left: 14px; bottom: 14px; font-size: 7px; }",
  "  .hero-direction .hero-copy { padding-top: 122px; } .hero-direction .hero-scene { top: 300px; } .hero-direction.split .hero-copy { display: block; padding-top: 145px; text-align: left; } .hero-direction.split .hero-copy h1 { max-width: 360px; } .hero-direction.split .hero-actions { justify-content: flex-start; } .hero-direction.split .hero-scene { top: 0; left: 36%; }",
  "  .proof { min-height: 430px; } .proof-grid { grid-template-columns: 1fr 1fr; gap: 26px 18px; } .proof-intro { grid-column: 1 / -1; font-size: 25px; } .proof-item { padding-left: 12px; } .proof-item span { font-size: 11px; }",
  "  .section { min-height: 820px; padding: 72px 0 54px; align-items: flex-start; } .section.short { min-height: 660px; } .section-head { grid-template-columns: 1fr; gap: 16px; margin-bottom: 30px; } .section-head h2 { margin-top: 12px; font-size: 50px; } .section-head p { font-size: 13px; }",
  "  .approach-grid { grid-template-columns: 1fr; } .approach-item { min-height: 245px; padding: 18px 0 20px; border-right: 0; border-bottom: 1px solid var(--hairline); } .approach-item + .approach-item { padding-left: 0; } .approach-item:last-child { border-bottom: 0; } .approach-item h3 { margin: 18px 0 9px; font-size: 28px; } .approach-item p { max-width: 330px; font-size: 12px; } .approach-art { height: 84px; margin-top: 15px; }",
  "  .route-section { min-height: 790px; } .route-track { grid-template-columns: 1fr 1fr; } .route-track::before { top: 52px; } .route-step { min-height: 245px; padding: 24px 12px 18px 0; } .route-step + .route-step { padding-left: 12px; } .route-step h3 { margin: 62px 0 9px; font-size: 27px; } .route-step p { font-size: 11px; } .route-step small, .route-step + .route-step small { display: none; }",
  "  .records-layout, .method-grid, .form-layout { grid-template-columns: 1fr; gap: 28px; } .records-copy h2, .method-copy h2 { font-size: 52px; } .records-copy p, .method-copy p { margin-top: 14px; font-size: 13px; } .record-stage { min-height: 460px; } .record-panel { width: 72%; min-height: 108px; padding: 14px; } .record-panel h3 { margin-top: 13px; font-size: 22px; } .record-panel p { margin-top: 6px; font-size: 9px; } .synthetic { font-size: 7px; }",
  "  .comparison { min-height: 830px; } .comparison-grid { grid-template-columns: 1fr; } .comparison-column, .comparison-column + .comparison-column { padding: 18px 0 0; border-left: 0; } .comparison-column + .comparison-column { margin-top: 22px; border-top: 1px solid var(--hairline); } .comparison-column h3 { font-size: 28px; } .comparison-row { grid-template-columns: 104px 1fr; gap: 12px; min-height: 60px; padding: 12px 0; } .comparison-row span { font-size: 11px; }",
  "  .method { min-height: 1050px; } .method-row { grid-template-columns: 112px 1fr; min-height: 78px; gap: 12px; } .method-row span { font-size: 11px; } .faq { margin-top: 45px; } .faq-title { font-size: 28px; } .faq-row { grid-template-columns: 1fr; gap: 5px; padding: 12px 0; } .faq-row strong { font-size: 19px; } .faq-row span { font-size: 11px; }",
  "  .measure { min-height: 470px; } .measure h2 { font-size: 58px; } .measure p { font-size: 13px; } .closing { min-height: 680px; } .closing h2 { font-size: 62px; } .closing p { font-size: 13px; }",
  "  .form { min-height: 980px; } .form-layout { gap: 22px; } .form-copy h2 { font-size: 54px; } .form-copy p { font-size: 13px; } .form-card { padding: 14px; } .form-grid { grid-template-columns: 1fr; gap: 8px; } .field.full { grid-column: auto; } .field { gap: 4px; } .field label { font-size: 7px; } .field-box { min-height: 34px; padding: 8px; font-size: 10px; } .field-box.large { min-height: 70px; } .consent { margin: 12px 0; font-size: 9px; } .form-foot { align-items: stretch; flex-direction: column; gap: 10px; } .form-foot .button { width: 100%; } .privacy { margin-top: 10px; font-size: 7px; } .states { gap: 6px; margin-top: 12px; } .state { padding: 7px 9px; } .state strong { font-size: 7px; } .state span { font-size: 9px; }",
  "  .doc { padding: 32px 20px; } .doc-head { display: block; margin-bottom: 28px; } .doc-head h1 { font-size: 54px; } .doc-head p { margin-top: 15px; font-size: 11px; } table { font-size: 9px; } th { padding: 7px 5px; font-size: 7px; } td { padding: 8px 5px; } .thesis-flow { grid-template-columns: 1fr 1fr; } .flow-cell { min-height: 170px; padding: 18px 10px 12px 0; } .flow-cell + .flow-cell { padding-left: 10px; } .flow-cell h2 { margin: 40px 0 8px; font-size: 24px; } .flow-cell p { font-size: 10px; } .tokens { grid-template-columns: 1fr 1fr; }",
  "}",
].join("\n");

const themeCss = [
  "body.theme-blue { background: #061220; color: #F7F8F5; --muted: #C6D5DF; --hairline: rgba(198,213,223,.28); }",
  ".theme-blue .announcement { background: #0B2B32; color: #F7F8F5; }",
  ".theme-blue .section.paper, .theme-blue .proof.paper { background: #061220; color: #F7F8F5; }",
  ".theme-blue .section.ice, .theme-blue .measure { background: #0B2B32; color: #F7F8F5; }",
  ".theme-blue .section.teal, .theme-blue .section.dark { background: #0B2B32; color: #F7F8F5; }",
  ".theme-blue .closing, .theme-blue .form { background: #061220; color: #F7F8F5; }",
  ".theme-blue .approach-art { border-color: rgba(198,213,223,.34); }",
  ".theme-blue .mini-record { color: #10212C; }",
  ".theme-blue .term-strip { color: #10212C; }",
  ".theme-blue .term-strip span, .theme-blue .record-panel p, .theme-blue .form-card .privacy, .theme-blue .form-card .state span { color: #647986; }",
  ".theme-blue .comparison-grid, .theme-blue .method-list, .theme-blue .faq-row, .theme-blue .comparison-row { border-color: rgba(198,213,223,.28); }",
  ".theme-blue .closing p, .theme-blue .form-copy p { color: #C6D5DF; }",
  ".theme-white .hero { background: #FFFFFF; color: #061220; }",
  ".theme-white .announcement { background: #EAF2F7; color: #061220; }",
  ".theme-white .hero-copy p { color: #647986; }",
  ".theme-white .hero-scene::before { background: linear-gradient(180deg, rgba(255,255,255,.98) 0%, rgba(255,255,255,.72) 29%, rgba(255,255,255,.08) 58%, rgba(6,18,32,.72) 100%); }",
  ".theme-white .hero .boundary, .theme-white .dark .boundary, .theme-white .teal .boundary { color: #2167F3; }",
  ".theme-white .button.light { background: #061220; color: #F7F8F5; }",
  ".theme-white .button.outline { border-color: #061220; color: #061220; }",
  ".theme-white .section.paper, .theme-white .proof.paper { background: #FFFFFF; color: #061220; }",
  ".theme-white .section.ice, .theme-white .measure { background: #EAF2F7; color: #061220; }",
  ".theme-white .section.teal, .theme-white .section.dark { background: #F7F8F5; color: #061220; }",
  ".theme-white .closing, .theme-white .form { background: #FFFFFF; color: #061220; }",
  ".theme-white .dark .eyebrow, .theme-white .teal .eyebrow { color: #2167F3; }",
  ".theme-white .dark .section-head p, .theme-white .teal .section-head p, .theme-white .route-step p, .theme-white .closing p, .theme-white .form-copy p { color: #647986; }",
  ".theme-white .route-track { border-color: #C6D5DF; }",
  ".theme-white .route-track::before { background: #2167F3; }",
  ".theme-white .route-step { border-color: #C6D5DF; }",
  ".theme-white .route-step small { color: #647986; }",
  ".theme-white .form-card { background: #EAF2F7; }",
].join("\n");

function announcement() {
  return "<div class='announcement'><strong>D&D recovery for importer finance teams</strong><span>Case-specific review · No guaranteed recovery</span><span class='link'>See the method →</span></div>";
}

function nav() {
  return "<div class='nav shell'><div class='wordmark'><span class='mark'></span><span>SheperD</span></div><div class='nav-links'><span>Approach</span><span>Evidence</span><span>Pilot</span><span>FAQ</span></div><span class='button primary'>Request a pilot</span></div>";
}

function marker(text) {
  return "<div class='synthetic'>" + text + "</div>";
}

function routeLabels() {
  return "<div class='hero-route'><span><i></i>Invoice</span><span><i></i>Event</span><span><i></i>Term</span><span><i></i>Human review</span></div>";
}

function hero(variant) {
  const options = {
    outcome: {
      image: heroOutcome,
      title: "Recover the D&amp;D money hiding in your invoices.",
      copy: "SheperD reviews detention and demurrage invoices alongside shipment events, operational records, and governing terms to identify case-specific recovery opportunities and support the path toward a carrier credit or refund.",
      className: "",
    },
    cinematic: {
      image: heroNight,
      title: "The invoice is where the review begins.",
      copy: "A charge becomes clearer when the container, the event, and the governing term stay in the same frame.",
      className: "hero-direction",
    },
    record: {
      image: heroSeal,
      title: "Follow the charge to the next question.",
      copy: "Connect the billed line to the records around it before a human decides what the case can support.",
      className: "hero-direction split",
    },
  };
  const item = options[variant];
  return "<section class='hero " + item.className + "'>" +
    announcement() +
    nav() +
    "<div class='hero-copy'>" +
      "<div class='eyebrow'>D&amp;D recovery for importer finance teams</div>" +
      "<h1>" + item.title + "</h1>" +
      "<p>" + item.copy + "</p>" +
      "<div class='hero-actions'><span class='button primary'>Request a pilot</span><span class='button outline'>See the recovery path</span></div>" +
      "<div class='boundary'>Case-specific review · No guaranteed recovery</div>" +
    "</div>" +
    "<div class='hero-scene'><img src='" + item.image + "' alt=''/>" + routeLabels() + "<div class='hero-caption'>Original synthetic visual · Container record in context</div></div>" +
  "</section>";
}

function proof() {
  return "<section class='proof paper'><div class='shell'><div class='proof-grid'>" +
    "<div class='proof-intro'>The invoice starts the question. The record carries it.</div>" +
    "<div class='proof-item'><strong>Billing record</strong><span>What was billed, when, and against which container reference.</span></div>" +
    "<div class='proof-item'><strong>Operational event</strong><span>What happened around availability, pickup, return, and notice.</span></div>" +
    "<div class='proof-item'><strong>Governing term</strong><span>What language and dates belong beside the charge.</span></div>" +
  "</div></div></section>";
}

function problem() {
  return "<section class='section paper'><div class='shell'>" +
    "<div class='section-head'><div><div class='eyebrow'>Our approach</div><h2>The invoice is only the first record.</h2></div><p>A billed amount is a starting point. The charge needs to sit beside the shipment events, operational records, and governing terms that shape a case-specific review.</p></div>" +
    "<div class='approach-grid'>" +
      "<div class='approach-item'><div class='eyebrow'>01 · Billed</div><h3>Billing record</h3><p>Invoice line, charge date, container reference, billing party, and payment state.</p><div class='approach-art'><div class='mini-record'><div><span>Charge date</span><b>14 MAY</b></div><div><span>Container</span><b>MSCU ····</b></div><div><span>Line state</span><b>TRACE</b></div></div></div></div>" +
      "<div class='approach-item'><div class='eyebrow'>02 · Recorded</div><h3>Operational event</h3><p>Availability, pickup, return, terminal timing, appointments, holds, closures, and notices.</p><div class='approach-art'><div class='event-strip'><div>08 MAY · availability record</div><div>10 MAY · appointment event</div><div>14 MAY · return or notice</div></div></div></div>" +
      "<div class='approach-item'><div class='eyebrow'>03 · Governed</div><h3>Governing term</h3><p>Free-time terms, tariff or contract language, route, effective dates, and source version.</p><div class='approach-art'><div class='term-strip'><strong>Effective terms</strong><span>Source date and applicability stay visible. Missing evidence stays marked.</span></div></div></div>" +
    "</div>" +
  "</div></section>";
}

function recoveryPath() {
  return "<section class='section teal route-section'><div class='shell'>" +
    "<div class='section-head'><div><div class='eyebrow'>Exclusive review path</div><h2>From billed to reviewed.</h2></div><p>The route stays visible while the conclusion stays conditional. Each record changes the next question, and human review remains the boundary.</p></div>" +
    "<div class='route-track'>" +
      "<div class='route-step'><div class='step-meta'><span class='dot'></span>01</div><h3>Invoice<br>&amp; data</h3><p>Anchor the charge, period, container reference, and source record.</p><small>Billed</small></div>" +
      "<div class='route-step'><div class='step-meta'><span class='dot'></span>02</div><h3>SheperD<br>review</h3><p>Join the billed line to events, records, and governing terms.</p><small>Traced</small></div>" +
      "<div class='route-step'><div class='step-meta'><span class='dot'></span>03</div><h3>Dispute<br>support</h3><p>Prepare the case-specific record and the questions that remain.</p><small>Reviewed</small></div>" +
      "<div class='route-step'><div class='step-meta'><span class='dot'></span>04</div><h3>Potential<br>recovery</h3><p>Stop at human review before any carrier credit or refund outcome.</p><small>Conditional</small></div>" +
    "</div>" +
  "</div></section>";
}

function evidence() {
  return "<section class='section ice'><div class='shell'><div class='records-layout'>" +
    "<div class='records-copy'><div class='eyebrow'>Powerful evidence</div><h2>One charge. Three records.</h2><p>The invoice is the anchor. The review gets clearer when the billing record, operational timeline, and governing terms travel together.</p><div style='margin-top:28px'><span class='button primary'>See the recovery path</span></div></div>" +
    "<div class='record-stage'><img src='" + materialStudy + "' alt=''/>" +
      "<div class='record-panel'><div>" + marker("ILLUSTRATIVE ARTIFACT · SYNTHETIC RECORD · NOT CUSTOMER DATA") + "</div><h3>Billing record</h3><p>What was billed, for which dates, by whom, and against which line item.</p></div>" +
      "<div class='record-panel dark-panel'><div>" + marker("OPERATIONAL EVENT · SYNTHETIC RECORD") + "</div><h3>Operational timeline</h3><p>What happened at the terminal, in the appointment trail, and around the notices.</p></div>" +
      "<div class='record-panel'><div>" + marker("GOVERNING TERM · SOURCE-LINKED REVIEW") + "</div><h3>Effective terms</h3><p>Which language, route, and dates belong beside the charge.</p></div>" +
    "</div>" +
  "</div></div></section>";
}

function pilotScope() {
  return "<section class='section paper'><div class='shell'><div class='method-grid'>" +
    "<div class='method-copy'><div class='eyebrow'>Pilot scope</div><h2>Start with a focused review.</h2><p>Bring the invoice and the records around the charge. SheperD reviews the evidence together, marks what is missing, and supports the path toward a carrier credit or refund, case by case.</p><div style='margin-top:27px'><span class='button primary'>Request a pilot</span></div><div class='boundary' style='color:var(--cobalt);margin-top:16px'>Case-specific review · No guaranteed recovery</div></div>" +
    "<div class='method-list'><div class='method-row'><strong>Importer provides</strong><span>Invoice, shipment references, governing terms, and the operational record available to the team.</span></div><div class='method-row'><strong>Records reviewed</strong><span>Charge dates, container events, terminal availability, appointments, notices, and communications.</span></div><div class='method-row'><strong>Review produces</strong><span>A case-specific evidence map, marked gaps, and a clearer next question for human review.</span></div><div class='method-row'><strong>What happens next</strong><span>Support for the path toward a carrier credit or refund, subject to the record and applicable terms.</span></div></div>" +
  "</div></div></section>";
}

function trustFaq() {
  return "<section class='section paper method'><div class='shell'>" +
    "<div class='method-grid'><div class='method-copy'><div class='eyebrow'>Trust and methodology</div><h2>Evidence first. Claims second.</h2><p>Trust comes from showing the records, source dates, human review, and limitations, not from badges or invented proof.</p></div>" +
    "<div class='method-list'><div class='method-row'><strong>Official sources</strong><span>Source-linked records stay identifiable.</span></div><div class='method-row'><strong>Published terms</strong><span>Effective dates and applicability stay visible.</span></div><div class='method-row'><strong>Shipment records</strong><span>Events remain tied to the case context.</span></div><div class='method-row'><strong>Human review</strong><span>The outcome boundary is explicit.</span></div><div class='method-row'><strong>Limitations</strong><span>Missing evidence is marked, not filled with certainty.</span></div></div></div>" +
    "<div class='faq'><div class='faq-title'>Questions before a pilot</div><div class='faq-row'><strong>What records are needed?</strong><span>Start with the D&amp;D invoice and the shipment, operational, and governing records available around the charge.</span></div><div class='faq-row'><strong>What if evidence is incomplete?</strong><span>Missing evidence is marked as a gap. It is not treated as a loss, a zero, or a conclusion.</span></div><div class='faq-row'><strong>Credits or cash?</strong><span>Potential outcomes can include a carrier credit or refund. No outcome is guaranteed.</span></div><div class='faq-row'><strong>What does the public form accept?</strong><span>The public form starts a conversation and does not accept invoice uploads.</span></div></div>" +
  "</div></section>";
}

function measure() {
  return "<section class='measure'><div class='shell'><div class='eyebrow'>How we measure success</div><h2>A clear case, a marked gap, a supportable next step.</h2><p>Sometimes the record supports a path toward a carrier credit or refund. Sometimes it shows what cannot yet be established. Both are useful outcomes.</p></div></section>";
}

function closing() {
  return "<section class='section dark closing'><div class='shell'><div class='eyebrow'>Next step</div><h2>Bring the next question to the record.</h2><p>Request a pilot and start with one charge, its surrounding events, and the terms that govern the review.</p><span class='button light'>Request a pilot</span><div class='boundary' style='margin-top:19px'>Case-specific review · No guaranteed recovery</div></div></section>";
}

function pilotForm() {
  return "<section class='section dark form'><div class='shell'><div class='form-layout'><div class='form-copy'><div class='eyebrow'>SheperD / Pilot request</div><h2>Start with the record.</h2><p>Tell us where the charge sits in your process. The first step is a conversation, not an invoice upload.</p><div class='boundary' style='margin-top:20px'>Case-specific review · No guaranteed recovery</div></div><div class='form-card'><div class='form-grid'><div class='field'><label>Name</label><div class='field-box'>Your name</div></div><div class='field'><label>Work email</label><div class='field-box'>name@company.com</div></div><div class='field'><label>Company</label><div class='field-box'>Company name</div></div><div class='field'><label>Role</label><div class='field-box'>CFO / Controller / AP / Logistics</div></div><div class='field full'><label>Annual volume</label><div class='field-box'>Select an annual container volume</div></div><div class='field full'><label>Review context</label><div class='field-box large'>What charge or review question should we understand first?</div></div></div><div class='consent'><span class='check'></span><span>I agree to be contacted about a SheperD pilot request.</span></div><div class='form-foot'><span class='boundary'>No invoice upload</span><span class='button primary'>Request a pilot</span></div><div class='privacy'>This visual shows the intended form experience. Production privacy, retention, access, and secure-transfer details require approval.</div><div class='states'><div class='state'><strong>DISABLED PREVIEW</strong><span>Submit is disabled until required fields are complete.</span></div><div class='state warn'><strong>VALIDATION ERROR</strong><span>Enter a work email and company before continuing.</span></div><div class='state warn'><strong>SUBMISSION FAILURE</strong><span>We could not send your request. Try again.</span></div></div></div></div></div></section>";
}

function landing() {
  return "<main>" + hero("outcome") + proof() + problem() + recoveryPath() + evidence() + pilotScope() + trustFaq() + measure() + closing() + pilotForm() + "</main>";
}

function matrix() {
  const rows = [
    ["Compound Planning", "Reference", "Announcement, compact nav, centered promise, visual proof, capability pillars, comparison, success definition, CTA.", "Copying brand assets, typography, photography, or exact layout.", "Use the page rhythm only. Replace the product dashboard with physical container evidence and a case-specific D&D path."],
    ["1Password", "B2B security", "Dark-to-light clarity and one disciplined interaction color.", "Copying the security metaphor or product language.", "Use navy, paper, ice, and cobalt as the evidence route."],
    ["11x", "B2B service", "Monumental type, cinematic pacing, and editorial confidence.", "Copying its cinematic composition or visual identity.", "Use the pause and scale for a container-film story."],
    ["Linear", "B2B SaaS", "Direct headline, calm navigation, compact CTA hierarchy.", "Defaulting to software UI as proof.", "Use precision for the record sequence, not a dashboard."],
    ["Ramp", "Finance / ops", "Job-oriented information architecture for finance teams.", "Broad product-grid framing.", "Keep one conversion path: charge to reviewed next step."],
    ["Pilot", "Service business", "Expertise framing and case-oriented storytelling.", "Using unsupported outcomes or testimonials.", "Make pilot scope and limitations explicit."],
    ["Flexport", "Logistics", "Physical-world supply-chain context.", "Stock logistics photography or partner proof.", "Use original container film and synthetic artifacts."],
    ["project44", "Supply chain", "Route and exception-management rhythm.", "Dashboard-first intelligence claims.", "Make the route visible and stop it at human review."],
    ["Pentagram", "Editorial service", "Confident whitespace and varied section rhythm.", "Becoming a portfolio instead of a conversion path.", "Use editorial pacing to clarify financial action."],
  ];
  return "<div class='doc paper'><div class='doc-head'><div><div class='eyebrow'>SheperD / Research matrix</div><h1>Reference rules, translated into a new record system.</h1></div><p>Borrow the landing-page logic. Keep the imagery, language, and brand system original to SheperD.</p></div><table><thead><tr><th>Reference</th><th>Category</th><th>Useful pattern</th><th>Imitation risk</th><th>SheperD adaptation</th></tr></thead><tbody>" +
    rows.map((row) => "<tr>" + row.map((cell) => "<td>" + cell + "</td>").join("") + "</tr>").join("") +
    "</tbody></table></div>";
}

function thesis() {
  return "<div class='doc dark'><div class='doc-head'><div><div class='eyebrow'>SheperD / Design thesis</div><h1>Container film outside. Evidence route inside.</h1></div><p>Compound gives us the landing-page spine. SheperD gets its own physical world: containers, records, terms, and human review.</p></div><div class='section-head'><div><div class='eyebrow'>Visual system</div><h2>Make the route visible. Make the boundary impossible to miss.</h2></div><p>Dark navy establishes seriousness. Paper and ice expose the evidence. Electric blue moves the eye from charge to record. Amber marks only the conditional gap.</p></div><div class='thesis-flow'><div class='flow-cell'><strong>01 / BILLED</strong><h2>Invoice</h2><p>Start with one highlighted line item inside a synthetic record.</p></div><div class='flow-cell'><strong>02 / RECORDED</strong><h2>Event</h2><p>Join availability, appointments, notices, and terminal timing.</p></div><div class='flow-cell'><strong>03 / GOVERNED</strong><h2>Term</h2><p>Keep route, effective date, and governing language beside the charge.</p></div><div class='flow-cell'><strong>04 / MARKED</strong><h2>Gap</h2><p>Use amber to show missing evidence rather than inventing certainty.</p></div><div class='flow-cell'><strong>05 / STOP</strong><h2>Human</h2><p>Stop before the potential credit or refund outcome.</p></div></div><div class='tokens'><div class='token'><i></i><span>PAPER / #F7F8F5</span></div><div class='token'><i></i><span>COBALT / #2167F3</span></div><div class='token'><i></i><span>AZURE / #70B8FF</span></div><div class='token'><i></i><span>CONDITIONAL / #D69A45</span></div></div></div>";
}

function documentHtml(body, theme) {
  return "<!doctype html><html><head><meta charset='utf-8'><meta name='viewport' content='width=device-width, initial-scale=1'><style>" + css + themeCss + "</style></head><body class='theme-" + theme + "'>" + body + "</body></html>";
}

async function render() {
  const browser = await chromium.launch({ headless: true });
  const page = await browser.newPage({ deviceScaleFactor: 1 });
  async function renderTheme(theme) {
    const themeDir = path.join(themeRoot, theme);
    await fs.mkdir(themeDir, { recursive: true });
    async function shot(name, body, width, height, fullPage) {
      await page.setViewportSize({ width, height });
      await page.setContent(documentHtml(body, theme), { waitUntil: "load" });
      await page.waitForFunction(() => Array.from(document.images).every((image) => image.complete));
      await page.screenshot({ path: path.join(themeDir, name), fullPage: Boolean(fullPage), animations: "disabled" });
    }

    await shot("research-matrix.png", matrix(), 1440, 1200, true);
    await shot("design-thesis.png", thesis(), 1440, 1024, false);
    await shot("01-hero-desktop.png", hero("outcome"), 1440, 1024, false);
    await shot("01-hero-mobile.png", hero("outcome"), 390, 844, false);
    await shot("02-proof-strip-desktop.png", proof(), 1440, 600, false);
    await shot("02-proof-strip-mobile.png", proof(), 390, 844, false);
    await shot("03-problem-desktop.png", problem(), 1440, 1024, false);
    await shot("03-problem-mobile.png", problem(), 390, 844, false);
    await shot("04-recovery-path-desktop.png", recoveryPath(), 1440, 1024, false);
    await shot("04-recovery-path-mobile.png", recoveryPath(), 390, 844, false);
    await shot("05-evidence-desktop.png", evidence(), 1440, 1024, false);
    await shot("05-evidence-mobile.png", evidence(), 390, 844, false);
    await shot("06-pilot-scope-desktop.png", pilotScope(), 1440, 1024, false);
    await shot("06-pilot-scope-mobile.png", pilotScope(), 390, 844, false);
    await shot("07-trust-faq-desktop.png", trustFaq(), 1440, 1024, false);
    await shot("07-trust-faq-mobile.png", trustFaq(), 390, 844, true);
    await shot("08-measure-success-desktop.png", measure(), 1440, 600, false);
    await shot("08-measure-success-mobile.png", measure(), 390, 844, false);
    await shot("09-closing-cta-desktop.png", closing(), 1440, 844, false);
    await shot("09-closing-cta-mobile.png", closing(), 390, 844, false);
    await shot("10-pilot-form-desktop.png", pilotForm(), 1440, 1024, false);
    await shot("10-pilot-form-mobile.png", pilotForm(), 390, 844, true);
    await shot("full-page-desktop.png", landing(), 1440, 1024, true);
    await shot("full-page-mobile.png", landing(), 390, 844, true);
    for (const width of [320, 375, 768, 1440, 1920]) {
      await shot("responsive-" + width + ".png", landing(), width, width < 800 ? 900 : 1024, true);
    }
  }

  await renderTheme("blue");
  await renderTheme("white");
  await browser.close();
}

await render();
