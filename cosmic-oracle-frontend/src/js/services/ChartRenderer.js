// cosmic-oracle-frontend/src/js/services/ChartRenderer.js
/**
 * Renders a beautiful SVG astrological chart from natal chart JSON data.
 * This module encapsulates all the complex drawing logic.
 */

// --- Constants and Configuration ---
const ZODIAC_GLYPHS = {
    aries: '♈', taurus: '♉', gemini: '♊', cancer: '♋', leo: '♌', virgo: '♍',
    libra: '♎', scorpio: '♏', sagittarius: '♐', capricorn: '♑', aquarius: '♒', pisces: '♓'
};
const PLANET_GLYPHS = {
    sun: '☉', moon: '☽', mercury: '☿', venus: '♀', mars: '♂', jupiter: '♃',
    saturn: '♄', uranus: '♅', neptune: '♆', pluto: '♇', true_node: '☊', chiron: '⚷',
    ascendant: 'Asc', midheaven: 'MC'
};
const ASPECT_GLYPHS = {
    conjunction: '☌', opposition: '☍', trine: '△', square: '□', sextile: '⚹'
};

const SVG_NS = 'http://www.w3.org/2000/svg';

function createSvgElement(tag, attributes = {}) {
    const el = document.createElementNS(SVG_NS, tag);
    for (const [key, value] of Object.entries(attributes)) {
        el.setAttribute(key, value);
    }
    return el;
}

function polarToCartesian(centerX, centerY, radius, angleInDegrees) {
    const angleInRadians = (angleInDegrees - 90) * Math.PI / 180.0;
    return {
        x: centerX + (radius * Math.cos(angleInRadians)),
        y: centerY + (radius * Math.sin(angleInRadians))
    };
}

export class ChartRenderer {
    constructor(containerId, chartData) {
        this.container = document.getElementById(containerId);
        if (!this.container) {
            throw new Error(`Container with id "${containerId}" not found.`);
        }
        this.chartData = chartData;
        this.size = Math.min(this.container.clientWidth, this.container.clientHeight, 600);
        this.center = this.size / 2;
        this.radii = {
            zodiac: this.center - 10,
            planets: this.center - 60,
            aspects: this.center - 110,
            cusps: this.center - 35,
        };
        this.svg = createSvgElement('svg', {
            width: this.size,
            height: this.size,
            viewBox: `0 0 ${this.size} ${this.size}`,
            class: 'astrology-chart'
        });
        this.container.innerHTML = ''; // Clear previous chart
        this.container.appendChild(this.svg);
    }

    render() {
        this.drawZodiacWheel();
        this.drawHouseCusps();
        this.drawAspectLines();
        this.drawPlanetsAndAngles();
    }

    drawZodiacWheel() {
        const group = createSvgElement('g', { id: 'zodiac-wheel' });
        // Outer circle
        group.appendChild(createSvgElement('circle', { cx: this.center, cy: this.center, r: this.radii.zodiac, class: 'zodiac-circle' }));
        // Ticks and glyphs
        for (let i = 0; i < 12; i++) {
            const angle = i * 30;
            const start = polarToCartesian(this.center, this.center, this.radii.zodiac, angle);
            const end = polarToCartesian(this.center, this.center, this.radii.zodiac - 10, angle);
            group.appendChild(createSvgElement('line', { x1: start.x, y1: start.y, x2: end.x, y2: end.y, class: 'zodiac-tick' }));

            const glyphPos = polarToCartesian(this.center, this.center, this.radii.zodiac - 25, angle + 15);
            const signKey = Object.keys(ZODIAC_GLYPHS)[i];
            const text = createSvgElement('text', { x: glyphPos.x, y: glyphPos.y, class: 'zodiac-glyph' });
            text.textContent = ZODIAC_GLYPHS[signKey];
            group.appendChild(text);
        }
        this.svg.appendChild(group);
    }

    drawHouseCusps() {
        const group = createSvgElement('g', { id: 'house-cusps' });
        const houseCusps = Object.values(this.chartData.house_cusps);

        for (let i = 0; i < 12; i++) {
            const cusp = houseCusps[i];
            const angle = cusp.longitude; // Assumes Aries is at 0 degrees
            const start = polarToCartesian(this.center, this.center, this.radii.planets - 20, angle);
            const end = polarToCartesian(this.center, this.center, this.radii.zodiac, angle);
            
            const lineClass = ['Ascendant', 'Midheaven', 'Descendant', 'Imum Coeli'].includes(cusp.name.replace(' Cusp', '')) ? 'house-cusp-angle' : 'house-cusp-line';
            group.appendChild(createSvgElement('line', { x1: start.x, y1: start.y, x2: end.x, y2: end.y, class: lineClass }));

            const numberPos = polarToCartesian(this.center, this.center, this.radii.cusps, angle + 15);
            const text = createSvgElement('text', { x: numberPos.x, y: numberPos.y, class: 'house-number' });
            text.textContent = i + 1;
            group.appendChild(text);
        }
        this.svg.appendChild(group);
    }

    drawAspectLines() {
        const group = createSvgElement('g', { id: 'aspect-lines' });
        const allPoints = { ...this.chartData.points, ...this.chartData.angles };

        for (const aspect of this.chartData.aspects) {
            if (aspect.aspect_type !== 'major') continue; // Only draw major aspects for clarity

            const p1 = allPoints[aspect.point1_name];
            const p2 = allPoints[aspect.point2_name];
            if (!p1 || !p2) continue;

            const start = polarToCartesian(this.center, this.center, this.radii.aspects, p1.longitude);
            const end = polarToCartesian(this.center, this.center, this.radii.aspects, p2.longitude);
            
            group.appendChild(createSvgElement('line', {
                x1: start.x, y1: start.y,
                x2: end.x, y2: end.y,
                class: `aspect-line ${aspect.aspect_name}`
            }));
        }
        this.svg.appendChild(group);
    }

    drawPlanetsAndAngles() {
        const group = createSvgElement('g', { id: 'planets' });
        const allPoints = { ...this.chartData.points, ...this.chartData.angles };

        for (const point of Object.values(allPoints)) {
            const pos = polarToCartesian(this.center, this.center, this.radii.planets, point.longitude);
            const text = createSvgElement('text', { x: pos.x, y: pos.y, class: 'planet-glyph' });
            text.textContent = PLANET_GLYPHS[point.key] || '?';
            text.setAttribute('data-point-name', point.name); // For tooltips
            group.appendChild(text);

            // Add degree text
            const degreeTextPos = polarToCartesian(this.center, this.center, this.radii.planets + 15, point.longitude);
            const degText = createSvgElement('text', { x: degreeTextPos.x, y: degreeTextPos.y, class: 'planet-degree' });
            degText.textContent = `${Math.floor(point.degrees_in_sign)}°`;
            group.appendChild(degText);
        }
        this.svg.appendChild(group);
    }
}