export function mediaUrl(value) {
  if (!value) return '';

  try {
    const parsed = new URL(value, window.location.origin);
    return `${parsed.pathname}${parsed.search}${parsed.hash}`;
  } catch {
    return value;
  }
}
