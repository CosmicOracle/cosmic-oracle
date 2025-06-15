// public/js/apiClient.js

// Configure the base URL of your backend API.
// When you deploy, you'll change this to your live server's address.
const BASE_URL = 'http://localhost:5000'; // Assuming your Flask app runs on port 5000

/**
 * A generic function to handle POST requests to the API.
 * @param {string} endpoint - The API endpoint to call (e.g., '/api/dignities/calculate').
 * @param {object} body - The JSON payload to send with the request.
 * @returns {Promise<object>} A promise that resolves with the JSON response data.
 * @throws {Error} Throws an error if the network request fails or the API returns an error.
 */
async function post(endpoint, body) {
    const url = `${BASE_URL}${endpoint}`;

    try {
        const response = await fetch(url, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(body),
        });

        const responseData = await response.json();

        // If the response is not "ok" (e.g., 400 or 500 status), throw an error
        // using the message provided by the backend.
        if (!response.ok) {
            // Use the error message from the API response, or a default message.
            const errorMessage = responseData.error || `HTTP error! status: ${response.status}`;
            throw new Error(errorMessage);
        }

        return responseData;

    } catch (error) {
        console.error(`API Client Error calling ${endpoint}:`, error);
        // Re-throw the error so the calling function can handle it.
        throw error;
    }
}

// Export the function so other service modules can use it.
export { post };