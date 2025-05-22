<script>
    import { onMount } from 'svelte';
    import { writable } from 'svelte/store';
    import { fetchResourceDetails } from '../utils/showUtils.js';
    import BatteryDetails from './BatteryDetails.svelte';
    import BatteryChart from '../charts/BatteryChart.svelte';

    export let plantBatterySystemId;
    export let plantId;

    const batterySystemDetails = writable(null);

    async function fetchBatterySystemDetails() {
        const data = await fetchResourceDetails('/plant_battery_system', `${plantBatterySystemId}`);
        batterySystemDetails.set(data);
    }

     // Aggiorna lo stato dopo che l'utente cambia impianto da visualizzare.     
     $: if (plantBatterySystemId) {                                                 
         fetchBatterySystemDetails();
     }

    onMount(() => {
        fetchBatterySystemDetails();
    });
</script>

<div class="object-details">
    {#if $batterySystemDetails}
        <h3>Sistema Batterie Impianto</h3>
        <BatteryDetails batteryIds={$batterySystemDetails.battery_ids} />
        <BatteryChart {plantId} />
    {:else}
        <p>Caricamento dettagli sistema batteria impianto...</p>
    {/if}
</div>
