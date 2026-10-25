document.addEventListener("DOMContentLoaded", () => {
  const modal = document.getElementById("addTransactionModal");
  const form = document.getElementById("addTransactionForm");
  const modalTitle = document.getElementById("modalTitle");
  const statusButtons = document.querySelectorAll(".status-btn");
  const statusInput = document.getElementById("statusInput");

  // --- Status button toggle ---
  statusButtons.forEach(btn => {
    btn.addEventListener("click", () => {
      statusInput.value = btn.dataset.status;
      statusButtons.forEach(b => b.classList.remove("selected"));
      btn.classList.add("selected");
    });
  });

  // --- Add Transaction ---
  document.querySelector(".add-btn").addEventListener("click", () => {
    modalTitle.textContent = "Add Transaction";
    form.action = "/add_transaction";
    form.reset();
    statusButtons.forEach(b => b.classList.remove("selected"));
    modal.style.display = "block";
  });

  // --- Edit Transaction ---
  document.querySelectorAll(".editBtn").forEach(btn => {
    btn.addEventListener("click", (event) => {
      event.preventDefault();
      const row = btn.closest("tr");
      const id = btn.dataset.id;

      if (!id) {
        alert("Transaction ID missing!");
        return;
      }

      // Fill modal with row data
      document.getElementById("transactionId").value = id;
      document.getElementById("categoryInput").value = row.children[0].innerText;
      document.getElementById("dateInput").value = row.children[1].innerText;
      document.getElementById("amountInput").value = row.children[2].innerText;
      document.getElementById("paymentInput").value = row.children[3].innerText;
      statusInput.value = row.children[4].innerText;

      // Highlight correct status button
      statusButtons.forEach(b => b.classList.remove("selected"));
      if (row.children[4].innerText === "Cash In") {
        document.querySelector(".cash-in").classList.add("selected");
      } else {
        document.querySelector(".cash-out").classList.add("selected");
      }

      // Switch form to edit mode
      modalTitle.textContent = "Edit Transaction";
      form.action = `/edit_transaction/${id}`;
      modal.style.display = "block";

      console.log("Editing transaction ID:", id);
      console.log("Form action:", form.action);
    });
  });

  // --- Delete Transaction ---
  document.querySelectorAll(".deleteBtn").forEach(btn => {
    btn.addEventListener("click", () => {
      const id = btn.dataset.id;
      if (confirm("Are you sure you want to delete this transaction?")) {
        fetch(`/delete_transaction/${id}`, {
          method: "POST",
          headers: { "Content-Type": "application/json" }
        })
        .then(res => res.json())
        .then(data => {
          if (data.success) {
            btn.closest("tr").remove();
            alert("✅ Transaction deleted successfully!");
          } else {
            alert("❌ Error deleting transaction");
          }
        })
        .catch(err => console.error("Delete failed:", err));
      }
    });
  });
});

// --- Close Modal ---
function closeModal() {
  document.getElementById("addTransactionModal").style.display = "none";
}
