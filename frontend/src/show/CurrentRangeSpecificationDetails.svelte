<script>
    import { onMount } from 'svelte';
    import { writable } from 'svelte/store';

    export let currentRangeId; // This will be passed as a prop

    const currentRange = writable(null);

    // Function to fetch current range details
    async function fetchCurrentRange() {
        try {
            const response = await fetch(`/current_range/${currentRangeId}`);
            if (!response.ok) {
                throw new Error('Network response was not ok');
            }
            const data = await response.json();
            currentRange.set(data);
        } catch (error) {
            console.error('Error fetching current range details:', error);
        }
    }

    // Fetch current range details on component mount
    onMount(() => {
        fetchCurrentRange();
    });
</script>

{#if $currentRange}
    <li><strong>Current range (A):</strong> {$currentRange.lower.toFixed(2)} - {$currentRange.upper.toFixed(2)}</li>
{:else}
    <li>Loading current range details...</li>
{/if}
