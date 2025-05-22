<script>
    import { onMount } from 'svelte';
    import { writable } from 'svelte/store';
    import { fetchResourceDetails } from '../utils/showUtils.js';
    import VoltageRangeSpecificationDetails from './VoltageRangeSpecificationDetails.svelte';
    import CurrentRangeSpecificationDetails from './CurrentRangeSpecificationDetails.svelte';
    import FrequencyRangeSpecificationDetails from './FrequencyRangeSpecificationDetails.svelte';

    export let acCurrentSystemId; // This will be passed as a prop

    const acCurrentSystem = writable(null);

    // Function to fetch current system details
    async function fetchAcCurrentSystem() {
        const data = await fetchResourceDetails('/ac_current_system', `${acCurrentSystemId}`);
        acCurrentSystem.set(data);
    }

    onMount(() => {
        fetchAcCurrentSystem();
    });
</script>

<div class="object-details">
    <h3>AC (~)</h3>
    {#if $acCurrentSystem}
        <ul>
            <CurrentRangeSpecificationDetails currentRangeId={$acCurrentSystem.current_range_id} />
            <VoltageRangeSpecificationDetails voltageRangeId={$acCurrentSystem.voltage_range_id} />
            <FrequencyRangeSpecificationDetails frequencyRangeId={$acCurrentSystem.frequency_range_id} />
        </ul>
    {:else}
        <p>Loading current system details...</p>
    {/if}
</div>
