<script>
    import { onMount } from 'svelte';
    import { writable } from 'svelte/store';
    import { fetchResourceDetails } from '../utils/showUtils.js'

    export let monthlyPowerRangeId;

    const monthlyPowerRangeDetails = writable(null);

    async function fetchMonthlyPowerRangeDetails() {
        const data = await fetchResourceDetails('/monthly_power_range', `${monthlyPowerRangeId}`);        
        monthlyPowerRangeDetails.set(data);                                                 
    }

    // Aggiorna lo stato dopo che l'utente cambia impianto da visualizzare. 
    $: if (monthlyPowerRangeId) {
        fetchMonthlyPowerRangeDetails();
    }

    onMount(() => {
        fetchMonthlyPowerRangeDetails();
    });
</script>

{#if $monthlyPowerRangeDetails}
    <li><strong>Monthly power range (kWh):</strong> {$monthlyPowerRangeDetails.lower.toFixed(2)} - {$monthlyPowerRangeDetails.upper.toFixed(2)}</li>
{:else}
    <li>Loading monthly power range details...</li>
{/if}
