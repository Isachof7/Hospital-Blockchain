document.addEventListener("DOMContentLoaded", function() {
    fetchInventory();
    fetchAlerts();

    document.getElementById("search").addEventListener("input", function() {
        let searchValue = this.value.toLowerCase();
        filterInventory(searchValue);
    });
});

function fetchInventory() {
    fetch('/get_chain')
        .then(response => response.json())
        .then(data => {
            let inventoryList = document.getElementById("inventory-list");
            inventoryList.innerHTML = "";

            data.chain.forEach(block => {
                if (block.index !== 0) {  // Skip Genesis Block
                    let item = document.createElement("div");
                    item.classList.add("inventory-item");
                    item.innerHTML = `<strong>${block.data.medicine}</strong> - Qty: ${block.data.quantity}, Expiry: ${block.data.expiry}`;
                    inventoryList.appendChild(item);
                }
            });
        });
}

function fetchAlerts() {
    fetch('/get_alerts')
        .then(response => response.json())
        .then(data => {
            let alertList = document.getElementById("alerts");
            alertList.innerHTML = "";

            data.alerts.forEach(alert => {
                let alertItem = document.createElement("div");
                alertItem.classList.add("alert");
                alertItem.textContent = alert;
                alertList.appendChild(alertItem);
            });
        });
}

function filterInventory(query) {
    let items = document.querySelectorAll(".inventory-item");
    items.forEach(item => {
        if (item.textContent.toLowerCase().includes(query)) {
            item.style.display = "block";
        } else {
            item.style.display = "none";
        }
    });
}
