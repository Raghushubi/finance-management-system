function showModal() {
    const modal = document.getElementById('transactionModal');
    if (modal) {
        modal.classList.add('active');
    }
}

// Close modal
function closeModal() {
    const modal = document.getElementById('transactionModal');
    if (modal) {
        modal.classList.remove('active');
        if (transactionForm) {
            transactionForm.reset();
        }
    }
}

// Add these event listeners to the existing DOMContentLoaded
document.addEventListener('DOMContentLoaded', () => {
    if (transactionForm) {
        transactionForm.addEventListener('submit', addTransaction);
        console.log('Transaction form handler attached');
    }
    
    // Modal close handlers
    const closeButtons = document.querySelectorAll('.close-modal');
    closeButtons.forEach(button => {
        button.addEventListener('click', closeModal);
    });

    window.addEventListener('click', (event) => {
        if (event.target === transactionModal) {
            closeModal();
        }
    });
});

// Transaction handling functionality with enhanced error logging
const transactionModal = document.getElementById('transactionModal');
const transactionTable = document.getElementById('transactionTable');
const transactionForm = document.getElementById('transactionForm');
const submitButton = document.getElementById('submitTransaction');

// Enhanced error logging function
function logError(stage, error) {
    console.error(`Transaction Error at ${stage}:`, error);
    console.error('Error details:', {
        message: error.message,
        stack: error.stack,
        response: error.response
    });
}

// Handle form submission with improved error handling
function addTransaction(event) {
    event.preventDefault();
    
    submitButton.disabled = true;
    
    // Validate form elements exist
    const category = document.getElementById('category');
    const type = document.getElementById('type');
    const amount = document.getElementById('amount');
    const date = document.getElementById('date');

    if (!category || !type || !amount || !date) {
        alert('Form elements not found. Please refresh the page.');
        submitButton.disabled = false;
        return;
    }

    const formData = {
        category: category.value,
        type: type.value,
        amount: parseFloat(amount.value),
        date: date.value
    };

    console.log('Submitting transaction with data:', formData);

    // Make API request to add transaction
    fetch('/add_transaction', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-Requested-With': 'XMLHttpRequest'
        },
        body: JSON.stringify(formData),
        credentials: 'same-origin'
    })
    .then(response => {
        console.log('Server response status:', response.status);
        
        if (response.redirected) {
            window.location.href = response.url;
            throw new Error('Session expired. Please login again.');
        }
        
        // Parse response even if it's an error
        return response.json().then(data => {
            if (!response.ok) {
                throw new Error(data.message || `Server error: ${response.status}`);
            }
            return data;
        });
    })
    .then(data => {
        if (data.success) {
            console.log('Transaction successful:', data);
            
            const formattedAmount = new Intl.NumberFormat('en-IN', {
                style: 'currency',
                currency: 'INR'
            }).format(formData.amount);

            const formattedDate = new Date(formData.date).toLocaleDateString('en-IN');

            // Add new row to table
            const newRow = document.createElement('tr');
            newRow.innerHTML = `
                <td>${formData.type}</td>
                <td>${formData.category}</td>
                <td>${formattedAmount}</td>
                <td>${formattedDate}</td>
            `;
            
            const tbody = transactionTable.querySelector('tbody') || transactionTable;
            tbody.insertBefore(newRow, tbody.firstChild);
            
            closeModal();
            showSuccessMessage('Transaction added successfully!');
        }
    })
    .catch((error) => {
        logError('API Request', error);
        
        // Show specific error message based on type
        let errorMessage = 'Error adding transaction. ';
        if (error.message.includes('Session expired')) {
            errorMessage = 'Your session has expired. Please login again.';
        } else if (error.message.includes('Database')) {
            errorMessage = 'Database error occurred. Please try again.';
        } else {
            errorMessage += error.message;
        }
        
        showErrorMessage(errorMessage);
    })
    .finally(() => {
        submitButton.disabled = false;
    });
}

// success message
function showSuccessMessage(message) {
    showMessage(message, 'success');
}

// error message
function showErrorMessage(message) {
    showMessage(message, 'error');
}

function showMessage(message, type) {
    const messageDiv = document.createElement('div');
    messageDiv.className = `alert alert-${type}`;
    messageDiv.textContent = message;
    
    const container = document.querySelector('.container');
    container.insertBefore(messageDiv, container.firstChild);
    
    setTimeout(() => messageDiv.remove(), 5000);
}

document.addEventListener('DOMContentLoaded', () => {
    if (transactionForm) {
        transactionForm.addEventListener('submit', addTransaction);
        console.log('Transaction form handler attached');
    } else {
        console.error('Transaction form not found in DOM');
    }
});