<script>
    import { onMount } from 'svelte';
    import { writable } from 'svelte/store';
    import { fetchResourceDetails } from '../utils/showUtils';

    export let frequencyRangeId;

    const frequencyRange = writable(null);

    // Function to fetch frequency range details
    async function fetchFrequencyRange() {
        const data = await fetchResourceDetails('/frequency_range', frequencyRangeId);
        frequencyRange.set(data);
    }

    onMount(() => {
        fetchFrequencyRange();
    });
</script>

{#if $frequencyRange}
    <li><strong>Range frequenza (Hz):</strong> {$frequencyRange.lower.toFixed(2)} - {$frequencyRange.upper.toFixed(2)}</li>
{:else}
    <li>Caricamento dettagli range frequenza...</li>
{/if}
