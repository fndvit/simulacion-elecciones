<script lang="ts">
  import '../app.css';
  import App from '$lib/components/App.svelte';
  import Footer from '$lib/components/Footer.svelte';
  let { children } = $props();
</script>

<!-- one persistent shell for /, /simula and /escenarios, so switching views animates instead of reloading;
     /metodologia and /quienes-somos render their own content below the bar -->
<App />
{@render children()}
<Footer />
