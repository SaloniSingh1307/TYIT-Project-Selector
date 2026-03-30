document.addEventListener("DOMContentLoaded", function () {

    const token = localStorage.getItem("token");
    const role = localStorage.getItem("role");
    const form = document.getElementById("projectForm");

    if (!token || role !== "student") {
        alert("Please login again");
        window.location.href = "Login.html";
        return;
    }

    form.addEventListener("submit", function (e) {

        e.preventDefault();

        const title1 = document.getElementById("title1").value.trim();
        const desc1 = document.getElementById("desc1").value.trim();

        const title2 = document.getElementById("title2").value.trim();
        const desc2 = document.getElementById("desc2").value.trim();

        const title3 = document.getElementById("title3").value.trim();
        const desc3 = document.getElementById("desc3").value.trim();

        // ✅ REQUIRED VALIDATION
        if (!title1 || !desc1 || !title2 || !desc2 || !title3 || !desc3) {
            alert("All fields are required");
            return;
        }

        // ✅ LENGTH VALIDATION
        if (title1.length < 5 || title2.length < 5 || title3.length < 5) {
            alert("Each title must be at least 5 characters");
            return;
        }

        if (desc1.length < 15 || desc2.length < 15 || desc3.length < 15) {
            alert("Each description must be at least 15 characters");
            return;
        }

        // ✅ DUPLICATE CHECK
        if (title1 === title2 || title1 === title3 || title2 === title3) {
            alert("Project titles must be different");
            return;
        }

        // ✅ CLEAN DATA
        const projects = [
            { title: title1, description: desc1 },
            { title: title2, description: desc2 },
            { title: title3, description: desc3 }
        ];

        // ✅ SUBMIT
        fetch("http://127.0.0.1:5000/projects", {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
                "Authorization": "Bearer " + token
            },
            body: JSON.stringify({ projects: projects })
        })
        .then(res => {
            if (!res.ok) throw new Error();
            return res.json();
        })
        .then(() => {
            alert("Projects submitted successfully!");
            window.location.href = "StudentDashboard.html";
        })
        .catch(() => {
            alert("Submission failed");
        });

    });

});