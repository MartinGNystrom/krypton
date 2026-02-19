/**
 * Map WMO weather codes to emoji icons
 * Based on Open-Meteo API weather codes
 */
function getWeatherIcon(code) {
    // Clear sky
    if (code === 0) return '☀️'; // Clear sky
    if (code === 1) return '🌤️'; // Mainly clear
    if (code === 2) return '⛅'; // Partly cloudy
    if (code === 3) return '☁️'; // Overcast
    
    // Fog
    if (code === 45 || code === 48) return '🌫️'; // Foggy
    
    // Drizzle
    if (code === 51 || code === 53 || code === 55) return '🌧️'; // Drizzle
    
    // Rain
    if (code === 61 || code === 63 || code === 65) return '🌧️'; // Rain
    if (code === 80 || code === 81 || code === 82) return '⛈️'; // Rain showers
    
    // Snow
    if (code === 71 || code === 73 || code === 75 || code === 77) return '❄️'; // Snow
    if (code === 85 || code === 86) return '🌨️'; // Snow showers
    
    // Thunderstorm
    if (code === 95 || code === 96 || code === 99) return '⛈️'; // Thunderstorm
    
    // Default
    return '🌤️';
}
