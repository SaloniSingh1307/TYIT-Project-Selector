// ===== Toggle Password Visibility =====
function togglePassword(id, toggleId) {
    const password = document.getElementById(id);
    const toggle = document.getElementById(toggleId);

    if (password.type === "password") {
        password.type = "text";
        toggle.textContent = "🔒";
    } else {
        password.type = "password";
        toggle.textContent = "👁️";
    }
}

document.getElementById("registerForm").addEventListener("submit", function (e) {

    e.preventDefault();

    const rollno = document.getElementById("rollno").value;
    const email = document.getElementById("email").value;
    const password = document.getElementById("password").value;
    const confirm = document.getElementById("confirm_password").value;

    if(password !== confirm){
        alert("Passwords do not match");
        return;
    }

    fetch("http://127.0.0.1:5000/register",{

        method:"POST",
        headers:{
            "Content-Type":"application/json"
        },
        body:JSON.stringify({
            rollno:rollno,
            username:email,
            password:password
        })

    })
    .then(res=>res.json())
    .then(data=>{

        if(data.error){
            alert(data.error);
            return;
        }

        alert("Registration successful");
        window.location.href="Login.html";

    });

});