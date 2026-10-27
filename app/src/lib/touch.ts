// Tooltips on phones. With a mouse a tooltip follows the pointer and goes when it leaves; with a finger there
// is no hover: a tap (or a drag on the line chart) opens it, and it stays until the reader taps elsewhere or
// scrolls. On narrow screens the tooltip docks to the width of its box instead of floating beside the
// finger, so it can never stick out of the page.

export const isTouch = (e: PointerEvent) => e.pointerType === 'touch' || e.pointerType === 'pen';

/** Svelte action: call `close` when the reader touches outside `node` or scrolls the page away (small shifts,
 *  like the layout settling after a tap selects a province, don't count) */
export function dismiss(node: Element, close: () => void) {
  let fn = close, y0 = 0, t0 = 0;
  const down = (e: PointerEvent) => { y0 = window.scrollY; t0 = Date.now(); if (!node.contains(e.target as Node)) fn(); };
  const scroll = () => {
    if (Date.now() - t0 < 800) { y0 = window.scrollY; return; }   // the page reflowing right after the tap
    if (Math.abs(window.scrollY - y0) > 60) fn();
  };
  document.addEventListener('pointerdown', down, true);
  window.addEventListener('scroll', scroll, { passive: true });
  return {
    update(c: () => void) { fn = c; },
    destroy() { document.removeEventListener('pointerdown', down, true); window.removeEventListener('scroll', scroll); }
  };
}

export const NARROW = 560;

/** inline style for a tooltip at (x, y) inside a box w × h wide. Wide boxes: beside the pointer, flipped near
 *  the right edge. Narrow boxes: docked to the box's width, below the finger in the upper half, above it in
 *  the lower half. */
export function tipStyle(x: number, y: number, w: number, h: number, tipW = 272): string {
  if (w < NARROW) {
    const below = y < h * 0.55;
    return `left:8px;right:8px;width:auto;max-width:none;top:${y}px;transform:translateY(${below ? '22px' : 'calc(-100% - 22px)'})`;
  }
  const flip = x > w - tipW - 16;
  return `left:${x}px;top:${y}px;transform:translate(${flip ? 'calc(-100% - 14px)' : '14px'}, 12px)`;
}
