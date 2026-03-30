document.addEventListener("DOMContentLoaded", function(){

    const token = localStorage.getItem("token");
    const role = localStorage.getItem("role");

    if(!token || role !== "student"){
        window.location.href = "Login.html";
    }

    const tableBody = document.getElementById("tableBody");
    const aiBtn = document.getElementById("aiBtn");

    function loadProjects(){

        fetch("http://127.0.0.1:5000/student/projects", {
            headers: { "Authorization": "Bearer " + token }
        })
        .then(res => {
            if (!res.ok) throw new Error();
            return res.json();
        })
        .then(data => {

            tableBody.innerHTML = "";

            if (data.projects.length === 0) {
                tableBody.innerHTML = "<tr><td colspan='5'>No projects found</td></tr>";
                return;
            }

            data.projects.forEach((p, index) => {

                let statusClass = p.is_ai_generated 
                    ? "ai-generated" 
                    : p.status.toLowerCase().replace(/\s+/g, "-");

                tableBody.innerHTML += `
                    <tr>
                        <td>${index+1}</td>
                        <td>${p.created_at}</td>
                        <td>${p.title}</td>
                        <td>${p.description}</td>
                        <td><span class="status ${statusClass}">${p.status}</span></td>
                    </tr>
                `;
            });

            // ✅ AI logic fixed
            aiBtn.style.display = data.all_rejected ? "block" : "none";

        })
        .catch(() => {
            tableBody.innerHTML = "<tr><td colspan='5'>Error loading data</td></tr>";
        });

    }

    loadProjects();
    setInterval(loadProjects, 3000); // ✅ auto refresh

    aiBtn.addEventListener("click", function(){

        fetch("http://127.0.0.1:5000/ai/recommend", {
            method: "POST",
            headers: { "Authorization": "Bearer " + token }
        })
        .then(res => {
            if (!res.ok) throw new Error();
            return res.json();
        })
        .then(() => {
            alert("AI Project Assigned");
            loadProjects();
        })
        .catch(() => alert("AI not allowed yet"));
    });

});

function logout(){
    localStorage.clear();
    window.location.href = "Login.html";
}