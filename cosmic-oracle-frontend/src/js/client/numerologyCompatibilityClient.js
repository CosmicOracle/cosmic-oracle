// js/combinedNumerologyCompatibility.js

document.addEventListener('DOMContentLoaded', function() {

    // --- Helper function to calculate Life Path Number (from second snippet) ---
    function calculateLifePathNumber(birthDate) {
        if (!birthDate) return null;

        // Ensure the date is parsed correctly, especially from date inputs
        // HTML date inputs return 'YYYY-MM-DD'
        const parts = birthDate.split('-');
        if (parts.length !== 3) { // Basic validation
             // Try parsing with new Date() as a fallback for other formats if necessary
            const dateObj = new Date(birthDate);
            if (isNaN(dateObj.getTime())) return null; // Invalid date
            let month = dateObj.getMonth() + 1;
            let day = dateObj.getDate();
            let year = dateObj.getFullYear();
            return reduceLifePath(month, day, year);
        }

        const year = parseInt(parts[0]);
        const month = parseInt(parts[1]);
        const day = parseInt(parts[2]);

        if (isNaN(year) || isNaN(month) || isNaN(day)) return null;


        return reduceLifePath(month, day, year);
    }

    function reduceLifePath(month, day, year) {
        const sumDigits = (numStr) => String(numStr).split('').reduce((sum, digit) => sum + parseInt(digit), 0);
        let totalSum = sumDigits(month) + sumDigits(day) + sumDigits(year);
        return reduceToSingleDigitOrMaster(totalSum);
    }

    // --- Helper function to reduce a number to a single digit or master number (from second snippet) ---
    function reduceToSingleDigitOrMaster(number) {
        while (number > 9 && number !== 11 && number !== 22 && number !== 33) {
            number = String(number).split('').reduce((sum, digit) => sum + parseInt(digit), 0);
        }
        return number;
    }

    // --- Core client-side compatibility logic (from second snippet) ---
    function getLifePathCompatibility(lp1, lp2) {
        const interactionTypes = {
            "Natural Match": [
                [1, 3], [1, 5], [1, 7], [2, 4], [2, 6], [2, 8], [3, 6], [3, 9], [4, 8],
                [1,1], [2,2], [3,3], [4,4], [5,5], [6,6], [7,7], [8,8], [9,9], [11,11], [22,22], [33,33]
            ],
            "Complementary": [
                [1, 2], [1, 6], [2, 3], [2, 5], [3, 5], [3, 7], [4, 5], [4, 6], [4, 7],
                [5, 7], [5, 8], [5, 9], [6, 7], [6, 8], [6, 9], [7, 8], [7, 9], [8, 9]
            ],
            "Challenging but Growthful": [
                [1, 4], [1, 8], [1, 9], [2, 7], [2, 9], [3, 4], [3, 8], [4, 9]
            ]
        };

        let interaction = "Dynamic Interplay";
        let score = 65;

        for (const type in interactionTypes) {
            if (interactionTypes[type].some(pair => (pair[0] === lp1 && pair[1] === lp2) || (pair[0] === lp2 && pair[1] === lp1))) {
                interaction = type;
                if (type === "Natural Match") score = Math.floor(Math.random() * 20) + 75; // 75-95
                else if (type === "Complementary") score = Math.floor(Math.random() * 20) + 60; // 60-80
                else if (type === "Challenging but Growthful") score = Math.floor(Math.random() * 20) + 40; // 40-60
                break;
            }
        }
        if (lp1 === lp2 && interaction !== "Natural Match") { // Ensure same numbers are distinct if not already in "Natural Match"
             interaction = "Mirror & Amplification";
             score = Math.floor(Math.random() * 15) + 70; // 70-85
        }


        let summary = `The combination of Life Path ${lp1} and Life Path ${lp2} creates a relationship characterized by...`;
        let strengths = ["Mutual respect for...", "Shared interest in..."];
        let challenges = ["Potential for disagreement over...", "Need to balance..."];
        let advice = "To thrive, this pair should focus on...";

        if ((lp1 === 1 && lp2 === 5) || (lp1 === 5 && lp2 === 1)) {
            summary = `Life Path 1 (The Leader) and Life Path 5 (The Adventurer) create a dynamic, exciting, and freedom-loving partnership. Both value independence and dislike routine. This can lead to a vibrant connection full of new experiences.`;
            strengths = ["Mutual love for freedom and adventure.", "Stimulating conversations and new ideas.", "Support for individual pursuits.", "High energy and enthusiasm."];
            challenges = ["Potential for inconsistency or lack of follow-through on shared commitments.", "Both can be restless and may struggle with deep emotional bonding if not consciously cultivated.", "Risk of becoming too self-focused and neglecting relationship needs.", "May avoid difficult emotional discussions."];
            advice = "Celebrate your shared love for adventure while consciously creating space for shared responsibilities and deeper emotional connection. Regular check-ins about individual and relationship needs are vital. Find projects you can passionately pursue together.";
        } else if ((lp1 === 2 && lp2 === 6) || (lp1 === 6 && lp2 === 2)) {
            summary = `Life Path 2 (The Peacemaker) and Life Path 6 (The Nurturer) often form a deeply harmonious, loving, and supportive bond. Both are relationship-oriented and value emotional connection, family, and beauty.`;
            strengths = ["Strong emotional connection and empathy.", "Shared focus on home, family, and relationships.", "Mutual desire for harmony and peace.", "Highly supportive and nurturing of each other."];
            challenges = ["Can become overly dependent or enmeshed.", "May avoid conflict to maintain peace, leading to unresolved issues.", "Risk of emotional sensitivity leading to hurt feelings.", "The 6 might over-give, and the 2 might struggle to assert needs directly."];
            advice = "Cherish your deep bond while ensuring healthy boundaries and individual expression. Encourage open communication even about difficult topics. The 6 should practice receiving care, and the 2 should practice asserting their needs gently but clearly. Create a beautiful and harmonious home together.";
        } else if ((lp1 === 4 && lp2 === 8) || (lp1 === 8 && lp2 === 4)) {
            summary = `Life Path 4 (The Builder) and Life Path 8 (The Powerhouse) can create a formidable and successful partnership, especially in achieving material goals. Both are practical, disciplined, and value hard work.`;
            strengths = ["Shared ambition and drive for success.", "Excellent at planning and executing long-term goals.", "Mutual respect for discipline and responsibility.", "Can build a very secure and stable life together."];
            challenges = ["Risk of relationship becoming too focused on work or material achievements, neglecting emotional intimacy.", "Both can be stubborn and resistant to change.", "Potential for power struggles if not collaborating as equals.", "May struggle with expressing vulnerability or softer emotions."];
            advice = "Balance your drive for achievement with dedicated time for emotional connection, fun, and relaxation. Celebrate successes together. Practice flexibility and open communication about feelings, not just goals. Ensure you are partners in all aspects of life, not just business associates.";
        }
        // Add many more interpretations for all pairs

        return { lp1, lp2, score, interactionType: interaction, summary, strengths, challenges, advice };
    }


    // --- Unified function to display compatibility results ---
    function displayCombinedResults(data, resultDiv, isApiClientData) {
        resultDiv.style.display = 'block';
        resultDiv.classList.remove('api-loading'); // Ensure loading class is removed

        const lifePath1 = isApiClientData ? data.life_path_1 : data.lp1;
        const lifePath2 = isApiClientData ? data.life_path_2 : data.lp2;
        const score = isApiClientData ? data.compatibility.overall_score : data.score;
        const interactionType = isApiClientData ? data.compatibility.interaction_type : data.interactionType;
        const summary = isApiClientData ? data.compatibility.summary : data.summary;
        const strengths = isApiClientData ? data.compatibility.key_strengths : data.strengths;
        const challenges = isApiClientData ? data.compatibility.potential_challenges : data.challenges;
        const advice = isApiClientData ? data.compatibility.advice : data.advice;

        const lifePathBoxes = resultDiv.querySelectorAll('.life-path-box .number');
        if (lifePathBoxes.length >= 2) {
            lifePathBoxes[0].textContent = lifePath1;
            lifePathBoxes[1].textContent = lifePath2;
        }

        const scoreNumberEl = resultDiv.querySelector('.score-number');
        if (scoreNumberEl) {
            scoreNumberEl.textContent = isApiClientData ? score : score + '%';
            const scoreCircleParent = scoreNumberEl.closest('.score-circle') || scoreNumberEl.parentElement;
            if (scoreCircleParent) {
                if (score >= 75) scoreCircleParent.style.borderColor = '#4CAF50';
                else if (score >= 50) scoreCircleParent.style.borderColor = '#FFC107';
                else scoreCircleParent.style.borderColor = '#F44336';
            }
        }
        
        const interactionTypeEl = resultDiv.querySelector('.interaction-type');
        if (interactionTypeEl) interactionTypeEl.textContent = interactionType;

        const summaryEl = resultDiv.querySelector('.compatibility-summary');
        if (summaryEl) summaryEl.textContent = summary;
        
        const strengthsListEl = resultDiv.querySelector('.key-strengths');
        if (strengthsListEl) {
            strengthsListEl.innerHTML = strengths.map(strength => `<li>${strength}</li>`).join('');
        }

        const challengesListEl = resultDiv.querySelector('.potential-challenges');
        if (challengesListEl) {
            challengesListEl.innerHTML = challenges.map(challenge => `<li>${challenge}</li>`).join('');
        }

        const adviceEl = resultDiv.querySelector('.compatibility-advice');
        if (adviceEl) adviceEl.textContent = advice;

        resultDiv.scrollIntoView({ behavior: 'smooth' });
    }

    // --- API Call Functionality (from first snippet, adapted) ---
    const calculateBtnNumerologyAPI = document.getElementById('calculateCompatibilityNumerology');
    const calculateBtnDailyAPI = document.getElementById('calculateCompatibilityDaily');
    const resultDivsAPI = document.querySelectorAll('.compatibility-result'); // Assuming this class for API results
    const birthDate1InputsAPI = document.querySelectorAll('#birthDate1'); // Assuming distinct IDs or classes for these inputs
    const birthDate2InputsAPI = document.querySelectorAll('#birthDate2');

    async function calculateApiCompatibility(birthDate1Input, birthDate2Input, resultDiv) {
        try {
            if (!birthDate1Input.value || !birthDate2Input.value) {
                alert('Please enter both birth dates');
                return;
            }
            
            resultDiv.classList.add('api-loading');
            resultDiv.style.display = 'block'; // Show it before filling
            resultDiv.innerHTML = 'Loading compatibility...'; // Basic loading text

            const response = await fetch('/api/numerology/compatibility', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    birth_date_1: birthDate1Input.value,
                    birth_date_2: birthDate2Input.value
                })
            });

            const data = await response.json();
            resultDiv.classList.remove('api-loading'); // Remove loading after fetch, before display

            if (!response.ok) {
                throw new Error(data.error || 'Failed to calculate compatibility via API');
            }
            displayCombinedResults(data, resultDiv, true); // True for API data structure
        } catch (error) {
            console.error('API Error:', error);
            if (resultDiv) {
                resultDiv.classList.remove('api-loading');
                resultDiv.innerHTML = `<p class="error-message">${error.message || 'An error occurred'}</p>`;
                resultDiv.style.display = 'block';
            } else {
                alert(error.message || 'An error occurred while calculating API compatibility');
            }
        }
    }

    if (calculateBtnNumerologyAPI && birthDate1InputsAPI.length > 0 && birthDate2InputsAPI.length > 0 && resultDivsAPI.length > 0) {
        calculateBtnNumerologyAPI.addEventListener('click', function() {
            calculateApiCompatibility(birthDate1InputsAPI[0], birthDate2InputsAPI[0], resultDivsAPI[0]);
        });
    }
    
    if (calculateBtnDailyAPI && birthDate1InputsAPI.length > 1 && birthDate2InputsAPI.length > 1 && resultDivsAPI.length > 1) {
        calculateBtnDailyAPI.addEventListener('click', function() {
            calculateApiCompatibility(birthDate1InputsAPI[1], birthDate2InputsAPI[1], resultDivsAPI[1]);
        });
    }

    // --- Client-Side Calculation Functionality (from second snippet, adapted) ---
    const calculateButtonClient = document.getElementById('calculateCompatibility'); // Button for client-side calculation
    const birthDate1InputClient = document.getElementById('birthDate1Client'); // Assuming specific ID for client version
    const birthDate2InputClient = document.getElementById('birthDate2Client'); // Assuming specific ID for client version
    const resultDivClient = document.getElementById('compatibilityResultClient'); // Assuming specific ID for client version

    if (calculateButtonClient && birthDate1InputClient && birthDate2InputClient && resultDivClient) {
        calculateButtonClient.addEventListener('click', () => {
            const date1 = birthDate1InputClient.value;
            const date2 = birthDate2InputClient.value;

            if (!date1 || !date2) {
                alert("Please enter both birth dates for client-side calculation.");
                return;
            }

            const lp1 = calculateLifePathNumber(date1);
            const lp2 = calculateLifePathNumber(date2);

            if (lp1 === null || lp2 === null) {
                alert("Invalid date format for client-side calculation.");
                return;
            }

            const compatibilityData = getLifePathCompatibility(lp1, lp2);
            displayCombinedResults(compatibilityData, resultDivClient, false); // False for client data structure
        });
    }
});