// Borrow Modal
function openBorrowModal(bookId, bookTitle) {
  const modal = document.getElementById('borrowModal');
  modal.classList.remove('hidden');
  document.getElementById('borrowBookTitle').innerText = bookTitle;
  document.getElementById('borrowForm').action = `/borrow/${bookId}`;
}

function closeBorrowModal() {
  document.getElementById('borrowModal').classList.add('hidden');
  document.getElementById('borrowBookTitle').innerText = '';
  document.getElementById('borrowForm').reset();
}

// Return Modal
function openReturnModal(borrowId, bookTitle) {
  const modal = document.getElementById('returnModal');
  modal.classList.remove('hidden');
  document.getElementById('returnBookTitle').innerText = bookTitle;
  document.getElementById('returnForm').action = `/return/${borrowId}`;
}

function closeReturnModal() {
  document.getElementById('returnModal').classList.add('hidden');
  document.getElementById('returnBookTitle').innerText = '';
  document.getElementById('returnForm').reset();
}
