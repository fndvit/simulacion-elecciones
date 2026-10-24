<script lang="ts">
  import '../app.css';
  import App from '$lib/components/App.svelte';
  let { children } = $props();
</script>

<!-- one persistent shell for /, /simula and /escenarios, so switching views animates instead of reloading -->
<App />
{@render children()}
