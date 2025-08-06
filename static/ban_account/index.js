let isBanning = false;
let logInterval = null;
let statusInterval = null; // 用于定期检查封禁状态

document.addEventListener('DOMContentLoaded', function() {
    // 初始化页面元素
    const banTypeAssign = document.querySelector('input[value="assign"]');
    const banTypeAll = document.querySelector('input[value="all"]');
    const assignSection = document.getElementById('assign_section');
    const allSection = document.getElementById('all_section');
    const startBanButton = document.getElementById('start_ban');
    const stopBanButton = document.getElementById('stop_ban');
    const logContainer = document.getElementById('log_container');
    
    // 创建状态显示元素
    const statusDisplay = document.createElement('div');
    statusDisplay.id = 'ban_status';
    statusDisplay.style.cssText = 'display: inline-block; margin-left: 10px; padding: 5px 10px; border-radius: 4px; font-weight: bold;';
    startBanButton.parentNode.appendChild(statusDisplay);

    // 检查配置文件
    checkConfig();

    // 切换封禁类型
    banTypeAssign.addEventListener('change', function() {
        if (this.checked) {
            assignSection.style.display = 'block';
            allSection.style.display = 'none';
        }
    });

    banTypeAll.addEventListener('change', function() {
        if (this.checked) {
            assignSection.style.display = 'none';
            allSection.style.display = 'block';
        }
    });

    // 开始封禁按钮事件
    startBanButton.addEventListener('click', startBan);

    // 停止封禁按钮事件
    stopBanButton.addEventListener('click', stopBan);

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
        // 创建模态框元素
        const modalOverlay = document.createElement('div');
        modalOverlay.className = 'modal-overlay show';
        modalOverlay.style.cssText = `
            position: fixed;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            background-color: rgba(0, 0, 0, 0.5);
            display: flex;
            justify-content: center;
            align-items: center;
            z-index: 10000;
        `;

        const modal = document.createElement('div');
        modal.className = 'modal error show';
        modal.style.cssText = `
            background: white;
            border-radius: 8px;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
            padding: 24px;
            min-width: 300px;
            max-width: 500px;
            text-align: center;
            position: relative;
            transform: scale(1);
            opacity: 1;
            transition: all 0.3s ease;
        `;

        const modalIcon = document.createElement('div');
        modalIcon.className = 'modal-icon';
        modalIcon.innerHTML = `<i class="bi bi-x-circle" style="font-size: 48px; color: #dc3545;"></i>`;
        modalIcon.style.cssText = 'margin-bottom: 16px;';

        const modalContent = document.createElement('div');
        modalContent.className = 'modal-content';
        modalContent.textContent = message;
        modalContent.style.cssText = 'margin-bottom: 20px;';

        const modalActions = document.createElement('div');
        modalActions.className = 'modal-actions';

        const confirmButton = document.createElement('button');
        confirmButton.className = 'modal-button primary';
        confirmButton.textContent = '确认';
        confirmButton.style.cssText = `
            background-color: #007bff;
            color: white;
            border: none;
            padding: 8px 16px;
            border-radius: 4px;
            cursor: pointer;
        `;
        confirmButton.onclick = function() {
            window.location.href = 'http://127.0.0.1:1146';
        };

        modalActions.appendChild(confirmButton);
        modal.appendChild(modalIcon);
        modal.appendChild(modalContent);
        modal.appendChild(modalActions);
        modalOverlay.appendChild(modal);
        document.body.appendChild(modalOverlay);

        // 添加点击遮罩层关闭
        modalOverlay.onclick = (e) => {
            if (e.target === modalOverlay) {
                document.body.removeChild(modalOverlay);
                window.location.href = 'http://127.0.0.1:1146';
            }
        };

        // 添加ESC键关闭
        const escHandler = (e) => {
            if (e.key === 'Escape') {
                if (document.body.contains(modalOverlay)) {
                    document.body.removeChild(modalOverlay);
                }
                window.location.href = 'http://127.0.0.1:1146';
                document.removeEventListener('keydown', escHandler);
            }
        };
        document.addEventListener('keydown', escHandler);
    }

    // 开始封禁功能
    function startBan() {
        if (isBanning) return;

        const banType = document.querySelector('input[name="ban_type"]:checked').value;
        
        // 清空日志容器
        logContainer.innerHTML = '';
        
        // 构造请求数据
        let requestData = {
            mode: banType
        };

        if (banType === 'assign') {
            const username = document.getElementById('username').value.trim();
            if (!username) {
                addLog('请输入要封禁的账号名称', 'error');
                return;
            }
            requestData.username = username;
        } else if (banType === 'all') {
            const whiteList = document.getElementById('white_list').value.trim();
            requestData.white_list = whiteList;
        }

        // 发送请求
        fetch('/api/ban_account/ban_account', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(requestData)
        })
        .then(response => response.json())
        .then(data => {
            if (data.status === 'success') {
                isBanning = true;
                startBanButton.style.display = 'none';
                stopBanButton.style.display = 'inline-block';
                addLog('开始执行封禁操作...', 'info');
                startLogPolling();
                updateBanStatus(); // 立即更新一次状态
            } else {
                addLog(`启动失败: ${data.msg}`, 'error');
            }
        })
        .catch(error => {
            addLog(`请求出错: ${error.message}`, 'error');
        });
    }

    // 停止封禁功能
    function stopBan() {
        if (!isBanning) return;

        fetch('/api/ban_account/stop', {
            method: 'GET'
        })
        .then(response => response.json())
        .then(data => {
            if (data.status === 'success') {
                isBanning = false;
                startBanButton.style.display = 'inline-block';
                stopBanButton.style.display = 'none';
                addLog('已发送停止封禁操作信号', 'info');
            } else {
                addLog(`停止失败: ${data.msg}`, 'error');
            }
        })
        .catch(error => {
            addLog(`请求出错: ${error.message}`, 'error');
        });
    }

    // 开始轮询日志
    function startLogPolling() {
        logInterval = setInterval(fetchLogs, 1000);
        // 同时开始轮询状态
        statusInterval = setInterval(checkBanStatus, 2000);
    }

    // 停止轮询日志和状态
    function stopLogPolling() {
        if (logInterval) {
            clearInterval(logInterval);
            logInterval = null;
        }
        if (statusInterval) {
            clearInterval(statusInterval);
            statusInterval = null;
        }
    }

    // 检查封禁状态
    function checkBanStatus() {
        fetch('/api/ban_account/status')
        .then(response => response.json())
        .then(data => {
            if (data.is_banning !== undefined) {
                isBanning = data.is_banning;
                updateBanStatus();
                
                // 如果is_banning变为false，更新按钮显示
                if (!isBanning) {
                    startBanButton.style.display = 'inline-block';
                    stopBanButton.style.display = 'none';
                }
            }
        })
        .catch(error => {
            // 忽略错误
        });
    }

    // 更新按钮旁边的状态显示
    function updateBanStatus() {
        if (isBanning) {
            statusDisplay.textContent = '运行中';
            statusDisplay.style.backgroundColor = '#d4edda';
            statusDisplay.style.color = '#155724';
        } else {
            statusDisplay.textContent = '空闲';
            statusDisplay.style.backgroundColor = '#f8d7da';
            statusDisplay.style.color = '#721c24';
        }
    }

    // 获取日志
    function fetchLogs() {
        fetch('/api/ban_account/get_logs')
        .then(response => response.json())
        .then(data => {
            if (data.status === 'success' && data.log) {
                try {
                    const logs = JSON.parse(data.log);
                    logs.forEach(log => {
                        addLog(log.message, log.type);
                    });
                } catch (e) {
                    // 如果不是JSON格式，按纯文本处理
                    addLog(data.log, 'info');
                }
            }
        })
        .catch(error => {
            // 忽略错误，避免日志刷屏
        });
    }

    // 添加日志到容器
    function addLog(message, type) {
        const logEntry = document.createElement('div');
        logEntry.className = `log-entry ${type}`;
        logEntry.textContent = `[${new Date().toLocaleTimeString()}] ${message}`;
        logContainer.appendChild(logEntry);
        logContainer.scrollTop = logContainer.scrollHeight;
    }

    // 页面卸载时清理
    window.addEventListener('beforeunload', function() {
        stopLogPolling();
    });
    
    // 初始化状态显示
    updateBanStatus();
});