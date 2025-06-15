// Filename: meditationController.js

/**
 * Manages the Guided Cosmic Meditation feature:
 * - Initializes UI elements and event listeners.
 * - Updates meditation guidance based on type.
 * - Controls the meditation timer.
 * - Handles mantra playback.
 */

let meditationTimerInterval = null;
let meditationTimeRemaining = 0;
let currentMeditationSpeech = null; // For Web Speech API

/**
 * Initializes the Meditation feature.
 */
function initMeditationFeature() {
    const typeSelect = document.getElementById('meditationType');
    const durationSelect = document.getElementById('meditationDuration');
    const startButton = document.getElementById('startMeditationBtn'); // Assuming this ID for the start button

    if (typeSelect) {
        typeSelect.addEventListener('change', displayMeditationGuidance);
    } else {
        console.error("Meditation type selector 'meditationType' not found.");
    }

    if (startButton) {
        startButton.addEventListener('click', startSelectedMeditation);
    } else {
        // If using onclick="startMeditation()" in HTML, ensure startSelectedMeditation is global.
        console.warn("Start Meditation button 'startMeditationBtn' not found. Ensure HTML is updated or use direct onclick for startSelectedMeditation.");
    }

    populateMantrasList();
    displayMeditationGuidance(); // Display guidance for the default selected type
    resetTimerDisplay();
}

/**
 * Populates the list of mantras.
 */
function populateMantrasList() {
    const container = document.getElementById('mantraList');
    if (!container) {
        console.error("Mantra list container 'mantraList' not found.");
        return;
    }

    // Using the mantra data structure previously defined in uiUpdate.js or script.js
    // This data should ideally be fetched or defined in a shared constants file.
    const mantrasData = [
        { name: "Om (AUM)", chantText: "Om", description: "Primordial sound, representing creation, preservation, dissolution. Calming, centering, connects to universal consciousness." },
        { name: "Om Mani Padme Hum", chantText: "Om Mani Padme Hum", description: "Tibetan Buddhist mantra for compassion, wisdom, and liberation." },
        { name: "Gayatri Mantra", chantText: "Om Bhur Bhuvaha Swaha, Tat Savitur Varenyam, Bhargo Devasya Dhimahi, Dhiyo Yo Nah Prachodayat", description: "Vedic mantra for illumination of intellect, spiritual wisdom, and dispelling ignorance." },
        { name: "So Hum", chantText: "So Hum. So Hum.", description: "Breath mantra: \"I am That.\" Connects individual consciousness with universal consciousness." },
        { name: "Aham Prema", chantText: "Aham Prema. Aham Prema.", description: "Sanskrit for \"I am Divine Love.\" Cultivates self-love, compassion, and loving-kindness towards all." },
        { name: "Ra Ma Da Sa Sa Say So Hung", chantText: "Ra Ma Da Sa, Sa Say So Hung.", description: "Siri Gaitri Mantra from Kundalini Yoga, a powerful mantra for healing energy." },
        { name: "Om Namah Shivaya", chantText: "Om Namah Shivaya. Om Namah Shivaya.", description: "Hindu mantra dedicated to Lord Shiva, representing transformation and auspiciousness." },
        { name: "Om Shanti Shanti Shanti", chantText: "Om Shanti, Shanti, Shanti.", description: "Invocation for peace. Calms the mind and environment." }
    ];

    container.innerHTML = mantrasData.map(mantra => `
        <div class="ritual-card"> <h4>${mantra.name}</h4>
            <p>${mantra.description}</p>
            <button onclick="playSelectedMantra('${mantra.chantText.replace(/'/g, "\\'")}', '${mantra.name.replace(/'/g, "\\'")}')" class="tab-button">Chant</button>
        </div>
    `).join('');
}

/**
 * Displays meditation guidance based on the selected type.
 */
function displayMeditationGuidance() {
    const type = document.getElementById('meditationType')?.value || 'mindfulness';
    const guidanceContainer = document.getElementById('meditationGuidance');
    if (!guidanceContainer) {
        console.error("Meditation guidance container 'meditationGuidance' not found.");
        return;
    }

    let guidanceText = `<h4>${type.charAt(0).toUpperCase() + type.slice(1)} Meditation Guidance</h4>`;
    const medGuidanceSource = (ALL_RITUAL_DATA && ALL_RITUAL_DATA.meditation_guidance) ? ALL_RITUAL_DATA.meditation_guidance : {};

    switch (type) {
        case 'mindfulness':
            guidanceText += `<p>${medGuidanceSource.mindfulness || "Focus on your breath. Observe thoughts without judgment. Anchor yourself in the present moment, noticing sensations, sounds, and feelings as they arise and pass."}</p>`;
            break;
        case 'chakra':
            const chakraKeys = (ALL_CHAKRA_DATA && typeof ALL_CHAKRA_DATA === 'object') ? Object.keys(ALL_CHAKRA_DATA) : ['root'];
            const randomChakraKey = chakraKeys[Math.floor(Math.random() * chakraKeys.length)];
            const chakraForMed = (ALL_CHAKRA_DATA && ALL_CHAKRA_DATA[randomChakraKey]) ? ALL_CHAKRA_DATA[randomChakraKey] : { name: "Root", color: "red", bija_mantra: "LAM", location: "base of spine", primary_focus: "grounding" };
            const chakraGuidanceTemplate = medGuidanceSource.chakra || `Focus on your {chakraName}. Visualize its vibrant {chakraColor} light at its location ({chakraLocation}). You may silently chant its bija mantra: "{chakraMantra}". Feel the qualities of {primaryFocus} awakening within you.`;
            guidanceText += `<p>${chakraGuidanceTemplate
                .replace('{chakraName}', chakraForMed.name)
                .replace('{chakraColor}', chakraForMed.color.toLowerCase())
                .replace('{chakraLocation}', chakraForMed.location.toLowerCase())
                .replace('{chakraMantra}', chakraForMed.bija_mantra)
                .replace('{primaryFocus}', chakraForMed.primary_focus.split(',')[0]) // Use first focus keyword
            }</p>`;
            break;
        case 'manifestation':
            guidanceText += `<p>${medGuidanceSource.manifestation || "Clearly visualize your desire as already fulfilled. Engage all your senses. Feel the emotions of success and gratitude. Release attachment to the outcome, trusting the universe."}</p>`;
            break;
        case 'healing':
            guidanceText += `<p>${medGuidanceSource.healing || "Visualize healing light (e.g., golden, green, or white) filling your body. Direct it to areas needing care. Affirm your wholeness and vitality. Breathe deeply, releasing tension."}</p>`;
            break;
        case 'zodiac':
            const signKeys = (ALL_ZODIAC_SIGNS_DATA && typeof ALL_ZODIAC_SIGNS_DATA === 'object') ? Object.keys(ALL_ZODIAC_SIGNS_DATA) : ['aries'];
            const randomSignKey = signKeys[Math.floor(Math.random() * signKeys.length)];
            const signForMed = (ALL_ZODIAC_SIGNS_DATA && ALL_ZODIAC_SIGNS_DATA[randomSignKey]) ? ALL_ZODIAC_SIGNS_DATA[randomSignKey] : { name: "Aries", keywords: ["courage", "initiative"] };
            const zodiacGuidanceTemplate = medGuidanceSource.zodiac || `Connect with the energy of {signName}. Meditate on its core qualities such as {signKeywords}. How can you embody these energies today?`;
            guidanceText += `<p>${zodiacGuidanceTemplate
                .replace('{signName}', signForMed.name)
                .replace('{signKeywords}', (signForMed.keywords || ["its unique essence"]).slice(0, 2).join(', '))
            }</p>`;
            break;
        default:
            guidanceText += "<p>Find a comfortable position. Close your eyes gently. Focus on your natural breath, allowing thoughts to pass without judgment. Relax and be present.</p>";
    }
    guidanceContainer.innerHTML = guidanceText;
}

/**
 * Starts the meditation timer for the selected duration.
 */
function startSelectedMeditation() {
    if (meditationTimerInterval) {
        clearInterval(meditationTimerInterval); // Clear any existing timer
    }
    if (currentMeditationSpeech && 'speechSynthesis' in window && speechSynthesis.speaking) {
        speechSynthesis.cancel(); // Stop any ongoing mantra
    }

    const durationSelect = document.getElementById('meditationDuration');
    const timerDisplay = document.getElementById('timerDisplay');

    if (!durationSelect || !timerDisplay) {
        console.error("Meditation duration selector or timer display not found.");
        return;
    }

    const durationMinutes = parseInt(durationSelect.value);
    meditationTimeRemaining = durationMinutes * 60;

    updateTimerDisplayUI(); // Show initial time

    meditationTimerInterval = setInterval(() => {
        meditationTimeRemaining--;
        updateTimerDisplayUI();
        if (meditationTimeRemaining < 0) {
            clearInterval(meditationTimerInterval);
            timerDisplay.textContent = "Namaste";
            // Consider a gentle sound notification here if desired
            alert("Meditation complete. Carry this peace and clarity with you. Om Shanti.");
            // Optionally reset guidance or offer post-meditation reflection
        }
    }, 1000);
}

/**
 * Updates the timer display element.
 */
function updateTimerDisplayUI() {
    const timerDisplay = document.getElementById('timerDisplay');
    if (!timerDisplay) return;

    const minutes = Math.floor(meditationTimeRemaining / 60);
    const seconds = meditationTimeRemaining % 60;
    timerDisplay.textContent = `${minutes.toString().padStart(2, '0')}:${seconds.toString().padStart(2, '0')}`;
}

/**
 * Resets the timer display to 00:00.
 */
function resetTimerDisplay() {
    const timerDisplay = document.getElementById('timerDisplay');
    if (timerDisplay) {
        timerDisplay.textContent = "00:00";
    }
    if (meditationTimerInterval) {
        clearInterval(meditationTimerInterval);
        meditationTimerInterval = null;
    }
    meditationTimeRemaining = 0;
}


/**
 * Plays the selected mantra using Web Speech API.
 * @param {string} chantText - The text of the mantra to be spoken.
 * @param {string} mantraName - The name of the mantra for display.
 */
function playSelectedMantra(chantText, mantraName) {
    const statusArea = document.getElementById('meditationGuidance'); // Use guidance area for status

    if (!('speechSynthesis' in window)) {
        alert(`Web Speech API not supported. Conceptual Chant for: ${mantraName}\n\n"${chantText}"\n\nRepeat with focused intention.`);
        if (statusArea) statusArea.innerHTML = `<p style="color: #ffcc00;">Web Speech API not supported. Please chant ${mantraName} manually: "${chantText}"</p>`;
        return;
    }

    if (currentMeditationSpeech && speechSynthesis.speaking) {
        speechSynthesis.cancel(); // Stop previous speech
    }

    currentMeditationSpeech = new SpeechSynthesisUtterance(chantText);
    // Attempt to find a suitable voice (can be unreliable across browsers)
    const voices = speechSynthesis.getVoices();
    // Example: Prefer a female voice if available and English
    let selectedVoice = voices.find(voice => voice.lang.startsWith('en') && voice.name.toLowerCase().includes('female'));
    if (!selectedVoice && voices.length > 0) { // Fallback to first available English voice
        selectedVoice = voices.find(voice => voice.lang.startsWith('en'));
    }
    if (selectedVoice) {
        currentMeditationSpeech.voice = selectedVoice;
    } else if (voices.length > 0) {
        currentMeditationSpeech.voice = voices[0]; // Fallback to any voice
    }


    currentMeditationSpeech.lang = currentMeditationSpeech.voice ? currentMeditationSpeech.voice.lang : 'en-US';
    currentMeditationSpeech.rate = 0.6; // Slower for chanting
    currentMeditationSpeech.pitch = 0.8; // Slightly lower pitch
    currentMeditationSpeech.volume = 0.9;

    currentMeditationSpeech.onstart = () => {
        if (statusArea) statusArea.innerHTML = `<p style="font-style:italic; color: #ffd700;">Now chanting: ${mantraName}. Focus and breathe...</p>`;
    };
    currentMeditationSpeech.onend = () => {
        if (statusArea && statusArea.innerHTML.includes(`Now chanting: ${mantraName}`)) {
            statusArea.innerHTML = `<p style="font-style:italic; color: #a8e063;">Chant for ${mantraName} complete. Carry its peace.</p>`;
        }
        currentMeditationSpeech = null;
    };
    currentMeditationSpeech.onerror = (event) => {
        console.error("Speech synthesis error:", event.error, event);
        let errorMsg = `Could not play chant for ${mantraName}. Error: ${event.error}.`;
        if (event.error === 'not-allowed' || event.error === 'audio-capture') {
            errorMsg += ' Please ensure your browser has permission to play audio/use microphone and try again.';
        } else if (event.error === 'language-unavailable' || event.error === 'voice-unavailable') {
            errorMsg += ' The selected voice or language for chanting is not available on your system.';
        }
        if (statusArea) statusArea.innerHTML = `<p style="color: #ff6b6b;">${errorMsg}</p>`;
        currentMeditationSpeech = null;
    };

    speechSynthesis.speak(currentMeditationSpeech);
}

// Expose functions to be callable from script.js or HTML
window.initMeditationFeature = initMeditationFeature;
window.startSelectedMeditation = startSelectedMeditation; // If called by onclick in HTML
window.playSelectedMantra = playSelectedMantra; // For onclick on mantra buttons

// Initial call if meditation tab is default or for direct linking
// document.addEventListener('DOMContentLoaded', initMeditationFeature); // This should be called by main script.js when tab is active

