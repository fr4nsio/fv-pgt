<script>
    import { onMount } from 'svelte';
    import { writable } from 'svelte/store';
    import { fetchResourceDetails } from '../utils/showUtils.js';
    import VoltageRangeSpecificationDetails from './VoltageRangeSpecificationDetails.svelte';
    import CurrentRangeSpecificationDetails from './CurrentRangeSpecificationDetails.svelte';

    export let dcCurrentSystemId;

    const dcCurrentSystem = writable(null);

    async function fetchDcCurrentSystem() {
        const data = await fetchResourceDetails('/dc_current_system', `${dcCurrentSystemId}`);
        dcCurrentSystem.set(data);
    }

    onMount(() => {
        fetchDcCurrentSystem();
    });
</script>

<div class="object-details">
    <h3>DC (---)</h3>
    {#if $dcCurrentSystem}
        <ul>
            <CurrentRangeSpecificationDetails currentRangeId={$dcCurrentSystem.current_range_id} />
            <VoltageRangeSpecificationDetails voltageRangeId={$dcCurrentSystem.voltage_range_id} />
        </ul>
    {:else}
        <p>Caricamento dettagli sistema corrente...</p>
    {/if}
</div>
