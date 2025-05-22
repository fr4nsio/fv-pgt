<script>
    import { onMount } from 'svelte';
    import { writable } from 'svelte/store';
    import { fetchResourceDetails } from '../utils/showUtils.js'

    export let dailyPowerRangeId;

    const dailyPowerRangeDetails = writable(null);

    async function fetchDailyPowerRangeDetails() {
        const data = await fetchResourceDetails('/daily_power_range', `${dailyPowerRangeId}`);        
        dailyPowerRangeDetails.set(data);
    }

    // Aggiorna lo stato dopo che l'utente cambia impianto da visualizzare. 
    $: if (dailyPowerRangeId) {
        fetchDailyPowerRangeDetails();
    }

    onMount(() => {
        fetchDailyPowerRangeDetails();
    });
</script>

{#if $dailyPowerRangeDetails}
    <li><strong>Range giornaliero potenza (kWh):</strong> {$dailyPowerRangeDetails.lower.toFixed(2)} - {$dailyPowerRangeDetails.upper.toFixed(2)}</li>
{:else}
    <li>Caricamento range giornaliero potenza...</li>
{/if}
