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

document.getElementById("loginForm").addEventListener("submit", function (e) {
    e.preventDefault();

    const email = document.getElementById("email").value.trim();
    const password = document.getElementById("password").value.trim();
    const role = document.getElementById("role").value;

    if (!email || !password || !role) {
        alert("Please fill all fields");
        return;
    }

    fetch("http://127.0.0.1:5000/login", {
        method: "POST",
        headers: {
            "Content-Type": "application/json"
        },
        body: JSON.stringify({
            username: email,
            password: password,
            role: role
        })
    })
    .then(response => response.json())
    .then(data => {

        if (data.error) {
            alert(data.error);
            return;
        }

        // Store token and role
        localStorage.setItem("token", data.token);
        localStorage.setItem("role", data.role);

        if (data.role === "admin") {
            window.location.href = "AdminDashboard.html";
        } else {
            window.location.href = "StudentDashboard.html";
        }
    })
    .catch(error => {
        console.error("Error:", error);
        alert("Server error. Please try again.");
    });
});
