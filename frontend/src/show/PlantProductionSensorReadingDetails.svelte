<script>
    import { onMount, onDestroy } from 'svelte';
    import { writable } from 'svelte/store';
    import { fetchResourceDetails } from '../utils/showUtils.js';

    export let plantProductionId;

    const plantProductionDetails = writable({ daily_power: null, monthly_power: null });

    async function fetchPlantProductionDetails() {
        const data = await fetchResourceDetails('/plant_production', `${plantProductionId}`);
        plantProductionDetails.set({ daily_power: data.daily_kwh, monthly_power: data.monthly_kwh });
    }

    let interval;

    // Aggiorna lo stato dopo che l'utente cambia impianto da visualizzare.
    $: if (plantProductionId) {
        fetchPlantProductionDetails();
        clearInterval(interval);
        interval = setInterval(fetchPlantProductionDetails, 5000);
    }

    onDestroy(() => {
        clearInterval(interval);
    })

    onMount(async () => {
        await fetchPlantProductionDetails();
        return () => clearInterval(interval);
    });
</script>

<div class="object-details">
    {#if $plantProductionDetails && $plantProductionDetails.daily_power !== null && $plantProductionDetails.monthly_power !== null}
        <h3>Valori istantanei</h3>
        <div class="object-details">
            <ul>
                <li><strong>Potenza giornaliera (kWh):</strong> {$plantProductionDetails.daily_power.toFixed(2)}</li>
                <li><strong>Potenza mensile (kWh):</strong> {$plantProductionDetails.monthly_power.toFixed(2)}</li>
            </ul>
        </div>
    {:else}
        <p>Caricamento dettagli produzione impianto...</p>
    {/if}
</div>
