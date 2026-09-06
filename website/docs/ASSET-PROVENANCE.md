# Asset Provenance

## `original-material-study.png`

- Date: 2026-07-15
- Method: OpenAI built-in image generation, original generation from a text prompt
- Source retained at: `/Users/barroca888/.codex/generated_images/019f6516-1870-7b01-845d-f45d369a89e1/exec-c7899d17-62cb-421c-991f-d1937359db30.png`
- Working copy: `website/design-experiments/assets/original-material-study.png`
- Dimensions: 1717 × 916
- SHA-256: `88fa33dd43ec91c2d7be30b36fc0fe687df7255a4985b9f1a502c94aa5b019ad`
- Rights/provenance note: generated specifically for this local SheperD design exploration; no third-party source image, logo, trademark, customer material, or personal data was supplied.

Prompt:

> Use case: stylized-concept. Asset type: original landing-page editorial material study. An abstract close-up still life suggesting three evidence layers coming into alignment, without depicting a real document or software interface. Deep matte charcoal surface, overlapping torn off-white archival paper edges, one oxidized-orange cotton thread tracing a continuous route, sparse cobalt graphite registration marks, and a small warm safety-yellow paper tab. Photorealistic macro editorial photography with tactile fibers, imperfect paper grain, subtle embossing, restrained documentary realism; wide landscape crop with strong diagonal movement and quiet negative space; calm raking daylight. No text, letters, numbers, logos, brands, seals, signatures, UI, legal symbols, customer data, watermarks, glossy glass effects, gradients, or extra props.

Use boundary: abstract editorial texture only. It does not depict a customer record, invoice, legal finding, operational event, product interface, company capability, or outcome.

## Delivery derivative

- Application path: `website/public/media/material-study.jpg`
- Direction artifact path: `website/design-experiments/direction-b-margin-notes/material-study.jpg`
- Dimensions: 1717 × 916
- Size: 541,875 bytes
- SHA-256: `a324f3fdeafa7e4e596067380d37ddad0badae632804c756ccc3eb73e9aabccc`
- Transformation: local JPEG delivery derivative of the generated PNG; no semantic edit or third-party material was added.

## `container-terminal-operations.jpg`

- Date: 2026-07-15
- Method: OpenAI built-in image generation, original generation from a text prompt
- Source retained at: `/Users/barroca888/.codex/generated_images/019f6516-1870-7b01-845d-f45d369a89e1/exec-d5c4dcc9-a555-447e-ba2d-f94b6a2cb92b.png`
- Application path: `website/public/media/container-terminal-operations.jpg`
- Dimensions: 1586 × 992
- Source SHA-256: `064784228cc7511cdee45265d66af6596506f806a8de0a4b5b104e95abc44d2b`
- Delivery SHA-256: `79f970ba1906e5bf410d8777e442067997e3b17f81f40406bba2bbc14ce4ae5d`
- Transformation: local JPEG delivery derivative; no semantic edit or third-party material was added.
- Rights/provenance note: generated specifically for this local SheperD landing page; no third-party source image, logo, trademark, customer material, or personal data was supplied.

Prompt:

> Use case: photorealistic-natural. Asset type: responsive landing-page editorial image for a shipping-container charge recovery company. Create an original, credible container-terminal operations photograph that instantly reads as import logistics to an industry audience. Show a working marine container yard at blue hour, orderly rows of generic intermodal containers, one rubber-tired gantry crane and a terminal tractor moving through a clear operational lane, distant ship-to-shore cranes, and soft harbor atmosphere. Use high-end documentary logistics photography, realistic industrial scale, physically plausible container geometry and handling equipment, natural textures, a restrained cinematic finish, deep navy, steel blue, cobalt, neutral gray, and limited safety orange. Use a wide 16:10 landscape composition with no company names, shipping-line logos, readable container IDs, flags, people, text overlays, UI, charts, or watermarks.

Use boundary: generic industry-context imagery only. It does not depict a SheperD customer, actual shipment, real terminal event, verified product capability, or recovery outcome.

## September 2026 redesign assets

- `website/public/media/recovery-terminal.png` is an unchanged copy of the
  approved `website/mockups/shepherd-v2/hero-direction-01-art.png` (1918 × 820).
  Next.js generates responsive delivery formats. The asset contains no invoice
  panel, route line, evidence labels, or
  caption. It remains illustrative terminal imagery, not a customer record.
- `website/public/og/sheperd-recovery.png` is a 1200 × 630 social graphic rendered
  with Next.js `ImageResponse` from that artwork, the existing SheperD animal
  logo, and the approved headline and recovery qualification. Georgia and Arial
  were used to render the graphic; no font binaries are shipped.

## September 2026 atmospheric loop

- Method: OpenAI built-in image generation produced a separate ground-fog plate,
  with `recovery-terminal.png` supplied only as a lighting reference. No external
  image API or fallback generation CLI was used.
- Generated source: `/Users/barroca888/.codex/generated_images/01a0775e-8a66-7a21-80bf-137878a67d1c/exec-5ca257f2-b0af-49fe-9241-f3db2c5c0203.png`
- Retained project plate: `website/design-experiments/assets/recovery-ground-fog.png`
- Plate SHA-256: `60d5888c6bd8801ba2ffdb9cb5c06d2874c62d05e65bf9c1ba3fcd795b795f90`
- `scripts/render-hero-loop.sh` uses FFmpeg to composite that plate over the
  unchanged terminal artwork. Periodic horizontal drift and soft light variation
  form a continuous 20-second loop; terminal geometry does not morph.
- Browser derivatives: `public/media/recovery-terminal-loop.webm` (1600 × 684,
  24 fps, 174,200 bytes) and `.mp4` (same dimensions and timing, H.264 fallback).
- `public/media/recovery-terminal-mobile.png` is an 820 × 820 delivery crop
  of the original artwork, preserving the same mobile focal position. Native
  picture selection and Next.js image optimization avoid decoding the unused
  panorama on phones; no scene content is generated or altered in this crop.
- Portable GIF: `public/media/recovery-terminal-loop.gif` (960 × 410, 12 fps,
  20 seconds). The website delivers the smaller video rather than downloading
  this export on page load.
- Static Next.js imagery remains visible until playback starts, and whenever
  reduced motion or a media failure prevents playback. The loop is decorative,
  silent, and contains no claims, customer data, overlays, or labels.

Exact generation prompt:

> Create one production VFX texture asset for a very restrained, slow atmospheric animation of the referenced container terminal. The reference is ONLY for the cool blue-gray lighting and ground-level fog character. Output a wide 1536 x 864 image containing ONLY pale blue-gray wisps of photorealistic ground fog on a perfectly pure black background. No port, containers, buildings, horizon, ground surface, lights, lettering, captions, diagrams or objects. The fog is a shallow horizontal bank concentrated in the lower middle third, layered with irregular soft wisps, small transparent-looking gaps, very gentle light diffusion, and almost-black falloff on all four edges. Fine natural volumetric texture, subdued low opacity appearance suitable for screen compositing over a dark maritime scene. The left and right edges must fade completely to pure black so the fog can drift without visible seams. Top half almost entirely black. Premium film VFX plate; calm, not a smoke explosion.
