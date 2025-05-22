<script>
    import { onMount } from 'svelte';
    import { writable } from 'svelte/store';
    import { fetchResourceDetails } from '../utils/showUtils.js';

    export let ownerId;

    const owner = writable(null);

    async function fetchOwnerDetails() {
        const data = await fetchResourceDetails('/owner', `${ownerId}`);
        owner.set(data);
    }

    // Aggiorna lo stato dopo che l'utente cambia impianto da visualizzare. 
    $: if (ownerId) {
        fetchOwnerDetails();
    }

    onMount(() => {
        fetchOwnerDetails();
    });
</script>

<div class="object-details">
    <h3>Proprietario</h3>
    {#if $owner}
        <ul>
            <li><strong>Nome:</strong> {$owner.first_name}</li>
            <li><strong>Cognome:</strong> {$owner.last_name}</li>
        </ul>
    {:else}
        <p>Caricamento dettagli proprietario...</p>
    {/if}
</div>
