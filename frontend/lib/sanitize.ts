/**
 * Minimal HTML sanitizer for rich-text content produced by TipTap.
 * Strips scripts, iframes and event handlers; keeps safe formatting tags.
 * For server-rendered output from admins only — not for untrusted user input.
 */

export function sanitizeHtml(html: string): string {
  if (!html) return "";

  let safe = html
    // Remove <script> blocks
    .replace(/<script\b[^<]*(?:(?!<\/script>)<[^<]*)*<\/script>/gi, "")
    // Remove <iframe> blocks
    .replace(/<iframe\b[^<]*(?:(?!<\/iframe>)<[^<]*)*<\/iframe>/gi, "")
    // Remove on* event attributes (onclick, onload, etc.)
    .replace(/\s+on\w+\s*=\s*(?:"[^"]*"|'[^']*'|[^\s>]+)/gi, "")
    // Remove javascript: URLs in href / src
    .replace(/(href|src)\s*=\s*["']?\s*javascript:[^"'\s>]*/gi, '$1="#"');

  return safe;
}
