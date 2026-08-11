"use client";
/**
 * Small, discreet "Powered by InvictaX Group GmbH" line.
 * Used on login pages, customer portal and admin sidebar footer.
 */
export default function PoweredByInvictaX({ variant = "light", align = "center" }) {
  const isDark = variant === "dark";
  const color = isDark ? "rgba(255,255,255,0.35)" : "rgba(0,0,0,0.4)";
  const linkColor = isDark ? "rgba(255,255,255,0.6)" : "rgba(0,0,0,0.6)";
  const border = isDark ? "rgba(255,255,255,0.25)" : "rgba(0,0,0,0.25)";
  return (
    <div
      data-testid="powered-by-invictax"
      style={{
        marginTop: "1.25rem",
        fontSize: "0.7rem",
        letterSpacing: "0.03em",
        color,
        textAlign: align,
      }}
    >
      Powered by{" "}
      <a
        href="https://www.invictaflow.ch"
        target="_blank"
        rel="noopener noreferrer"
        style={{
          color: linkColor,
          textDecoration: "none",
          borderBottom: `1px dotted ${border}`,
        }}
      >
        InvictaX Group GmbH
      </a>
    </div>
  );
}
