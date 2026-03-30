document.getElementById("forgotForm").addEventListener("submit", function (e) {

    e.preventDefault();

    const email = document.getElementById("email").value.trim();
    const password = document.getElementById("password").value.trim();

    if (!email || !password) {
        alert("All fields required");
        return;
    }

    if (!email.includes("@")) {
        alert("Enter valid email");
        return;
    }

    if (password.length < 4) {
        alert("Password must be at least 4 characters");
        return;
    }

    fetch("http://127.0.0.1:5000/forgot-password", {
        method: "POST",
        headers: {
            "Content-Type": "application/json"
        },
        body: JSON.stringify({
            username: email,
            password: password
        })
    })
    .then(res => {
        if (!res.ok) throw new Error();
        return res.json();
    })
    .then(() => {
        alert("Password updated successfully");
        window.location.href = "Login.html";
    })
    .catch(() => {
        alert("User not found");
    });

});