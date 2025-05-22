<script>
    import { onMount, onDestroy } from 'svelte';
    import { writable } from 'svelte/store';
    import NewPlant from '../new/NewPlant.svelte';
    import PlantModuleSystemDetails from './PlantModuleSystemDetails.svelte';
    import PlantBatterySystemDetails from './PlantBatterySystemDetails.svelte';
    import PlantProductionDetails from './PlantProductionDetails.svelte';
    import OwnerDetails from './OwnerDetails.svelte';
    import AlarmDetails from './AlarmDetails.svelte';
    import APIDetails from './APIDetails.svelte';
    import TicketDetails from './TicketDetails.svelte';
    import { fetchResource } from '../utils/formUtils.js';
    import { fetchResourceDetails } from '../utils/showUtils.js';

    // Store to hold plant details and list of plants
    const plantDetails = writable(null);
    const plantList = writable([]);
    const selectedPlantId = writable(null);

    // Vista attuale.
    const currentView = writable(null);

    let showNewPlant = false; // State to control visibility of the form

    function showAlarms()
    {
        currentView.set('alarms');
    }

    function showTickets()
    {
        currentView.set('tickets');
    }

    function showAPI()
    {
        currentView.set('api');
    }

    // Function to toggle the visibility of the NewPlant
    function toggleNewPlant() {
        showNewPlant = !showNewPlant; // Toggle the form visibility
    }

    // Function to fetch all plants
    async function fetchPlants() {
        const data = await fetchResource('/plant');
        plantList.set(data);
    }

    async function fetchPlantDetails(plantId) {
        const data = await fetchResourceDetails('/plant', `${plantId}`);
        plantDetails.set(data);
    }

    // Fetch all plants on component mount
    let interval;

    onMount(() => {
        interval = setInterval(fetchPlants, 5000);
        fetchPlants();
    });

    onDestroy(() => {
        clearInterval(interval);
    });

    // Function to handle plant selection
    function selectPlant(plantId) {
        /* Resetta la vista corrente: fai in modo che gli impianti possano
         * essere selezionati.
         */
        currentView.set(null);

        selectedPlantId.set(plantId);
        fetchPlantDetails(plantId);
    }
</script>

<style>
    /* Basic styling for layout */
    .container {
        display: flex;
    }

    .sidebar {
        width: 200px;
        padding: 20px;
        border-right: 1px solid var(--sidebar-border-color, #ccc);
        background-color: var(--sidebar-background-color, #ffffff); /* Light background for sidebar */
    }

    .main-content {
        padding: 20px;
        flex-grow: 1;
        background-color: var(--main-background-color, #ffffff); /* Light background for main content */
        color: var(--main-text-color, #213547); /* Dark text color for light mode */
    }

    .plant-item {
        cursor: pointer;
        margin: 5px 0;
        background: none;
        border: none;
        color: var(--plant-item-text-color, black); /* Default text color */
        text-align: left;
        padding: 5px;
        width: 100%;
        transition: background 0.2s;
    }

    .plant-item:hover {
        background: var(--plant-item-hover-background, #f0f0f0); /* Light hover background */
    }

    /* Dark mode styles */
    @media (prefers-color-scheme: dark) {
        .sidebar {
            border-right: 1px solid #444; /* Darker border for sidebar */
            background-color: #242424; /* Dark background for sidebar */
        }

        .main-content {
            background-color: #121212; /* Dark background for main content */
            color: rgba(255, 255, 255, 0.87); /* Light text color for dark mode */
        }

        .plant-item {
            color: white; /* Light text color for plant items */
        }

        .plant-item:hover {
            background: #333; /* Darker hover background */
        }
    }

    /* Light mode styles */
    @media (prefers-color-scheme: light) {
        .sidebar {
            border-right: 1px solid #ccc; /* Light border for sidebar */
            background-color: #ffffff; /* Light background for sidebar */
        }

        .main-content {
            background-color: #ffffff; /* Light background for main content */
            color: #213547; /* Dark text color for light mode */
        }

        .plant-item {
            color: black; /* Dark text color for plant items */
        }

        .plant-item:hover {
            background: #f0f0f0; /* Light hover background */
        }
    }
</style>

<div class="container">

    <button on:click={toggleNewPlant}>
        {showNewPlant ? 'Annulla' : 'Nuovo Impianto (+)'}
    </button>
    
    {#if showNewPlant}
        <NewPlant />
    {:else}
        <div class="sidebar">
            <h3>Impianti</h3>
            {#if $plantList.length > 0}
                {#each $plantList as plant}
                    <button class="plant-item" on:click={() => selectPlant(plant.id)}>
                        {plant.name}
                    </button>
                {/each}
            {:else}
                <p>Loading plants...</p>
            {/if}
            <h3>Gestione</h3>
            <button class="plant-item" on:click={showAlarms}>Allarmi</button>
            <button class="plant-item" on:click={showTickets}>Ticket</button>
            <button class="plant-item" on:click={showAPI}>API</button>
        </div>
        <div class="main-content">
            {#if $currentView === 'alarms'}
                <AlarmDetails />
            {:else if $currentView === 'tickets'}
                <TicketDetails />
            {:else if $currentView === 'api'}
                <APIDetails />
            {:else if $plantDetails}
                <h2>Dettagli impianto</h2>
                <ul>
                    <li><strong>Nome:</strong> {$plantDetails.name}</li>
                    <li><strong>UUID:</strong> {$plantDetails.uuid}</li>
                    <li><strong>Stato:</strong> {$plantDetails.status}</li>

                    <li>
                        {#if $plantDetails.owner_id}
                            <OwnerDetails ownerId={$plantDetails.owner_id} />
                        {/if}
                    </li>

                    <li>
                        {#if $plantDetails.plant_module_system_id}
                            <PlantModuleSystemDetails plantModuleSystemId={$plantDetails.plant_module_system_id} />
                        {/if}
                    </li>

                    <li>
                        {#if $plantDetails.plant_battery_system_id}
                            <PlantBatterySystemDetails plantBatterySystemId={$plantDetails.plant_battery_system_id} plantId={$plantDetails.id} />
                        {/if}
                    </li>

                    <li>
                        {#if $plantDetails.plant_production_id}
                            <PlantProductionDetails plantProductionId={$plantDetails.plant_production_id} />
                        {/if}
                    </li>

                </ul>
            {:else}
                <p>Seleziona un impianto per vederne i dettagli</p>
            {/if}
        </div>
    {/if}
</div>
