const form = document.getElementById("urlForm");

form.addEventListener("submit", function(event) {
    event.preventDefault();
    shortenURL();
});

async function shortenURL() {
    const urlInput = document.getElementById("urlInput");
    const result = document.getElementById("result");

    const url = urlInput.value.trim();

    if (!url) {
        result.textContent = "Please enter a URL.";
        result.style.color = "red";
        return;
    }

    try {
        const response = await fetch("/shorten", {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify({
                url: url
            })
        });

        const data = await response.json();

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
        result.textContent = error.message;
        result.style.color = "red";
    }
}