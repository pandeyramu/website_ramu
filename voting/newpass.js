document.addEventListener('DOMContentLoaded', function () {
    const resetForm = document.getElementById('resetForm');

    resetForm.addEventListener('submit', function (event) {
        event.preventDefault();

        const email = document.getElementById('email').value;
        const newpass = document.getElementById('pass').value;
        window.location.href = 'login.html';
    });
});
