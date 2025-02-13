const socket = io();

// Online istifadəçi sayını yenilə
socket.on("update_online_count", (count) => {
    document.getElementById("online_count").innerText = count;
});

// Neofetch məlumatlarını yenilə
socket.on("update_neofetch", (data) => {
    document.getElementById("neofetch_output").innerText = data;
});

// Ziyarətçi məlumatları aç bağla butonu //
function toggleVisitorLogs() {
    let logs = document.getElementById('visitor-logs');
    logs.style.display = logs.style.display === 'none' ? 'block' : 'none';
}

function toggleDetails(id) {
    // Mövcud açıq blokları bağlayırıq (id-si tələb olunan blokdan fərqli olanları)
    const allDetails = document.querySelectorAll('.details-row');
    allDetails.forEach(row => {
        if (row.id !== id && (row.style.display !== "none" && row.style.display !== "")) {
            row.style.display = "none";
            // Həmin blokun düyməsini də + işarəsinə dəyişirik
            let btn = document.querySelector("button[onclick=\"toggleDetails('" + row.id + "')\"]");
            if (btn) {
                btn.textContent = "+";
            }
        }
    });

    // Seçilmiş blokun vəziyyətini dəyişirik
    let row = document.getElementById(id);
    let btn = document.querySelector("button[onclick=\"toggleDetails('" + id + "')\"]");
    if (row.style.display === "none" || row.style.display === "") {
        row.style.display = "table-row";
        if (btn) {
            btn.textContent = "-";
        }
    } else {
        row.style.display = "none";
        if (btn) {
            btn.textContent = "+";
        }
    }
}

function searchVisitorLogs() {
    const input = document.getElementById("search-input");
    const filter = input.value.toLowerCase();
    // Summary sətrlərini seçirik
    const summaryRows = document.querySelectorAll("#visitor-logs table tr.visitor-summary");
    
    summaryRows.forEach(summaryRow => {
        // Növbəti elementin details sətiri olduğunu qəbul edirik
        const detailsRow = summaryRow.nextElementSibling;
        let combinedText = summaryRow.textContent.toLowerCase();
        if (detailsRow && detailsRow.classList.contains("visitor-details")) {
            combinedText += " " + detailsRow.textContent.toLowerCase();
        }
        // Əgər axtarış meyarına uyğun gəlirsə, hər iki sətri göstər; əks halda gizlə
        if (combinedText.includes(filter)) {
            summaryRow.style.display = "";
            if (detailsRow) detailsRow.style.display = summaryRow.style.display === "none" ? "none" : ""; 
        } else {
            summaryRow.style.display = "none";
            if (detailsRow) detailsRow.style.display = "none";
        }
    });
}