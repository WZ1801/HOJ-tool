document.addEventListener('DOMContentLoaded', function () {
    const userRankCtx = document.getElementById('userRankChart').getContext('2d');
    const statusRankCtx = document.getElementById('statusRankChart').getContext('2d');
    const submissionTimeCtx = document.getElementById('submissionTimeChart').getContext('2d');
    const topProblemsCtx = document.getElementById('topProblemsChart').getContext('2d');
    const userStatusCtx = document.getElementById('userStatusChart').getContext('2d');
    const userSubmissionTimeCtx = document.getElementById('userSubmissionTimeChart').getContext('2d');
    let userRankChart, statusRankChart, submissionTimeChart, topProblemsChart, userStatusChart, userSubmissionTimeChart, userLanguageChart; // 确保userLanguageChart已声明
    let isLoading = false;
    let loadingTipInterval = null; // 用于保存提示轮播的定时器

    // 定义加载提示信息数组
    const loadingTips = [
        '加载数据中，约一分钟，请耐心等待……',
        '你看什么看，只是条Tip!',
        '听说你是个人🤔',
        '你知道么，HOJ Tool从2024年2月开始开发!',
        '*/！……%）*%#|}）——{$]&[',
        '你知道么，每一行注释都是一行注释',
        'Submitted Failed!',
        'give me a starrrrrr!!!!!!!',
        'FIX A BUG TO MAKE A BUG!'
    ];

    // 显示加载提示
    function showLoading(show) {
        const container = document.querySelector('.container');
        let loadingDiv = document.getElementById('loading-indicator');
        
        if (show) {
            if (!loadingDiv) {
                loadingDiv = document.createElement('div');
                loadingDiv.id = 'loading-indicator';
                loadingDiv.style.cssText = `
                    position: fixed;
                    top: 0;
                    left: 0;
                    width: 100%;
                    height: 100%;
                    background: rgba(255, 255, 255, 0.7);
                    display: flex;
                    flex-direction: column;
                    justify-content: center;
                    align-items: center;
                    z-index: 9999;
                    backdrop-filter: blur(2px);
                `;
                
                // 创建旋转动画元素
                const spinner = document.createElement('div');
                spinner.style.cssText = `
                    border: 8px solid #f3f3f3;
                    border-top: 8px solid #3498db;
                    border-radius: 50%;
                    width: 60px;
                    height: 60px;
                    animation: spin 1s linear infinite;
                    margin-bottom: 16px;
                `;
                
                // 添加旋转动画
                const style = document.createElement('style');
                style.textContent = `
                    @keyframes spin {
                        0% { transform: rotate(0deg); }
                        100% { transform: rotate(360deg); }
                    }
                `;
                
                // 创建提示文字元素
                const tipText = document.createElement('div');
                tipText.id = 'loading-tip';
                tipText.style.cssText = `
                    margin-top: 16px;
                    font-size: 16px;
                    color: #333;
                    animation: fadeInOut 3s ease-in-out infinite;
                `;
                
                // 添加淡入淡出动画
                const animationStyle = document.createElement('style');
                animationStyle.textContent = `
                    @keyframes fadeInOut {
                        0% { opacity: 0; transform: translateY(10px); }
                        20% { opacity: 1; transform: translateY(0); }
                        80% { opacity: 1; transform: translateY(0); }
                        100% { opacity: 0; transform: translateY(-10px); }
                    }
                `;
                
                // 初始化提示文字
                const randomTip = loadingTips[Math.floor(Math.random() * loadingTips.length)];
                tipText.textContent = randomTip;
                
                // 添加定时器实现提示文字轮播
                loadingTipInterval = setInterval(() => {
                    const currentTip = loadingTips[Math.floor(Math.random() * loadingTips.length)];
                    tipText.textContent = currentTip;
                }, 3000); // 每3秒切换一次提示文字
                
                loadingDiv.appendChild(spinner);
                loadingDiv.appendChild(tipText);
                document.head.appendChild(style);
                document.head.appendChild(animationStyle);
                document.body.appendChild(loadingDiv);
            }
        } else {
            if (loadingDiv) {
                document.body.removeChild(loadingDiv);
                const style = document.querySelector('style[type="text/css"]');
                if (style) {
                    document.head.removeChild(style);
                }
                // 清除定时器
                if (loadingTipInterval) {
                    clearInterval(loadingTipInterval);
                    loadingTipInterval = null;
                }
            }
        }
    }

    // 显示错误模态框
    function showErrorModal(message) {
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
        modalIcon.innerHTML = `<i class="bi bi-exclamation-triangle" style="font-size: 48px; color: #ffc107;"></i>`;
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
            document.body.removeChild(modalOverlay);
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
            }
        };

        // 添加ESC键关闭
        const escHandler = (e) => {
            if (e.key === 'Escape') {
                if (document.body.contains(modalOverlay)) {
                    document.body.removeChild(modalOverlay);
                }
                document.removeEventListener('keydown', escHandler);
            }
        };
        document.addEventListener('keydown', escHandler);
    }

    function fetchDataAndRenderCharts() {
        showLoading(true);
        fetch('/api/statistics')
            .then(response => response.json())
            .then(data => {
                if (data.error) {
                    showErrorModal(data.error);
                    return;
                }
                renderStackedBarChart(data.top_users_stacked_data);
                renderStatusRankChart(data.status_ranking);
                renderSubmissionTimeChart(data.submission_by_hour);
                renderTopProblemsChart(data.top_problems);
                // 添加语言分布图表渲染
                if (data.language_distribution && data.language_distribution.length > 0) {
                    renderLanguageChart(data.language_distribution);
                } else {
                    console.warn('No language distribution data available');
                }
            })
            .finally(() => {
                setTimeout(() => {
                    showLoading(false);
                }, 500);
            });
    }

    function renderStackedBarChart(stackedData) {
        if (!stackedData || !stackedData.users || !stackedData.datasets) {
            console.error("Invalid data for stacked bar chart:", stackedData);
            showErrorModal("Failed to load chart data. The data format is incorrect.");
            return;
        }
        const labels = stackedData.users;
        const datasets = stackedData.datasets;

        const statusColors = {
            'Accepted': 'rgba(40, 167, 69, 0.7)',
            'Wrong Answer': 'rgba(220, 53, 69, 0.7)',
            'Time Limit Exceeded': 'rgba(255, 193, 7, 0.7)',
            'Memory Limit Exceeded': 'rgba(23, 162, 184, 0.7)',
            'Runtime Error': 'rgba(108, 117, 125, 0.7)',
            'Compile Error': 'rgba(255, 99, 132, 0.7)',
            'Presentation Error': 'rgba(75, 192, 192, 0.7)',
            'Submitted Failed': 'rgba(153, 102, 255, 0.7)',
            'Pending': 'rgba(255, 159, 64, 0.7)',
            'Compiling': 'rgba(54, 162, 235, 0.7)',
            'Running': 'rgba(100, 100, 100, 0.7)',
            'Other': 'rgba(200, 200, 200, 0.7)'
        };

        datasets.forEach(dataset => {
            dataset.backgroundColor = statusColors[dataset.label] || statusColors['Other'];
        });

        if (userRankChart) {
            userRankChart.destroy();
        }
        userRankChart = new Chart(userRankCtx, {
            type: 'bar',
            data: {
                labels: labels,
                datasets: datasets
            },
            options: {
                plugins: {
                    title: {
                        display: true,
                        text: 'Top 20 用户提交状态分布'
                    },
                    tooltip: {
                        callbacks: {
                            label: function(context) {
                                let label = context.dataset.label || '';
                                if (label) {
                                    label += ': ';
                                }
                                if (context.parsed.y !== null) {
                                    label += context.parsed.y.toFixed(2) + '%';
                                }
                                return label;
                            }
                        }
                    }
                },
                responsive: true,
                scales: {
                    x: {
                        stacked: true,
                        title: {
                            display: true,
                            text: '用户'
                        }
                    },
                    y: {
                        stacked: true,
                        beginAtZero: true,
                        ticks: {
                            callback: function(value) {
                                return value.toFixed(2) + '%'
                            }
                        },
                        title: {
                            display: true,
                            text: '评测结果分布'
                        }
                    }
                }
            }
        });
    }

    function renderTopProblemsChart(topProblems) {
        if (!topProblems) {
            console.error("Invalid data for top problems chart:", topProblems);
            showErrorModal("Failed to load top problems chart data. The data format is incorrect.");
            return;
        }

        if (topProblemsChart) {
            topProblemsChart.destroy();
        }

        topProblemsChart = new Chart(topProblemsCtx, {
            type: 'bar',
            data: {
                labels: topProblems.map(p => p.problem),
                datasets: [{
                    label: '提交次数',
                    data: topProblems.map(p => p.count),
                    backgroundColor: 'rgba(255, 159, 64, 0.6)',
                    borderColor: 'rgba(255, 159, 64, 1)',
                    borderWidth: 1
                }]
            },
            options: {
                indexAxis: 'y',
                responsive: true,
                plugins: {
                    legend: {
                        display: false
                    },
                    title: {
                        display: true,
                        text: 'Top 20 热门题目'
                    }
                },
                scales: {
                    x: {
                        beginAtZero: true,
                        title: {
                            display: true,
                            text: '提交次数'
                        }
                    },
                    y: {
                        title: {
                            display: true,
                            text: '题目'
                        }
                    }
                }
            }
        });
    }

    function renderSubmissionTimeChart(submissionByHour) {
        if (!submissionByHour || !submissionByHour.hours || !submissionByHour.counts) {
            console.error("Invalid data for submission time chart:", submissionByHour);
            showErrorModal("Failed to load submission time chart data. The data format is incorrect.");
            return;
        }

        if (submissionTimeChart) {
            submissionTimeChart.destroy();
        }

        submissionTimeChart = new Chart(submissionTimeCtx, {
            type: 'bar',
            data: {
                labels: submissionByHour.hours,
                datasets: [{
                    label: '提交数量',
                    data: submissionByHour.counts,
                    backgroundColor: 'rgba(54, 162, 235, 0.6)',
                    borderColor: 'rgba(54, 162, 235, 1)',
                    borderWidth: 1
                }]
            },
            options: {
                responsive: true,
                plugins: {
                    legend: {
                        display: false
                    },
                    title: {
                        display: true,
                        text: '各时间段提交数量'
                    }
                },
                scales: {
                    x: {
                        title: {
                            display: true,
                            text: '时间段'
                        }
                    },
                    y: {
                        beginAtZero: true,
                        title: {
                            display: true,
                            text: '提交数量'
                        }
                    }
                }
            }
        });
    }

    function renderStatusRankChart(statusRanking) {
        const labels = statusRanking.map(item => item[0]);
        const values = statusRanking.map(item => item[1]);

        if (statusRankChart) {
            statusRankChart.destroy();
        }
        statusRankChart = new Chart(statusRankCtx, {
            type: 'pie',
            data: {
                labels: labels,
                datasets: [{
                    label: '评测结果分布',
                    data: values,
                    backgroundColor: [
                        'rgba(40, 167, 69, 0.6)',
                        'rgba(255, 193, 7, 0.6)',
                        'rgba(220, 53, 69, 0.6)',
                        'rgba(23, 162, 184, 0.6)',
                        'rgba(108, 117, 125, 0.6)',
                        'rgba(255, 99, 132, 0.6)',
                        'rgba(75, 192, 192, 0.6)',
                        'rgba(153, 102, 255, 0.6)',
                        'rgba(255, 159, 64, 0.6)'
                    ],
                    borderWidth: 1
                }]
            },
            options: {
                responsive: true,
                plugins: {
                    legend: {
                        position: 'top',
                    },
                    tooltip: {
                        callbacks: {
                            label: function(tooltipItem) {
                                let label = tooltipItem.label || '';
                                if (label) {
                                    label += ': ';
                                }
                                if (tooltipItem.raw !== null) {
                                    label += tooltipItem.raw.toFixed(2) + '%';
                                }
                                return label;
                            }
                        }
                    }
                }
            }
        });
    }

    function renderLanguageChart(languageDistribution) {
        // 添加严格的类型检查
        if (languageChart && typeof languageChart.destroy === 'function') {
            languageChart.destroy();
        }
        
        if (!languageDistribution || !Array.isArray(languageDistribution) || languageDistribution.length === 0) {
            console.warn('Invalid language distribution data:', languageDistribution);
            showErrorModal("无效的语言分布数据");
            return;
        }

        const ctx = document.getElementById('languageChart').getContext('2d');
        
        languageChart = new Chart(ctx, {
            type: 'pie',
            data: {
                labels: languageDistribution.map(item => item[0]),
                datasets: [{
                    label: '语言占比',
                    data: languageDistribution.map(item => item[1]),
                    backgroundColor: [
                        'rgba(255, 99, 132, 0.6)',
                        'rgba(54, 162, 235, 0.6)',
                        'rgba(255, 206, 86, 0.6)',
                        'rgba(75, 192, 192, 0.6)',
                        'rgba(153, 102, 255, 0.6)',
                        'rgba(255, 159, 64, 0.6)',
                        'rgba(40, 167, 69, 0.6)',
                        'rgba(220, 53, 69, 0.6)',
                    ],
                    borderWidth: 1
                }]
            },
            options: {
                responsive: true,
                plugins: {
                    legend: {
                        position: 'top',
                    },
                    tooltip: {
                        callbacks: {
                            label: function(tooltipItem) {
                                return `${tooltipItem.label}: ${tooltipItem.raw.toFixed(2)}%`;
                            }
                        }
                    }
                }
            }
        });
    }

    function renderUserLanguageChart(languagePercentage) {
        const ctx = document.getElementById('userLanguageChart');
        if (!ctx) {
            console.error('Canvas element #userLanguageChart not found');
            return;
        }
        
        if (userLanguageChart instanceof Chart) {
            userLanguageChart.destroy();
        }

        userLanguageChart = new Chart(ctx, {
            type: 'pie',
            data: {
                labels: languagePercentage.map(item => item[0]),
                datasets: [{
                    data: languagePercentage.map(item => item[1]),
                    backgroundColor: [
                        'rgba(255, 99, 132, 0.6)',
                        'rgba(54, 162, 235, 0.6)',
                        'rgba(255, 206, 86, 0.6)',
                        'rgba(75, 192, 192, 0.6)',
                        'rgba(153, 102, 255, 0.6)',
                        'rgba(255, 159, 64, 0.6)',
                        'rgba(40, 167, 69, 0.6)',
                        'rgba(220, 53, 69, 0.6)',
                    ],
                    borderWidth: 1
                }]
            },
            options: {
                responsive: true,
                plugins: {
                    legend: {
                        display: true,
                        position: 'top',
                    },
                    tooltip: {
                        callbacks: {
                            label: function(tooltipItem) {
                                return `${tooltipItem.label}: ${tooltipItem.raw.toFixed(2)}%`;
                            }
                        }
                    }
                }
            }
        });
    }

    // 修改搜索按钮事件监听器
    document.getElementById('searchButton').addEventListener('click', function() {
        const username = document.getElementById('usernameInput').value;
        if (!username) {
            showErrorModal('请输入用户名');
            return;
        }
        showLoading(true);
        fetch(`/api/statistics?username=${username}`)
            .then(response => response.json())
            .then(data => {
                const resultContainer = document.getElementById('userResultContainer');
                const notFoundP = document.getElementById('userNotFound');

                if (data.error) {
                    showErrorModal(data.error);
                    resultContainer.style.display = 'none';
                    notFoundP.style.display = 'none';
                } else if (data.user_specific) {
                    const userData = data.user_specific;
                    document.getElementById('userResultTitle').textContent = `${userData.username} 的统计`;
                    document.getElementById('userResultSubmissionCount').textContent = `总提交数: ${userData.submission_count}`;
                    
                    renderUserStatusChart(userData.status_percentage);
                    renderUserSubmissionTimeChart(userData.submission_by_hour);
                    renderUserLanguageChart(userData.language_percentage);

                    resultContainer.style.display = 'block';
                    notFoundP.style.display = 'none';
                } else {
                    notFoundP.textContent = `未找到用户 ${username} 的提交记录。`;
                    notFoundP.style.display = 'block';
                    resultContainer.style.display = 'none';
                }
            })
            .catch(error => {
                showErrorModal(`获取数据时发生错误: ${error.message}`);
            })
            .finally(() => {
                setTimeout(() => {
                    showLoading(false);
                }, 500);
            });
    });

    function renderUserStatusChart(statusPercentage) {
        if (userStatusChart) {
            userStatusChart.destroy();
        }
        userStatusChart = new Chart(userStatusCtx, {
            type: 'pie',
            data: {
                labels: statusPercentage.map(item => item[0]),
                datasets: [{
                    data: statusPercentage.map(item => item[1]),
                    backgroundColor: [
                        'rgba(40, 167, 69, 0.6)',
                        'rgba(255, 193, 7, 0.6)',
                        'rgba(220, 53, 69, 0.6)',
                        'rgba(23, 162, 184, 0.6)',
                        'rgba(108, 117, 125, 0.6)',
                        'rgba(255, 99, 132, 0.6)',
                        'rgba(75, 192, 192, 0.6)',
                        'rgba(153, 102, 255, 0.6)',
                        'rgba(255, 159, 64, 0.6)'
                    ],
                    borderWidth: 1
                }]
            },
            options: {
                responsive: true,
                plugins: {
                    legend: {
                        position: 'top',
                    },
                    tooltip: {
                        callbacks: {
                            label: function(tooltipItem) {
                                return `${tooltipItem.label}: ${tooltipItem.raw.toFixed(2)}%`;
                            }
                        }
                    }
                }
            }
        });
    }

    function renderUserSubmissionTimeChart(submissionByHour) {
        if (userSubmissionTimeChart) {
            userSubmissionTimeChart.destroy();
        }
        userSubmissionTimeChart = new Chart(userSubmissionTimeCtx, {
            type: 'bar',
            data: {
                labels: submissionByHour.hours,
                datasets: [{
                    label: '提交数量',
                    data: submissionByHour.counts,
                    backgroundColor: 'rgba(54, 162, 235, 0.6)',
                    borderColor: 'rgba(54, 162, 235, 1)',
                    borderWidth: 1
                }]
            },
            options: {
                responsive: true,
                plugins: {
                    legend: {
                        display: false
                    }
                },
                scales: {
                    x: {
                        title: {
                            display: true,
                            text: '时间段'
                        }
                    },
                    y: {
                        beginAtZero: true,
                        title: {
                            display: true,
                            text: '提交数量'
                        }
                    }
                }
            }
        });
    }

    fetchDataAndRenderCharts();
});