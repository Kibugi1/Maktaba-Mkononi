// dashboard-modals.js

// 📚 BOOK DETAILS MODAL
const bookModal = document.getElementById("bookModal");
const modalCloseBtns = document.querySelectorAll(".close-button");

modalCloseBtns.forEach(btn => {
  btn.addEventListener("click", () => {
    btn.closest(".modal").classList.add("hidden");
  });
});

// 📝 APPROVAL MODAL FUNCTIONS
function openApprovalModal(requestId, bookTitle) {
  const modal = document.getElementById('approval-modal');
  modal.classList.remove('hidden');
  document.getElementById('request_id').value = requestId;
  document.getElementById('approval-form').action = '/librarian/approve_borrow/' + requestId;
}

function closeModal() {
  document.getElementById('approval-modal').classList.add('hidden');
  document.getElementById('approval-form').reset();
}
