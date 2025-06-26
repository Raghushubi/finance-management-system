function redirectTo(page) {
    window.location.href = page;
}

function logout() {
    localStorage.removeItem('user');
}