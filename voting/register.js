document.addEventListener('DOMContentLoaded', function() {
    const form = document.querySelector('#registrationForm');
    const pass = document.querySelector('#pass');
    const conpass = document.querySelector('#conpass');

    form.addEventListener('submit', function(event) {
        event.preventDefault();
        if (pass !== conpass) {
            alert('Password do not match!');
            return; 
        }
        window.location.href = 'otp.html';
    });
});
