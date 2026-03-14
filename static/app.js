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
            
            // Update Navbar Profile
            document.getElementById("nav-avatar").src = `https://github.com/identicons/${currentUser.username}.png`;
            navActions.style.display = "flex";

            const repoRes = await fetch("/api/repos", { headers: { "Authorization": `Bearer ${token}` } });
            const repos = await repoRes.json();
            
            // Populate Sidebar Repos
            const renderSidebarRepos = (filter = "") => {
                const sidebarList = document.getElementById("repo-list-sidebar");
                sidebarList.innerHTML = "";
                const filtered = repos.filter(r => r.name.toLowerCase().includes(filter.toLowerCase()));
                filtered.forEach(repo => {
                    const item = document.createElement("a");
                    item.href = "#";
                    item.className = "sidebar-repo-item";
                    item.innerHTML = `<i class="fa-solid fa-book-bookmark"></i> ${repo.owner}/${repo.name}`;
                    item.addEventListener("click", (e) => {
                        e.preventDefault();
                        loadRepoView(repo.owner, repo.name);
                    });
                    sidebarList.appendChild(item);
                });
                if (filtered.length === 0) sidebarList.innerHTML = `<div style="font-size:12px; color:var(--text-muted); padding:8px 0;">No repositories found.</div>`;
            };
            
            renderSidebarRepos();

            // Sidebar Search logic
            const sidebarSearch = document.querySelector(".sidebar-input");
            sidebarSearch.addEventListener("input", (e) => renderSidebarRepos(e.target.value));

            // Populate Feed with Mock Activity
            const feed = document.getElementById("activity-feed");
            feed.innerHTML = "";
            const activities = [
                { user: "gokul-1998", action: "added a repository to", target: "smart_life", time: "3 hours ago", repo: "smart_ways_to_spend_less", stars: 1 },
                { user: "gokul-1998", action: "starred a repository", target: "smart_ways_to_spend_less", time: "3 hours ago", repo: "smart_ways_to_spend_less", stars: 1 }
            ];

            activities.forEach(act => {
                const item = document.createElement("div");
                item.className = "feed-item";
                item.innerHTML = `
                    <div class="feed-item-header">
                        <img src="https://github.com/identicons/${act.user}.png" class="avatar-sm">
                        <span><strong>${act.user}</strong> <span class="feed-action">${act.action}</span> <strong>${act.target}</strong></span>
                        <span class="text-muted" style="font-size:12px; margin-left:auto;">${act.time}</span>
                    </div>
                    <div class="feed-repo-card">
                        <div>
                            <strong style="color:var(--accent-color);">${act.user}/${act.repo}</strong>
                            <div style="font-size:12px; color:var(--text-muted); margin-top:4px;">${act.stars} star</div>
                        </div>
                        <button class="feed-star-btn"><i class="fa-regular fa-star"></i> Star</button>
                    </div>
                `;
                feed.appendChild(item);
            });

            // Auto-resize for Ask Textarea
            const askText = document.querySelector(".ask-box textarea");
            askText.addEventListener("input", () => {
                askText.style.height = "auto";
                askText.style.height = (askText.scrollHeight) + "px";
            });

        } catch (e) {
            console.error(e);
            localStorage.removeItem("token");
            showView("view-auth");
        }
    }

    // Modal Triggers
    const openNewRepo = () => document.getElementById("new-repo-modal").classList.remove("hidden");
    const dashNewBtn = document.getElementById("btn-create-repo-modal-dash");
    if (dashNewBtn) dashNewBtn.addEventListener("click", (e) => { e.preventDefault(); openNewRepo(); });

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
            const row = document.createElement("div");
            row.className = "list-row";
            row.style.flexDirection = "column";
            row.style.alignItems = "stretch";
            
            let mergeBtn = pr.state === "open" ? `<button class="btn btn-primary btn-sm btn-merge" data-id="${pr.id}" style="padding:4px 12px; margin-top:8px;"><i class="fa-solid fa-code-merge"></i> Merge Pull Request</button>` : `<span class="badge" style="background:var(--secondary-color); color:white; width:fit-content; margin-top:8px;">${pr.state.toUpperCase()}</span>`;
            
            row.innerHTML = `
                <div style="display:flex; gap:12px;">
                    <div class="list-icon" style="color:#a371f7;"><i class="fa-solid fa-code-pull-request"></i></div>
                    <div class="list-content">
                        <h4 style="margin-bottom:4px;">${pr.title}</h4>
                        <div class="list-meta">#${pr.id} opened by ${pr.author} • branch: ${pr.branch_name}</div>
                        ${pr.state === "open" ? `<div class="pr-preview-box glass-panel" style="margin-top:12px; padding:12px; font-size:13px; border:1px solid rgba(255,255,255,0.05); background:rgba(0,0,0,0.2);">
                            <div style="color:var(--text-muted); margin-bottom:8px; border-bottom:1px solid var(--border-color); padding-bottom:4px;">AI Code Review</div>
                            <div style="font-style:italic; margin-bottom:12px;">"${pr.ai_review || "No review available."}"</div>
                            <div style="color:var(--text-muted); margin-bottom:4px;">Target File: <code style="color:var(--accent-color);">${pr.target_path}</code></div>
                            ${mergeBtn}
                        </div>` : mergeBtn}
                    </div>
                </div>
            `;
            
            const btn = row.querySelector(".btn-merge");
            if (btn) {
                btn.addEventListener("click", async () => {
                    if (!confirm("Are you sure you want to merge these AI changes? This will overwrite the source file.")) return;
                    btn.disabled = true;
                    btn.textContent = "Merging...";
                    const mRes = await fetch(`/api/repos/${currentRepo.owner}/${currentRepo.name}/prs/${pr.id}/merge`, {
                        method: "POST",
                        headers: { "Authorization": `Bearer ${token}` }
                    });
                    if (mRes.ok) {
                        alert("PR Merged successfully!");
                        fetchPRs(); fetchFiles(); fetchIssues();
                    } else alert("Merge failed.");
                });
            }
            
            list.appendChild(row);
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
