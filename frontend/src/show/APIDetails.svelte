<script>
    import { onMount, onDestroy } from 'svelte';
    import { writable } from 'svelte/store';
    import { fetchResource } from '../utils/formUtils.js';
    import { fetchResourceDetails } from '../utils/showUtils.js';

    const plantList = writable([]);
    let interval;
    let plantModuleSystemDetails = {};
    let plantBatterySystemDetails = {};
    let plantTokenDetails = {};
    let loading = true;

    async function fetchPlants()
    {
        const data = await fetchResource('/plant');  
        plantList.set(data);
    }

    async function fetchPlantModuleDetails(plantModuleSystemId)
    {
        return await fetchResourceDetails('/plant_module_system', `${plantModuleSystemId}`);
    }

    async function fetchPlantBatteryDetails(plantBatterySystemId)
    {
        return await fetchResourceDetails('/plant_battery_system', `${plantBatterySystemId}`);
    }

    async function fetchPlantTokenDetails(plantId)
    {
        // Vedere commento in prossima funzione.
        return await fetchResourceDetails('/token', `1`);
    }

    async function fetchAllPlantDetails()
    {
        loading = true;
        try {
            const plants = $plantList;

            for (let i = 0; i < plants.length; i++) {
                const plant = plants[i];
                if (!plantModuleSystemDetails[plant.id]) {
                    plantModuleSystemDetails[plant.id] = await fetchPlantModuleDetails(plant.plant_module_system_id);
                }
                if (!plantBatterySystemDetails[plant.id]) {
                    plantBatterySystemDetails[plant.id] = await fetchPlantBatteryDetails(plant.plant_battery_system_id);
                }

                // Per semplicità tutti gli impianti hanno lo stesso API token.
                // In realtà ci vorrebbe un token diverso per ogni impianto.
                if (!plantTokenDetails[plant.id]) {
                    plantTokenDetails[plant.id] = await fetchPlantTokenDetails(plant.id);
                }
            }

        } catch (error) {
            console.error('Error fetching plant details:', error);
        } finally {
            // Una volta caricati i dati non serve più la dicitura `loading`.
            loading = false;
        }
    }

    onMount(async () => {
        await fetchPlants();
        await fetchAllPlantDetails();

        interval = setInterval(() => {
            fetchPlants().then(fetchAllPlantDetails());
        }, 5000);
    });

    onDestroy(() => {
        clearInterval(interval);
    });
</script>

<h3>API</h3>
{#if $plantList.length > 0}
    <table>
        <thead>
            <tr>
                <th>Nome impianto</th>
                <th>UUID impianto</th>
<!--
                <th>UUID inverter</th>
                <th>UUID batterie</th>
-->
                <th>Marca inverter</th>
                <th>Marca batterie</th>
                <th>Token ID</th>
            </tr>
        </thead>
        <tbody>
            {#each $plantList as plant}
                <tr>
                    <td>{plant?.name || 'Loading...'}</td>
                    <td>{plant?.uuid || 'Loading...'}</td>
<!--
                    <td>{plantModuleSystemDetails[plant.id]?.uuid}</td>
                    <td>{plantBatterySystemDetails[plant.id]?.uuid}</td>
-->
                    <td>{plantModuleSystemDetails[plant.id]?.make}</td>
                    <td>{plantBatterySystemDetails[plant.id]?.make}</td>
                    <td>{plantTokenDetails[plant.id]?.api_token}</td>
                </tr>
            {/each}
        </tbody>
    </table>
{:else}
    <p>Caricamento...</p>
{/if}
