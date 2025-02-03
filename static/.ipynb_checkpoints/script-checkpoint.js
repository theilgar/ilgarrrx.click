const socket = io();

// Online istifadəçi sayını yenilə
socket.on("update_online_count", (count) => {
    document.getElementById("online_count").innerText = count;
});

// Neofetch məlumatlarını yenilə
socket.on("update_neofetch", (data) => {
    document.getElementById("neofetch_output").innerText = data;
});

// Ziyarətçi məlumatlarını açıb-bağlama funksiyası
function toggleVisitorInfo() {
    const section = document.getElementById("visitor-section");
    section.style.display = section.style.display === "none" || section.style.display === "" ? "block" : "none";
}

// Müəllif animasiyası
const authorText = "Developed by ilgarrrx🦧";
let index = 0;
let typing = true;

function typeWriterEffect() {
    const authorElement = document.getElementById("author-text");

    if (typing) {
        authorElement.innerText = authorText.substring(0, index++);
        if (index > authorText.length) {
            typing = false;
            setTimeout(() => (typing = false), 2000);
        }
    } else {
        authorElement.innerText = authorText.substring(0, index--);
        if (index < 0) typing = true;
    }

    setTimeout(typeWriterEffect, typing ? 100 : 50);
}

document.addEventListener("DOMContentLoaded", typeWriterEffect);

// İstifadəçi cihaz və ekran məlumatlarını backend-ə göndər
function sendVisitorInfo() {
    fetch('/collect-info', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
            screen_width: window.screen.width || "Bilinmir",
            screen_height: window.screen.height || "Bilinmir",
            platform: navigator.platform || "Bilinmir",
            language: navigator.language || "Bilinmir"
        })
    });
}

document.addEventListener("DOMContentLoaded", sendVisitorInfo);

// Ziyarətçi məlumatlarını açıb-bağlama funksiyası
function toggleDetails(ip) {
    const detailsElement = document.getElementById(`details-${ip}`);
    if (detailsElement) {
        detailsElement.style.display = detailsElement.style.display === "none" ? "block" : "none";
    }
}