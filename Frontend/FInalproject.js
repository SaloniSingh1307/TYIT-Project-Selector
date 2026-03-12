document.addEventListener("DOMContentLoaded", function () {

    const token = localStorage.getItem("token");
    const role = localStorage.getItem("role");
    const message = document.getElementById("message");
    const form = document.getElementById("projectForm");

    if (!token || role !== "student") {
        alert("Session expired. Please login again.");
        window.location.href = "Login.html";
        return;
    }

    fetch("http://127.0.0.1:5000/student/projects", {
        method: "GET",
        headers: {
            "Authorization": token
        }
    })
    .then(res => {
        if(res.status === 401){
            localStorage.clear();
            window.location.href = "Login.html";
        }
        return res.json();
    })
    .then(data => {

        if (data.is_locked) {
            message.textContent = "Final project selected. You cannot submit again.";
            form.style.display = "none";
            return;
        }

        if (data.attempt_count >= 5) {
            message.textContent = "You have used all 5 attempts. Please use AI recommendation.";
            form.style.display = "none";
            return;
        }

    })
    .catch(() => {
        message.textContent = "Error checking submission status.";
    });

    form.addEventListener("submit", function (e) {

        e.preventDefault();

        const projects = [
            {
                title: document.getElementById("title1").value,
                description: document.getElementById("desc1").value
            },
            {
                title: document.getElementById("title2").value,
                description: document.getElementById("desc2").value
            },
            {
                title: document.getElementById("title3").value,
                description: document.getElementById("desc3").value
            }
        ];

        fetch("http://127.0.0.1:5000/projects", {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
                "Authorization": token
            },
            body: JSON.stringify({ projects: projects })
        })
        .then(res => res.json())
        .then(data => {

            if (data.error) {
                alert(data.error);
                return;
            }

            alert("Projects submitted successfully!");
            window.location.href = "StudentDashboard.html";
        })
        .catch(() => {
            alert("Server error. Please try again.");
        });

    });

});