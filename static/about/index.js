document.addEventListener('DOMContentLoaded', () => {
    // 为按钮添加点击事件处理
    const buttons = document.querySelectorAll('.button');
    buttons.forEach(button => {
        button.addEventListener('click', (e) => {
            // 如果按钮有 onclick 属性，让它正常执行
            if (button.onclick) {
                return;
            }
            
            // 处理外部链接
            const href = button.getAttribute('href');
            if (href && href.startsWith('http')) {
                e.preventDefault();
                // 在父窗口中打开外部链接
                if (window.parent) {
                    window.parent.open(href, '_blank');
                } else {
                    window.open(href, '_blank');
                }
            }
        });
    });

    // 添加页面加载动画
    const sections = document.querySelectorAll('.content-section');
    sections.forEach((section, index) => {
        section.style.opacity = '0';
        section.style.transform = 'translateY(20px)';
        section.style.transition = 'opacity 0.6s ease, transform 0.6s ease';
        
        setTimeout(() => {
            section.style.opacity = '1';
            section.style.transform = 'translateY(0)';
        }, index * 100);
    });

    // 添加特性卡片的悬停效果
    const featureCards = document.querySelectorAll('.feature-card');
    featureCards.forEach(card => {
        card.addEventListener('mouseenter', () => {
            card.style.transform = 'translateY(-5px) scale(1.02)';
        });
        
        card.addEventListener('mouseleave', () => {
            card.style.transform = 'translateY(0) scale(1)';
        });
    });

    // 添加帮助列表项的点击效果
    const helpItems = document.querySelectorAll('.help-list li');
    helpItems.forEach(item => {
        item.addEventListener('click', () => {
            // 添加点击动画
            item.style.transform = 'scale(0.98)';
            setTimeout(() => {
                item.style.transform = 'scale(1)';
            }, 150);
        });
    });

});

// 辅助函数：平滑滚动到指定元素
function scrollToElement(elementId) {
    const element = document.getElementById(elementId);
    if (element) {
        element.scrollIntoView({
            behavior: 'smooth',
            block: 'start'
        });
    }
}

// 添加键盘导航支持
document.addEventListener('keydown', (e) => {
    // 按 ESC 键返回主界面
    if (e.key === 'Escape') {
        if (window.parent && window.parent.switchToModule) {
            window.parent.switchToModule('auto_solver');
        }
    }
});