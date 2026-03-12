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
            headers: { "Authorization": token }
        })
        .then(res => res.json())
        .then(data => {

            tableBody.innerHTML = "";

            data.projects.forEach((p, index) => {

                let statusClass = p.status.toLowerCase().replace(/\s+/g, "-");

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

            if(data.attempt_count >= 5 && !data.is_locked){
                aiBtn.style.display = "block";
            } 
            else{
                aiBtn.style.display = "none";
            }

        });

    }

    loadProjects();

    aiBtn.addEventListener("click", function(){

        fetch("http://127.0.0.1:5000/ai/recommend", {
            method: "POST",
            headers: { "Authorization": token }
        })
        .then(res => res.json())
        .then(data => {
            loadProjects();
        });

    });

});

function logout(){
    localStorage.clear();
    window.location.href = "Login.html";
}