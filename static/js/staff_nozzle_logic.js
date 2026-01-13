/**
 * Logic for Staff Management Nozzle Allocation
 */

function initializeNozzleManager() {
    const checkbox = document.getElementById("id_nozzle_applicable");
    const container = document.getElementById("nozzleTableContainer");
    const tbody = document.querySelector("#nozzleTable tbody");
    const addBtn = document.getElementById("addNozzleRow");

    if (!checkbox || !container || !tbody || !addBtn) {
        return;
    }

    function addRow(data = null) {
        const tr = document.createElement("tr");

        // Note: window.TANKS must be defined in the template
        tr.innerHTML = `
            <td>
                <select name="tank_id[]" class="form-select tank-select">
                    <option value="">Select Tank</option>
                    ${window.TANKS || ''}
                </select>
            </td>
            <td>
                <select name="nozzle_name[]" class="form-select nozzle-select">
                    <option value="">Select Nozzle</option>
                </select>
            </td>
            <td style="display:none;">
                <input type="hidden" name="product_name[]" class="product-name">
            </td>
            <td>
                <button type="button" class="btn btn-danger btn-sm deleteRow">Delete</button>
            </td>
        `;

        tbody.appendChild(tr);

        const tankSelect = tr.querySelector(".tank-select");
        const nozzleSelect = tr.querySelector(".nozzle-select");
        const productInput = tr.querySelector(".product-name");

        tankSelect.addEventListener("change", function () {
            const tankId = this.value;
            const product = this.selectedOptions[0]?.dataset.product || "";

            nozzleSelect.innerHTML = '<option value="">Select Nozzle</option>';

            if (window.NOZZLES_BY_TANK_ID && window.NOZZLES_BY_TANK_ID[tankId]) {
                nozzleSelect.innerHTML += window.NOZZLES_BY_TANK_ID[tankId];
            }

            productInput.value = product;
        });

        if (data) {
            tankSelect.value = data.tank_id;
            tankSelect.dispatchEvent(new Event("change"));
            nozzleSelect.value = data.nozzle_name;
            productInput.value = data.product_name || "";
        }
    }

    function toggleTable() {
        if (checkbox.checked) {
            container.classList.remove("d-none");
            if (tbody.children.length === 0) {
                if (window.EXISTING_ALLOCATIONS && window.EXISTING_ALLOCATIONS.length) {
                    window.EXISTING_ALLOCATIONS.forEach(addRow);
                } else {
                    addRow();
                }
            }
        } else {
            container.classList.add("d-none");
            tbody.innerHTML = "";
        }
    }

    checkbox.addEventListener("change", toggleTable);
    addBtn.addEventListener("click", () => addRow());
    
    // Initial check
    if (checkbox.checked) toggleTable();

    // Event delegation for delete
    document.addEventListener("click", function (e) {
        if (e.target.classList.contains("deleteRow")) {
            e.target.closest("tr").remove();
        }
    });
}

document.addEventListener("DOMContentLoaded", initializeNozzleManager);

// Export for testing if using a module system, otherwise it's global
if (typeof module !== 'undefined') {
    module.exports = { initializeNozzleManager };
}
