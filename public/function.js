var Password = document.getElementById("password");
var Confirm_Password = document.getElementById("confirm-password");

// Verify if Password is the same as Confirm Password
function PasswordIsEqual() {
  if (Password.value != Confirm_Password.value) {
    Confirm_Password.setCustomValidity("Password don't match");
  } else {
    Confirm_Password.setCustomValidity("");
  }
}

Password.onchange = PasswordIsEqual;
Confirm_Password.onkeyup = PasswordIsEqual;

function IsValid(name) {
  if (name.checkValidity()) {
    name.classList.add("InputField");
  } else {
    name.classList.remove("InputField");
  }
}

Password.onchange = function () {
  IsValid(Password);
};
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
