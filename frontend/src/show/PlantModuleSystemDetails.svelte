<script>
    import { onMount, onDestroy } from 'svelte';
    import { writable } from 'svelte/store';
    import { fetchResourceDetails } from '../utils/showUtils.js';
    import DcCurrentSystemDetails from './DcCurrentSystemDetails.svelte';
    import AcCurrentSystemDetails from './AcCurrentSystemDetails.svelte';
    import PlantModuleSystemSensorReadingsDetails from './PlantModuleSystemSensorReadingsDetails.svelte';
    import PlantModuleSystemSensorReadingsChart from '../charts/PlantModuleSystemSensorReadingsChart.svelte';

    // Passato come prop.
    export let plantModuleSystemId;

    let showRangeDetails = false;

    const plantModuleSystem = writable(null);

    async function fetchPlantModuleSystem() {
        const data = await fetchResourceDetails('/plant_module_system', `${plantModuleSystemId}`);
        plantModuleSystem.set(data);
    }

    // Aggiorna lo stato dopo che l'utente cambia impianto da visualizzare.    
    $: if (plantModuleSystemId) {
        fetchPlantModuleSystem();
    }

    onMount(async () => {
        // Aspetta di avere tutti i dati di base prima di prendere le letture.
        await fetchPlantModuleSystem();
    });

    // Fai vedere i range.
    function toggleRangeDetails() {
        showRangeDetails = !showRangeDetails;
    }
</script>

<div class="object-details">
    <h3>Sistema Modulo Impianto</h3>
    {#if $plantModuleSystem}
        {#if $plantModuleSystem.plant_id}
            <PlantModuleSystemSensorReadingsDetails plantId={$plantModuleSystem.plant_id} />
        {/if}

        <br />

        <!--
        <button on:click={toggleRangeDetails}>
            {showRangeDetails ? 'Nascondi' : 'Espandi'}
        </button>
        -->

        {#if showRangeDetails}
            <div class="object-details">
                <h3>Range</h3>
                <ul>
                    <li>
                        {#if $plantModuleSystem.ac_current_id}
                            <AcCurrentSystemDetails acCurrentSystemId={$plantModuleSystem.ac_current_id} />
                        {/if}                                                       
                    </li>
                    <li>
                        {#if $plantModuleSystem.dc_current_id}
                            <DcCurrentSystemDetails dcCurrentSystemId={$plantModuleSystem.dc_current_id} />
                        {/if}
                    </li>
                </ul>
            </div>
        {/if}

        <PlantModuleSystemSensorReadingsChart plantId={$plantModuleSystem.plant_id} />
    {:else}
        <p>Caricamento dettagli sistema modulo impianto...</p>
    {/if}
</div>
