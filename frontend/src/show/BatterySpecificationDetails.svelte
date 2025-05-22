<script>
    import { onMount } from 'svelte';
    import { writable } from 'svelte/store';
    import { fetchResourceDetails } from '../utils/showUtils';
    import VoltageRangeSpecificationDetails from './VoltageRangeSpecificationDetails.svelte'; // Import the VoltageRangeSpecificationDetails component
    import CurrentRangeSpecificationDetails from './CurrentRangeSpecificationDetails.svelte'; // Import the VoltageRangeSpecificationDetails component

    // Props passati dal componente padre.
    export let batterySpecificationId;
    export let showRangeDetails;
    export let showCapacity;

    const batterySpecification = writable(null);

    async function fetchBatterySpecification() {                                        
        const data = await fetchResourceDetails('/battery_specification', batterySpecificationId);
        batterySpecification.set(data);
    }

    // Aggiorna lo stato dopo che l'utente cambia impianto da visualizzare.     
    $: if (batterySpecificationId) {                                                        
        fetchBatterySpecification();                                                       
    }

    onMount(async () => {
        fetchBatterySpecification();
    });
</script>

{#if $batterySpecification}
    <!--
        <li><strong>Tipo:</strong> {$batterySpecification.type}</li>
    -->
    {#if showCapacity}
        <li><strong>Capacità:</strong> {$batterySpecification.capacity.toFixed(2)}</li>
    {/if}

    {#if showRangeDetails}
        <div class="object-details">
            <h3>Range</h3>
            <div class="object-details">
                <CurrentRangeSpecificationDetails currentRangeId={$batterySpecification.current_range_id} />
                <VoltageRangeSpecificationDetails voltageRangeId={$batterySpecification.voltage_range_id} />
            </div>
        </div>
    {/if}
{:else}
    <p>Caricamento specifiche batteria...</p>
{/if}
