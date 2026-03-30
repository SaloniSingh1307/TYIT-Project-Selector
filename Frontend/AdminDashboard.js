const token = localStorage.getItem("token");
const role = localStorage.getItem("role");

if (!token || role !== "admin") {
    alert("Unauthorized");
    window.location.href = "Login.html";
}

const tableBody = document.getElementById("tableBody");

function getStatusClass(status) {
    return status.toLowerCase().replace(/\s+/g, "-");
}

function loadProjects() {

    fetch("http://127.0.0.1:5000/admin/projects", {
        headers: { "Authorization": "Bearer " + token }
    })
    .then(res => {
        if (!res.ok) throw new Error();
        return res.json();
    })
    .then(data => {

        tableBody.innerHTML = "";

        if (data.length === 0) {
            tableBody.innerHTML = "<tr><td colspan='7'>No projects</td></tr>";
            return;
        }

        data.forEach((p, index) => {

            let action = "-";

            if (p.status === "Under Review" && !p.is_ai_generated) {
                action = `
                    <button class="action-btn approve" onclick="approve(${p.project_id})">Approve</button>
     <button class="action-btn reject" onclick="reject(${p.project_id})">Reject</button>
                `;
            }

            tableBody.innerHTML += `
                <tr>
                    <td>${index + 1}</td>
                    <td>${p.rollno}</td>
                    <td>${p.title}</td>
                    <td>${p.description}</td>
                    <td>${p.status}</td>
                    <td>${p.created_at}</td>
                    <td>${action}</td>
                </tr>
            `;
        });

    })
    .catch(() => {
        tableBody.innerHTML = "<tr><td colspan='7'>Error loading data</td></tr>";
    });

}

loadProjects();
setInterval(loadProjects, 3000); // ✅ auto refresh

function approve(id) {

    if (!confirm("Approve this project?")) return;

    fetch(`http://127.0.0.1:5000/admin/approve/${id}`, {
        method: "POST",
        headers: { "Authorization": "Bearer " + token }
    })
    .then(() => loadProjects());

}

function reject(id) {

    if (!confirm("Reject this project?")) return;

    fetch(`http://127.0.0.1:5000/admin/reject/${id}`, {
        method: "POST",
        headers: { "Authorization": "Bearer " + token }
    })
    .then(() => loadProjects());

}

document.getElementById("exportCsvBtn").onclick = function () {

    fetch("http://127.0.0.1:5000/admin/download", {
        headers: { "Authorization": "Bearer " + token }
    })
    .then(res => res.blob())
    .then(blob => {

        const url = window.URL.createObjectURL(blob);
        const a = document.createElement("a");

        a.href = url;
        a.download = "projects.csv";
        a.click();

    });

}

function logout() {
    localStorage.clear();
    window.location.href = "Login.html";
}