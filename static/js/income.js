const incomeTable = document.getElementById('incomeTable');

const income = [
    { source: 'Salary', amount: 5000, date: '2024-12-01' },
    { source: 'Freelancing', amount: 1500, date: '2024-12-03' },
];

function renderIncome() {
    incomeTable.innerHTML = '';
    income.forEach((item, index) => {
        const row = `
            <tr>
                <td>${item.source}</td>
                <td>${item.amount}</td>
                <td>${item.date}</td>
                <td><button onclick="deleteIncome(${index})">Delete</button></td>
            </tr>
        `;
        incomeTable.innerHTML += row;
    });
}

function deleteIncome(index) {
    income.splice(index, 1);
    renderIncome();
}

function redirectTo(page) {
    window.location.href = page;
}

renderIncome();
