let isBanning = false;
let logInterval = null;
let statusInterval = null;

document.addEventListener('DOMContentLoaded', function () {

    const banTypeAssign = document.querySelector('input[value="assign"]');
    const banTypeAll = document.querySelector('input[value="all"]');
    const assignSection = document.getElementById('assign_section');
    const allSection = document.getElementById('all_section');
    const startBanButton = document.getElementById('start_ban');
    const stopBanButton = document.getElementById('stop_ban');
    const logContainer = document.getElementById('log_container');


    const statusDisplay = document.createElement('div');
    statusDisplay.id = 'ban_status';
    statusDisplay.style.cssText = 'display: inline-block; margin-left: 10px; padding: 5px 10px; border-radius: 4px; font-weight: bold;';
    startBanButton.parentNode.appendChild(statusDisplay);


    checkConfig();


    banTypeAssign.addEventListener('change', function () {
        if (this.checked) {
            assignSection.style.display = 'block';
            allSection.style.display = 'none';
        }
    });

    banTypeAll.addEventListener('change', function () {
        if (this.checked) {
            assignSection.style.display = 'none';
            allSection.style.display = 'block';
        }
    });


    startBanButton.addEventListener('click', startBan);


    stopBanButton.addEventListener('click', stopBan);


    async function checkConfig() {
        try {
            const response = await fetch('/api/config_ok');
            const result = await response.json();

            if (result.status !== 'success') {

                showConfigErrorModal('配置文件错误: ' + result.msg);
            }
        } catch (error) {
            console.error('检查配置文件时发生错误:', error);
            showConfigErrorModal('检查配置文件时发生错误: ' + error.message);
        }
    }


    function showConfigErrorModal(message) {

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
        confirmButton.onclick = function () {
            location.reload();
        };

        modalActions.appendChild(confirmButton);
        modal.appendChild(modalIcon);
        modal.appendChild(modalContent);
        modal.appendChild(modalActions);
        modalOverlay.appendChild(modal);
        document.body.appendChild(modalOverlay);


        modalOverlay.onclick = (e) => {
            if (e.target === modalOverlay) {
                document.body.removeChild(modalOverlay);
                location.reload();
            }
        };


        const escHandler = (e) => {
            if (e.key === 'Escape') {
                if (document.body.contains(modalOverlay)) {
                    document.body.removeChild(modalOverlay);
                }
                location.reload();
                document.removeEventListener('keydown', escHandler);
            }
        };
        document.addEventListener('keydown', escHandler);
    }


    function startBan() {
        if (isBanning) return;

        const banType = document.querySelector('input[name="ban_type"]:checked').value;


        logContainer.innerHTML = '';


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
                    updateBanStatus();
                } else {
                    addLog(`启动失败: ${data.msg}`, 'error');
                }
            })
            .catch(error => {
                addLog(`请求出错: ${error.message}`, 'error');
            });
    }


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


    function startLogPolling() {
        logInterval = setInterval(fetchLogs, 1000);

        statusInterval = setInterval(checkBanStatus, 2000);
    }


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


    function checkBanStatus() {
        fetch('/api/ban_account/status')
            .then(response => response.json())
            .then(data => {
                if (data.is_banning !== undefined) {
                    isBanning = data.is_banning;
                    updateBanStatus();


                    if (!isBanning) {
                        startBanButton.style.display = 'inline-block';
                        stopBanButton.style.display = 'none';
                    }
                }
            })
            .catch(error => {

            });
    }


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

                        addLog(data.log, 'info');
                    }
                }
            })
            .catch(error => {

            });
    }


    function addLog(message, type) {
        const logEntry = document.createElement('div');
        logEntry.className = `log-entry ${type}`;
        logEntry.textContent = `[${new Date().toLocaleTimeString()}] ${message}`;
        logContainer.appendChild(logEntry);
        logContainer.scrollTop = logContainer.scrollHeight;
    }


    window.addEventListener('beforeunload', function () {
        stopLogPolling();
    });


    updateBanStatus();
});