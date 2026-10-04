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

    result.textContent = "Generating short URL...";
    result.style.color = "black";

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

            <div class="short-url-box">
                <a href="${data.short_url}" target="_blank">
                    ${data.short_url}
                </a>

                <button type="button" onclick="copyURL('${data.short_url}')">
                    Copy
                </button>
            </div>
        `;

        result.style.color = "green";

    } catch (error) {

        console.error("Error:", error);

        result.textContent = error.message;
        result.style.color = "red";
    }
}


function copyURL(url) {

    navigator.clipboard.writeText(url);

    alert("Short URL copied!");
}