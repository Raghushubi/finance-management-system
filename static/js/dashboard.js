function redirectTo(page) {
    window.location.href = page;
}

function logout() {
    localStorage.removeItem('user');
}

const userInfo = document.getElementById('userInfo');
const user = JSON.parse(localStorage.getItem('user'));
if (user) {
    userInfo.innerHTML = <p>Welcome, <strong>${user.name}</strong></p>; 
} 