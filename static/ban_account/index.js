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
            if (!whiteList) {
                addLog('请输入白名单账号，避免误封重要账号', 'error');
                return;
            }
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