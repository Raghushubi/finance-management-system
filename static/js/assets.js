function redirectTo(page) {
    window.location.href = page;
}

function showAddAssetModal() {
    const modal = document.getElementById('addAssetModal');
    modal.classList.add('active');
    document.body.insertAdjacentHTML('beforeend', '<div class="modal-backdrop"></div>');
    const backdrop = document.querySelector('.modal-backdrop');
    backdrop.classList.add('active');
}

function closeAddAssetModal() {
    const modal = document.getElementById('addAssetModal');
    modal.classList.remove('active');
    const backdrop = document.querySelector('.modal-backdrop');
    if (backdrop) {
        backdrop.remove();
    }
}

function addNewAsset(e) {
    e.preventDefault();

    const formData = {
        assetType: document.getElementById('assetType').value,
        assetValue: document.getElementById('assetValue').value,
        purchaseDate: document.getElementById('purchaseDate').value
    };

    fetch('/add_asset', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify(formData)
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            // Refresh the page to show the new asset
            window.location.reload();
        } else {
            alert(data.message || 'Error adding asset');
        }
    })
    .catch(error => {
        console.error('Error:', error);
        alert('An error occurred while adding the asset');
    });
}

document.getElementById('addAssetForm').addEventListener('submit', addNewAsset);

function logout() {
    localStorage.removeItem('user');
}