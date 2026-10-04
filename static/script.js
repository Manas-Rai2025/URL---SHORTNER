console.log("URL Shortener JavaScript loaded");

const form = document.getElementById("urlForm");

if (!form) {
    console.error("Form not found!");
} else {

    form.addEventListener("submit", function(event) {
        event.preventDefault();

        console.log("Form submitted");

        shortenURL();
    });
}

async function shortenURL() {

    console.log("shortenURL() started");

    const urlInput = document.getElementById("urlInput");
    const result = document.getElementById("result");

    const url = urlInput.value.trim();

    console.log("URL:", url);

    if (!url) {
        result.textContent = "Please enter a URL.";
        result.style.color = "red";
        return;
    }

    try {

        console.log("Sending POST request...");

        const response = await fetch("/shorten", {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify({
                url: url
            })
        });

        console.log("Response status:", response.status);

        const data = await response.json();

        console.log("Server response:", data);

        if (!response.ok) {
            throw new Error(data.error || "Something went wrong");
        }

        result.innerHTML = `
            <p>Your Short URL:</p>

            <a href="${data.short_url}" target="_blank">
                ${data.short_url}
            </a>
        `;

        result.style.color = "green";

    } catch (error) {

        console.error("ERROR:", error);

        result.textContent = error.message;
        result.style.color = "red";
    }
}