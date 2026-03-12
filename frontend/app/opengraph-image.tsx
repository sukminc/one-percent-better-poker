import { ImageResponse } from "next/og";

export const runtime = "edge";
export const alt = "onepercentbetter.poker — GTO Defends. We Exploit.";
export const size = { width: 1200, height: 630 };
export const contentType = "image/png";

export default function OGImage() {
  return new ImageResponse(
    (
      <div
        style={{
          background: "#000000",
          width: "100%",
          height: "100%",
          display: "flex",
          flexDirection: "column",
          justifyContent: "space-between",
          padding: "72px 80px",
          fontFamily: "sans-serif",
        }}
      >
        {/* Top: logo + chip */}
        <div style={{ display: "flex", alignItems: "center", gap: "16px" }}>
          <div
            style={{
              width: "52px",
              height: "52px",
              borderRadius: "50%",
              border: "2px solid #007AFF",
              display: "flex",
              alignItems: "center",
              justifyContent: "center",
              color: "#007AFF",
              fontSize: "16px",
              fontWeight: 700,
            }}
          >
            1%
          </div>
          <span style={{ color: "#555", fontSize: "18px", letterSpacing: "0.05em" }}>
            onepercentbetter.poker
          </span>
        </div>

        {/* Middle: headline */}
        <div style={{ display: "flex", flexDirection: "column", gap: "20px" }}>
          <div
            style={{
              fontSize: "64px",
              fontWeight: 700,
              color: "#ffffff",
              lineHeight: 1.05,
              letterSpacing: "-0.02em",
            }}
          >
            GTO Defends.{" "}
            <span style={{ color: "#007AFF" }}>We Exploit.</span>
          </div>
          <div style={{ fontSize: "24px", color: "#666666", maxWidth: "700px", lineHeight: 1.4 }}>
            Quantify your opponent&apos;s GTO deviations and turn them into measurable bb/100 edge.
          </div>
        </div>

        {/* Bottom: builder tag + stats */}
        <div style={{ display: "flex", justifyContent: "space-between", alignItems: "flex-end" }}>
          <div
            style={{
              display: "flex",
              alignItems: "center",
              gap: "12px",
              background: "#0a0a0a",
              border: "1px solid #1a1a1a",
              borderRadius: "8px",
              padding: "12px 20px",
            }}
          >
            <div
              style={{
                width: "36px",
                height: "36px",
                borderRadius: "50%",
                border: "1.5px solid #007AFF",
                display: "flex",
                alignItems: "center",
                justifyContent: "center",
                color: "#007AFF",
                fontSize: "11px",
                fontWeight: 700,
              }}
            >
              SY
            </div>
            <div style={{ display: "flex", flexDirection: "column", gap: "2px" }}>
              <span style={{ color: "#ffffff", fontSize: "14px", fontWeight: 600 }}>
                Sukmin Yoon
              </span>
              <span style={{ color: "#555", fontSize: "12px" }}>
                Built with AI · linkedin.com/in/sukminyoon
              </span>
            </div>
          </div>

          <div style={{ display: "flex", gap: "32px" }}>
            {[
              { value: "+2.3 bb/100", label: "Avg exploit edge" },
              { value: "94%", label: "GTO accuracy" },
            ].map((s) => (
              <div
                key={s.label}
                style={{ display: "flex", flexDirection: "column", alignItems: "flex-end", gap: "4px" }}
              >
                <span style={{ color: "#007AFF", fontSize: "22px", fontWeight: 700, fontFamily: "monospace" }}>
                  {s.value}
                </span>
                <span style={{ color: "#444", fontSize: "12px", textTransform: "uppercase", letterSpacing: "0.1em" }}>
                  {s.label}
                </span>
              </div>
            ))}
          </div>
        </div>
      </div>
    ),
    { ...size }
  );
}
