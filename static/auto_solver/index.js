// 全局状态
let isRunning = false;
let isAiLoggedIn = false;
let logUpdateInterval = null;

// 显示模态框
function showModal(message, type = 'success') {
    const modal = document.getElementById('modal');
    const modalOverlay = document.getElementById('modalOverlay');
    const modalContent = document.getElementById('modalContent');
    const modalIcon = document.getElementById('modalIcon');

    modalContent.textContent = message;
    modal.className = `modal ${type}`;
    modalIcon.className = `bi ${type === 'success' ? 'bi-check-circle' : 'bi-x-circle'}`;

    modalOverlay.classList.add('show');
    requestAnimationFrame(() => {
        modal.classList.add('show');
    });

    // 添加点击遮罩层关闭
    modalOverlay.onclick = (e) => {
        if (e.target === modalOverlay) {
            closeModal();
        }
    };

    // 添加ESC键关闭
    const escHandler = (e) => {
        if (e.key === 'Escape') {
            closeModal();
            document.removeEventListener('keydown', escHandler);
        }
    };
    document.addEventListener('keydown', escHandler);
}

// 关闭模态框
function closeModal() {
    const modal = document.getElementById('modal');
    const modalOverlay = document.getElementById('modalOverlay');
    
    modal.classList.remove('show');
    setTimeout(() => {
        modalOverlay.classList.remove('show');
        // 清除事件监听
        modalOverlay.onclick = null;
    }, 300);
}

// 检查配置文件
async function checkConfig() {
    try {
        const response = await fetch('/api/config_ok');
        const result = await response.json();
        
        if (result.status !== 'success') {
            // 显示错误信息并添加确认按钮
            showConfigErrorModal('配置文件错误: ' + result.msg);
        }
    } catch (error) {
        console.error('检查配置文件时发生错误:', error);
        showConfigErrorModal('检查配置文件时发生错误: ' + error.message);
    }
}

// 显示配置错误模态框
function showConfigErrorModal(message) {
    const modal = document.getElementById('modal');
    const modalOverlay = document.getElementById('modalOverlay');
    const modalContent = document.getElementById('modalContent');
    const modalIcon = document.getElementById('modalIcon');
    
    // 清空现有内容
    const modalActions = document.querySelector('.modal-actions');
    if (modalActions) {
        modalActions.remove();
    }
    
    // 创建新的操作按钮容器
    const actionsDiv = document.createElement('div');
    actionsDiv.className = 'modal-actions';
    
    const confirmButton = document.createElement('button');
    confirmButton.className = 'modal-button primary';
    confirmButton.textContent = '确认';
    confirmButton.onclick = function() {
        window.location.href = 'http://127.0.0.1:1146';
    };
    
    actionsDiv.appendChild(confirmButton);
    
    modalContent.textContent = message;
    modal.className = 'modal error';
    modalIcon.className = 'bi bi-x-circle';
    
    // 添加按钮到模态框
    modal.appendChild(actionsDiv);
    
    modalOverlay.classList.add('show');
    requestAnimationFrame(() => {
        modal.classList.add('show');
    });
    
    // 添加点击遮罩层关闭
    modalOverlay.onclick = (e) => {
        if (e.target === modalOverlay) {
            closeModal();
            window.location.href = 'http://127.0.0.1:1146';
        }
    };
    
    // 添加ESC键关闭
    const escHandler = (e) => {
        if (e.key === 'Escape') {
            closeModal();
            window.location.href = 'http://127.0.0.1:1146';
            document.removeEventListener('keydown', escHandler);
        }
    };
    document.addEventListener('keydown', escHandler);
}

// 更新状态显示
function updateStatus() {
    const runningStatus = document.getElementById('runningStatus');
    const aiLoginStatus = document.getElementById('aiLoginStatus');
    const stopButton = document.getElementById('stopButton');
    
    fetch('/api/auto_solver/status')
        .then(response => response.json())
        .then(data => {
            isRunning = data.is_running;
            isAiLoggedIn = data.is_login_360ai;
            
            runningStatus.textContent = isRunning ? '运行中' : '未运行';
            aiLoginStatus.textContent = isAiLoggedIn ? '已登录' : '未登录';
            stopButton.disabled = !isRunning;

            if (isRunning) {
                document.getElementById('statusSection').classList.add('running');
            } else {
                document.getElementById('statusSection').classList.remove('running');
            }
        })
        .catch(error => {
            console.error('获取状态失败:', error);
        });
}

// 更新日志显示
function updateLogs() {
    fetch('/api/auto_solver/get_logs')
        .then(response => response.json())
        .then(data => {
            if (data.status === 'success' && data.log) {
                const logContainer = document.getElementById('logContainer');
                const logContent = document.querySelector('.log-content');
                
                // 解析日志数据
                let logs;
                try {
                    logs = JSON.parse(data.log);
                } catch (e) {
                    // 如果解析失败，按原来的纯文本方式处理
                    logContent.innerHTML = data.log.split('\\n').join('<br>');
                    logContainer.scrollTop = logContainer.scrollHeight;
                    return;
                }
                
                // 清空现有内容
                logContent.innerHTML = '';
                
                // 为每条日志创建带颜色的元素
                logs.forEach(logEntry => {
                    const logElement = document.createElement('div');
                    logElement.textContent = logEntry.message;
                    logElement.classList.add('log-entry', logEntry.type);
                    
                    // 根据日志类型设置样式
                    switch (logEntry.type) {
                        case 'success':
                            logElement.style.color = '#28a745';
                            logElement.style.fontWeight = 'bold';
                            break;
                        case 'error':
                            logElement.style.color = '#dc3545';
                            logElement.style.fontWeight = 'bold';
                            break;
                        case 'warning':
                            logElement.style.color = '#ffc107';
                            logElement.style.fontWeight = 'bold';
                            break;
                        case 'info':
                            logElement.style.color = '#17a2b8';
                            logElement.style.fontWeight = 'bold';
                            break;
                        case 'debug':
                            logElement.style.color = '#6c757d';
                            logElement.style.fontWeight = 'bold';
                            break;
                        default:
                            logElement.style.fontWeight = 'bold';
                    }
                    
                    logContent.appendChild(logElement);
                });
                
                logContainer.scrollTop = logContainer.scrollHeight;
            }
        })
        .catch(error => {
            console.error('获取日志失败:', error);
        });
}

// 创建登录按钮
function createLoginButton() {
    const container = document.getElementById('loginButtonContainer');
    if (!document.getElementById('loginButton')) {
        const button = document.createElement('button');
        button.id = 'loginButton';
        button.className = 'button success';
        button.onclick = confirmAiLogin;
        button.innerHTML = '<i class="bi bi-check-circle"></i> 已完成AI登录';
        container.appendChild(button);
    }
}

// 开始刷个题
async function startProblemSolver() {
    if (isRunning) {
        showModal('当前有任务正在运行', 'error');
        return;
    }
    
    createLoginButton();
    const pids = document.getElementById('problemIds').value.trim();
    if (!pids) {
        showModal('请输入题目ID', 'error');
        return;
    }

    try {
        const response = await fetch('/api/auto_solver/problem_code', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                pids: pids,
                notes: document.getElementById('problemNotes').value
            })
        });

        const result = await response.json();
        if (result.status === 'success') {
            showModal('已启动刷题任务，请在弹出的浏览器窗口中登录360BOT', 'success');
            startStatusUpdate();
        } else {
            showModal('启动失败：' + result.msg, 'error');
        }
    } catch (error) {
        showModal('启动失败：' + error.message, 'error');
    }
}

// 开始刷训练题
async function startTrainingSolver() {
    if (isRunning) {
        showModal('当前有任务正在运行', 'error');
        return;
    }
    
    createLoginButton();
    const tids = document.getElementById('trainingIds').value.trim();
    if (!tids) {
        showModal('请输入训练集ID', 'error');
        return;
    }

    try {
        const response = await fetch('/api/auto_solver/training_code', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                tids: tids,
                notes: document.getElementById('trainingNotes').value
            })
        });

        const result = await response.json();
        if (result.status === 'success') {
            showModal('已启动刷题任务，请在弹出的浏览器窗口中登录360BOT', 'success');
            startStatusUpdate();
        } else {
            showModal('启动失败：' + result.msg, 'error');
        }
    } catch (error) {
        showModal('启动失败：' + error.message, 'error');
    }
}

// 开始刷全部题
async function startAllSolver() {
    if (isRunning) {
        showModal('当前有任务正在运行', 'error');
        return;
    }
    
    createLoginButton();
    try {
        const response = await fetch('/api/auto_solver/all_code');
        const result = await response.json();
        if (result.status === 'success') {
            showModal('已启动刷题任务，请在弹出的浏览器窗口中登录360BOT', 'success');
            startStatusUpdate();
        } else {
            showModal('启动失败：' + result.msg, 'error');
        }
    } catch (error) {
        showModal('启动失败：' + error.message, 'error');
    }
}

// 停止刷题
async function stopSolver() {
    try {
        const response = await fetch('/api/auto_solver/stop');
        const result = await response.json();
        if (result.status === 'success') {
            showModal('正在停止刷题任务...', 'success');
        } else {
            showModal('停止失败：' + result.msg, 'error');
        }
    } catch (error) {
        showModal('停止失败：' + error.message, 'error');
    }
}

// 开始状态更新
function startStatusUpdate() {
    // 立即更新一次状态
    updateStatus();
    updateLogs();

    // 设置定期更新
    if (!logUpdateInterval) {
        logUpdateInterval = setInterval(() => {
            updateStatus();
            updateLogs();
        }, 1000);
    }
}

// 确认AI登录
async function confirmAiLogin() {
    try {
        const response = await fetch('/api/auto_solver/login_360ai');
        const result = await response.json();
        if (result.status === 'success') {
            showModal('已确认AI登录成功！', 'success');
            // 立即更新状态显示
            updateStatus();
            // 移除登录按钮
            const button = document.getElementById('loginButton');
            if (button) {
                button.remove();
            }
        } else {
            showModal('确认登录失败：' + result.msg, 'error');
        }
    } catch (error) {
        showModal('确认登录失败：' + error.message, 'error');
    }
}

// 页面加载时初始化
document.addEventListener('DOMContentLoaded', function() {
    checkConfig();
    startStatusUpdate();
});