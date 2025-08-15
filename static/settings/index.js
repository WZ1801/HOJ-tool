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

// 去除网址末尾斜杠的函数
function removeTrailingSlash(url) {
    if (url && url.endsWith('/')) {
        return url.slice(0, -1);
    }
    return url;
}

// 检测网址是否有效
function isValidUrl(string) {
    try {
        if (!string) return false;
        
        if (!/^https?:\/\//.test(string)) {
            return false;
        }
        
        const url = new URL(string);
        
        const hostname = url.hostname;
        if (!hostname) {
            return false;
        }
        
        const port = url.port;
        if (port && (isNaN(port) || port < 1 || port > 65535)) {
            return false;
        }
        
        return true;
    } catch (e) {
        return false;
    }
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

    // 失焦
    document.getElementById('ojUrl').addEventListener('blur', function() {
        if (this.value) {
            // 去除末尾多余的斜杠
            this.value = removeTrailingSlash(this.value);
            if (!isValidUrl(this.value)) {
                showModal('OJ网址格式不正确，请输入有效的URL', 'error');
                this.focus();
                return;
            }
        }
    });
    
    document.getElementById('ojApiUrl').addEventListener('blur', function() {
        if (this.value) {
            // 去除末尾多余的斜杠
            this.value = removeTrailingSlash(this.value);
            if (!isValidUrl(this.value)) {
                showModal('OJ API网址格式不正确，请输入有效的URL', 'error');
                this.focus();
                return;
            }
        }
    });
    
    document.getElementById('aiUrl').addEventListener('blur', function() {
        if (this.value) {
            // 去除末尾多余的斜杠再
            this.value = removeTrailingSlash(this.value);
            if (!isValidUrl(this.value)) {
                showModal('AI对话地址格式不正确，请输入有效的URL', 'error');
                this.focus();
                return;
            }
        }
    });

    document.getElementById('settingsForm').addEventListener('submit', async (e) => {
        e.preventDefault();
        
        // 在提交前再次验证所有网址
        const ojUrl = document.getElementById('ojUrl').value;
        const ojApiUrl = document.getElementById('ojApiUrl').value;
        const aiUrl = document.getElementById('aiUrl').value;
        
        if (ojUrl) {
            const cleanOjUrl = removeTrailingSlash(ojUrl);
            if (!isValidUrl(cleanOjUrl)) {
                showModal('OJ网址格式不正确，请输入有效的URL', 'error');
                return;
            }
        }
        
        if (ojApiUrl) {
            const cleanOjApiUrl = removeTrailingSlash(ojApiUrl);
            if (!isValidUrl(cleanOjApiUrl)) {
                showModal('OJ API网址格式不正确，请输入有效的URL', 'error');
                return;
            }
        }
        
        if (aiUrl) {
            const cleanAiUrl = removeTrailingSlash(aiUrl);
            if (!isValidUrl(cleanAiUrl)) {
                showModal('AI对话地址格式不正确，请输入有效的URL', 'error');
                return;
            }
        }
        
        const formData = {
            OJ: {
                URL: ojUrl ? removeTrailingSlash(ojUrl) : ojUrl,
                APIURL: ojApiUrl ? removeTrailingSlash(ojApiUrl) : ojApiUrl,
                username: document.getElementById('username').value,
                password: document.getElementById('password').value
            },
            AI_URL: aiUrl ? removeTrailingSlash(aiUrl) : aiUrl,
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