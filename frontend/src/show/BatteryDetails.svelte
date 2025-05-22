<script>
    import { onMount } from 'svelte';
    import { writable } from 'svelte/store';
    import BatterySpecification from './BatterySpecificationDetails.svelte';
    import PlantBatterySystemSensorReading from './PlantBatterySystemSensorReadingDetails.svelte';

    // Passato come prop.
    export let batteryIds;

    let showRangeDetails = false;

    const batteries = writable([]);
    let selectedBatteryId = null;

    // Function to fetch battery details
    async function fetchBatteries() {
        try {
            const response = await fetch('/battery');
            if (!response.ok) {
                throw new Error('Network response was not ok');
            }
            const data = await response.json();

            // Filter batteries based on the provided battery IDs.
            const filteredBatteries = data.filter(battery => batteryIds.includes(battery.id));

            batteries.set(filteredBatteries);
        } catch (error) {
            console.error('Error fetching battery details:', error);
        }
    }

    // Aggiorna lo stato dopo che l'utente cambia impianto da visualizzare. 
    $: if (batteryIds) {
        fetchBatteries();
    }

    onMount(async () => {
        await fetchBatteries();
    });

    // Fai vedere i range.              
    function toggleRangeDetails() {
        showRangeDetails = !showRangeDetails;
    }
</script>

<div class="object-details">
    <h3>Batterie</h3>
    {#if $batteries.length > 0}

        <!--
        <button on:click={toggleRangeDetails}>
            {showRangeDetails ? 'Nascondi' : 'Espandi'}
        </button>
        -->

        <ul>
            {#each $batteries as battery}

                <div class="object-details">
                    <li><strong>Nome:</strong> {battery.name}</li>

                    <BatterySpecification
                         batterySpecificationId={battery.battery_specification_id}
                         showRangeDetails={showRangeDetails}
                         showCapacity={battery.name === 'Modulo BMS (Master)'}
                    />

                    <PlantBatterySystemSensorReading batteryId={battery.id} />
                </div>
            {/each}
        </ul>
    {:else}
        <p>Batterie non trovate</p>
    {/if}
</div>
