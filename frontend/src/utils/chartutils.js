export function manageChartColorScheme()
{
    // Controllo se il dark mode è attivo.
    const isDarkMode = window.matchMedia('(prefers-color-scheme: dark)').matches;

    // Opzioni grafico.
    return {
        responsive: true,
        plugins: {
            legend: {
                labels: {
                    color: isDarkMode ? 'rgba(255, 255, 255, 0.87)' : '#213547', // Legend text color
                },
            },
            tooltip: {
                bodyColor: isDarkMode ? 'rgba(255, 255, 255, 0.87)' : '#213547', // Tooltip text color
            },
        },
        scales: {
            x: {
                ticks: {
                    color: isDarkMode ? 'rgba(255, 255, 255, 0.87)' : '#213547', // X-axis ticks color
                },
            },
            y: {
                ticks: {
                    color: isDarkMode ? 'rgba(255, 255, 255, 0.87)' : '#213547', // Y-axis ticks color
                },
            },
        },
    };
}
