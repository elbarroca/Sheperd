import { ImageResponse } from "next/og";

export const alt = "SheperD Preview wordmark with abstract container lines";
export const size = { width: 1200, height: 630 };
export const contentType = "image/png";

export default function OpenGraphImage(): ImageResponse {
  return new ImageResponse(
    <div
      style={{
        alignItems: "stretch",
        background: "#fbfcfc",
        color: "#15202b",
        display: "flex",
        fontFamily: "Arial, sans-serif",
        height: "100%",
        justifyContent: "space-between",
        padding: "72px",
        width: "100%",
      }}
    >
      <div style={{ display: "flex", flexDirection: "column", justifyContent: "space-between" }}>
        <div style={{ fontSize: 30, fontWeight: 700, letterSpacing: "-0.04em" }}>SheperD</div>
        <div style={{ display: "flex", flexDirection: "column", gap: 18 }}>
          <div style={{ color: "#6f2d17", fontSize: 20, letterSpacing: "0.12em", textTransform: "uppercase" }}>
            Preview
          </div>
          <div style={{ fontSize: 76, fontWeight: 500, letterSpacing: "-0.04em", lineHeight: 1 }}>
            Start with the record.
          </div>
        </div>
      </div>
      <div style={{ display: "flex", flexDirection: "column", gap: 22, justifyContent: "center", width: 360 }}>
        {["#15202b", "#465a69", "#8a3b20"].map((color) => (
          <div key={color} style={{ border: `3px solid ${color}`, height: 92, width: "100%" }} />
        ))}
      </div>
    </div>,
    size,
  );
}
