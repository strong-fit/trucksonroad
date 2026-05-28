/**
 * Date formatting helpers — Swiss locale (de-CH).
 *
 * formatSwissDate("2026-08-15")          → "15.08.2026"
 * formatSwissDate("2026-08-15T10:30:00") → "15.08.2026"
 * formatSwissDateTime("2026-08-15T10:30:00") → "15.08.2026, 10:30"
 *
 * Empty / null / unparseable values return the fallback (default: "–").
 */

export function formatSwissDate(value, fallback = "–") {
  if (!value || value === "-" || value === "–") return fallback;
  try {
    const d = value instanceof Date ? value : new Date(value);
    if (isNaN(d.getTime())) return String(value);
    return d.toLocaleDateString("de-CH", {
      day: "2-digit",
      month: "2-digit",
      year: "numeric",
    });
  } catch {
    return String(value);
  }
}

export function formatSwissDateTime(value, fallback = "–") {
  if (!value || value === "-" || value === "–") return fallback;
  try {
    const d = value instanceof Date ? value : new Date(value);
    if (isNaN(d.getTime())) return String(value);
    return d.toLocaleString("de-CH", {
      day: "2-digit",
      month: "2-digit",
      year: "numeric",
      hour: "2-digit",
      minute: "2-digit",
    });
  } catch {
    return String(value);
  }
}
