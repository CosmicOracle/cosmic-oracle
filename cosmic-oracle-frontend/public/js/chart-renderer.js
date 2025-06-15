/**
 * Cosmic Oracle Chart Renderer
 * Handles rendering of astrological charts using HTML5 Canvas
 */

class ChartRenderer {
    constructor(canvasId) {
        this.canvas = document.getElementById(canvasId);
        if (!this.canvas) return;
        
        this.ctx = this.canvas.getContext('2d');
        this.centerX = this.canvas.width / 2;
        this.centerY = this.canvas.height / 2;
        this.radius = Math.min(this.centerX, this.centerY) * 0.9;
        
        // Chart settings
        this.zodiacColors = {
            fire: '#FF6B6B',
            earth: '#4ECDC4',
            air: '#95A5A6',
            water: '#3498DB'
        };
        
        this.aspectColors = {
            conjunction: '#FFD93D',
            opposition: '#FF6B6B',
            trine: '#4ECDC4',
            square: '#E74C3C',
            sextile: '#3498DB'
        };
        
        this.planetSymbols = {
            Sun: '☉',
            Moon: '☽',
            Mercury: '☿',
            Venus: '♀',
            Mars: '♂',
            Jupiter: '♃',
            Saturn: '♄',
            Uranus: '♅',
            Neptune: '♆',
            Pluto: '♇'
        };
    }

    clear() {
        this.ctx.clearRect(0, 0, this.canvas.width, this.canvas.height);
    }

    drawChart(data) {
        this.clear();
        
        // Draw the outer wheel (zodiac)
        this.drawZodiacWheel();
        
        // Draw house cusps
        this.drawHouseCusps(data.houses);
        
        // Draw planets
        this.drawPlanets(data.planets);
        
        // Draw aspects
        if (data.aspects) {
            this.drawAspects(data.aspects);
        }
    }

    drawZodiacWheel() {
        const signs = [
            { name: 'Aries', element: 'fire' },
            { name: 'Taurus', element: 'earth' },
            { name: 'Gemini', element: 'air' },
            { name: 'Cancer', element: 'water' },
            { name: 'Leo', element: 'fire' },
            { name: 'Virgo', element: 'earth' },
            { name: 'Libra', element: 'air' },
            { name: 'Scorpio', element: 'water' },
            { name: 'Sagittarius', element: 'fire' },
            { name: 'Capricorn', element: 'earth' },
            { name: 'Aquarius', element: 'air' },
            { name: 'Pisces', element: 'water' }
        ];

        signs.forEach((sign, index) => {
            const startAngle = (index * 30) * Math.PI / 180;
            const endAngle = ((index + 1) * 30) * Math.PI / 180;
            
            // Draw sign sector
            this.ctx.beginPath();
            this.ctx.moveTo(this.centerX, this.centerY);
            this.ctx.arc(this.centerX, this.centerY, this.radius, startAngle, endAngle);
            this.ctx.closePath();
            
            this.ctx.fillStyle = this.zodiacColors[sign.element];
            this.ctx.globalAlpha = 0.2;
            this.ctx.fill();
            this.ctx.globalAlpha = 1;
            
            // Draw sign symbol
            const symbolAngle = (index * 30 + 15) * Math.PI / 180;
            const symbolX = this.centerX + Math.cos(symbolAngle) * (this.radius * 0.85);
            const symbolY = this.centerY + Math.sin(symbolAngle) * (this.radius * 0.85);
            
            this.ctx.font = '20px Arial';
            this.ctx.fillStyle = '#333';
            this.ctx.textAlign = 'center';
            this.ctx.textBaseline = 'middle';
            this.ctx.fillText(sign.name.charAt(0), symbolX, symbolY);
        });
    }

    drawHouseCusps(houses) {
        houses.forEach((cusp, index) => {
            const angle = cusp * Math.PI / 180;
            
            this.ctx.beginPath();
            this.ctx.moveTo(this.centerX, this.centerY);
            this.ctx.lineTo(
                this.centerX + Math.cos(angle) * this.radius,
                this.centerY + Math.sin(angle) * this.radius
            );
            
            this.ctx.strokeStyle = '#666';
            this.ctx.lineWidth = index % 3 === 0 ? 2 : 1;
            this.ctx.stroke();
            
            // Draw house numbers
            const numberAngle = (cusp + 5) * Math.PI / 180;
            const numberX = this.centerX + Math.cos(numberAngle) * (this.radius * 0.3);
            const numberY = this.centerY + Math.sin(numberAngle) * (this.radius * 0.3);
            
            this.ctx.font = '14px Arial';
            this.ctx.fillStyle = '#333';
            this.ctx.textAlign = 'center';
            this.ctx.textBaseline = 'middle';
            this.ctx.fillText((index + 1).toString(), numberX, numberY);
        });
    }

    drawPlanets(planets) {
        planets.forEach(planet => {
            const angle = planet.longitude * Math.PI / 180;
            const distance = this.radius * 0.6;
            
            const x = this.centerX + Math.cos(angle) * distance;
            const y = this.centerY + Math.sin(angle) * distance;
            
            // Draw planet symbol
            this.ctx.font = '16px Arial';
            this.ctx.fillStyle = '#000';
            this.ctx.textAlign = 'center';
            this.ctx.textBaseline = 'middle';
            this.ctx.fillText(this.planetSymbols[planet.name] || planet.name.charAt(0), x, y);
            
            // Draw degree
            const degreeAngle = angle + (Math.PI / 36); // Offset by 5 degrees
            const degreeX = this.centerX + Math.cos(degreeAngle) * (distance - 15);
            const degreeY = this.centerY + Math.sin(degreeAngle) * (distance - 15);
            
            this.ctx.font = '12px Arial';
            this.ctx.fillText(Math.floor(planet.longitude % 30) + '°', degreeX, degreeY);
        });
    }

    drawAspects(aspects) {
        aspects.forEach(aspect => {
            const angle1 = aspect.planet1.longitude * Math.PI / 180;
            const angle2 = aspect.planet2.longitude * Math.PI / 180;
            
            const x1 = this.centerX + Math.cos(angle1) * (this.radius * 0.4);
            const y1 = this.centerY + Math.sin(angle1) * (this.radius * 0.4);
            const x2 = this.centerX + Math.cos(angle2) * (this.radius * 0.4);
            const y2 = this.centerY + Math.sin(angle2) * (this.radius * 0.4);
            
            this.ctx.beginPath();
            this.ctx.moveTo(x1, y1);
            this.ctx.lineTo(x2, y2);
            
            this.ctx.strokeStyle = this.aspectColors[aspect.type] || '#999';
            this.ctx.lineWidth = 1;
            this.ctx.globalAlpha = 0.5;
            this.ctx.stroke();
            this.ctx.globalAlpha = 1;
        });
    }

    // Helper methods for calculations
    degreesToRadians(degrees) {
        return degrees * Math.PI / 180;
    }

    calculateAspectAngle(angle1, angle2) {
        let diff = Math.abs(angle1 - angle2);
        return diff > 180 ? 360 - diff : diff;
    }
}

// Create a singleton instance
window.chartRenderer = new ChartRenderer('chart-canvas');
