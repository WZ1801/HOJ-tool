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
    setTimeout(() => modal.classList.add('show'), 10);
}

// 关闭模态框
function closeModal() {
    const modal = document.getElementById('modal');
    const modalOverlay = document.getElementById('modalOverlay');
    
    modal.classList.remove('show');
    setTimeout(() => {
        modalOverlay.classList.remove('show');
    }, 300);
}

document.addEventListener('DOMContentLoaded', async () => {
    // 加载现有配置
    const config = await loadConfig();
    if (config) {
        document.getElementById('ojUrl').value = config.OJ.URL;
        document.getElementById('ojApiUrl').value = config.OJ.APIURL;
        document.getElementById('username').value = config.OJ.username;
        document.getElementById('password').value = config.OJ.password;
        document.getElementById('aiUrl').value = config.AI_URL;
        document.getElementById('browserType').value = config.Browser.Type;
        document.getElementById('driverPath').value = config.Browser.Driver_path;
    }

    // 处理驱动文件选择
    document.getElementById('driverFile').addEventListener('change', (e) => {
        const file = e.target.files[0];
        if (file) {
            document.getElementById('driverPath').value = file.path;
        }
    });

    // 处理表单提交
    document.getElementById('settingsForm').addEventListener('submit', async (e) => {
        e.preventDefault();
        
        const formData = {
            OJ: {
                URL: document.getElementById('ojUrl').value,
                APIURL: document.getElementById('ojApiUrl').value,
                username: document.getElementById('username').value,
                password: document.getElementById('password').value
            },
            AI_URL: document.getElementById('aiUrl').value,
            Browser: {
                Type: document.getElementById('browserType').value,
                Driver_path: document.getElementById('driverPath').value
            }
        };

        try {
            const response = await fetch('/api/config/save', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(formData)
            });

            const result = await response.json();
            if (result.status === 'success') {
                showModal('配置保存成功！', 'success');
            } else {
                showModal('保存失败：' + result.msg, 'error');
            }
        } catch (error) {
            showModal('保存失败：' + error.message, 'error');
        }
    });
});

async function loadConfig() {
    try {
        const response = await fetch('/api/config/get');
        const config = await response.json();
        return config;
    } catch (error) {
        console.error('加载配置失败：', error);
        return null;
    }
}