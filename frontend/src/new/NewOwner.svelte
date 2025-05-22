<script>
    import { writable } from 'svelte/store';
    import { createEventDispatcher } from 'svelte';
    import { submit } from '../utils/formUtils.js';

    const newOwner = writable({
        first_name: '',
        last_name: '',
    });

    const dispatch = createEventDispatcher();

    async function handleSubmit(event) {
        event.preventDefault(); // Prevent default form submission

        try {
            const result = await submit(event, '/owner', $newOwner);
            alert('Proprietario creato con successo! Selezionalo dalla lista dei proprietari');
            dispatch('ownerCreated'); // Dispatch the event to notify the parent
            // Optionally reset the form or perform other actions with the result
            newOwner.set({ first_name: '', last_name: '' }); // Reset the form
        } catch (error) {
            alert('Errore creazione proprietario: ' + error.message);
        }
    }
</script>

<div class="new-form">
    <form on:submit={handleSubmit}>
        <h3>Nuovo Proprietario</h3>
        <div>
            <label for="first_name">Nome:</label>
            <input type="text" id="first_name" bind:value={$newOwner.first_name} required />
        </div>
        <div>
            <label for="last_name">Cognome:</label>
            <input type="text" id="last_name" bind:value={$newOwner.last_name} required />
        </div>
        <button type="submit">Crea</button>
    </form>
</div>

