const password = document.getElementById("password");
const confirm_password = document.getElementById("confirm");

function validarPassword() {
    if (password.value !== confirm_password.value) {
        confirm_password.setCustomValidity("Las contraseñas no coinciden.");
    }
    else {
        confirm_password.setCustomValidity("");
    }
}

password.oninput = validarPassword;
confirm_password.oninput = validarPassword;