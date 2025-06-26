const formTitle = document.getElementById('formTitle');
const toggleText = document.getElementById('toggleText');
const toggleForm = document.getElementById('toggleForm');
const submitButton = document.querySelector('button[type="submit"]');
const authForm = document.getElementById('authForm');
const usernameGroup = document.getElementById('usernameGroup');
const phoneNumbers = document.getElementById('phoneNumbers');
const addPhoneBtn = document.getElementById('addPhone');

toggleForm.addEventListener('click', (e) => {
    e.preventDefault();
    const isRegister = formTitle.textContent === 'Login';
    formTitle.textContent = isRegister ? 'Register' : 'Login';
    toggleText.textContent = isRegister ? 'Already have an account?' : "Don't have an account?";
    toggleForm.textContent = isRegister ? 'Login' : 'Register';
    submitButton.textContent = isRegister ? 'Register' : 'Login';
    usernameGroup.style.display = isRegister ? 'block' : 'none';
    phoneNumbers.style.display = isRegister ? 'block' : 'none';
    authForm.action = isRegister ? '/register' : '/login';
});

addPhoneBtn.addEventListener('click', () => {
    const phoneGroup = document.createElement('div');
    phoneGroup.className = 'form-group phone-group';
    phoneGroup.innerHTML = `
        <label>Phone Number</label>
        <input type="tel" class="phone" pattern="[0-9]{10}" maxlength="10">
        <button type="button" class="remove-phone">Remove</button>
    `;
    phoneNumbers.insertBefore(phoneGroup, addPhoneBtn);
});

phoneNumbers.addEventListener('click', (e) => {
    if (e.target.classList.contains('remove-phone')) {
        e.target.parentElement.remove();
    }
});

authForm.addEventListener('submit', async (e) => {
    e.preventDefault();
    const formData = {
        email: document.getElementById('email').value,
        password: document.getElementById('password').value
    };

    const isRegister = formTitle.textContent === 'Register';
    const endpoint = isRegister ? '/register' : '/login';
    
    if (isRegister) {
        formData.username = document.getElementById('username').value;
        formData.phones = [...document.querySelectorAll('.phone')].map(input => input.value).filter(Boolean);
    }

    try {
        const response = await fetch(endpoint, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(formData)
        });

        const result = await response.json();
        
        if (result.success) {
            window.location.href = "/dashboard";
        } else {
            alert(result.message || "Operation failed");
        }
    } catch (error) {
        console.error('Error:', error);
        alert("An error occurred. Please try again.");
    }
});