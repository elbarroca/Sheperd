import { ImageResponse } from "next/og";

export const size = { width: 180, height: 180 };
export const contentType = "image/png";

export default function AppleIcon(): ImageResponse {
  return new ImageResponse(
    <div
      style={{
        alignItems: "center",
        background: "#15202b",
        color: "#fbfcfc",
        display: "flex",
        fontFamily: "Arial, sans-serif",
        fontSize: 96,
        fontWeight: 700,
        height: "100%",
        justifyContent: "center",
        letterSpacing: "-0.04em",
        width: "100%",
      }}
    >
      S<span style={{ color: "#8a3b20" }}>.</span>
    </div>,
    size,
  );
}
