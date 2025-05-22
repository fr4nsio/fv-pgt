<script>
    import { onMount } from 'svelte';
    import { writable } from 'svelte/store';

    export let voltageRangeId; // This will be passed as a prop

    const voltageRange = writable(null);

    async function fetchVoltageRange() {
        const data = await fetchResourceDetails('/voltage_range', `${voltageRangeId}`);
        voltageRange.set(data);
    }

    // Aggiorna lo stato dopo che l'utente cambia impianto da visualizzare. 
    $: if (voltageRange) {
        fetchVoltageRange();
    }

    onMount(() => {
        fetchVoltageRange();
    });
</script>

{#if $voltageRange}
    <li><strong>Range voltaggio (V):</strong> {$voltageRange.lower.toFixed(2)} - {$voltageRange.upper.toFixed(2)}</li>
{:else}
    <li>Caricamento range voltaggio...</li>
{/if}
