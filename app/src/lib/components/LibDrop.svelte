<script lang="ts" generics="T extends string | number">
  // An inline madlib dropdown: a highlighted word that opens a listbox of options.
  // Follows the WAI-ARIA listbox-popup pattern — the trigger is a button with
  // aria-haspopup/aria-expanded, the menu is role="listbox" with role="option"
  // children, and the arrow keys / Home / End / Enter / Escape all work.
  //
  // With `filter`, the menu grows a search box at the top and becomes a combobox:
  // typing narrows the options, arrows move a highlight, Enter picks it. Focus
  // stays in the search box (options are highlighted, not focused).
  let { value = $bindable(), options, label, filter = false }:
    { value: T; options: { value: T; label: string; ct?: string }[]; label?: string; filter?: boolean } = $props();

  let open = $state(false);
  let active = $state(-1); // highlighted (focused/marked) option while open
  let query = $state('');
  let el: HTMLSpanElement;
  let triggerEl: HTMLButtonElement;
  let inputEl: HTMLInputElement | undefined;
  let optEls: HTMLDivElement[] = [];

  const norm = (s: string) => s.normalize('NFD').replace(/[̀-ͯ]/g, '').toLowerCase();
  const shown = $derived(filter && query.trim() ? options.filter((o) => norm(o.label).includes(norm(query))) : options);

  const current = $derived(options.find((o) => o.value === value)?.label ?? String(value));
  const selectedIndex = $derived(Math.max(0, shown.findIndex((o) => o.value === value)));

  function openMenu(to: 'selected' | 'first' | 'last' = 'selected') {
    query = '';
    active = filter ? -1 : to === 'first' ? 0 : to === 'last' ? options.length - 1 : selectedIndex;
    open = true;
  }
  function closeMenu(returnFocus = true) {
    open = false; active = -1; query = '';
    if (returnFocus) triggerEl?.focus();
  }
  function pick(v: T) { value = v; closeMenu(); }

  // filter mode: keep focus in the search box, scroll the highlight into view;
  // plain mode: move DOM focus onto the highlighted option
  $effect(() => { if (open && filter && inputEl) inputEl.focus(); });
  $effect(() => {
    if (!open || active < 0 || !optEls[active]) return;
    if (filter) optEls[active].scrollIntoView({ block: 'nearest' });
    else optEls[active].focus();
  });

  function onTriggerKey(e: KeyboardEvent) {
    if (e.key === 'ArrowDown' || e.key === 'Enter' || e.key === ' ') { e.preventDefault(); openMenu('selected'); }
    else if (e.key === 'ArrowUp') { e.preventDefault(); openMenu('last'); }
  }
  function onSearchKey(e: KeyboardEvent) {
    switch (e.key) {
      case 'ArrowDown': e.preventDefault(); active = Math.min((active < 0 ? -1 : active) + 1, shown.length - 1); break;
      case 'ArrowUp': e.preventDefault(); active = Math.max(active - 1, 0); break;
      case 'Enter': e.preventDefault(); if (shown[active]) pick(shown[active].value); break;
      case 'Escape': e.preventDefault(); closeMenu(); break;
    }
  }
  function onOptionKey(e: KeyboardEvent, i: number) {
    switch (e.key) {
      case 'ArrowDown': e.preventDefault(); active = (i + 1) % shown.length; break;
      case 'ArrowUp': e.preventDefault(); active = (i - 1 + shown.length) % shown.length; break;
      case 'Home': e.preventDefault(); active = 0; break;
      case 'End': e.preventDefault(); active = shown.length - 1; break;
      case 'Enter': case ' ': e.preventDefault(); pick(shown[i].value); break;
      case 'Escape': e.preventDefault(); closeMenu(); break;
      case 'Tab': closeMenu(false); break; // let focus move on, but shut the menu
    }
  }

  $effect(() => {
    if (!open) return;
    const onDoc = (e: MouseEvent) => { if (!el.contains(e.target as Node)) closeMenu(false); };
    window.addEventListener('click', onDoc);
    return () => window.removeEventListener('click', onDoc);
  });
</script>

<span class="drop" bind:this={el}>
  <button
    class="word"
    bind:this={triggerEl}
    aria-haspopup="listbox"
    aria-expanded={open}
    aria-label={label}
    onclick={(e) => { e.stopPropagation(); open ? closeMenu(false) : openMenu('selected'); }}
    onkeydown={onTriggerKey}
  >
    {current}<span class="chev" aria-hidden="true">▾</span>
  </button>
  {#if open}
    <div class="menu" role="listbox" aria-label={label}>
      {#if filter}
        <input
          class="search" type="text" bind:this={inputEl} bind:value={query}
          placeholder="Buscar…" aria-label={label ? `Buscar ${label}` : 'Buscar'}
          autocomplete="off" spellcheck="false"
          onkeydown={onSearchKey} oninput={() => (active = 0)}
        />
      {/if}
      <div class="opts">
        {#each shown as o, i}
          <div
            class="opt"
            class:on={o.value === value}
            class:hl={filter && i === active}
            role="option"
            aria-selected={o.value === value}
            tabindex="-1"
            bind:this={optEls[i]}
            onclick={() => pick(o.value)}
            onkeydown={(e) => onOptionKey(e, i)}
          >{o.label}{#if o.ct}<span class="ct">{o.ct}</span>{/if}</div>
        {/each}
        {#if filter && shown.length === 0}<div class="noopt">Sin resultados</div>{/if}
      </div>
    </div>
  {/if}
</span>

<style>
  .drop { position: relative; display: inline-block; }
  .word {
    display: inline-flex; align-items: center; gap: 8px; text-align: left;
    font: inherit; font-family: var(--font-ui); font-weight: 300; cursor: pointer; border: 0; border-radius: var(--radius);
    background: var(--highlight); color: var(--hl-ink); padding: 4px 12px;
    -webkit-backdrop-filter: blur(6px); backdrop-filter: blur(6px);
  }
  .word:focus-visible { outline: 2px solid var(--fg); outline-offset: 2px; }
  .chev { font-size: 12px; opacity: 0.75; }
  .menu {
    position: absolute; top: calc(100% + 4px); left: 0; z-index: 20;
    display: flex; flex-direction: column; min-width: 100%;
    border-radius: var(--radius); overflow: hidden;
    box-shadow: 0 3px 16px rgba(0, 0, 0, 0.12);
  }
  .opts { display: flex; flex-direction: column; overflow-y: auto; }
  .search {
    font: inherit; border: 0; border-bottom: 1px solid var(--line);
    padding: 6px 12px; background: var(--menu); color: var(--fg); font-family: var(--font-ui);
    -webkit-backdrop-filter: blur(6px); backdrop-filter: blur(6px);
  }
  .search:focus { outline: none; }
  .opt {
    font: inherit; font-family: var(--font-ui); font-weight: 300; text-align: left; white-space: nowrap; cursor: pointer;
    padding: 4px 12px;
    background: var(--menu); color: var(--muted);
    -webkit-backdrop-filter: blur(6px); backdrop-filter: blur(6px);
  }
  .opt.on { background: var(--highlight); color: var(--hl-ink); }
  .ct { margin-left: 14px; float: right; font-size: 0.75em; opacity: 0.7; font-variant-numeric: tabular-nums; }
  .opt:hover, .opt.hl { color: var(--hl-ink); }
  .opt:focus { outline: none; }
  .opt:focus-visible, .opt:focus, .opt.hl { background: var(--highlight); color: var(--hl-ink); }
  .noopt {
    font: inherit; padding: 6px 12px; color: var(--muted);
    background: var(--menu);
  }
</style>
