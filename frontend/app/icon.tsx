import { ImageResponse } from "next/og";

const BRAND = {
  background: "#f6f0e6",
  surface: "#efe3d3",
  border: "#cdb99a",
  ink: "#4c3c2a",
};

export const size = {
  width: 512,
  height: 512,
};

export const contentType = "image/png";

export default function Icon() {
  return new ImageResponse(
    (
      <div
        style={{
          width: "100%",
          height: "100%",
          display: "flex",
          alignItems: "center",
          justifyContent: "center",
          background: BRAND.background,
        }}
      >
        <div
          style={{
            width: 416,
            height: 416,
            borderRadius: 118,
            display: "flex",
            alignItems: "center",
            justifyContent: "center",
            background: BRAND.surface,
            border: `10px solid ${BRAND.border}`,
            boxShadow: "inset 0 1px 0 rgba(255,255,255,0.65)",
          }}
        >
          <div
            style={{
              display: "flex",
              alignItems: "center",
              justifyContent: "center",
              color: BRAND.ink,
              fontSize: 182,
              fontWeight: 700,
              letterSpacing: "-0.16em",
            }}
          >
            1%
          </div>
        </div>
      </div>
    ),
    size
  );
}
