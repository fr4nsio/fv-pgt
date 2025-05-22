<script>
    import { onMount } from 'svelte';
    import { writable } from 'svelte/store';
    import { fetchResourceDetails } from '../utils/showUtils.js';
    import DailyPowerRangeDetails from './DailyPowerRangeDetails.svelte';
    import MonthlyPowerRangeDetails from './MonthlyPowerRangeDetails.svelte';
    import PlantProductionChart from '../charts/PlantProductionChart.svelte';
    import PlantProductionSensorReading from './PlantProductionSensorReadingDetails.svelte';

    export let plantProductionId;

    const plantProductionDetails = writable(null);
    let showRangeDetails = false;

    async function fetchPlantProductionDetails() {
        const data = await fetchResourceDetails('/plant_production', `${plantProductionId}`);
        plantProductionDetails.set(data);
    }

    // Aggiorna lo stato dopo che l'utente cambia impianto da visualizzare. 
    $: if (plantProductionId) {
        fetchPlantProductionDetails(plantProductionId);
    }

    onMount(() => {
        fetchPlantProductionDetails();
    });

    // Fai vedere i range.
    function toggleRangeDetails() {
        showRangeDetails = !showRangeDetails;
    }
</script>

<div class="object-details">
    {#if $plantProductionDetails}
        <h3>Dati Produzione Impianto</h3>

        <PlantProductionSensorReading plantProductionId={plantProductionId} />

        <br />

        <!--
        <button on:click={toggleRangeDetails}>                                 
            {showRangeDetails ? 'Nascondi' : 'Espandi'}                        
        </button>
        -->

        {#if showRangeDetails}
            <div class="object-details">
                <h3>Range</h3>
                <div class="object-details">
                    <DailyPowerRangeDetails dailyPowerRangeId={$plantProductionDetails.daily_power_range_id} />
                    <MonthlyPowerRangeDetails monthlyPowerRangeId={$plantProductionDetails.monthly_power_range_id} />
                </div>
            </div>
        {/if}

        <PlantProductionChart {plantProductionId} />
    {:else}
        <p>Caricamento dettagli produzione impianto...</p>
    {/if}
</div>
