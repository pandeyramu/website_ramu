function generateOTP() {
    let otp= '';
    for (let i=0;i<6;i++){
        otp+= Math.floor(Math.random()*10);
    }
    return(otp);
}
let otp = generateOTP();
console.log("Generated OTP:", otp);
document.addEventListener('DOMContentLoaded', function() {
    const btn = document.querySelector('#btn');
    const num = document.querySelectorAll('input[type="text"]');
    btn.addEventListener("click", function(event) {
        event.preventDefault();
        let Enteredotp = '';
        num.forEach(function(input) {
            Enteredotp+= input.value.trim();
        });
        if(Enteredotp!==otp)
            {
                alert('OTP doesnt match');
            }
            else{
        window.location.href = 'newpass.html';
            }
    });
});