document.addEventListener("DOMContentLoaded", () => {
    // Auth elements
    const authView = document.getElementById("view-auth");
    const dashboardView = document.getElementById("view-dashboard");
    const repoView = document.getElementById("view-repo");
    const navUsername = document.getElementById("nav-username");
    const navActions = document.getElementById("nav-actions");
    const authUsernameInput = document.getElementById("auth-username");
    const authPasswordInput = document.getElementById("auth-password");
    const authMsg = document.getElementById("auth-msg");

    let currentRepo = null;
    let currentUser = null;

    // View Navigation
    function showView(viewId) {
        document.querySelectorAll(".view").forEach(v => {
            v.classList.remove("active-view");
            v.classList.add("hidden");
        });
        const target = document.getElementById(viewId);
        target.classList.remove("hidden");
        target.classList.add("active-view");
    }

    document.getElementById("nav-home").addEventListener("click", () => {
        if (localStorage.getItem("token")) loadDashboard();
        else showView("view-auth");
    });

    document.getElementById("btn-logout").addEventListener("click", () => {
        localStorage.removeItem("token");
        currentUser = null;
        navActions.style.display = "none";
        navUsername.textContent = "AIHub";
        showView("view-auth");
    });

    // --- Authentication --- //
    document.getElementById("btn-login").addEventListener("click", async () => {
        const username = authUsernameInput.value;
        const password = authPasswordInput.value;
        try {
            const formData = new URLSearchParams();
            formData.append('username', username);
            formData.append('password', password);
            const res = await fetch("/api/auth/login", {
                method: "POST",
                headers: { "Content-Type": "application/x-www-form-urlencoded" },
                body: formData
            });
            if (!res.ok) throw new Error("Invalid credentials");
            const data = await res.json();
            localStorage.setItem("token", data.access_token);
            authUsernameInput.value = "";
            authPasswordInput.value = "";
            loadDashboard();
        } catch (e) {
            authMsg.textContent = e.message;
        }
    });

    document.getElementById("btn-signup").addEventListener("click", async () => {
        const username = authUsernameInput.value;
        const password = authPasswordInput.value;
        try {
            const res = await fetch("/api/auth/signup", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ username, password })
            });
            if (!res.ok) throw new Error("Username already taken");
            authMsg.style.color = "var(--primary-color)";
            authMsg.textContent = "Account created! You can now log in.";
        } catch (e) {
            authMsg.style.color = "var(--danger-color)";
            authMsg.textContent = e.message;
        }
    });

    // --- Dashboard --- //
    async function loadDashboard() {
        showView("view-dashboard");
        try {
            const token = localStorage.getItem("token");
            const meRes = await fetch("/api/me", { headers: { "Authorization": `Bearer ${token}` } });
            if (!meRes.ok) throw new Error("Not authenticated");
            currentUser = await meRes.json();
            navUsername.textContent = currentUser.username;
            navActions.style.display = "block";

            // Populate Sidebar Profile
            document.getElementById("profile-name").textContent = currentUser.username;
            document.getElementById("profile-login").textContent = currentUser.username;

            const repoRes = await fetch("/api/repos", { headers: { "Authorization": `Bearer ${token}` } });
            const repos = await repoRes.json();
            
            document.getElementById("repo-count-badge").textContent = repos.length;
            
            const list = document.getElementById("repo-list");
            list.innerHTML = "";
            repos.forEach(repo => {
                const card = document.createElement("div");
                card.className = "repo-list-item";
                card.innerHTML = `
                    <div style="flex-grow: 1;">
                        <div style="display: flex; align-items: center; gap: 8px; margin-bottom: 4px;">
                            <h3 style="color: var(--accent-color); font-size: 20px; font-weight: 600; cursor: pointer;">${repo.name}</h3>
                            <span class="badge public" style="font-size: 12px; border-radius: 2em; padding: 0 7px; color: var(--text-muted); border: 1px solid var(--border-color);">${repo.visibility}</span>
                        </div>
                        <p style="color: var(--text-muted); font-size: 14px; margin-bottom: 16px;">${repo.description || "No description provided."}</p>
                        <div style="display: flex; gap: 16px; font-size: 12px; color: var(--text-muted); align-items: center;">
                            <span style="display:flex; align-items:center; gap:4px;"><span style="width:12px; height:12px; border-radius:50%; background-color:#3fb950; display:inline-block;"></span>${repo.language}</span>
                            <span><i class="fa-regular fa-star"></i> ${repo.stars}</span>
                            <span><i class="fa-solid fa-code-fork"></i> ${repo.forks}</span>
                            <span>Updated on ${repo.updated_at}</span>
                        </div>
                    </div>
                    <div>
                        <button class="btn btn-secondary" style="display:flex; align-items:center; gap:6px; padding: 3px 12px;"><i class="fa-regular fa-star"></i> Star</button>
                    </div>
                `;
                card.querySelector("h3").addEventListener("click", () => loadRepoView(repo.owner, repo.name));
                list.appendChild(card);
            });
            if (repos.length === 0) {
                list.innerHTML = `
                <div style="text-align: center; padding: 48px 0; border: 1px dashed var(--border-color); border-radius: 6px; margin-top: 16px;">
                    <h3 style="margin-bottom: 8px;">You don't have any public repositories yet.</h3>
                    <button class="btn btn-primary" onclick="document.getElementById('new-repo-modal').classList.remove('hidden')">Create a repository</button>
                </div>`;
            }
        } catch (e) {
            localStorage.removeItem("token");
            showView("view-auth");
        }
    }

    document.getElementById("btn-create-repo-modal").addEventListener("click", () => {
        document.getElementById("new-repo-modal").classList.remove("hidden");
    });

    document.getElementById("btn-create-repo").addEventListener("click", async () => {
        const name = document.getElementById("repo-name").value;
        const description = document.getElementById("repo-desc-input").value;
        const token = localStorage.getItem("token");
        const res = await fetch("/api/repos", {
            method: "POST",
            headers: { "Content-Type": "application/json", "Authorization": `Bearer ${token}` },
            body: JSON.stringify({ name, description })
        });
        if (res.ok) {
            document.getElementById("new-repo-modal").classList.add("hidden");
            loadDashboard();
        } else alert("Failed to create repo");
    });

    // --- REPO VIEW --- //
    async function loadRepoView(owner, name) {
        showView("view-repo");
        currentRepo = { owner, name };
        document.getElementById("repo-full-name").textContent = `${owner} / ${name}`;
        
        switchTab("code-tab");
        fetchFiles();
        fetchIssues();
        fetchPRs();
    }

    // Tabs
    const tabBtns = document.querySelectorAll(".tab-btn");
    const tabContents = document.querySelectorAll(".tab-content");

    function switchTab(targetId) {
        tabBtns.forEach(b => b.classList.remove("active"));
        tabContents.forEach(c => c.classList.remove("active"));
        document.querySelector(`[data-target="${targetId}"]`).classList.add("active");
        document.getElementById(targetId).classList.add("active");
    }

    tabBtns.forEach(btn => {
        btn.addEventListener("click", () => switchTab(btn.getAttribute("data-target")));
    });

    async function fetchFiles() {
        const token = localStorage.getItem("token");
        const res = await fetch(`/api/repos/${currentRepo.owner}/${currentRepo.name}/files`, { headers: { "Authorization": `Bearer ${token}` } });
        const files = await res.json();
        const list = document.getElementById("file-list");
        list.innerHTML = "";
        files.forEach(f => {
            list.innerHTML += `<div class="file-row"><i class="fa-regular fa-file-code"></i><span>${f}</span></div>`;
        });
    }

    async function fetchIssues() {
        const token = localStorage.getItem("token");
        const res = await fetch(`/api/repos/${currentRepo.owner}/${currentRepo.name}/issues`, { headers: { "Authorization": `Bearer ${token}` } });
        const issues = await res.json();
        const list = document.getElementById("issue-list");
        list.innerHTML = "";
        issues.forEach(i => {
            list.innerHTML += `<div class="list-row"><div class="list-icon"><i class="fa-regular fa-circle-dot"></i></div><div class="list-content"><h4>${i.title}</h4><div class="list-meta">#${i.id} opened by ${i.author}</div></div></div>`;
        });
        if (!issues.length) list.innerHTML = `<div class="loading">No issues.</div>`;
    }

    async function fetchPRs() {
        const token = localStorage.getItem("token");
        const res = await fetch(`/api/repos/${currentRepo.owner}/${currentRepo.name}/prs`, { headers: { "Authorization": `Bearer ${token}` } });
        const prs = await res.json();
        const list = document.getElementById("pr-list");
        list.innerHTML = "";
        prs.forEach(pr => {
            list.innerHTML += `<div class="list-row"><div class="list-icon"><i class="fa-solid fa-code-pull-request"></i></div><div class="list-content"><h4>${pr.title}</h4><div class="list-meta">#${pr.id} opened by ${pr.author}</div></div></div>`;
        });
        if (!prs.length) list.innerHTML = `<div class="loading">No PRs yet.</div>`;
    }

    // AI Issue Logic
    document.getElementById("btn-new-issue").addEventListener("click", () => {
        document.getElementById("issue-modal").classList.remove("hidden");
        document.getElementById("modal-actions").classList.remove("hidden");
        document.getElementById("ai-status").classList.add("hidden");
    });

    document.getElementById("btn-submit-issue").addEventListener("click", async () => {
        const title = document.getElementById("issue-title").value;
        const body = document.getElementById("issue-body").value;
        const token = localStorage.getItem("token");

        document.getElementById("modal-actions").classList.add("hidden");
        document.getElementById("ai-status").classList.remove("hidden");
        
        // Simulating the steps UI
        const updateClass = (id) => {
            document.querySelectorAll(".status-step").forEach(s => s.classList.remove("active"));
            document.getElementById(id).classList.add("active");
        };
        const markDone = (id) => document.getElementById(id).classList.add("done");

        updateClass("step-github");
        fetch(`/api/repos/${currentRepo.owner}/${currentRepo.name}/issues`, {
            method: "POST",
            headers: { "Content-Type": "application/json", "Authorization": `Bearer ${token}` },
            body: JSON.stringify({ title, body })
        });
        markDone("step-github");

        updateClass("step-reading");
        setTimeout(() => { markDone("step-reading"); updateClass("step-finding"); }, 1000);
        setTimeout(() => { markDone("step-finding"); updateClass("step-coding"); }, 3000);

        try {
            const prRes = await fetch(`/api/repos/${currentRepo.owner}/${currentRepo.name}/generate-pr`, {
                method: "POST",
                headers: { "Content-Type": "application/json", "Authorization": `Bearer ${token}` },
                body: JSON.stringify({ title, body })
            });
            const data = await prRes.json();
            markDone("step-coding"); updateClass("step-pr");
            
            setTimeout(() => {
                if (data.status === "success") {
                    alert("AI fixed it! PR URL: " + data.data.pull_request_url);
                    document.getElementById("issue-modal").classList.add("hidden");
                    fetchIssues(); fetchPRs(); fetchFiles(); // Refresh
                    switchTab("prs-tab");
                } else alert("AI failed: " + data.message);
            }, 1000);
        } catch(e) { alert("Error: " + e.message); }
    });

    // Auto-login check
    if (localStorage.getItem("token")) loadDashboard();
});
