const expenseModal = document.getElementById('expenseModal');
const expenseTable = document.getElementById('expenseTable');

function showModal() {
    expenseModal.classList.add('active');
}

function closeModal() {
    expenseModal.classList.remove('active');
}

function addExpense() {
    const category = document.getElementById('category').value;
    const amount = document.getElementById('amount').value;
    const date = document.getElementById('date').value;

    if (category && amount && date) {
        const row = `<tr>
            <td>${category}</td>
            <td>${amount}</td>
            <td>${date}</td>
            <td><button onclick="deleteRow(this)">Delete</button></td>
        </tr>`;
        expenseTable.innerHTML += row;
        closeModal();
    } else {
        alert('All fields are required!');
    }
}

function deleteRow(button) {
    const row = button.parentElement.parentElement;
    expenseTable.removeChild(row);
}

function redirectTo(page) {
    window.location.href = page;
}
