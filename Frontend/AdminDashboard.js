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
        headers: { "Authorization": token }
    })
    .then(res => res.json())
    .then(data => {

        tableBody.innerHTML = "";

        data.forEach((p, index) => {

            let action = "-";

            if (p.status === "Under Review" && !p.is_ai_generated) {
                action = `
                    <button class="action-btn approve" onclick="approve(${p.project_id})">Approve</button>
                    <button class="action-btn reject" onclick="reject(${p.project_id})">Reject</button>
                `;
            }

            const statusClass = getStatusClass(p.status);

            tableBody.innerHTML += `
                <tr>
                    <td>${index + 1}</td>
                    <td>${p.rollno}</td>
                    <td>${p.title}</td>
                    <td>${p.description}</td>
                    <td><span class="status ${statusClass}">${p.status}</span></td>
                    <td>${p.created_at}</td>
                    <td>${action}</td>
                </tr>
            `;
        });

    });

}

loadProjects();

function approve(id) {

    fetch(`http://127.0.0.1:5000/admin/approve/${id}`, {
        method: "POST",
        headers: { "Authorization": token }
    })
    .then(() => loadProjects());

}

function reject(id) {

    fetch(`http://127.0.0.1:5000/admin/reject/${id}`, {
        method: "POST",
        headers: { "Authorization": token }
    })
    .then(() => loadProjects());

}

document.getElementById("exportCsvBtn").onclick = function () {

    fetch("http://127.0.0.1:5000/admin/download", {
        headers: { "Authorization": token }
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