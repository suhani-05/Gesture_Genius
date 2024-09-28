const API_KEY = "VF.DM.66f764be14474ccce826fdb8.6hhvZiDY5FO99kGB"; // Keep this a secret!

// Function to send an interaction to the Voiceflow API and log the response
async function interact(user_id, request) {
    console.log("...");

    try {
        const response = await fetch(https://general-runtime.voiceflow.com/state/user/${user_id}/interact, {
            method: "POST",
            headers: {
                "Authorization": API_KEY,
                "Content-Type": "application/json"
            },
            body: JSON.stringify(request)
        });

        const data = await response.json();

        // Loop through the response and handle different types of responses
        for (let trace of data) {
            if (trace.type === "text" || trace.type === "speak") {
                console.log(trace.payload.message);
            } else if (trace.type === "end") {
                // An end trace means the Voiceflow dialog has ended
                return false;
            }
        }

        return true;
    } catch (error) {
        console.error("Error interacting with the API:", error);
        return false;
    }
}

// Main function to run the interaction loop
async function main() {
    const user_id = prompt("> What is your name? ");
    
    // Send a simple launch request to start the dialog
    let isRunning = await interact(user_id, { type: "launch" });

    while (isRunning) {
        const nextInput = prompt("> Say something: ");
        
        // Send a simple text-type request with the user input
        isRunning = await interact(user_id, { type: "text", payload: nextInput });
    }

    console.log("The end! Start me again.");
}

// Start the program
main();


