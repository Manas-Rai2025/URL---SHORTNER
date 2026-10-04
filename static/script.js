const urlInput = document.getElementById("urlInput");
const result = document.getElementById("result");
const loading = document.getElementById("loading");
const button = document.getElementById("shortenButton");

async function shortenURL() {

    const url = urlInput.value.trim();

    result.classList.add("hidden");

    if (!url) {
        showError("Please enter a URL.");
        return;
    }

    if (!url.startsWith("http://") && !url.startsWith("https://")) {
        showError("Please enter a valid URL starting with http:// or https://");
        return;
    }

    loading.classList.remove("hidden");

    button.disabled = true;
    button.style.opacity = "0.6";

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
            throw new Error(
                data.error || "Something went wrong."
            );
        }

        showResult(data.short_url);

    } catch (error) {

        showError(error.message);

    } finally {

        loading.classList.add("hidden");

        button.disabled = false;
        button.style.opacity = "1";
    }
}


function showResult(shortUrl) {

    result.classList.remove("hidden");

    result.innerHTML = `
        <div class="result-title">
            ✓ YOUR SHORT LINK IS READY
        </div>

        <div class="result-row">

            <a href="${shortUrl}" target="_blank">
                ${shortUrl}
            </a>

            <button
                class="copy-button"
                onclick="copyURL('${shortUrl}')">
                Copy
            </button>

        </div>
    `;
}


function showError(message) {

    result.classList.remove("hidden");

    result.style.background =
        "rgba(239,68,68,0.06)";

    result.style.borderColor =
        "rgba(239,68,68,0.2)";

    result.innerHTML = `
        <div style="color:#fca5a5;font-size:13px;">
            ✕ ${message}
        </div>
    `;
}


async function copyURL(url) {

    try {

        await navigator.clipboard.writeText(url);

        const button =
            document.querySelector(".copy-button");

        button.textContent = "Copied ✓";

        setTimeout(() => {
            button.textContent = "Copy";
        }, 2000);

    } catch (error) {

        alert("Unable to copy the URL.");
    }
}


urlInput.addEventListener("keydown", function(event) {

    if (event.key === "Enter") {
        shortenURL();
    }

});