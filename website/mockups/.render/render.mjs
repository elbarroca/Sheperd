import fs from "node:fs/promises";
import path from "node:path";
import { fileURLToPath } from "node:url";
import { chromium } from "@playwright/test";

const root = path.resolve(path.dirname(fileURLToPath(import.meta.url)), "../../..");
const outputDir = path.join(root, "website", "mockups");
const renderDir = path.join(outputDir, ".render");

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
  muted: "#66808E",
};

const materialOne = `data:image/png;base64,${(await fs.readFile(path.join(outputDir, "assets", "evidence-route-study.png"))).toString("base64")}`;
const materialTwo = `data:image/png;base64,${(await fs.readFile(path.join(outputDir, "assets", "terminal-evidence-study.png"))).toString("base64")}`;

const css = `
  :root {
    --navy: ${colors.navy}; --teal: ${colors.teal}; --paper: ${colors.paper}; --ice: ${colors.ice};
    --cobalt: ${colors.cobalt}; --azure: ${colors.azure}; --amber: ${colors.amber}; --hairline: ${colors.hairline};
    --ink: ${colors.ink}; --muted: ${colors.muted}; --serif: Georgia, "Times New Roman", serif;
    --sans: Inter, ui-sans-serif, system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
    --mono: "SFMono-Regular", Consolas, "Liberation Mono", monospace;
  }
  * { box-sizing: border-box; }
  html, body { margin: 0; padding: 0; background: var(--paper); color: var(--ink); }
  body { font-family: var(--sans); font-size: 16px; line-height: 1.45; -webkit-font-smoothing: antialiased; }
  main { overflow: hidden; }
  h1, h2, h3, p { margin: 0; }
  h1, h2, h3 { font-family: var(--serif); font-weight: 400; letter-spacing: -0.055em; }
  .shell { width: min(1180px, calc(100% - 112px)); margin: 0 auto; }
  .section { position: relative; min-height: 1024px; padding: 86px 0; display: flex; align-items: center; }
  .section.compact { min-height: 840px; }
  .section.dark { background: var(--navy); color: var(--paper); }
  .section.teal { background: var(--teal); color: var(--paper); }
  .section.ice { background: var(--ice); }
  .section.paper { background: var(--paper); }
  .nav { position: absolute; top: 32px; left: 0; right: 0; display: flex; align-items: center; justify-content: space-between; z-index: 3; }
  .wordmark { display: flex; align-items: center; gap: 10px; font-size: 17px; font-weight: 700; letter-spacing: -0.04em; }
  .mark { width: 24px; height: 24px; border: 1px solid currentColor; position: relative; display: inline-block; }
  .mark::before, .mark::after { content: ""; position: absolute; background: currentColor; }
  .mark::before { width: 1px; top: 4px; bottom: 4px; left: 11px; }
  .mark::after { height: 1px; left: 4px; right: 4px; top: 11px; }
  .nav-links { display: flex; align-items: center; gap: 28px; color: inherit; font-size: 12px; }
  .nav-links span { opacity: .72; }
  .button { display: inline-flex; align-items: center; justify-content: center; min-height: 44px; padding: 0 22px; border-radius: 999px; font-size: 12px; font-weight: 700; letter-spacing: .01em; border: 1px solid transparent; }
  .button.primary { background: var(--cobalt); color: white; }
  .button.light { background: var(--paper); color: var(--navy); }
  .button.outline { border-color: currentColor; color: inherit; background: transparent; }
  .eyebrow, .mono { font-family: var(--mono); font-size: 10px; line-height: 1.2; letter-spacing: .12em; text-transform: uppercase; }
  .eyebrow { color: var(--azure); }
  .dark .eyebrow, .teal .eyebrow { color: var(--azure); }
  .boundary { color: var(--azure); font-family: var(--mono); font-size: 10px; letter-spacing: .04em; text-transform: uppercase; }
  .hero-grid { width: 100%; display: grid; grid-template-columns: minmax(0, .93fr) minmax(480px, 1.07fr); gap: 72px; align-items: center; }
  .hero-copy { padding-top: 38px; max-width: 620px; }
  .hero-copy h1 { font-size: clamp(64px, 7vw, 104px); line-height: .93; margin: 20px 0 28px; }
  .hero-copy p { max-width: 520px; color: #C6D5DF; font-size: 18px; line-height: 1.55; }
  .hero-actions { display: flex; gap: 12px; align-items: center; margin: 34px 0 18px; }
  .hero-art { position: relative; min-height: 620px; border: 1px solid rgba(198,213,223,.26); background: #0B202A; overflow: hidden; }
  .hero-art img { width: 100%; height: 100%; object-fit: cover; opacity: .54; filter: saturate(.72) contrast(1.04); }
  .hero-art::after { content: ""; position: absolute; inset: 0; background: linear-gradient(90deg, rgba(6,18,32,.9), rgba(6,18,32,.2) 60%, rgba(6,18,32,.62)); }
  .invoice-card { position: absolute; z-index: 1; width: 71%; left: 8%; top: 13%; padding: 24px; background: rgba(247,248,245,.96); color: var(--ink); box-shadow: 0 24px 48px rgba(0,0,0,.3); transform: rotate(-2deg); }
  .invoice-top { display: flex; justify-content: space-between; align-items: flex-start; padding-bottom: 18px; border-bottom: 1px solid var(--hairline); }
  .invoice-title { font-family: var(--serif); font-size: 26px; letter-spacing: -.04em; }
  .invoice-stamp { border: 1px solid var(--cobalt); color: var(--cobalt); padding: 5px 8px; font-family: var(--mono); font-size: 8px; letter-spacing: .08em; }
  .invoice-meta { display: grid; grid-template-columns: 1fr 1fr; gap: 12px; margin: 18px 0 22px; }
  .invoice-meta b, .mini-label { display: block; font-family: var(--mono); font-size: 8px; letter-spacing: .1em; text-transform: uppercase; color: var(--muted); font-weight: 500; }
  .invoice-meta span { font-family: var(--mono); font-size: 11px; }
  .line-row { display: grid; grid-template-columns: 1fr 72px; gap: 10px; padding: 12px 8px; border-top: 1px solid var(--hairline); font-size: 12px; }
  .line-row span:last-child { text-align: right; font-family: var(--mono); }
  .line-row.highlight { background: #DDEBFF; outline: 2px solid var(--cobalt); outline-offset: -2px; }
  .route-svg { position: absolute; z-index: 2; inset: 0; width: 100%; height: 100%; pointer-events: none; }
  .route-svg path { fill: none; stroke: var(--azure); stroke-width: 2; stroke-dasharray: 7 7; }
  .route-svg circle { fill: var(--cobalt); stroke: var(--paper); stroke-width: 2; }
  .route-endpoint { position: absolute; z-index: 3; right: 7%; bottom: 12%; width: 32%; padding: 16px; border: 1px solid var(--azure); background: rgba(6,18,32,.78); }
  .route-endpoint strong { display: block; margin-top: 8px; font-family: var(--serif); font-size: 22px; font-weight: 400; line-height: 1; }
  .route-endpoint small { color: var(--azure); }
  .section-heading { display: grid; grid-template-columns: .88fr 1.12fr; gap: 72px; align-items: end; margin-bottom: 52px; }
  .section-heading h2 { font-size: clamp(50px, 5vw, 76px); line-height: .95; }
  .section-heading p { max-width: 510px; color: var(--muted); font-size: 17px; line-height: 1.55; }
  .dark .section-heading p, .teal .section-heading p { color: #C6D5DF; }
  .record-bands { border-top: 1px solid var(--hairline); }
  .record-band { display: grid; grid-template-columns: 210px 1fr 150px; gap: 28px; align-items: center; min-height: 148px; border-bottom: 1px solid var(--hairline); }
  .record-band h3 { font-size: 28px; line-height: 1; }
  .record-band p { max-width: 460px; color: var(--muted); font-size: 14px; }
  .record-band .band-note { color: var(--cobalt); font-family: var(--mono); font-size: 10px; text-transform: uppercase; letter-spacing: .08em; text-align: right; }
  .route-rail { position: absolute; width: 1px; background: linear-gradient(var(--cobalt), transparent); top: 0; bottom: 0; left: 9.5%; opacity: .34; }
  .process-grid { display: grid; grid-template-columns: repeat(4, 1fr); gap: 0; border-top: 1px solid rgba(198,213,223,.38); border-bottom: 1px solid rgba(198,213,223,.38); position: relative; }
  .process-grid::before { content: ""; position: absolute; top: 58px; left: 7%; right: 7%; height: 1px; background: var(--azure); opacity: .82; }
  .process-step { position: relative; min-height: 370px; padding: 34px 26px 28px 0; border-right: 1px solid rgba(198,213,223,.25); }
  .process-step:not(:first-child) { padding-left: 26px; }
  .process-step:last-child { border-right: 0; }
  .process-step .step-number { display: flex; align-items: center; gap: 12px; font-family: var(--mono); font-size: 11px; color: var(--azure); }
  .process-step .dot { width: 10px; height: 10px; border-radius: 50%; background: var(--cobalt); box-shadow: 0 0 0 5px rgba(112,184,255,.14); }
  .process-step h3 { font-size: 34px; margin: 90px 0 16px; }
  .process-step p { color: #C6D5DF; font-size: 14px; max-width: 210px; }
  .process-step .step-note { position: absolute; bottom: 28px; color: rgba(198,213,223,.6); font-family: var(--mono); font-size: 9px; text-transform: uppercase; letter-spacing: .08em; }
  .artifact-grid { display: grid; grid-template-columns: repeat(3, 1fr); gap: 18px; align-items: stretch; }
  .artifact { position: relative; min-height: 430px; padding: 22px; border: 1px solid var(--hairline); background: rgba(255,255,255,.48); overflow: hidden; }
  .artifact.dark-artifact { background: #0D222C; border-color: rgba(198,213,223,.28); color: var(--paper); }
  .artifact .synthetic { color: var(--cobalt); margin-bottom: 26px; }
  .artifact.dark-artifact .synthetic { color: var(--azure); }
  .artifact h3 { font-size: 31px; line-height: .95; margin-bottom: 12px; }
  .artifact .artifact-copy { color: var(--muted); font-size: 13px; line-height: 1.45; }
  .artifact.dark-artifact .artifact-copy { color: #C6D5DF; }
  .artifact-lines { margin-top: 26px; border-top: 1px solid var(--hairline); }
  .artifact-line { display: grid; grid-template-columns: 1fr 76px; gap: 12px; padding: 11px 0; border-bottom: 1px solid var(--hairline); font-family: var(--mono); font-size: 9px; }
  .artifact-line b { color: var(--cobalt); font-weight: 500; }
  .artifact-line strong { text-align: right; font-weight: 500; }
  .timeline { margin-top: 30px; border-left: 1px solid var(--azure); padding-left: 22px; }
  .event { position: relative; margin: 0 0 20px; }
  .event::before { content: ""; position: absolute; width: 9px; height: 9px; left: -27px; top: 2px; border-radius: 50%; background: var(--cobalt); border: 2px solid var(--ice); }
  .event .date { color: var(--cobalt); font-family: var(--mono); font-size: 9px; }
  .event .event-title { margin-top: 4px; font-size: 13px; }
  .terms-box { margin-top: 30px; padding: 18px; border-left: 3px solid var(--amber); background: rgba(214,154,69,.1); }
  .terms-box .term { font-family: var(--serif); font-size: 26px; line-height: 1; }
  .terms-box p { color: var(--muted); font-size: 12px; margin-top: 10px; }
  .scope-grid { display: grid; grid-template-columns: .82fr 1.18fr; gap: 54px; align-items: start; }
  .scope-copy h2 { font-size: clamp(50px, 5.6vw, 82px); line-height: .9; max-width: 550px; }
  .scope-copy p { margin-top: 24px; max-width: 470px; color: var(--muted); font-size: 17px; line-height: 1.55; }
  .scope-list { border-top: 1px solid var(--hairline); }
  .scope-row { display: grid; grid-template-columns: 160px 1fr; gap: 24px; min-height: 104px; align-items: center; border-bottom: 1px solid var(--hairline); }
  .scope-row strong { font-family: var(--mono); font-size: 10px; text-transform: uppercase; letter-spacing: .08em; color: var(--cobalt); }
  .scope-row span { font-size: 16px; }
  .method-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 22px; }
  .method-panel { border: 1px solid var(--hairline); padding: 30px; min-height: 300px; }
  .method-panel h3 { font-size: 34px; margin-bottom: 20px; }
  .method-panel p { color: var(--muted); font-size: 14px; }
  .source-row { display: flex; justify-content: space-between; gap: 18px; padding: 17px 0; border-top: 1px solid var(--hairline); font-size: 13px; }
  .source-row span:last-child { color: var(--muted); font-family: var(--mono); font-size: 9px; text-transform: uppercase; }
  .faq { margin-top: 24px; border-top: 1px solid var(--hairline); }
  .faq-row { display: grid; grid-template-columns: 260px 1fr; gap: 28px; padding: 17px 0; border-bottom: 1px solid var(--hairline); }
  .faq-row strong { font-family: var(--serif); font-size: 22px; font-weight: 400; }
  .faq-row span { color: var(--muted); font-size: 13px; }
  .closing { text-align: center; }
  .closing h2 { font-size: clamp(66px, 8vw, 124px); line-height: .88; max-width: 920px; margin: 0 auto 32px; }
  .closing p { max-width: 480px; color: #C6D5DF; margin: 0 auto 28px; font-size: 17px; }
  .form-shell { display: grid; grid-template-columns: .8fr 1.2fr; gap: 80px; align-items: start; }
  .form-copy h2 { font-size: clamp(60px, 6vw, 90px); line-height: .88; margin: 18px 0 24px; }
  .form-copy p { max-width: 430px; color: #C6D5DF; font-size: 17px; }
  .form-card { background: var(--paper); color: var(--ink); padding: 32px; border: 1px solid rgba(198,213,223,.4); }
  .form-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 16px; }
  .field { display: grid; gap: 8px; }
  .field.full { grid-column: 1 / -1; }
  .field label { font-family: var(--mono); color: var(--muted); font-size: 9px; letter-spacing: .1em; text-transform: uppercase; }
  .field-box { min-height: 48px; border: 1px solid var(--hairline); padding: 14px; color: #81939B; font-size: 13px; background: white; }
  .field-box.large { min-height: 108px; }
  .consent { display: flex; gap: 10px; align-items: flex-start; margin: 22px 0; color: var(--muted); font-size: 11px; }
  .check { width: 15px; height: 15px; border: 1px solid var(--cobalt); flex: none; }
  .form-foot { display: flex; justify-content: space-between; gap: 18px; align-items: center; }
  .privacy { margin-top: 20px; color: var(--muted); font-family: var(--mono); font-size: 9px; line-height: 1.5; }
  .states { display: grid; gap: 10px; margin-top: 26px; }
  .state { border-left: 3px solid var(--cobalt); background: rgba(234,242,247,.76); padding: 11px 14px; }
  .state.warn { border-left-color: var(--amber); }
  .state strong { display: block; font-family: var(--mono); color: var(--cobalt); font-size: 9px; letter-spacing: .08em; }
  .state.warn strong { color: #9A6A24; }
  .state span { display: block; margin-top: 4px; font-size: 11px; color: var(--muted); }
  .matrix-page, .thesis-page { min-height: 100vh; padding: 60px; }
  .matrix-page { background: var(--paper); }
  .matrix-title, .thesis-title { display: flex; justify-content: space-between; gap: 40px; align-items: flex-end; margin-bottom: 40px; }
  .matrix-title h1, .thesis-title h1 { max-width: 780px; font-size: 78px; line-height: .88; }
  .matrix-title p, .thesis-title p { max-width: 300px; color: var(--muted); font-size: 13px; }
  table { width: 100%; border-collapse: collapse; font-size: 12px; }
  th { color: var(--cobalt); font-family: var(--mono); font-size: 9px; letter-spacing: .08em; text-transform: uppercase; text-align: left; padding: 11px 12px; border-top: 1px solid var(--ink); border-bottom: 1px solid var(--hairline); }
  td { vertical-align: top; padding: 14px 12px; border-bottom: 1px solid var(--hairline); line-height: 1.4; }
  td:first-child { width: 17%; font-weight: 700; }
  td:nth-child(2) { width: 13%; color: var(--cobalt); font-family: var(--mono); font-size: 9px; text-transform: uppercase; }
  td:nth-child(3) { width: 25%; }
  td:nth-child(4) { width: 22%; color: var(--muted); }
  td:nth-child(5) { width: 23%; }
  .thesis-page { background: var(--navy); color: var(--paper); }
  .thesis-page .thesis-title p { color: #C6D5DF; }
  .thesis-page .eyebrow { color: var(--azure); }
  .thesis-hero { display: grid; grid-template-columns: 1.08fr .92fr; gap: 70px; align-items: end; margin-bottom: 58px; }
  .thesis-hero h2 { font-size: 112px; line-height: .82; max-width: 780px; }
  .thesis-hero p { color: #C6D5DF; max-width: 330px; font-size: 15px; }
  .thesis-flow { display: grid; grid-template-columns: repeat(5, 1fr); border-top: 1px solid rgba(198,213,223,.34); border-bottom: 1px solid rgba(198,213,223,.34); }
  .flow-cell { min-height: 210px; border-right: 1px solid rgba(198,213,223,.25); padding: 24px 18px 18px 0; }
  .flow-cell:not(:first-child) { padding-left: 18px; }
  .flow-cell:last-child { border: 0; }
  .flow-cell strong { color: var(--azure); font-family: var(--mono); font-size: 9px; letter-spacing: .08em; }
  .flow-cell h3 { font-size: 30px; margin: 54px 0 12px; }
  .flow-cell p { color: #C6D5DF; font-size: 12px; }
  .token-strip { display: grid; grid-template-columns: repeat(4, 1fr); gap: 12px; margin-top: 26px; }
  .token { min-height: 110px; padding: 14px; border: 1px solid rgba(198,213,223,.26); }
  .token i { display: block; width: 32px; height: 32px; margin-bottom: 18px; background: var(--paper); }
  .token:nth-child(2) i { background: var(--cobalt); } .token:nth-child(3) i { background: var(--azure); } .token:nth-child(4) i { background: var(--amber); }
  .token span { display: block; font-family: var(--mono); font-size: 9px; color: #C6D5DF; }
  @media (max-width: 720px) {
    .shell { width: calc(100% - 40px); }
    .section { min-height: 844px; padding: 74px 0 46px; align-items: flex-start; }
    .section.compact { min-height: 760px; }
    .nav { top: 18px; } .nav-links { display: none; } .nav .button { min-height: 36px; padding: 0 14px; font-size: 10px; }
    .hero-grid, .section-heading, .scope-grid, .form-shell, .thesis-hero { grid-template-columns: 1fr; gap: 30px; }
    .hero-copy { padding-top: 54px; } .hero-copy h1 { font-size: 56px; line-height: .91; margin: 18px 0 20px; }
    .hero-copy p { font-size: 15px; } .hero-actions { margin: 22px 0 12px; flex-wrap: wrap; }
    .hero-art { min-height: 390px; } .invoice-card { width: 84%; left: 6%; top: 9%; padding: 15px; }
    .invoice-title { font-size: 19px; } .invoice-meta { margin: 12px 0 14px; gap: 8px; } .line-row { padding: 8px 4px; font-size: 9px; }
    .route-endpoint { right: 5%; bottom: 5%; width: 46%; padding: 10px; } .route-endpoint strong { font-size: 17px; }
    .section-heading { margin-bottom: 30px; } .section-heading h2, .scope-copy h2 { font-size: 50px; }
    .section-heading p { font-size: 14px; }
    .record-band { grid-template-columns: 1fr 92px; gap: 12px; min-height: 136px; } .record-band h3 { font-size: 24px; } .record-band p { grid-column: 1 / -1; grid-row: 2; font-size: 12px; margin-top: -22px; } .record-band .band-note { font-size: 8px; }
    .process-grid { grid-template-columns: 1fr 1fr; } .process-grid::before { top: 52px; left: 7%; right: 7%; } .process-step { min-height: 250px; padding: 24px 14px 18px 0; } .process-step:not(:first-child) { padding-left: 14px; } .process-step h3 { font-size: 27px; margin: 64px 0 10px; } .process-step p { font-size: 11px; } .process-step .step-note { display: none; }
    .artifact-grid, .method-grid { grid-template-columns: 1fr; gap: 12px; } .artifact { min-height: 250px; padding: 16px; } .artifact h3 { font-size: 26px; } .artifact .synthetic { margin-bottom: 16px; } .artifact-lines { margin-top: 16px; } .artifact-line { padding: 7px 0; font-size: 8px; } .timeline { margin-top: 18px; }
    .scope-copy p { font-size: 14px; margin-top: 14px; } .scope-row { grid-template-columns: 112px 1fr; min-height: 86px; gap: 12px; } .scope-row span { font-size: 12px; }
    .method-panel { padding: 20px; min-height: 230px; } .method-panel h3 { font-size: 28px; } .source-row { font-size: 11px; } .faq-row { grid-template-columns: 1fr; gap: 6px; padding: 13px 0; } .faq-row strong { font-size: 19px; }
    .closing h2 { font-size: 62px; } .closing p { font-size: 14px; }
    .form-shell { gap: 18px; } .form-copy h2 { font-size: 52px; } .form-copy p { font-size: 12px; } .form-copy .boundary { margin-top: 10px !important; } .form-card { padding: 12px; } .form-grid { grid-template-columns: 1fr; gap: 7px; } .field.full { grid-column: auto; } .field { gap: 3px; } .field label { font-size: 7px; } .field-box { min-height: 32px; padding: 8px; font-size: 10px; } .field-box.large { min-height: 55px; } .consent { margin: 10px 0; font-size: 9px; } .form-foot { align-items: flex-start; flex-direction: column; gap: 8px; } .form-foot .button { width: 100%; min-height: 34px; } .privacy { margin-top: 9px; font-size: 7px; } .states { gap: 5px; margin-top: 10px; } .state { padding: 6px 8px; } .state strong { font-size: 7px; } .state span { font-size: 9px; }
    .matrix-page, .thesis-page { padding: 32px 20px; } .matrix-title, .thesis-title { display: block; margin-bottom: 28px; } .matrix-title h1, .thesis-title h1 { font-size: 54px; } .matrix-title p, .thesis-title p { margin-top: 16px; }
    table { font-size: 9px; } th { font-size: 7px; padding: 7px 5px; } td { padding: 8px 5px; } td:first-child { width: 18%; } td:nth-child(2) { width: 13%; font-size: 7px; } td:nth-child(3), td:nth-child(4), td:nth-child(5) { width: auto; }
    .thesis-hero h2 { font-size: 72px; } .thesis-flow { grid-template-columns: 1fr 1fr; } .flow-cell { min-height: 170px; padding: 18px 10px 12px 0; } .flow-cell:not(:first-child) { padding-left: 10px; } .flow-cell h3 { font-size: 24px; margin: 40px 0 8px; } .flow-cell p { font-size: 10px; } .token-strip { grid-template-columns: 1fr 1fr; }
  }
`;

function shell(content) { return `<div class="shell">${content}</div>`; }
function nav(dark = true) {
  return `<div class="nav shell"><div class="wordmark"><span class="mark"></span><span>SheperD</span></div><div class="nav-links"><span>Method</span><span>Evidence</span><span>Pilot</span><span>Limits</span></div><span class="button ${dark ? "primary" : "primary"}">Request a pilot</span></div>`;
}
function synthetic() { return `<div class="synthetic mono">ILLUSTRATIVE ARTIFACT · SYNTHETIC RECORD · NOT CUSTOMER DATA</div>`; }
function routeSvg() {
  return `<svg class="route-svg" viewBox="0 0 760 620" preserveAspectRatio="none" aria-hidden="true"><path d="M92 238 C182 192 218 284 302 259 S430 195 493 284 S594 374 687 424"></path><circle cx="92" cy="238" r="7"></circle><circle cx="302" cy="259" r="7"></circle><circle cx="493" cy="284" r="7"></circle><circle cx="687" cy="424" r="7"></circle></svg>`;
}
function invoiceArtifact() {
  return `<div class="invoice-card">${synthetic()}<div class="invoice-top"><div class="invoice-title">Detention &amp; demurrage</div><div class="invoice-stamp">REVIEW OPEN</div></div><div class="invoice-meta"><div><b>Container</b><span>MSCU 481203 7</span></div><div><b>Charge period</b><span>08–14 MAY</span></div><div><b>Billing party</b><span>Carrier record</span></div><div><b>Reference</b><span>INV–2048</span></div></div><div class="line-row"><span>Storage / free-time line</span><span>$—</span></div><div class="line-row highlight"><span>Detention · day 05 · 14 MAY</span><span>$—</span></div><div class="line-row"><span>Terminal handling line</span><span>$—</span></div></div>`;
}
function heroArt(variant = "final") {
  if (variant === "cinematic") {
    return `<div class="hero-art" style="background:#0B202A"><img src="${materialOne}" alt="" style="opacity:.7"/><div class="route-endpoint"><span class="mono">HUMAN REVIEW BOUNDARY</span><strong>Potential credit or refund</strong><small class="mono">case-specific outcome</small></div></div>`;
  }
  if (variant === "ledger") {
    return `<div class="hero-art"><img src="${materialTwo}" alt=""/>${invoiceArtifact()}${routeSvg()}<div class="route-endpoint"><span class="mono">HUMAN REVIEW BOUNDARY</span><strong>Potential credit or refund</strong><small class="mono">case-specific outcome</small></div></div>`;
  }
  return `<div class="hero-art"><img src="${materialOne}" alt=""/>${invoiceArtifact()}${routeSvg()}<div class="route-endpoint"><span class="mono">HUMAN REVIEW BOUNDARY</span><strong>Potential credit or refund</strong><small class="mono">case-specific outcome</small></div></div>`;
}
function hero(variant = "final") {
  const titles = { ledger: "A charge is not a conclusion.", cinematic: "Follow the record to the next question.", final: "Recover the D&amp;D money hiding in your invoices." };
  const title = titles[variant];
  const support = variant === "final" ? "SheperD reviews detention and demurrage invoices alongside shipment events, operational records, and governing terms to identify case-specific recovery opportunities and support the path toward a carrier credit or refund." : "One invoice line can point to a billing record, an operational event, a governing term, and a human-reviewed next step.";
  return `<section class="section dark hero-section">${nav(true)}${shell(`<div class="hero-grid"><div class="hero-copy"><div class="eyebrow">D&amp;D RECOVERY FOR IMPORTER FINANCE TEAMS</div><div class="mono" style="color:#C6D5DF;margin-top:16px">EVIDENCE-TO-RECOVERY CONTROL ROOM</div><h1>${title}</h1><p>${support}</p><div class="hero-actions"><span class="button primary">Request a pilot</span><span class="button outline">See the recovery path</span></div><div class="boundary">Case-specific review · No guaranteed recovery</div></div>${heroArt(variant)}</div>`)}</section>`;
}
function problem() {
  return `<section class="section paper"><div class="route-rail"></div>${shell(`<div class="section-heading"><div><div class="eyebrow">01 / FINANCIAL PROBLEM</div><h2>The invoice is only the first record.</h2></div><p>A billed amount is a starting point. The charge needs to sit beside the shipment events, operational records, and governing terms that shape a case-specific review.</p></div><div class="record-bands"><div class="record-band"><h3>Billing record</h3><p>Invoice line, charge date, container reference, billing party, and payment state.</p><div class="band-note">what was billed</div></div><div class="record-band"><h3>Operational record</h3><p>Availability, pickup, return, terminal timing, appointments, holds, closures, and notices.</p><div class="band-note">what happened</div></div><div class="record-band"><h3>Governing terms</h3><p>Free-time terms, tariff or contract language, route, effective dates, and source version.</p><div class="band-note">what governs</div></div></div>`)}</section>`;
}
function recoveryPath() {
  return `<section class="section teal"><div class="route-rail"></div>${shell(`<div class="section-heading"><div><div class="eyebrow">02 / RECOVERY PATH</div><h2>From billed to reviewed.</h2></div><p>The route stays visible while the conclusion stays conditional: each record changes the next question, and human review remains the boundary.</p></div><div class="process-grid"><div class="process-step"><div class="step-number"><span class="dot"></span>01</div><h3>Invoice<br>&amp; data</h3><p>Anchor the charge, period, container reference, and source record.</p><div class="step-note">billed</div></div><div class="process-step"><div class="step-number"><span class="dot"></span>02</div><h3>SheperD<br>analysis</h3><p>Join the billed line to events, records, and governing terms.</p><div class="step-note">traced</div></div><div class="process-step"><div class="step-number"><span class="dot"></span>03</div><h3>Dispute<br>support</h3><p>Prepare the case-specific record and the questions that remain.</p><div class="step-note">reviewed</div></div><div class="process-step"><div class="step-number"><span class="dot"></span>04</div><h3>Potential<br>recovery</h3><p>Stop at human review before any carrier credit or refund outcome.</p><div class="step-note">conditional</div></div></div>`)}</section>`;
}
function evidence() {
  return `<section class="section ice"><div class="route-rail"></div>${shell(`<div class="section-heading"><div><div class="eyebrow">03 / EVIDENCE LAYERS</div><h2>One charge. Three records.</h2></div><p>The invoice is the anchor. The review gets clearer when the billing record, operational timeline, and governing terms travel together.</p></div><div class="artifact-grid"><div class="artifact">${synthetic()}<h3>Billing record</h3><p class="artifact-copy">What was billed, for which dates, by whom, and against which line item.</p><div class="artifact-lines"><div class="artifact-line"><span>Charge date</span><b>14 MAY</b></div><div class="artifact-line"><span>Container ref.</span><b>MSCU 481203 7</b></div><div class="artifact-line"><span>Payment state</span><strong>OPEN</strong></div><div class="artifact-line"><span>Highlighted line</span><strong>TRACE</strong></div></div></div><div class="artifact dark-artifact">${synthetic()}<h3>Operational timeline</h3><p class="artifact-copy">What happened at the terminal, in the appointment trail, and around the notices.</p><div class="timeline"><div class="event"><div class="date">08 MAY · 09:14</div><div class="event-title">Availability record</div></div><div class="event"><div class="date">10 MAY · 12:05</div><div class="event-title">Appointment event</div></div><div class="event"><div class="date">14 MAY · 16:42</div><div class="event-title">Return / notice event</div></div></div></div><div class="artifact">${synthetic()}<h3>Governing term</h3><p class="artifact-copy">Which free-time terms, tariff or contract language, route, and source date belong beside the charge.</p><div class="terms-box"><div class="term">Effective terms</div><p>Source date and applicability stay visible. Missing evidence stays marked.</p></div><div class="artifact-lines"><div class="artifact-line"><span>Record status</span><strong>CONDITIONAL</strong></div><div class="artifact-line"><span>Review boundary</span><strong>HUMAN</strong></div></div></div></div>`)}</section>`;
}
function scope() {
  return `<section class="section paper"><div class="route-rail"></div>${shell(`<div class="scope-grid"><div class="scope-copy"><div class="eyebrow">04 / PILOT SCOPE</div><h2>Start with a focused review.</h2><p>Bring the invoice and the records around the charge. SheperD reviews the evidence together, marks what is missing, and supports the path toward a carrier credit or refund—case by case.</p><div style="margin-top:28px"><span class="button primary">Request a pilot</span></div><div class="boundary" style="margin-top:16px;color:var(--cobalt)">Case-specific review · No guaranteed recovery</div></div><div class="scope-list"><div class="scope-row"><strong>Importer provides</strong><span>Invoice, shipment references, governing terms, and the operational record available to the team.</span></div><div class="scope-row"><strong>Records reviewed</strong><span>Charge dates, container events, terminal availability, appointments, notices, and communications.</span></div><div class="scope-row"><strong>Review produces</strong><span>A case-specific evidence map, marked gaps, and a clearer next question for human review.</span></div><div class="scope-row"><strong>What happens next</strong><span>Support for the path toward a carrier credit or refund, subject to the record and the applicable terms.</span></div></div></div>`)}</section>`;
}
function trustFaq() {
  return `<section class="section ice compact"><div class="route-rail"></div>${shell(`<div class="section-heading"><div><div class="eyebrow">05 / TRUST &amp; METHOD</div><h2>Evidence first. Claims second.</h2></div><p>Trust comes from showing the records, source dates, human review, and limitations—not from badges or invented proof.</p></div><div class="method-grid"><div class="method-panel"><h3>Method</h3><div class="source-row"><span>Official sources</span><span>source-linked</span></div><div class="source-row"><span>Published terms</span><span>date-aware</span></div><div class="source-row"><span>Shipment records</span><span>case-specific</span></div><div class="source-row"><span>Human review</span><span>required boundary</span></div><div class="source-row"><span>Explicit limitations</span><span>visible</span></div></div><div class="method-panel"><h3>FAQ</h3><div class="faq"><div class="faq-row"><strong>What is the pilot?</strong><span>A focused review of a defined D&amp;D invoice question and the records around it.</span></div><div class="faq-row"><strong>What if evidence is incomplete?</strong><span>Missing evidence is marked as a gap. It is not filled with an assumption.</span></div><div class="faq-row"><strong>Credits or cash?</strong><span>Potential outcomes can include a carrier credit or refund. No outcome is guaranteed.</span></div><div class="faq-row"><strong>How fast?</strong><span>Timing depends on scope and record completeness; confirm it in the pilot discussion.</span></div></div></div></div>`)}</section>`;
}
function closing() {
  return `<section class="section dark compact"><div class="closing">${shell(`<div class="eyebrow">06 / NEXT STEP</div><h2>Bring the next question to the record.</h2><p>Request a pilot and start with one charge, its surrounding events, and the terms that govern the review.</p><span class="button light">Request a pilot</span><div class="boundary" style="margin-top:20px">Case-specific review · No guaranteed recovery</div>`)}</div></section>`;
}
function form() {
  return `<section class="section dark"><div class="route-rail"></div>${nav(true)}${shell(`<div class="form-shell"><div class="form-copy"><div class="eyebrow">SHEPERD / PILOT REQUEST</div><h2>Start with the record.</h2><p>Tell us where the charge sits in your process. The first step is a conversation, not an invoice upload.</p><div class="boundary" style="margin-top:22px">Case-specific review · No guaranteed recovery</div></div><div class="form-card"><div class="form-grid"><div class="field"><label>Name</label><div class="field-box">Your name</div></div><div class="field"><label>Work email</label><div class="field-box">name@company.com</div></div><div class="field"><label>Company</label><div class="field-box">Company name</div></div><div class="field"><label>Role</label><div class="field-box">CFO / Controller / AP / Logistics</div></div><div class="field full"><label>Annual volume</label><div class="field-box">Select an annual container volume</div></div><div class="field full"><label>Review context</label><div class="field-box large">What charge or review question should we understand first?</div></div></div><div class="consent"><span class="check"></span><span>I agree to be contacted about a SheperD pilot request.</span></div><div class="form-foot"><span class="boundary" style="color:var(--cobalt)">No invoice upload</span><span class="button primary">Request a pilot</span></div><div class="privacy">Honest privacy language: this mockup shows the intended form experience. Production privacy, retention, access, and secure-transfer details require approval.</div><div class="states"><div class="state"><strong>DISABLED PREVIEW</strong><span>Submit is disabled until required fields are complete.</span></div><div class="state warn"><strong>VALIDATION ERROR</strong><span>Enter a work email and company before continuing.</span></div><div class="state warn"><strong>SUBMISSION FAILURE</strong><span>We couldn't send your request. Try again; no invoice upload is enabled here.</span></div></div></div></div>`)}</section>`;
}
function landing() { return `<main>${hero("final")}${problem()}${recoveryPath()}${evidence()}${scope()}${trustFaq()}${closing()}</main>`; }
function docPage(kind) {
  if (kind === "matrix") {
    const rows = [
      ["1Password", "B2B security", "Dark-to-light clarity; one blue interaction signal; crisp product authority.", "Risk of copying the security metaphor, gradient, or product UI language.", "Use navy-to-paper pacing and reserve cobalt for the evidence route and CTA."],
      ["11x", "B2B service", "Editorial pacing, giant type, full-bleed photography, shadowless warm surfaces.", "Risk of imitation through cinematic layout, serif scale, or pastel palette.", "Borrow the pause and image scale; keep SheperD’s navy, paper, and record-specific artifacts."],
      ["SheperD current site", "Own baseline", "Research target for existing brand, CTA, imagery, and conversion behavior.", "Browser fetch was unavailable; do not invent findings.", "Use the pasted brief and local assets as the approved rebrand baseline."],
      ["Linear", "B2B SaaS", "A direct headline, calm navigation, compact CTA hierarchy, and product-led precision.", "Risk of default dark SaaS composition and UI-first proof.", "Use the precision and restraint for the record route, not a software dashboard."],
      ["Vercel", "Enterprise", "Monochrome confidence, strong type, terse nav, and clear split between self-serve and sales.", "Risk of copying developer infrastructure voice or black-white minimalism.", "Use confident negative space while keeping warm paper and financial nouns."],
      ["Ramp", "Finance / ops", "Deep information architecture for finance jobs and operational categories.", "Risk of broad product-grid navigation and generic spend-software framing.", "Translate breadth into one review path: billed → traced → reviewed → conditional."],
      ["Pilot", "Accounting service", "Service storytelling, expertise framing, and case-oriented narrative structure.", "Risk of using customer proof, results, or service promises without evidence.", "Use focused pilot scope and honest review states; omit proof claims."],
      ["Stripe", "Finance", "Infrastructure headline, structured sections, and high-contrast financial clarity.", "Risk of borrowing metrics, global-scale claims, or gradient spectacle.", "Use the financial directness without numbers; let the invoice carry the tension."],
      ["Flexport", "Logistics", "Operational imagery, visibility language, and physical-world supply chain context.", "Risk of stock logistics photography, partner logos, or savings claims.", "Use synthetic paper artifacts and event records instead of ports or customer proof."],
      ["project44", "Supply chain", "System-level route language, product families, and exception-management rhythm.", "Risk of dashboard-first AI claims and fake network intelligence.", "Use one continuous evidence route and stop it at human review."],
      ["Pentagram", "Editorial / service", "Portfolio-scale visual rhythm, restrained typography, and confident work index.", "Risk of becoming a studio portfolio instead of a conversion path.", "Use editorial pacing only where it clarifies the record and the pilot next step."],
    ];
    return `<div class="matrix-page"><div class="matrix-title"><div><div class="eyebrow">SHEPERD / RESEARCH MATRIX</div><h1>Premium references, translated into a new record system.</h1></div><p>Visual research is a source of rules, not a moodboard. Each reference contributes one useful behavior and one boundary.</p></div><table><thead><tr><th>Reference</th><th>Category</th><th>Useful pattern</th><th>Imitation risk</th><th>SheperD adaptation</th></tr></thead><tbody>${rows.map((row) => `<tr>${row.map((cell) => `<td>${cell}</td>`).join("")}</tr>`).join("")}</tbody></table></div>`;
  }
  return `<div class="thesis-page"><div class="thesis-title"><div><div class="eyebrow">SHEPERD / DESIGN THESIS</div><h1>Evidence-to-recovery control room</h1></div><p>A premium visual system where every blue line is a question moving through a record—not a promise moving toward a result.</p></div><div class="thesis-hero"><h2>Make the route visible. Make the boundary impossible to miss.</h2><p>Dark navy establishes seriousness. Paper and ice expose the evidence. Electric blue moves the eye from charge to record. Amber marks only the conditional gap.</p></div><div class="thesis-flow"><div class="flow-cell"><strong>01 / BILLED</strong><h3>Invoice</h3><p>Start with one highlighted line item inside a synthetic invoice.</p></div><div class="flow-cell"><strong>02 / RECORDED</strong><h3>Event</h3><p>Join availability, appointments, notices, and terminal timing.</p></div><div class="flow-cell"><strong>03 / GOVERNED</strong><h3>Term</h3><p>Keep route, effective date, and governing language beside the charge.</p></div><div class="flow-cell"><strong>04 / MARKED</strong><h3>Gap</h3><p>Use amber to show missing evidence rather than inventing certainty.</p></div><div class="flow-cell"><strong>05 / STOP</strong><h3>Human</h3><p>Stop before the potential credit or refund outcome.</p></div></div><div class="token-strip"><div class="token"><i></i><span>PAPER / #F7F8F5</span></div><div class="token"><i></i><span>COBALT / #2167F3</span></div><div class="token"><i></i><span>AZURE / #70B8FF</span></div><div class="token"><i></i><span>CONDITIONAL / #D69A45</span></div></div></div>`;
}
function documentHtml(body) { return `<!doctype html><html><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1"><style>${css}</style></head><body>${body}</body></html>`; }

async function render() {
  await fs.mkdir(renderDir, { recursive: true });
  const browser = await chromium.launch({ headless: true });
  const page = await browser.newPage({ deviceScaleFactor: 1 });
  async function shot(name, body, width, height, fullPage = false) {
    await page.setViewportSize({ width, height });
    await page.setContent(documentHtml(body), { waitUntil: "load" });
    await page.waitForFunction(() => Array.from(document.images).every((image) => image.complete));
    await page.screenshot({ path: path.join(outputDir, name), fullPage, animations: "disabled" });
  }

  await shot("research-matrix.png", docPage("matrix"), 1440, 1200);
  await shot("design-thesis.png", docPage("thesis"), 1440, 1024);
  await shot("hero-direction-01.png", hero("ledger"), 1440, 1024);
  await shot("hero-direction-02.png", hero("cinematic"), 1440, 1024);
  await shot("hero-direction-03.png", hero("final"), 1440, 1024);
  await shot("hero-final-desktop.png", hero("final"), 1440, 1024);
  await shot("hero-final-mobile.png", hero("final"), 390, 844);
  await shot("problem-desktop.png", problem(), 1440, 1024);
  await shot("problem-mobile.png", problem(), 390, 844);
  await shot("process-desktop.png", recoveryPath(), 1440, 1024);
  await shot("process-mobile.png", recoveryPath(), 390, 844);
  await shot("evidence-desktop.png", evidence(), 1440, 1024);
  await shot("evidence-mobile.png", evidence(), 390, 844);
  await shot("pilot-scope-desktop.png", scope(), 1440, 1024);
  await shot("pilot-scope-mobile.png", scope(), 390, 844);
  await shot("trust-faq-desktop.png", trustFaq(), 1440, 1024);
  await shot("trust-faq-mobile.png", trustFaq(), 390, 844);
  await shot("closing-cta-desktop.png", closing(), 1440, 844);
  await shot("closing-cta-mobile.png", closing(), 390, 844);
  await shot("pilot-form-desktop.png", form(), 1440, 1024);
  await shot("pilot-form-mobile.png", form(), 390, 844, true);
  await shot("full-page-desktop.png", landing(), 1440, 1024, true);
  await shot("full-page-mobile.png", landing(), 390, 844, true);
  for (const width of [320, 375, 768, 1440, 1920]) {
    await shot(`responsive-${width}.png`, landing(), width, width < 800 ? 900 : 1024, true);
  }
  await browser.close();
}

await render();
