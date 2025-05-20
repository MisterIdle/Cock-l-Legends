var Password = document.getElementById("password");
var Confirm_Password = document.getElementById("confirm-password");
var Email = document.getElementById("email");
var Username = document.getElementById("username");

function PasswordIsEqual() {
    if (Password.value !== Confirm_Password.value) {
        Confirm_Password.setCustomValidity("Les mots de passe ne correspondent pas");
    } else {
        Confirm_Password.setCustomValidity("");
    }
}

function IsValid(input) {
    if (input.checkValidity()) {
        input.classList.add("InputField");
    } else {
        input.classList.remove("InputField");
    }
}

Password.onchange = function () {
    PasswordIsEqual();
    IsValid(Password);
};

Confirm_Password.onkeyup = PasswordIsEqual;
Confirm_Password.onchange = function () {
    IsValid(Confirm_Password);
};

Email.onchange = function () {
    IsValid(Email);
};

Username.onchange = function () {
    IsValid(Username);
};

document.getElementById("myForm").addEventListener("submit", function (event) {
    if (
        !Password.checkValidity() ||
        !Confirm_Password.checkValidity() ||
        !Email.checkValidity() ||
        !Username.checkValidity()
    ) {
        event.preventDefault();
    }
});

function search() {
    const query = document.getElementById("search-bar").value;
    document.getElementById("results").innerHTML = `Résultats pour : ${query}`;
}


