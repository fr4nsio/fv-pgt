<script>
    import { onMount } from 'svelte';
    import { writable } from 'svelte/store';
    import NewOwner from './NewOwner.svelte';
    import { fetchResource } from '../utils/formUtils.js';
    import { submit } from '../utils/formUtils.js';

    const owners = writable([]);
    const plantModuleSystems = writable([]);
    const plantBatterySystems = writable([]);
    const plantProductions = writable([]);

    const newPlant = writable({
        name: '',
        owner_id: null,
        plant_module_system_id: null,
        plant_battery_system_id: null,
        plant_production_id: null,
    });

    onMount(async () => {
        await fetchOwners();
        await fetchPlantModuleSystems();
        await fetchPlantBatterySystems();
        await fetchPlantProductions();
    });

    async function fetchOwners() {
        const data = await fetchResource('/owner');
        owners.set(data);
    }

    async function fetchPlantModuleSystems() {
        const data = await fetchResource('/plant_module_system');
        plantModuleSystems.set(data);
    }

    async function fetchPlantBatterySystems() {
        const data = await fetchResource('/plant_battery_system');
        plantBatterySystems.set(data);
    }

    async function fetchPlantProductions() {
        const data = await fetchResource('/plant_production');
        plantProductions.set(data);
    }

    async function handleSubmit(event) {
        try {
            const result = await submit(event, '/plant', $newPlant);
            alert('Impianto creato con successo!');
        } catch (error) {
            alert('Errore crezione impianto: ' + error.message);
        }
    }

    const showNewOwnerForm = writable(false);
    function toggleNewOwnerForm() {
        showNewOwnerForm.update(value => !value);
    }

    // Function to handle the event when a new owner is created
    function handleOwnerCreated() {
        fetchOwners(); // Refresh the list of owners
    }
</script>

<div class="new-form">
    <h3>Nuovo impianto</h3>
    <form on:submit={handleSubmit}>
        <div>
            <label for="name">Nome impianto:</label>
            <input type="text" id="name" bind:value={$newPlant.name} required />
        </div>

        <div>
            <label for="owner">Proprietari:</label>
            <select id="owner" bind:value={$newPlant.owner_id} required>
                <option value="" disabled>Seleziona proprietario</option>
                {#each $owners as owner}
                    <option value={owner.id}>{owner.first_name} {owner.last_name}</option>
                {/each}
            </select>

            <button type="button" on:click={toggleNewOwnerForm}>
                {#if $showNewOwnerForm}
                    Nascondi
                {:else}
                    Nuovo Proprietario
                {/if}
            </button>

            {#if $showNewOwnerForm}
                <NewOwner on:ownerCreated={handleOwnerCreated} />
            {/if}
        </div>

        <div>
            <label for="plantModuleSystem">Select Plant Module System:</label>
            <select id="plantModuleSystem" bind:value={$newPlant.plant_module_system_id} required>
                <option value="" disabled>Sistema modulo impianto</option>
                {#each $plantModuleSystems as system}
                    <option value={system.id}>{system.id}</option>
                {/each}
            </select>
        </div>

        <div>
            <label for="plantBatterySystem">Select Plant Battery System:</label>
            <select id="plantBatterySystem" bind:value={$newPlant.plant_battery_system_id} required>
                <option value="" disabled>Sistema batteria impianto</option>
                {#each $plantBatterySystems as system}
                    <option value={system.id}>{system.id}</option>
                {/each}
            </select>
        </div>

        <div>
            <label for="plantBatterySystem">Selziona l'oggetto di produzione impianto:</label>
            <select id="plantBatterySystem" bind:value={$newPlant.plant_production_id} required>
                <option value="" disabled>Sistema batteria impianto</option>
                {#each $plantProductions as system}
                    <option value={system.id}>{system.id}</option>
                {/each}
            </select>
        </div>

        <button type="submit">Crea</button>
    </form>
</div>
