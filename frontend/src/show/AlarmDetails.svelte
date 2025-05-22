<script>
    import { onMount, onDestroy } from 'svelte';
    import { writable } from 'svelte/store';
    import { fetchResource } from '../utils/formUtils.js';
    import { fetchResourceDetails, formatTimestamp } from '../utils/showUtils.js';

    const alarmList = writable([]);
    let interval;
    let plantDetails = {};
    let loading = true;

    async function fetchAlarms() {
        const data = await fetchResource('/alarm');
        alarmList.set(data);
    }

    async function fetchPlantDetails(plantId)
    {
        return await fetchResourceDetails('/plant', `${plantId}`);
    }

    async function fetchAllPlantDetails()
    {
        loading = true;
        try {
            const alarms = $alarmList;

            for (let i = 0; i < alarms.length; i++) {
                const alarm = alarms[i];
                if (alarm.visible && !plantDetails[alarm.plant_id]) {
                    plantDetails[alarm.plant_id] = await fetchPlantDetails(alarm.plant_id);
                }
            }

        } catch (error) {
            console.error('Error fetching plant details:', error);
        } finally {
            // Una volta caricati i dati non serve più la dicitura `loading`.
            loading = false;
        }
    }

    onMount(async () => {
        await fetchAlarms();
        await fetchAllPlantDetails();

        interval = setInterval(() => {
            fetchAlarms().then(fetchAllPlantDetails);
        }, 5000);
    });

    onDestroy(() => {
        clearInterval(interval);
    });
</script>

<h3>Allarmi</h3>
{#if $alarmList.length > 0}
    <table>
        <thead>
            <tr>
                <th>Nome impianto</th>
                <th>UUID impianto</th>
                <th>Timestamp (UTC)</th>
                <th>Descrizione</th>
                <th>Codice</th>
                <th>Gravità</th>
            </tr>
        </thead>
        <tbody>
            {#each $alarmList as alarm}
                {#if alarm.visible}
                    <tr>
                        <td>{plantDetails[alarm.plant_id]?.name || 'Loading...'}</td>
                        <td>{plantDetails[alarm.plant_id]?.uuid || 'Loading...'}</td>
                        <td>{formatTimestamp(alarm.timestamp)}</td>
                        <td>{alarm.description}</td>
                        <td>{alarm.code}</td>
                        <td>{alarm.severity_level}</td>
                    </tr>
                {/if}
            {/each}
        </tbody>
    </table>
{:else}
    <p>Caricamento...</p>
{/if}
