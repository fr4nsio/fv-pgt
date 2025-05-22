<script>
    import { onMount } from 'svelte';
    import { writable } from 'svelte/store';
    import { fetchResourceDetails } from '../utils/showUtils.js';

    // Passato come prop.
    export let batteryId;
    let data;
    let error;

    async function fetchPlantBatterySystemReading(batteryId)
    {
        const response = await fetch(`/plant_battery_system_sensor_reading?battery_id=${batteryId}&results=1`);
        if (!response.ok) {
            throw new Error('Network response was not ok');
        }
        const jsonData = await response.json();

        // Abbiamo bisogno del primo elemento per la lattura istantanea.
        return jsonData[0];
    }

    async function fetchData()
    {
        try {
            data = await fetchPlantBatterySystemReading(batteryId);
            error = null;
        } catch (err) {
            error = err;
            data = null;
        }
    }

    // Aggiorna lo stato dopo che l'utente cambia impianto da visualizzare. 
    $: if (batteryId) {
        fetchData();
    }

    let interval;
    onMount(async () => {
        await fetchData();
        interval = setInterval(fetchData, 5000);

        return () => {
            clearInterval(interval);
        };
    });
</script>

<div class="object-details">                                                    
    <h3>Valori istantanei</h3>
    <div class="object-details">
        {#if data}
            <li><strong>Corrente (A):</strong> {data.current.toFixed(2)}</li>
            <li><strong>Voltaggio (V):</strong> {data.voltage.toFixed(2)}</li>
        {:else if error}
            <p>Errore recupero dati: {error.message}</p>
        {:else}
            <p>Caricamento...</p>
        {/if}
    </div>
</div>
