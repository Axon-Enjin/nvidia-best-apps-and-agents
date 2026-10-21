import assert from "node:assert/strict";
import { readFileSync } from "node:fs";
import { test } from "node:test";

// Contrast is measured from the real theme so a token change cannot slip past.
const css = readFileSync(new URL("./globals.css", import.meta.url), "utf8");
const theme = css.slice(css.indexOf("@theme"));
const tokens = new Map([...theme.matchAll(/--color-([a-z-]+):\s*(#[0-9a-fA-F]{6})\s*;/g)].map((m) => [m[1], m[2]]));

function color(name: string): string {
  if (name === "white") return "#FFFFFF";
  const value = tokens.get(name);
  assert.ok(value, `missing token --color-${name}`);
  return value;
}

function luminance(hex: string): number {
  const channel = (offset: number) => {
    const value = parseInt(hex.slice(offset, offset + 2), 16) / 255;
    return value <= 0.04045 ? value / 12.92 : ((value + 0.055) / 1.055) ** 2.4;
  };
  return 0.2126 * channel(1) + 0.7152 * channel(3) + 0.0722 * channel(5);
}

function contrast(a: string, b: string): number {
  const [light, dark] = [luminance(color(a)), luminance(color(b))].sort((x, y) => y - x) as [number, number];
  return (light + 0.05) / (dark + 0.05);
}

const TEXT: [string, string][] = [
  ["ink", "paper"], ["ink", "surface"], ["ink-muted", "paper"], ["ink-muted", "surface"],
  ["white", "forest"], ["white", "teal"], ["passed", "passed-tint"], ["attention", "attention-tint"],
  ["blocking", "blocking-tint"], ["ink", "highlight"], ["forest", "paper"], ["teal", "surface"],
];
const UI: [string, string][] = [["teal", "paper"], ["teal", "surface"], ["rule", "paper"], ["rule", "surface"]];

for (const [foreground, background] of TEXT) {
  test(`text ${foreground} on ${background} meets 4.5:1`, () => {
    assert.ok(contrast(foreground, background) >= 4.5, `${contrast(foreground, background).toFixed(2)}:1`);
  });
}

for (const [foreground, background] of UI) {
  test(`indicator ${foreground} on ${background} meets 3:1`, () => {
    assert.ok(contrast(foreground, background) >= 3, `${contrast(foreground, background).toFixed(2)}:1`);
  });
}
