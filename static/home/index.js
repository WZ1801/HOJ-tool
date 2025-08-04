// 页面加载完成后的初始化
document.addEventListener('DOMContentLoaded', () => {
    // 添加卡片点击效果
    const cards = document.querySelectorAll('.feature-card');
    cards.forEach(card => {
        card.addEventListener('click', (e) => {
            // 如果点击的是按钮，不触发卡片的点击事件
            if (e.target.classList.contains('button')) {
                e.stopPropagation();
                return;
            }
            // 获取卡片中的按钮链接并跳转
            const link = card.querySelector('.button').getAttribute('href');
            window.location.href = link;
        });
    });
});
