// 框架管理器
class FrameworkManager {
    constructor() {
        this.currentModule = 'about';
        this.frames = new Map();
        this.navItems = document.querySelectorAll('.nav-item');
        this.modules = ['about', 'auto_solver', 'statistics', 'ban_account', 'settings'];
        this.sidebar = document.querySelector('.sidebar');
        this.hoverTimeout = null;
        this.isExpanded = false;
        this.init();
        this.initSidebarHover();
    }

    init() {
        // 初始化所有 iframe 引用
        this.modules.forEach(module => {
            const frameElement = document.getElementById(`frame-${module}`);
            if (frameElement) {
                this.frames.set(module, frameElement);
            }
        });

        // 绑定导航项点击事件
        this.navItems.forEach(item => {
            item.addEventListener('click', (e) => {
                e.preventDefault();
                const module = item.getAttribute('data-module');
                this.switchModule(module);
            });
        });

        // 处理返回按钮
        window.addEventListener('popstate', () => {
            const hash = window.location.hash.slice(1) || 'home';
            this.switchModule(hash);
        });

        // 恢复之前的模块（如果有）
        const hash = window.location.hash.slice(1);
        if (hash) {
            this.switchModule(hash);
        } else {
            // 默认显示关于页面
            this.switchModule('about');
        }
    }

    initSidebarHover() {
        // 鼠标进入侧边栏
        this.sidebar.addEventListener('mouseenter', () => {
            this.hoverTimeout = setTimeout(() => {
                this.expandSidebar();
            }, 500);
        });

        // 鼠标离开侧边栏
        this.sidebar.addEventListener('mouseleave', () => {
            if (this.hoverTimeout) {
                clearTimeout(this.hoverTimeout);
            }
            this.collapseSidebar();
        });
    }

    expandSidebar() {
        if (!this.isExpanded) {
            this.sidebar.classList.add('expanded');
            this.isExpanded = true;
        }
    }

    collapseSidebar() {
        if (this.isExpanded) {
            this.sidebar.classList.remove('expanded');
            this.isExpanded = false;
        }
    }

    switchModule(module) {
        // 验证模块是否有效
        if (!this.modules.includes(module)) {
            console.error(`Invalid module: ${module}`);
            return;
        }

        // 如果是同一个模块，不进行切换
        if (this.currentModule === module) {
            return;
        }

        // 更新URL
        window.location.hash = module;

        // 获取当前和目标 iframe
        const currentFrame = this.frames.get(this.currentModule);
        const targetFrame = this.frames.get(module);

        if (!currentFrame || !targetFrame) {
            console.error('Frame not found');
            return;
        }

        // 移除当前活跃状态
        this.navItems.forEach(item => {
            if (item.getAttribute('data-module') === this.currentModule) {
                item.classList.remove('active');
            }
        });

        // 移除当前 iframe 的 active 类，触发淡出动画
        currentFrame.classList.remove('active');

        // 延迟切换到新 iframe，保证动画流畅
        setTimeout(() => {
            this.currentModule = module;

            // 添加目标 iframe 的 active 类，触发淡入动画
            targetFrame.classList.add('active');

            // 更新导航项的活跃状态
            this.navItems.forEach(item => {
                if (item.getAttribute('data-module') === module) {
                    item.classList.add('active');
                }
            });
        }, 300);
    }

    // 刷新指定模块
    refreshModule(module = null) {
        const targetModule = module || this.currentModule;
        const frame = this.frames.get(targetModule);
        
        if (frame) {
            const src = frame.src;
            frame.src = '';
            setTimeout(() => {
                frame.src = src;
            }, 100);
        }
    }

    // 获取指定模块的 iframe
    getFrameElement(module) {
        return this.frames.get(module);
    }

    // 获取当前模块
    getCurrentModule() {
        return this.currentModule;
    }

    // 获取当前 iframe
    getCurrentFrame() {
        return this.frames.get(this.currentModule);
    }
}

// 初始化框架管理器
let frameManager;
document.addEventListener('DOMContentLoaded', () => {
    frameManager = new FrameworkManager();
    console.log('Framework initialized with multiple iframes');
});

// 暴露给全局的刷新函数（可在 iframe 中调用）
window.refreshModule = function(module = null) {
    frameManager.refreshModule(module);
};

// 暴露给全局的模块切换函数（可在 iframe 中调用）
window.switchToModule = function(module) {
    frameManager.switchModule(module);
};

// 暴露给全局的获取 iframe 函数
window.getFrameElement = function(module) {
    return frameManager.getFrameElement(module);
};

// 导出 FrameworkManager 类
window.FrameworkManager = FrameworkManager;