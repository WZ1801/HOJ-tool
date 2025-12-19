let isRunning = false;
let isAiLoggedIn = false;
let logUpdateInterval = null;

function showModal(message, type = "success") {
    const modal = document.getElementById("modal");
    const modalOverlay = document.getElementById("modalOverlay");
    const modalContent = document.getElementById("modalContent");
    const modalIcon = document.getElementById("modalIcon");

    if (!modal || !modalOverlay || !modalContent || !modalIcon) {
        console.warn("Modal elements not found");
        return;
    }

    modalContent.textContent = message;
    modal.className = `modal ${type}`;
    modalIcon.className = `bi ${type === "success" ? "bi-check-circle" : "bi-x-circle"
        }`;

    modalOverlay.classList.add("show");
    setTimeout(() => {
        modal.classList.add("show");
    }, 10);

    modalOverlay.onclick = (e) => {
        if (e.target === modalOverlay) {
            closeModal();
        }
    };

    const escHandler = (e) => {
        if (e.key === "Escape") {
            closeModal();
            document.removeEventListener("keydown", escHandler);
        }
    };
    document.addEventListener("keydown", escHandler);
}

function closeModal() {
    const modal = document.getElementById("modal");
    const modalOverlay = document.getElementById("modalOverlay");

    if (!modal || !modalOverlay) {
        return;
    }

    modal.classList.remove("show");
    setTimeout(() => {
        modalOverlay.classList.remove("show");
        modalOverlay.onclick = null;
    }, 300);
}

async function checkConfig() {
    try {
        const response = await fetch("/api/config_ok");
        const result = await response.json();

        if (result.status !== "success") {
            showConfigErrorModal("配置文件错误: " + result.msg);
        }
    } catch (error) {
        console.error("检查配置文件时发生错误:", error);
        showConfigErrorModal("检查配置文件时发生错误: " + error.message);
    }
}

function showConfigErrorModal(message) {
    const modal = document.getElementById("modal");
    const modalOverlay = document.getElementById("modalOverlay");
    const modalContent = document.getElementById("modalContent");
    const modalIcon = document.getElementById("modalIcon");

    if (!modal || !modalOverlay || !modalContent || !modalIcon) {
        alert(message);
        return;
    }

    const modalActions = document.querySelector(".modal-actions");
    if (modalActions) {
        modalActions.remove();
    }

    const actionsDiv = document.createElement("div");
    actionsDiv.className = "modal-actions";

    const confirmButton = document.createElement("button");
    confirmButton.className = "modal-button primary";
    confirmButton.textContent = "确认";
    confirmButton.onclick = function () {
        location.reload()
    };

    actionsDiv.appendChild(confirmButton);

    modalContent.textContent = message;
    modal.className = "modal error";
    modalIcon.className = "bi bi-x-circle";

    modal.appendChild(actionsDiv);

    modalOverlay.classList.add("show");
    setTimeout(() => {
        modal.classList.add("show");
    }, 10);

    modalOverlay.onclick = (e) => {
        if (e.target === modalOverlay) {
            closeModal();
            location.reload()
        }
    };

    const escHandler = (e) => {
        if (e.key === "Escape") {
            closeModal();
            location.reload()
            document.removeEventListener("keydown", escHandler);
        }
    };
    document.addEventListener("keydown", escHandler);
}

function updateStatus() {
    fetch("/api/auto_solver/status")
        .then((response) => response.json())
        .then((data) => {
            isRunning = data.is_running;
            isAiLoggedIn = data.is_login_360ai;

            const runningStatus = document.getElementById("runningStatus");
            const aiLoginStatus = document.getElementById("aiLoginStatus");
            const stopButton = document.getElementById("stopButton");
            const statusSection = document.getElementById("statusSection");

            if (runningStatus)
                runningStatus.textContent = isRunning ? "运行中" : "未运行";
            if (aiLoginStatus)
                aiLoginStatus.textContent = isAiLoggedIn ? "已登录" : "未登录";
            if (stopButton) stopButton.disabled = !isRunning;

            if (statusSection) {
                if (isRunning) {
                    statusSection.classList.add("running");
                } else {
                    statusSection.classList.remove("running");
                }
            }
        })
        .catch((error) => {
            console.error("获取状态失败:", error);
        });
}

function updateLogs() {
    fetch("/api/auto_solver/get_logs")
        .then((response) => response.json())
        .then((data) => {
            if (data.status === "success" && data.log) {
                const logContainer = document.getElementById("logContainer");
                const logContent = document.querySelector(".log-content");

                if (!logContainer || !logContent) {
                    return;
                }

                let logs;
                try {
                    logs = JSON.parse(data.log);
                } catch (e) {
                    logContent.innerHTML += data.log.split("\\n").join("<br>");
                    logContainer.scrollTop = logContainer.scrollHeight;
                    return;
                }

                logs.forEach((logEntry) => {
                    const logElement = document.createElement("div");
                    logElement.textContent = logEntry.message;
                    logElement.classList.add("log-entry", logEntry.type);

                    switch (logEntry.type) {
                        case "success":
                            logElement.style.color = "#28a745";
                            logElement.style.fontWeight = "bold";
                            break;
                        case "error":
                            logElement.style.color = "#dc3545";
                            logElement.style.fontWeight = "bold";
                            break;
                        case "warning":
                            logElement.style.color = "#ffc107";
                            logElement.style.fontWeight = "bold";
                            break;
                        case "info":
                            logElement.style.color = "#17a2b8";
                            logElement.style.fontWeight = "bold";
                            break;
                        case "debug":
                            logElement.style.color = "#6c757d";
                            logElement.style.fontWeight = "bold";
                            break;
                        default:
                            logElement.style.fontWeight = "bold";
                    }

                    logContent.appendChild(logElement);
                });

                logContainer.scrollTop = logContainer.scrollHeight;
            }
        })
        .catch((error) => {
            console.error("获取日志失败:", error);
        });
}

function createLoginButton() {
    const container = document.getElementById("loginButtonContainer");
    if (!container) {
        return;
    }

    if (!document.getElementById("loginButton")) {
        const button = document.createElement("button");
        button.id = "loginButton";
        button.className = "button success";
        button.onclick = confirmAiLogin;
        button.innerHTML = '<i class="bi bi-check-circle"></i> 已完成AI登录';
        container.appendChild(button);
    }
}

async function startProblemSolver() {
    if (isRunning) {
        showModal("当前有任务正在运行", "error");
        return;
    }

    createLoginButton();
    const pids = document.getElementById("problemIds").value.trim();
    if (!pids) {
        showModal("请输入题目ID", "error");
        return;
    }

    try {
        const response = await fetch("/api/auto_solver/problem_code", {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
            },
            body: JSON.stringify({
                pids: pids,
                notes: document.getElementById("problemNotes").value,
            }),
        });

        const result = await response.json();
        if (result.status === "success") {
            showModal("已启动刷题任务，请在弹出的浏览器窗口中登录360BOT", "success");
            startStatusUpdate();
        } else {
            showModal("启动失败：" + result.msg, "error");
        }
    } catch (error) {
        showModal("启动失败：" + error.message, "error");
    }
}

async function startTrainingSolver() {
    if (isRunning) {
        showModal("当前有任务正在运行", "error");
        return;
    }

    createLoginButton();
    const tids = document.getElementById("trainingIds").value.trim();
    if (!tids) {
        showModal("请输入训练集ID", "error");
        return;
    }

    try {
        const response = await fetch("/api/auto_solver/training_code", {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
            },
            body: JSON.stringify({
                tids: tids,
                notes: document.getElementById("trainingNotes").value,
            }),
        });

        const result = await response.json();
        if (result.status === "success") {
            showModal("已启动刷题任务，请在弹出的浏览器窗口中登录360BOT", "success");
            startStatusUpdate();
        } else {
            showModal("启动失败：" + result.msg, "error");
        }
    } catch (error) {
        showModal("启动失败：" + error.message, "error");
    }
}

async function startAllSolver() {
    if (isRunning) {
        showModal("当前有任务正在运行", "error");
        return;
    }

    createLoginButton();
    try {
        const response = await fetch("/api/auto_solver/all_code");
        const result = await response.json();
        if (result.status === "success") {
            showModal("已启动刷题任务，请在弹出的浏览器窗口中登录360BOT", "success");
            startStatusUpdate();
        } else {
            showModal("启动失败：" + result.msg, "error");
        }
    } catch (error) {
        showModal("启动失败：" + error.message, "error");
    }
}

async function stopSolver() {
    try {
        const response = await fetch("/api/auto_solver/stop");
        const result = await response.json();
        if (result.status === "success") {
            showModal("正在停止刷题任务...", "success");
        } else {
            showModal("停止失败：" + result.msg, "error");
        }
    } catch (error) {
        showModal("停止失败：" + error.message, "error");
    }
}

function startStatusUpdate() {
    updateStatus();
    updateLogs();

    if (!logUpdateInterval) {
        logUpdateInterval = setInterval(() => {
            updateStatus();
            updateLogs();
        }, 1000);
    }
}

async function confirmAiLogin() {
    try {
        const response = await fetch("/api/auto_solver/login_360ai");
        const result = await response.json();
        if (result.status === "success") {
            showModal("已确认AI登录成功！", "success");

            updateStatus();

            const button = document.getElementById("loginButton");
            if (button) {
                button.remove();
            }
        } else {
            showModal("确认登录失败：" + result.msg, "error");
        }
    } catch (error) {
        showModal("确认登录失败：" + error.message, "error");
    }
}

document.addEventListener("DOMContentLoaded", function () {
    checkConfig();
    startStatusUpdate();
});
