document.addEventListener('DOMContentLoaded', function () {
    let progressCheckInterval = null;
    let isRefreshInProgress = false;
    let hasShownCacheModal = false;
    
    const userRankCtx = document.getElementById('userRankChart').getContext('2d');
    const statusRankCtx = document.getElementById('statusRankChart').getContext('2d');
    const submissionTimeCtx = document.getElementById('submissionTimeChart').getContext('2d');
    const topProblemsCtx = document.getElementById('topProblemsChart').getContext('2d');
    const userStatusCtx = document.getElementById('userStatusChart').getContext('2d');
    const userSubmissionTimeCtx = document.getElementById('userSubmissionTimeChart').getContext('2d');
    let userRankChart, statusRankChart, submissionTimeChart, topProblemsChart, userStatusChart, userSubmissionTimeChart, userLanguageChart, languageChart;
    let isLoading = false;
    let loadingTipInterval = null;
    
    function checkCacheStatus() {
        fetch('/api/statistics/cache_status')
            .then(response => response.json())
            .then(data => {
                updateCacheStatusUI(data);
                
                if (!hasShownCacheModal && (!data.has_cache || data.is_expired)) {
                    hasShownCacheModal = true;
                    setTimeout(() => {
                        showRefreshConfirmModal();
                    }, 1000);
                }
            })
            .catch(error => {
                console.error('获取缓存状态失败:', error);
                document.getElementById('cacheStatusText').textContent = '获取失败';
                document.getElementById('cacheStatusText').style.color = '#dc3545';
            });
    }
    
    function updateCacheStatusUI(cacheStatus) {
        const cacheStatusText = document.getElementById('cacheStatusText');
        const lastUpdateTime = document.getElementById('lastUpdateTime');
        
        if (cacheStatus.has_cache) {
            if (cacheStatus.is_expired) {
                cacheStatusText.textContent = '已过期';
                cacheStatusText.style.color = '#ffc107';
            } else {
                cacheStatusText.textContent = '有效';
                cacheStatusText.style.color = '#28a745';
            }
        } else {
            cacheStatusText.textContent = '无缓存';
            cacheStatusText.style.color = '#dc3545';
        }
        
        if (cacheStatus.has_cache && cacheStatus.last_modified) {
            const date = new Date(cacheStatus.last_modified);
            lastUpdateTime.textContent = date.toLocaleString('zh-CN');
        } else {
            lastUpdateTime.textContent = '从未更新';
        }
    }
    
    function showRefreshConfirmModal(message = null) {
        const modal = document.getElementById('refreshConfirmModal');
        const modalMessage = document.getElementById('modalMessage');
        
        if (message) {
            modalMessage.textContent = message;
        } else {
            modalMessage.textContent = '缓存已过期或不存在，是否重新统计？';
        }
        
        modal.style.display = 'flex';
        
        const closeBtn = document.querySelector('.close-modal-btn');
        const cancelBtn = document.getElementById('cancelRefreshBtn');
        const confirmBtn = document.getElementById('confirmRefreshBtn');
        
        const closeModal = () => {
            modal.style.display = 'none';
        };
        
        closeBtn.onclick = closeModal;
        cancelBtn.onclick = closeModal;
        
        confirmBtn.onclick = () => {
            closeModal();
            refreshStatistics();
        };
        
        modal.onclick = (e) => {
            if (e.target === modal) {
                closeModal();
            }
        };
    }
    
    function refreshStatistics() {
        if (isRefreshInProgress) {
            showErrorModal('统计任务已在运行中，请稍后再试');
            return;
        }
        
        isRefreshInProgress = true;
        hasShownCacheModal = false;
        document.getElementById('refreshStatisticsBtn').disabled = true;
        document.getElementById('refreshStatisticsBtn').innerHTML = '<i class="bi bi-arrow-clockwise"></i> 刷新中...';
        updateProgressStatus({ is_running: true, progress: 0, total_pages: 0, current_page: 0, error: null });
        
        if (progressCheckInterval) {
            clearInterval(progressCheckInterval);
        }
        progressCheckInterval = setInterval(checkProgress, 1000);
        
        fetch('/api/statistics/refresh', {
            method: 'POST'
        })
        .then(response => response.json())
        .then(data => {
            if (data.status === 'error') {
                showErrorModal(data.msg);
                stopRefreshProgress();
            }
        })
        .catch(error => {
            showErrorModal(`启动刷新任务失败: ${error.message}`);
            stopRefreshProgress();
        });
    }
    
    function checkProgress() {
        if (!isRefreshInProgress) return;
        
        fetch('/api/statistics/progress')
            .then(response => response.json())
            .then(progress => {
                updateProgressStatus(progress);
                
                if (!progress.is_running) {
                    stopRefreshProgress();
                    
                    if (progress.error) {
                        showErrorModal(`统计过程中出错: ${progress.error}`);
                    } else if (progress.status === 'completed' || progress.progress === 100) {
                        setTimeout(() => {
                            fetchDataAndRenderCharts();
                            checkCacheStatus();
                            showErrorModal('统计刷新完成！');
                        }, 1000);
                    }
                }
            })
            .catch(error => {
                console.error('获取进度失败:', error);
                const retryCount = window.retryCount || 0;
                if (retryCount >= 3) {
                    stopRefreshProgress();
                    showErrorModal('获取进度失败，请手动检查刷新状态');
                } else {
                    window.retryCount = retryCount + 1;
                }
            });
    }
    
    function updateProgressStatus(progress) {
        const progressStatusText = document.getElementById('progressStatusText');
        const progressBarFill = document.getElementById('progressBarFill');
        const progressPercentage = document.getElementById('progressPercentage');
        const progressDetails = document.getElementById('progressDetails');
        
        if (progress.is_running) {
            progressStatusText.textContent = '进行中';
            progressStatusText.style.color = '#007bff';
            
            let percent = 0;
            if (progress.total_pages > 0) {
                percent = Math.round((progress.current_page / progress.total_pages) * 100);
            } else if (progress.progress > 0) {
                percent = progress.progress;
            }
            
            progressBarFill.style.width = `${percent}%`;
            progressPercentage.textContent = `${percent}%`;
            
            if (progress.total_pages > 0) {
                progressDetails.textContent = `正在处理第 ${progress.current_page} 页 / 共 ${progress.total_pages} 页`;
            } else {
                progressDetails.textContent = '正在获取数据...';
            }
        } else {
            progressStatusText.textContent = '空闲';
            progressStatusText.style.color = '#6c757d';
            progressBarFill.style.width = '0%';
            progressPercentage.textContent = '0%';
            progressDetails.textContent = '等待开始...';
        }
    }
    
    function stopRefreshProgress() {
        isRefreshInProgress = false;
        window.retryCount = 0;
        
        if (progressCheckInterval) {
            clearInterval(progressCheckInterval);
            progressCheckInterval = null;
        }
        
        const refreshBtn = document.getElementById('refreshStatisticsBtn');
        if (refreshBtn) {
            refreshBtn.disabled = false;
            refreshBtn.innerHTML = '<i class="bi bi-arrow-clockwise"></i> 刷新统计';
        }
        
        updateProgressStatus({ is_running: false, progress: 0, total_pages: 0, current_page: 0, error: null });
    }
    
    function clearCache() {
        if (isRefreshInProgress) {
            showErrorModal('统计任务正在运行中，无法清空缓存');
            return;
        }
        
        if (!confirm('确定要清空统计缓存吗？清空后需要重新统计才能查看数据。')) {
            return;
        }
        
        fetch('/api/statistics/clear_cache', {
            method: 'GET'
        })
        .then(response => response.json())
        .then(data => {
            if (data.status === 'success') {
                document.getElementById('cacheStatusText').textContent = '已清空';
                document.getElementById('cacheStatusText').style.color = '#dc3545';
                document.getElementById('lastUpdateTime').textContent = '从未更新';
                showErrorModal('缓存已成功清空');
            } else {
                showErrorModal(`清空缓存失败: ${data.msg}`);
            }
        })
        .catch(error => {
            showErrorModal(`清空缓存失败: ${error.message}`);
        });
    }
    
    function initEventListeners() {
        document.getElementById('refreshStatisticsBtn').addEventListener('click', refreshStatistics);
        document.getElementById('clearCacheBtn').addEventListener('click', clearCache);
        
        document.getElementById('refreshConfirmModal').addEventListener('click', function(e) {
            if (e.target === this) {
                this.style.display = 'none';
            }
        });
    }
    
    initEventListeners();
    checkCacheStatus();

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

                const style = document.createElement('style');
                style.id = 'loading-style-spin';
                style.textContent = `
                    @keyframes spin {
                        0% { transform: rotate(0deg); }
                        100% { transform: rotate(360deg); }
                    }
                `;

                const animationStyle = document.createElement('style');
                animationStyle.id = 'loading-style-fade';
                animationStyle.textContent = `
                    @keyframes fadeInOut {
                        0% { opacity: 0; transform: translateY(10px); }
                        20% { opacity: 1; transform: translateY(0); }
                        80% { opacity: 1; transform: translateY(0); }
                        100% { opacity: 0; transform: translateY(-10px); }
                    }
                `;

                loadingDiv.appendChild(spinner);
                loadingDiv.appendChild(tipText);
                document.head.appendChild(style);
                document.head.appendChild(animationStyle);
                document.body.appendChild(loadingDiv);
            }
        } else {
            if (loadingDiv) {
                document.body.removeChild(loadingDiv);
                const style = document.getElementById('loading-style-spin');
                if (style) {
                    document.head.removeChild(style);
                }
                const animationStyle = document.getElementById('loading-style-fade');
                if (animationStyle) {
                    document.head.removeChild(animationStyle);
                }
                if (loadingTipInterval) {
                    clearInterval(loadingTipInterval);
                    loadingTipInterval = null;
                }
            }
        }
    }

    function showErrorModal(message) {
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
        confirmButton.onclick = function () {
            document.body.removeChild(modalOverlay);
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
            }
        };

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
                            label: function (context) {
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
                            callback: function (value) {
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
                            label: function (tooltipItem) {
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
                            label: function (tooltipItem) {
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
                            label: function (tooltipItem) {
                                return `${tooltipItem.label}: ${tooltipItem.raw.toFixed(2)}%`;
                            }
                        }
                    }
                }
            }
        });
    }

    document.getElementById('searchButton').addEventListener('click', function () {
        if (isRefreshInProgress) {
            showErrorModal('统计刷新正在进行中，请稍后再搜索');
            return;
        }
        
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
                            label: function (tooltipItem) {
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
