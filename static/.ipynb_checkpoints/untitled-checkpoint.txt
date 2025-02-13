const texts = ["DEVELOPED BY ILGARRRX", "WELCOME TO MY WEBSITE", "FLASK-SOCKETIO PROJECT"];
let textIndex = 0;
let index = 0;
let typing = true;
let glitchCount = 0;
let originalText = "";
let timeoutId = null;

function getRandomChar() {
    const chars = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789!@#$%^&*()_+-=[]{}|;:',.<>?";
    return chars[Math.floor(Math.random() * chars.length)];
}

function glitchText(text) {
    return text.split("").map(char => (Math.random() > 0.3 ? getRandomChar() : char)).join("");
}

function typeWriterEffect() {
    clearTimeout(timeoutId);

    const authorElement = document.getElementById("author-text");
    let currentText = texts[textIndex];

    if (typing) {
        authorElement.innerHTML = currentText.substring(0, index++) + `<span class="cursor">|</span>`;
        if (index > currentText.length) {
            typing = false;
            originalText = currentText;
            setTimeout(startGlitchEffect, 1000);
            return;
        }
    } else {
        authorElement.innerHTML = currentText.substring(0, index--) + `<span class="cursor">|</span>`;
        if (index < 0) {
            typing = true;
            textIndex = (textIndex + 1) % texts.length;
        }
    }

    timeoutId = setTimeout(typeWriterEffect, typing ? 100 : 50);
}

function startGlitchEffect() {
    clearTimeout(timeoutId);

    const authorElement = document.getElementById("author-text");
    glitchCount = Math.floor(Math.random() * 6) + 1; // 1-6 dəfə aralığında olacaq

    function glitchStep(step) {
        if (step >= glitchCount * 2) {
            authorElement.innerHTML = originalText + `<span class="cursor">|</span>`;
            setTimeout(() => {
                index = originalText.length;
                typing = false;
                typeWriterEffect();
            }, 500);
            return;
        }

        authorElement.innerHTML = (step % 2 === 0 ? glitchText(originalText) : originalText) + `<span class="cursor">|</span>`;
        
        // Glitch animasiyasının sürətini random 0.1s - 0.3s aralığında təyin edirik
        const randomSpeed = Math.random() * (300 - 100) + 100;

        timeoutId = setTimeout(() => glitchStep(step + 1), randomSpeed);
    }

    glitchStep(0);
}

document.addEventListener("DOMContentLoaded", typeWriterEffect);
