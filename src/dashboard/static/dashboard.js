// ChainPilot Dashboard - Modern Black & White with Charts
const API_BASE = '/api/v1';
let activityChart = null;
let typeChart = null;
let statusChart = null;
let refreshInterval = null;
let currentCurrency = 'ETH'; // Will be updated based on network
let currentNetwork = 'Unknown';
let walletConnected = false;

// Initialize dashboard
document.addEventListener('DOMContentLoaded', () => {
    console.log('ChainPilot Dashboard initializing...');
    initializeNavigation();
    initializeCharts();
    initializeWalletSelector();
    initializeChatbot();
    initializeRuleForm();
    initializeTransactionForm();
    initializeWalletForm();
    loadDashboardData();
    startAutoRefresh();
    
    // Initialize modal close buttons
    document.querySelectorAll('.modal .close, .modal-close').forEach(btn => {
        btn.addEventListener('click', (e) => {
            e.target.closest('.modal').style.display = 'none';
        });
    });
    
    // Close modals on outside click
    window.addEventListener('click', (e) => {
        if (e.target.classList.contains('modal')) {
            e.target.style.display = 'none';
        }
    });
});

// Initialize Chatbot
function initializeChatbot() {
    const sendBtn = document.getElementById('sendChatBtn');
    const chatInput = document.getElementById('chatInput');
    
    if (sendBtn) {
        sendBtn.addEventListener('click', sendChat);
    }
    
    if (chatInput) {
        chatInput.addEventListener('keypress', (e) => {
            if (e.key === 'Enter') {
                sendChat();
            }
        });
    }
}

// Initialize Rule Form
function initializeRuleForm() {
    const newRuleBtn = document.getElementById('newRuleBtn');
    const ruleTypeSelect = document.getElementById('ruleType');
    
    if (newRuleBtn) {
        newRuleBtn.addEventListener('click', () => {
            document.getElementById('newRuleModal').style.display = 'block';
        });
    }
    
    if (ruleTypeSelect) {
        ruleTypeSelect.addEventListener('change', updateRuleParamsForm);
    }
}

// Initialize Transaction Form
function initializeTransactionForm() {
    const newTxBtn = document.getElementById('newTransactionBtn');
    
    if (newTxBtn) {
        newTxBtn.addEventListener('click', () => {
            document.getElementById('newTransactionModal').style.display = 'block';
        });
    }
}

// Initialize Wallet Form
function initializeWalletForm() {
    const createWalletBtn = document.getElementById('createWalletBtn');
    const importWalletBtn = document.getElementById('importWalletBtn');
    
    if (createWalletBtn) {
        createWalletBtn.addEventListener('click', () => {
            document.getElementById('createWalletModal').style.display = 'block';
        });
    }
    
    if (importWalletBtn) {
        importWalletBtn.addEventListener('click', () => {
            document.getElementById('importWalletModal').style.display = 'block';
        });
    }
}

// Navigation
function initializeNavigation() {
    document.querySelectorAll('.nav-btn').forEach(btn => {
        btn.addEventListener('click', () => {
            const view = btn.dataset.view;
            switchView(view);
        });
    });
}

function switchView(viewName) {
    // Update nav buttons
    document.querySelectorAll('.nav-btn').forEach(btn => {
        btn.classList.remove('active');
        if (btn.dataset.view === viewName) {
            btn.classList.add('active');
        }
    });
    
    // Update views
    document.querySelectorAll('.view').forEach(view => {
        view.classList.remove('active');
    });
    document.getElementById(`${viewName}-view`).classList.add('active');
    
    // Load view-specific data
    if (viewName === 'transactions') {
        loadTransactions();
    } else if (viewName === 'rules') {
        loadRules();
    } else if (viewName === 'wallets') {
        loadWalletsEnhanced();
    }
}

// Initialize Charts
function initializeCharts() {
    // Activity Chart (Line Chart)
    const activityCtx = document.getElementById('activityChart');
    if (activityCtx) {
        activityChart = new Chart(activityCtx, {
            type: 'line',
            data: {
                labels: ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'],
                datasets: [{
                    label: 'Transactions',
                    data: [0, 0, 0, 0, 0, 0, 0],
                    borderColor: '#000000',
                    backgroundColor: 'rgba(0, 0, 0, 0.05)',
                    fill: true,
                    tension: 0.4,
                    borderWidth: 2
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: { display: false }
                },
                scales: {
                    y: {
                        beginAtZero: true,
                        ticks: { stepSize: 1 },
                        grid: { color: '#E5E5E5' }
                    },
                    x: {
                        grid: { display: false }
                    }
                }
            }
        });
    }
    
    // Type Chart (Doughnut Chart)
    const typeCtx = document.getElementById('typeChart');
    if (typeCtx) {
        typeChart = new Chart(typeCtx, {
            type: 'doughnut',
            data: {
                labels: ['Native', 'Token', 'Contract'],
                datasets: [{
                    data: [0, 0, 0],
                    backgroundColor: ['#000000', '#525252', '#A3A3A3'],
                    borderWidth: 0
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        position: 'bottom',
                        labels: {
                            usePointStyle: true,
                            padding: 15,
                            font: { size: 12 }
                        }
                    }
                }
            }
        });
    }
    
    // Status Chart (BIG Doughnut Chart) - GREEN for SUCCESS, RED for BLOCKED
    const statusCtx = document.getElementById('statusChart');
    if (statusCtx) {
        statusChart = new Chart(statusCtx, {
            type: 'doughnut',
            data: {
                labels: ['✅ Success', '🛡️ Blocked'],
                datasets: [{
                    data: [0, 0],
                    backgroundColor: ['#10B981', '#EF4444'], // Green & Red
                    borderWidth: 4,
                    borderColor: '#FFFFFF',
                    hoverOffset: 15
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                cutout: '60%',
                plugins: {
                    legend: {
                        position: 'bottom',
                        labels: {
                            usePointStyle: true,
                            padding: 20,
                            font: { 
                                size: 16,
                                weight: 'bold'
                            }
                        }
                    },
                    tooltip: {
                        backgroundColor: 'rgba(0,0,0,0.8)',
                        titleFont: { size: 16 },
                        bodyFont: { size: 14 },
                        padding: 12
                    }
                }
            }
        });
    }
}

// Load Dashboard Data
async function loadDashboardData() {
    try {
        // Load health status
        const health = await fetch('/health').then(r => r.json());
        updateNetworkStatus(health);
        
        // Load wallet list - use enhanced loading for selector
        await loadWalletsEnhanced();
        
        // Load balance and update active wallet info
        try {
            const balance = await fetch(`${API_BASE}/wallet/balance`).then(r => r.json());
            updateBalance(balance);
            updateActiveWalletInfo(balance);
        } catch (e) {
            console.log('No wallet loaded');
            updateActiveWalletInfo(null);
        }
        
        // Load transactions
        const transactions = await fetch(`${API_BASE}/audit/transactions?limit=100`).then(r => r.json());
        await updateTransactionStats(transactions);
        updateRecentActivity(transactions);
        updateCharts(transactions);
        
        // Load rules
        const rules = await fetch(`${API_BASE}/rules`).then(r => r.json());
        updateRulesCount(rules);
        
        // Also load full rules for the rules view
        await loadRules();
        
    } catch (error) {
        console.error('Error loading dashboard data:', error);
    }
}

// Update Active Wallet Info
function updateActiveWalletInfo(balance) {
    const container = document.getElementById('activeWalletInfo');
    const banner = document.getElementById('walletConnectionBanner');
    
    if (!balance || !balance.address) {
        container.innerHTML = '<div class="empty-message">No wallet loaded. Import a wallet to get started.</div>';
        walletConnected = false;
        
        // Show wallet connection banner
        if (banner) {
            banner.classList.remove('hidden');
        }
        return;
    }
    
    walletConnected = true;
    
    // Hide wallet connection banner
    if (banner) {
        banner.classList.add('hidden');
    }
    
    const currency = balance.currency || currentCurrency;
    
    container.innerHTML = `
        <div class="wallet-info-item">
            <span class="wallet-info-label">Address</span>
            <span class="wallet-info-value" title="${balance.address}">${balance.address.substring(0, 10)}...${balance.address.substring(balance.address.length - 8)}</span>
        </div>
        <div class="wallet-info-item">
            <span class="wallet-info-label">Network</span>
            <span class="wallet-info-value">${balance.network || currentNetwork}</span>
        </div>
        <div class="wallet-info-item">
            <span class="wallet-info-label">Balance</span>
            <span class="wallet-info-value">${parseFloat(balance.balance_ether || 0).toFixed(4)} ${currency}</span>
        </div>
    `;
}

// Update Network Status
function updateNetworkStatus(health) {
    const networkName = document.getElementById('networkName');
    const networkValue = document.getElementById('networkValue');
    const chainId = document.getElementById('chainId');
    
    let networkNameText = 'Unknown';
    let chainIdText = 'N/A';
    
    if (health.network && typeof health.network === 'object') {
        networkNameText = health.network.name || 'Unknown';
        chainIdText = health.network.chain_id || 'N/A';
        currentCurrency = health.network.currency || 'ETH';
    } else {
        networkNameText = health.network || 'Unknown';
        chainIdText = health.chain_id || 'N/A';
    }
    
    // Set currency based on network
    currentNetwork = networkNameText;
    if (networkNameText.toLowerCase().includes('polygon')) {
        currentCurrency = 'MATIC';
    } else if (networkNameText.toLowerCase().includes('sepolia')) {
        currentCurrency = 'SepoliaETH';
    } else if (networkNameText.toLowerCase().includes('mainnet') && !networkNameText.toLowerCase().includes('polygon')) {
        currentCurrency = 'ETH';
    } else if (networkNameText.toLowerCase().includes('sandbox')) {
        currentCurrency = 'ETH';
    }
    
    if (networkName) networkName.textContent = networkNameText;
    if (networkValue) networkValue.textContent = networkNameText;
    if (chainId) chainId.textContent = `Chain ID: ${chainIdText}`;
}

// Update Wallet Selector
function updateWalletSelector(walletList) {
    const dropdown = document.getElementById('walletDropdown');
    if (!dropdown) return; // Skip if element not found
    
    dropdown.innerHTML = '<option value="">No Wallet</option>';
    
    const wallets = walletList.wallets || walletList || [];
    wallets.forEach(wallet => {
        const option = document.createElement('option');
        option.value = wallet.name || wallet;
        option.textContent = wallet.name || wallet;
        dropdown.appendChild(option);
    });
    
    // Remove old listeners by cloning
    const newDropdown = dropdown.cloneNode(true);
    dropdown.parentNode.replaceChild(newDropdown, dropdown);
    
    newDropdown.addEventListener('change', async (e) => {
        if (e.target.value) {
            await switchWallet(e.target.value);
        }
    });
}

// Initialize wallet selector event listener
function initializeWalletSelector() {
    const walletSelect = document.getElementById('walletSelect');
    if (walletSelect) {
        walletSelect.addEventListener('change', async (e) => {
            if (e.target.value) {
                await switchWallet(e.target.value);
            }
        });
    }
    
    const refreshWalletBtn = document.getElementById('refreshWalletBtn');
    if (refreshWalletBtn) {
        refreshWalletBtn.addEventListener('click', async () => {
            await loadWalletsEnhanced();
            await loadDashboardData();
            showNotification('Wallets refreshed', 'success');
        });
    }
}

// Update Balance
function updateBalance(balance) {
    const balanceValue = document.getElementById('balanceValue');
    const walletNameValue = document.getElementById('walletNameValue');
    const walletAddressShort = document.getElementById('walletAddressShort');
    
    if (balance && balance.balance_ether !== undefined) {
        const currency = balance.currency || currentCurrency;
        balanceValue.textContent = `${parseFloat(balance.balance_ether).toFixed(4)} ${currency}`;
        walletConnected = true;
        
        // Update wallet display in stats
        if (balance.address) {
            if (walletAddressShort) {
                walletAddressShort.textContent = `${balance.address.substring(0, 6)}...${balance.address.substring(balance.address.length - 4)}`;
                walletAddressShort.title = balance.address;
            }
        }
        
        // Hide wallet connection banner
        const banner = document.getElementById('walletConnectionBanner');
        if (banner) {
            banner.classList.add('hidden');
        }
    } else {
        balanceValue.textContent = `0.00 ${currentCurrency}`;
        walletConnected = false;
        
        if (walletNameValue) {
            walletNameValue.textContent = 'Connected';
        }
        if (walletAddressShort) {
            walletAddressShort.textContent = '-';
        }
    }
}

// Update Transaction Stats - USES SAME DATA AS CHART
async function updateTransactionStats(transactions) {
    const txCountValue = document.getElementById('txCountValue');
    const txConfirmed = document.getElementById('txConfirmed');
    const txDenied = document.getElementById('txDenied');
    const txs = transactions.transactions || [];
    
    // Count successful transactions (same as chart)
    const successCount = txs.filter(tx => 
        tx.status === 'confirmed' || tx.status === 'pending' || tx.status === 'SUBMITTED'
    ).length;
    
    // Fetch blocked count from audit events (same as chart)
    let blockedCount = 0;
    try {
        const events = await fetch(`${API_BASE}/audit/events?limit=100`).then(r => r.json());
        const eventList = events.events || [];
        blockedCount = eventList.filter(e => 
            e.event_type === 'TX_BLOCKED' || e.event_type === 'TX_DENIED'
        ).length;
    } catch (error) {
        console.error('Failed to fetch blocked transactions:', error);
    }
    
    // Update stats card with correct counts
    const totalCount = successCount + blockedCount;
    txCountValue.textContent = totalCount;
    
    if (txConfirmed) {
        txConfirmed.textContent = successCount;
    }
    if (txDenied) {
        txDenied.textContent = blockedCount;
    }
}

// Update Rules Count
function updateRulesCount(rules) {
    const rulesCountValue = document.getElementById('rulesCountValue');
    const rulesList = rules.rules || [];
    const activeRules = rulesList.filter(r => r.enabled).length;
    rulesCountValue.textContent = activeRules;
}

// Update Recent Activity
function updateRecentActivity(transactions) {
    const activityList = document.getElementById('recentActivity');
    const txs = transactions.transactions || [];
    
    if (txs.length === 0) {
        activityList.innerHTML = '<div class="empty-message">No recent transactions</div>';
        return;
    }
    
    // Show only first 3 transactions
    activityList.innerHTML = txs.slice(0, 3).map(tx => `
        <div class="activity-item">
            <div class="left">
                <span class="icon">💸</span>
                <div>
                    <div><strong>${tx.to_address.substring(0, 10)}...</strong></div>
                    <div class="time">${new Date(tx.timestamp).toLocaleString()}</div>
                </div>
            </div>
            <div class="right">
                <div><strong>${parseFloat(tx.value_ether || 0).toFixed(4)} ${currentCurrency}</strong></div>
                <div class="status-${tx.status.toLowerCase()}">${tx.status}</div>
            </div>
        </div>
    `).join('');
}

// Update Charts
function updateCharts(transactions) {
    const txs = transactions.transactions || [];
    
    // Update activity chart - This week (Mon-Sun) with proper labels
    const today = new Date();
    const currentDayOfWeek = today.getDay(); // 0 = Sunday, 1 = Monday, etc.
    const daysFromMonday = currentDayOfWeek === 0 ? 6 : currentDayOfWeek - 1; // Days since Monday
    
    const weekDays = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'];
    const weekData = Array(7).fill(0);
    
    // Get Monday of this week
    const monday = new Date(today);
    monday.setDate(today.getDate() - daysFromMonday);
    monday.setHours(0, 0, 0, 0);
    
    txs.forEach(tx => {
        const txDate = new Date(tx.timestamp);
        txDate.setHours(0, 0, 0, 0);
        
        // Calculate days since Monday
        const daysSinceMonday = Math.floor((txDate - monday) / (1000 * 60 * 60 * 24));
        
        // Only count transactions from Monday to today
        if (daysSinceMonday >= 0 && daysSinceMonday <= daysFromMonday && daysSinceMonday < 7) {
            weekData[daysSinceMonday]++;
        }
    });
    
    if (activityChart) {
        // Update labels to show only up to today
        const currentWeekLabels = weekDays.slice(0, daysFromMonday + 1);
        const currentWeekData = weekData.slice(0, daysFromMonday + 1);
        
        // Inject sample data for Mon-Wed if real data is empty (Demo visualization)
        if (currentWeekData.every(val => val === 0)) {
            const demoData = [2, 3, 1, 0, 0, 0, 0]; // Sample data: Mon=2, Tue=3, Wed=1
            for (let i = 0; i <= daysFromMonday && i < 3; i++) {
                currentWeekData[i] = demoData[i];
            }
        }
        
        activityChart.data.labels = currentWeekLabels;
        activityChart.data.datasets[0].data = currentWeekData;
        activityChart.update();
    }
    
    // Update type chart - REAL DATA ONLY (with fallback for demo)
    let nativeCount = txs.filter(tx => !tx.token_address).length;
    let tokenCount = txs.filter(tx => tx.token_address).length;
    
    // Fake data for demo if empty
    if (nativeCount === 0 && tokenCount === 0) {
        nativeCount = 25;
        tokenCount = 14;
    }
    
    if (typeChart) {
        typeChart.data.datasets[0].data = [nativeCount, tokenCount, 0];
        typeChart.update();
    }
    
    // Update status chart - SUCCESS (Green) vs BLOCKED (Red)
    updateStatusChartAsync(txs);
}

// Async function to update status chart with blocked count from audit events
async function updateStatusChartAsync(txs) {
    // Count successful transactions (confirmed or pending)
    let successCount = txs.filter(tx => 
        tx.status === 'confirmed' || tx.status === 'pending' || tx.status === 'SUBMITTED'
    ).length;
    
    // Fetch blocked count from audit events
    let blockedCount = 0;
    try {
        const events = await fetch(`${API_BASE}/audit/events?limit=100`).then(r => r.json());
        const eventList = events.events || [];
        blockedCount = eventList.filter(e => 
            e.event_type === 'TX_BLOCKED' || e.event_type === 'TX_DENIED'
        ).length;
    } catch (error) {
        console.error('Failed to fetch blocked transactions:', error);
    }
    
    // Update chart with real-time data
    if (statusChart) {
        statusChart.data.datasets[0].data = [successCount, blockedCount];
        statusChart.update('active'); // Animate the update
    }
}

// Load Transactions
// Update Transaction Status Display (Main Focus)
async function updateTransactionStatusDisplay(transactions) {
    const txs = transactions.transactions || [];
    
    // Count successful transactions
    let successCount = 0;
    let latestSuccess = null;
    
    txs.forEach(tx => {
        if (tx.status === 'confirmed' || tx.status === 'pending' || tx.status === 'SUBMITTED') {
            successCount++;
            if (!latestSuccess) latestSuccess = tx;
        }
    });
    
    // Fetch audit events to count blocked transactions
    let blockedCount = 0;
    let latestBlocked = null;
    try {
        const events = await fetch(`${API_BASE}/audit/events?limit=100`).then(r => r.json());
        const eventList = events.events || [];
        
        eventList.forEach(event => {
            if (event.event_type === 'TX_BLOCKED' || event.event_type === 'TX_DENIED') {
                blockedCount++;
                if (!latestBlocked) {
                    try {
                        const details = typeof event.details === 'string' ? JSON.parse(event.details) : event.details;
                        latestBlocked = details;
                    } catch (e) {
                        // Ignore parse errors
                    }
                }
            }
        });
    } catch (error) {
        console.error('Failed to fetch audit events:', error);
    }
    
    // Update success card
    document.getElementById('successCount').textContent = successCount;
    if (latestSuccess) {
        document.getElementById('successDetail').textContent = 
            `Last: ${latestSuccess.value} ${currentCurrency} at ${new Date(latestSuccess.timestamp).toLocaleTimeString()}`;
    } else {
        document.getElementById('successDetail').textContent = 'No transactions yet';
    }
    
    // Update blocked card
    document.getElementById('blockedCount').textContent = blockedCount;
    if (latestBlocked && latestBlocked.value) {
        document.getElementById('blockedDetail').textContent = 
            `Last blocked: ${latestBlocked.value} ${currentCurrency}`;
    } else {
        document.getElementById('blockedDetail').textContent = 'All transactions within limits';
    }
    
    // Add animation on update
    const successCard = document.getElementById('successCard');
    const blockedCard = document.getElementById('blockedCard');
    if (successCount > 0) {
        successCard.style.animation = 'pulse 0.5s ease';
        setTimeout(() => successCard.style.animation = '', 500);
    }
    if (blockedCount > 0) {
        blockedCard.style.animation = 'pulse 0.5s ease';
        setTimeout(() => blockedCard.style.animation = '', 500);
    }
}

async function loadTransactions() {
    try {
        const transactions = await fetch(`${API_BASE}/audit/transactions?limit=50`).then(r => r.json());
        const tbody = document.getElementById('transactionsTableBody');
        const txs = transactions.transactions || [];
        
        // Update the main status display
        await updateTransactionStatusDisplay(transactions);
        
        // Fetch blocked transactions from audit events
        let blockedTxs = [];
        try {
            const events = await fetch(`${API_BASE}/audit/events?limit=100`).then(r => r.json());
            const eventList = events.events || [];
            
            blockedTxs = eventList
                .filter(e => e.event_type === 'TX_BLOCKED' || e.event_type === 'TX_DENIED')
                .map(e => {
                    try {
                        const details = typeof e.details === 'string' ? JSON.parse(e.details) : e.details;
                        return {
                            timestamp: e.timestamp,
                            tx_hash: 'N/A (blocked)',
                            from_address: details.from || 'N/A',
                            to_address: details.to || 'N/A',
                            value: details.value || 0,
                            status: 'blocked',
                            risk_level: details.risk_level || 'high'
                        };
                    } catch (err) {
                        return null;
                    }
                })
                .filter(tx => tx !== null);
        } catch (error) {
            console.error('Failed to fetch blocked transactions:', error);
        }
        
        // Merge successful and blocked transactions
        const allTxs = [...txs, ...blockedTxs].sort((a, b) => 
            new Date(b.timestamp) - new Date(a.timestamp)
        );
        
        if (allTxs.length === 0) {
            // Demo data if no real transactions
            tbody.innerHTML = `
                <tr>
                    <td>${new Date().toLocaleString()}</td>
                    <td>0xabc123...</td>
                    <td>0xYourWallet...</td>
                    <td>0xDemoDest...</td>
                    <td>0.5 MATIC</td>
                    <td class="status-confirmed">confirmed</td>
                </tr>
                <tr>
                    <td>${new Date(Date.now() - 86400000).toLocaleString()}</td>
                    <td>0xdef456...</td>
                    <td>0xYourWallet...</td>
                    <td>0xDemoDest...</td>
                    <td>100 USDC</td>
                    <td class="status-confirmed">confirmed</td>
                </tr>
                <tr>
                    <td>${new Date(Date.now() - 172800000).toLocaleString()}</td>
                    <td>0x789ghi...</td>
                    <td>0xYourWallet...</td>
                    <td>0xBadActor...</td>
                    <td>5000 MATIC</td>
                    <td class="status-denied">denied</td>
                </tr>
            `;
            return;
        }
        
        // Display all transactions (successful + blocked)
        tbody.innerHTML = allTxs.map(tx => {
            const txHashDisplay = tx.tx_hash === 'N/A (blocked)' 
                ? 'N/A (blocked)' 
                : `<span title="${tx.tx_hash}">${tx.tx_hash.substring(0, 10)}...</span>`;
            
            const valueDisplay = tx.value_ether 
                ? `${parseFloat(tx.value_ether).toFixed(4)} ${currentCurrency}`
                : `${parseFloat(tx.value || 0).toFixed(4)} ${currentCurrency}`;
            
            const statusClass = tx.status.toLowerCase();
            const statusDisplay = tx.status === 'blocked' 
                ? `<span class="status-blocked">🛡️ BLOCKED</span>`
                : `<span class="status-${statusClass}">${tx.status}</span>`;
            
            return `
                <tr class="${tx.status === 'blocked' ? 'blocked-row' : ''}">
                    <td>${new Date(tx.timestamp).toLocaleString()}</td>
                    <td>${txHashDisplay}</td>
                    <td title="${tx.from_address}">${tx.from_address.substring(0, 10)}...</td>
                    <td title="${tx.to_address}">${tx.to_address.substring(0, 10)}...</td>
                    <td>${valueDisplay}</td>
                    <td>${statusDisplay}</td>
                </tr>
            `;
        }).join('');
        
        // Update transaction count in stats
        const successCount = txs.length;
        const blockedCount = blockedTxs.length;
        const totalCount = allTxs.length;
        
        document.getElementById('txCountValue').textContent = totalCount;
        document.getElementById('txConfirmed').textContent = successCount;
        document.getElementById('txDenied').textContent = blockedCount;
        
    } catch (error) {
        console.error('Error loading transactions:', error);
    }
}

// Load Rules
async function loadRules() {
    try {
        const rules = await fetch(`${API_BASE}/rules`).then(r => r.json());
        const container = document.getElementById('rulesGrid');
        const activeRulesContainer = document.getElementById('activeRulesList');
        const rulesList = rules.rules || [];
        
        // Debug log
        console.log('Loaded rules:', rulesList);
        
        if (rulesList.length === 0) {
            container.innerHTML = '<div class="empty-message">No rules configured</div>';
            if (activeRulesContainer) {
                activeRulesContainer.innerHTML = '<div class="empty-message">No active rules</div>';
            }
            return;
        }
        
        // Update active rules summary
        const activeRules = rulesList.filter(r => r.enabled);
        if (activeRulesContainer) {
            if (activeRules.length === 0) {
                activeRulesContainer.innerHTML = '<div class="empty-message">No active rules - all transactions allowed</div>';
            } else {
                activeRulesContainer.innerHTML = activeRules.map(rule => {
                    const shortDesc = getShortRuleDescription(rule);
                    return `
                        <div class="active-rule-item">
                            <div class="rule-info">
                                <div class="rule-name">${rule.rule_name}</div>
                                <div class="rule-details">${shortDesc}</div>
                            </div>
                            <div class="rule-badge">${rule.action.toUpperCase()}</div>
                        </div>
                    `;
                }).join('');
            }
        }
        
        // Update all rules grid
        container.innerHTML = rulesList.map(rule => {
            const description = getRuleDescription(rule);
            const parametersHtml = formatRuleParameters(rule);
            
            return `
                <div class="rule-card ${rule.enabled ? 'rule-active' : 'rule-inactive'}">
                    <div class="rule-header">
                        <div class="rule-info">
                            <h4>${rule.rule_name}</h4>
                            <span class="rule-type-badge">${rule.rule_type.replace(/_/g, ' ')}</span>
                        </div>
                        <div class="rule-actions">
                            <label class="toggle-switch">
                                <input type="checkbox" ${rule.enabled ? 'checked' : ''} 
                                    onchange="toggleRule(${rule.rule_id}, this.checked)">
                                <span class="toggle-slider"></span>
                            </label>
                            <button class="btn-icon" onclick="editRule(${rule.rule_id})" title="Edit">✏️</button>
                            <button class="btn-icon" onclick="deleteRule(${rule.rule_id})" title="Delete">🗑️</button>
                        </div>
                    </div>
                    <div class="rule-description">${description}</div>
                    <div class="rule-details">
                        ${parametersHtml}
                    </div>
                    <div class="rule-footer">
                        <span class="rule-action">Action: <strong>${rule.action}</strong></span>
                        <span class="rule-priority">Priority: ${rule.priority}</span>
                    </div>
                </div>
            `;
        }).join('');
    } catch (error) {
        console.error('Error loading rules:', error);
    }
}

// Get short rule description for active rules summary
function getShortRuleDescription(rule) {
    const params = rule.parameters || {};
    
    switch(rule.rule_type) {
        case 'spending_limit':
            const period = params.type || 'daily';
            const amount = params.amount || 0;
            return `Max ${amount} ${currentCurrency} per ${period.replace('_', ' ')}`;
        
        case 'amount_threshold':
            return `Transactions over ${params.threshold || 0} ${currentCurrency}`;
        
        case 'address_whitelist':
            const whitelistCount = (params.addresses || []).length;
            return `Only ${whitelistCount} whitelisted address${whitelistCount !== 1 ? 'es' : ''} allowed`;
        
        case 'address_blacklist':
            const blacklistCount = (params.addresses || []).length;
            return `${blacklistCount} address${blacklistCount !== 1 ? 'es' : ''} blocked`;
        
        case 'time_restriction':
            return `Only during ${params.allowed_hours || 'specified hours'}`;
        
        case 'daily_transaction_count':
            return `Max ${params.max_count || 0} transactions per day`;
        
        default:
            return rule.rule_type.replace(/_/g, ' ');
    }
}

// Get rule description
function getRuleDescription(rule) {
    const descriptions = {
        'spending_limit': 'Controls how much can be spent within a specific time period',
        'address_whitelist': 'Only allows transactions to pre-approved addresses',
        'address_blacklist': 'Blocks transactions to specific addresses',
        'time_restriction': 'Limits transactions to specific hours or days',
        'amount_threshold': 'Requires approval for transactions above a certain amount',
        'daily_transaction_count': 'Limits the number of transactions per day'
    };
    return descriptions[rule.rule_type] || 'Custom rule';
}

// Format rule parameters
function formatRuleParameters(rule) {
    const params = rule.parameters;
    const type = rule.rule_type;
    
    if (type === 'spending_limit') {
        const limitType = params.type || 'daily';
        const amount = params.amount || 0;
        return `<div class="param-item">Limit: <strong>${amount} ETH</strong> per ${limitType}</div>`;
    } else if (type === 'address_whitelist' || type === 'address_blacklist') {
        const addresses = params.addresses || [];
        if (addresses.length === 0) return '<div class="param-item">No addresses configured</div>';
        return `<div class="param-item">${addresses.length} address(es) configured</div>`;
    } else if (type === 'time_restriction') {
        const hours = params.allowed_hours || 'Not set';
        const timezone = params.timezone || 'UTC';
        return `<div class="param-item">Hours: <strong>${hours}</strong> (${timezone})</div>`;
    } else if (type === 'amount_threshold') {
        const threshold = params.threshold || 0;
        return `<div class="param-item">Threshold: <strong>${threshold} ETH</strong></div>`;
    } else if (type === 'daily_transaction_count') {
        const maxCount = params.max_count || 0;
        return `<div class="param-item">Max transactions: <strong>${maxCount}</strong> per day</div>`;
    }
    
    return '<div class="param-item">Custom parameters</div>';
}

// Toggle Rule
async function toggleRule(ruleId, enabled) {
    try {
        const response = await fetch(`${API_BASE}/rules/${ruleId}`, {
            method: 'PUT',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ enabled })
        });
        
        if (!response.ok) throw new Error('Failed to toggle rule');
        
        showNotification(`Rule ${enabled ? 'enabled' : 'disabled'} successfully`, 'success');
        await loadRules();
    } catch (error) {
        console.error('Error toggling rule:', error);
        showNotification('Failed to toggle rule', 'error');
        await loadRules(); // Reload to reset toggle state
    }
}

// Edit Rule
async function editRule(ruleId) {
    try {
        const rules = await fetch(`${API_BASE}/rules`).then(r => r.json());
        const rule = rules.rules.find(r => r.rule_id === ruleId);
        
        if (!rule) throw new Error('Rule not found');
        
        // Populate edit modal
        document.getElementById('editRuleId').value = rule.rule_id;
        document.getElementById('editRuleName').value = rule.rule_name;
        document.getElementById('editRuleType').value = rule.rule_type;
        document.getElementById('editRuleAction').value = rule.action;
        document.getElementById('editRulePriority').value = rule.priority;
        
        // Update parameters based on rule type
        updateEditRuleParams(rule.rule_type, rule.parameters);
        
        // Show modal
        document.getElementById('editRuleModal').style.display = 'block';
    } catch (error) {
        console.error('Error loading rule for edit:', error);
        showNotification('Failed to load rule', 'error');
    }
}

// Update edit rule parameters section
function updateEditRuleParams(ruleType, currentParams = {}) {
    const paramsGroup = document.getElementById('editRuleParamsGroup');
    
    if (ruleType === 'spending_limit') {
        paramsGroup.innerHTML = `
            <label>Period:</label>
            <select id="editParamType">
                <option value="per_transaction" ${currentParams.type === 'per_transaction' ? 'selected' : ''}>Per Transaction</option>
                <option value="daily" ${currentParams.type === 'daily' ? 'selected' : ''}>Daily</option>
                <option value="weekly" ${currentParams.type === 'weekly' ? 'selected' : ''}>Weekly</option>
                <option value="monthly" ${currentParams.type === 'monthly' ? 'selected' : ''}>Monthly</option>
            </select>
            <label>Amount (ETH):</label>
            <input type="number" id="editParamAmount" step="0.01" value="${currentParams.amount || 1.0}" required>
        `;
    } else if (ruleType === 'amount_threshold') {
        paramsGroup.innerHTML = `
            <label>Threshold (ETH):</label>
            <input type="number" id="editParamThreshold" step="0.01" value="${currentParams.threshold || 0.5}" required>
        `;
    } else if (ruleType === 'address_whitelist' || ruleType === 'address_blacklist') {
        const addresses = currentParams.addresses || [];
        paramsGroup.innerHTML = `
            <label>Addresses (one per line):</label>
            <textarea id="editParamAddresses" rows="4" placeholder="0x...">${addresses.join('\n')}</textarea>
        `;
    } else if (ruleType === 'time_restriction') {
        paramsGroup.innerHTML = `
            <label>Allowed Hours (HH:MM-HH:MM):</label>
            <input type="text" id="editParamHours" value="${currentParams.allowed_hours || '09:00-17:00'}" required>
            <label>Timezone:</label>
            <input type="text" id="editParamTimezone" value="${currentParams.timezone || 'UTC'}" required>
        `;
    } else if (ruleType === 'daily_transaction_count') {
        paramsGroup.innerHTML = `
            <label>Max Transactions per Day:</label>
            <input type="number" id="editParamMaxCount" value="${currentParams.max_count || 10}" required>
        `;
    }
}

// Delete Rule
async function deleteRule(ruleId) {
    if (!confirm('Are you sure you want to delete this rule?')) return;
    
    try {
        const response = await fetch(`${API_BASE}/rules/${ruleId}`, {
            method: 'DELETE'
        });
        
        if (!response.ok) throw new Error('Failed to delete rule');
        
        showNotification('Rule deleted successfully', 'success');
        await loadRules();
    } catch (error) {
        console.error('Error deleting rule:', error);
        showNotification('Failed to delete rule', 'error');
    }
}

// Submit Edit Rule Form
async function submitEditRule(event) {
    event.preventDefault();
    
    const ruleId = document.getElementById('editRuleId').value;
    const ruleType = document.getElementById('editRuleType').value;
    
    // Build parameters object based on rule type
    let parameters = {};
    
    if (ruleType === 'spending_limit') {
        parameters = {
            type: document.getElementById('editParamType').value,
            amount: parseFloat(document.getElementById('editParamAmount').value)
        };
    } else if (ruleType === 'amount_threshold') {
        parameters = {
            threshold: parseFloat(document.getElementById('editParamThreshold').value)
        };
    } else if (ruleType === 'address_whitelist' || ruleType === 'address_blacklist') {
        const addressesText = document.getElementById('editParamAddresses').value;
        parameters = {
            addresses: addressesText.split('\n').map(a => a.trim()).filter(a => a)
        };
    } else if (ruleType === 'time_restriction') {
        parameters = {
            allowed_hours: document.getElementById('editParamHours').value,
            timezone: document.getElementById('editParamTimezone').value
        };
    } else if (ruleType === 'daily_transaction_count') {
        parameters = {
            max_count: parseInt(document.getElementById('editParamMaxCount').value)
        };
    }
    
    const priority = parseInt(document.getElementById('editRulePriority').value);
    
    try {
        const response = await fetch(`${API_BASE}/rules/${ruleId}`, {
            method: 'PUT',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ parameters, priority })
        });
        
        if (!response.ok) throw new Error('Failed to update rule');
        
        showNotification('Rule updated successfully', 'success');
        document.getElementById('editRuleModal').style.display = 'none';
        await loadRules();
    } catch (error) {
        console.error('Error updating rule:', error);
        showNotification('Failed to update rule', 'error');
    }
}

// Load Wallets with Enhanced Display
async function loadWalletsEnhanced() {
    try {
        const response = await fetch(`${API_BASE}/wallet/list`);
        const wallets = await response.json();
        const walletsContainer = document.getElementById('walletsList');
        const walletSelect = document.getElementById('walletSelect');
        
        // Get current wallet
        let currentWalletAddress = null;
        let currentWalletName = null;
        try {
            const balanceResponse = await fetch(`${API_BASE}/wallet/balance`);
            if (balanceResponse.ok) {
                const balanceData = await balanceResponse.json();
                currentWalletAddress = balanceData.address;
                
                // Find wallet name
                const currentWallet = wallets.find(w => w.address === currentWalletAddress);
                if (currentWallet) {
                    currentWalletName = currentWallet.name;
                    
                    // Update wallet name in stats
                    const walletNameValue = document.getElementById('walletNameValue');
                    if (walletNameValue) {
                        walletNameValue.textContent = currentWalletName;
                    }
                }
            }
        } catch (e) {
            // No wallet loaded
        }
        
        if (wallets.length === 0) {
            walletsContainer.innerHTML = '<div class="empty-state">No wallets found</div>';
            walletSelect.innerHTML = '<option value="">No wallets</option>';
            return;
        }
        
        // Update select dropdown with enhanced options
        walletSelect.innerHTML = wallets.map(w => `
            <option value="${w.name}" ${w.address === currentWalletAddress ? 'selected' : ''}>
                ${w.name} - ${w.address.substring(0, 8)}... (${w.network})
            </option>
        `).join('');
        
        // Update wallets list view with cards
        walletsContainer.innerHTML = await Promise.all(wallets.map(async wallet => {
            const isActive = wallet.address === currentWalletAddress;
            
            // Try to get balance for this wallet
            let balance = '---';
            if (isActive) {
                try {
                    const balanceResponse = await fetch(`${API_BASE}/wallet/balance`);
                    if (balanceResponse.ok) {
                        const balanceData = await balanceResponse.json();
                        balance = parseFloat(balanceData.balance_eth).toFixed(4);
                    }
                } catch (e) {
                    // Ignore balance fetch errors
                }
            }
            
            return `
                <div class="wallet-card ${isActive ? 'wallet-active' : ''}">
                    <div class="wallet-header">
                        <div class="wallet-icon">${isActive ? '✅' : '👛'}</div>
                        <div class="wallet-info">
                            <h4>${wallet.name} ${isActive ? '<span class="active-badge">ACTIVE</span>' : ''}</h4>
                            <div class="wallet-address" title="${wallet.address}">${wallet.address}</div>
                        </div>
                    </div>
                    <div class="wallet-details">
                        <div class="wallet-detail-item">
                            <span class="label">Network:</span>
                            <span class="value">${wallet.network}</span>
                        </div>
                        <div class="wallet-detail-item">
                            <span class="label">Balance:</span>
                            <span class="value">${balance} ${currentCurrency}</span>
                        </div>
                    </div>
                    <div class="wallet-actions">
                        ${!isActive ? `<button class="btn btn-primary btn-small" onclick="switchWallet('${wallet.name}')">Switch to this wallet</button>` : '<span class="wallet-status">Currently Active</span>'}
                    </div>
                </div>
            `;
        })).then(cards => cards.join(''));
        
    } catch (error) {
        console.error('Error loading wallets:', error);
        // COMMENTED OUT: showNotification('Failed to load wallets', 'error');
    }
}

// Switch Wallet
async function switchWallet(walletName) {
    try {
        const response = await fetch(`${API_BASE}/wallet/load`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ wallet_name: walletName })
        });
        
        if (!response.ok) throw new Error('Failed to switch wallet');
        
        // COMMENTED OUT: showNotification(`Switched to wallet: ${walletName}`, 'success');
        await loadWalletsEnhanced();
        await loadDashboardData();
    } catch (error) {
        console.error('Error switching wallet:', error);
        // COMMENTED OUT: showNotification('Failed to switch wallet', 'error');
    }
}

// COMMENTED OUT: Notification System
/*
function showNotification(message, type = 'info') {
    // Create notification element
    const notification = document.createElement('div');
    notification.className = `notification notification-${type}`;
    notification.textContent = message;
    
    // Add to body
    document.body.appendChild(notification);
    
    // Show notification
    setTimeout(() => {
        notification.classList.add('notification-show');
    }, 10);
    
    // Remove after 3 seconds
    setTimeout(() => {
        notification.classList.remove('notification-show');
        setTimeout(() => {
            document.body.removeChild(notification);
        }, 300);
    }, 3000);
}
*/

// Chat Functions
async function sendChat() {
    const input = document.getElementById('chatInput');
    const messages = document.getElementById('chatMessages');
    const text = input.value.trim();
    
    if (!text) return;
    
    // Add user message
    const userMessageDiv = document.createElement('div');
    userMessageDiv.className = 'chat-message user';
    userMessageDiv.innerHTML = `
        <div class="message-avatar">👤</div>
        <div class="message-content">
            <p>${escapeHtml(text)}</p>
        </div>
    `;
    messages.appendChild(userMessageDiv);
    
    input.value = '';
    messages.scrollTop = messages.scrollHeight;
    
    // Add loading indicator
    const loadingDiv = document.createElement('div');
    loadingDiv.className = 'chat-message bot loading';
    loadingDiv.innerHTML = `
        <div class="message-avatar">🤖</div>
        <div class="message-content">
            <p>Processing...</p>
        </div>
    `;
    messages.appendChild(loadingDiv);
    messages.scrollTop = messages.scrollHeight;
    
    try {
        // Send to AI with execution
        const response = await fetch(`${API_BASE}/ai/parse`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ text, execute: true })
        });
        
        // Remove loading indicator
        messages.removeChild(loadingDiv);
        
        const result = await response.json();
        
        // Format bot response based on intent
        let botMessage = '';
        
        if (result.intent === 'check_balance' && result.execution_result) {
            const balance = result.execution_result.balance_ether || result.execution_result.balance || 0;
            const currency = result.execution_result.currency || 'ETH';
            botMessage = `Your current balance is <strong>${balance} ${currency}</strong>`;
        } else if (result.intent === 'send_transaction' && result.action_status === 'executed') {
            const tx = result.execution_result || {};
            botMessage = `✅ Transaction sent successfully!<br>
                <strong>Amount:</strong> ${tx.value || result.entities?.amount || 'N/A'}<br>
                <strong>To:</strong> ${(tx.to_address || result.entities?.address || 'N/A').substring(0, 20)}...<br>
                <strong>Status:</strong> ${tx.status || 'pending'}<br>
                ${tx.tx_hash ? `<strong>TX Hash:</strong> ${tx.tx_hash.substring(0, 20)}...` : ''}`;
        } else if (result.intent === 'send_transaction' && result.action_status === 'denied') {
            botMessage = `❌ Transaction denied by security rules.<br>
                <strong>Reason:</strong> ${result.denial_reason || 'Rule violation'}`;
        } else if (result.intent === 'create_rule' && result.action_status === 'executed') {
            botMessage = `✅ Rule created successfully!<br>
                <strong>Rule:</strong> ${result.execution_result?.rule_name || 'New rule'}`;
        } else {
            // Generic response
            botMessage = `<strong>Intent:</strong> ${result.intent}<br>
                <strong>Confidence:</strong> ${(result.confidence * 100).toFixed(0)}%<br>
                ${result.response || ''}`;
        }
        
        // Add bot response
        const botMessageDiv = document.createElement('div');
        botMessageDiv.className = 'chat-message bot';
        botMessageDiv.innerHTML = `
            <div class="message-avatar">🤖</div>
            <div class="message-content">
                <p>${botMessage}</p>
            </div>
        `;
        messages.appendChild(botMessageDiv);
        messages.scrollTop = messages.scrollHeight;
        
        // Refresh dashboard data if transaction was executed
        if (result.action_status === 'executed' || result.execution_result) {
            setTimeout(() => {
                loadDashboardData();
                loadTransactions();
                loadRules();
            }, 1000);
        }
    } catch (error) {
        console.error('Chat error:', error);
        
        // Remove loading indicator
        if (messages.contains(loadingDiv)) {
            messages.removeChild(loadingDiv);
        }
        
        // Add error message
        const errorDiv = document.createElement('div');
        errorDiv.className = 'chat-message bot error';
        errorDiv.innerHTML = `
            <div class="message-avatar">⚠️</div>
            <div class="message-content">
                <p><strong>Error:</strong> ${error.message || 'Failed to process request'}</p>
            </div>
        `;
        messages.appendChild(errorDiv);
        messages.scrollTop = messages.scrollHeight;
    }
}

// Helper function to escape HTML
function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

function handleChatKeyPress(event) {
    if (event.key === 'Enter') {
        sendChat();
    }
}

// Update Rule Params Form dynamically
function updateRuleParamsForm() {
    const ruleType = document.getElementById('ruleType').value;
    const paramsGroup = document.getElementById('ruleParamsGroup');
    
    if (ruleType === 'spending_limit') {
        paramsGroup.innerHTML = `
            <div class="form-group">
                <label>Period</label>
                <select id="paramType">
                    <option value="per_transaction">Per Transaction</option>
                    <option value="daily">Daily</option>
                    <option value="weekly">Weekly</option>
                    <option value="monthly">Monthly</option>
                </select>
            </div>
            <div class="form-group">
                <label>Amount</label>
                <input type="number" id="paramAmount" step="0.01" placeholder="1.0" required>
            </div>
        `;
    } else if (ruleType === 'amount_threshold') {
        paramsGroup.innerHTML = `
            <div class="form-group">
                <label>Threshold Amount</label>
                <input type="number" id="paramThreshold" step="0.01" placeholder="0.5" required>
            </div>
        `;
    } else if (ruleType === 'address_whitelist' || ruleType === 'address_blacklist') {
        paramsGroup.innerHTML = `
            <div class="form-group">
                <label>Addresses (one per line)</label>
                <textarea id="paramAddresses" rows="4" placeholder="0x...&#10;0x..."></textarea>
            </div>
        `;
    } else if (ruleType === 'time_restriction') {
        paramsGroup.innerHTML = `
            <div class="form-group">
                <label>Allowed Hours (HH:MM-HH:MM)</label>
                <input type="text" id="paramHours" placeholder="09:00-17:00" required>
            </div>
            <div class="form-group">
                <label>Timezone</label>
                <input type="text" id="paramTimezone" value="UTC" required>
            </div>
        `;
    } else if (ruleType === 'daily_transaction_count') {
        paramsGroup.innerHTML = `
            <div class="form-group">
                <label>Max Transactions per Day</label>
                <input type="number" id="paramMaxCount" placeholder="10" required>
            </div>
        `;
    }
}

// Submit Rule Form
async function submitRule(event) {
    event.preventDefault();
    
    const ruleType = document.getElementById('ruleType').value;
    const ruleName = document.getElementById('ruleName').value;
    const ruleAction = document.getElementById('ruleAction').value;
    const rulePriority = parseInt(document.getElementById('rulePriority').value);
    
    // Build parameters based on rule type
    let parameters = {};
    
    if (ruleType === 'spending_limit') {
        parameters = {
            type: document.getElementById('paramType').value,
            amount: parseFloat(document.getElementById('paramAmount').value)
        };
    } else if (ruleType === 'amount_threshold') {
        parameters = {
            threshold: parseFloat(document.getElementById('paramThreshold').value)
        };
    } else if (ruleType === 'address_whitelist' || ruleType === 'address_blacklist') {
        const addressesText = document.getElementById('paramAddresses').value;
        parameters = {
            addresses: addressesText.split('\n').map(a => a.trim()).filter(a => a)
        };
    } else if (ruleType === 'time_restriction') {
        parameters = {
            allowed_hours: document.getElementById('paramHours').value,
            timezone: document.getElementById('paramTimezone').value
        };
    } else if (ruleType === 'daily_transaction_count') {
        parameters = {
            max_count: parseInt(document.getElementById('paramMaxCount').value)
        };
    }
    
    try {
        const response = await fetch(`${API_BASE}/rules/create`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                rule_type: ruleType,
                rule_name: ruleName,
                parameters: parameters,
                action: ruleAction,
                enabled: true,
                priority: rulePriority
            })
        });
        
        if (!response.ok) {
            const error = await response.json();
            throw new Error(error.detail || 'Failed to create rule');
        }
        
        showNotification('Rule created successfully', 'success');
        closeModal('ruleModal');
        await loadRules();
        await loadDashboardData();
    } catch (error) {
        console.error('Error creating rule:', error);
        showNotification(`Failed to create rule: ${error.message}`, 'error');
    }
}

// Submit Transaction Form
async function submitTransaction(event) {
    event.preventDefault();
    
    const toAddress = document.getElementById('txTo').value;
    const amount = parseFloat(document.getElementById('txAmount').value);
    
    try {
        const response = await fetch(`${API_BASE}/transaction/send`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                to_address: toAddress,
                value: amount
            })
        });
        
        if (!response.ok) {
            const error = await response.json();
            throw new Error(error.detail?.message || error.detail || 'Transaction failed');
        }
        
        const result = await response.json();
        showNotification(`Transaction sent! Hash: ${result.tx_hash.substring(0, 20)}...`, 'success');
        closeModal('txModal');
        
        // Refresh data
        setTimeout(() => {
            loadDashboardData();
            loadTransactions();
        }, 1000);
    } catch (error) {
        console.error('Error sending transaction:', error);
        showNotification(`Transaction failed: ${error.message}`, 'error');
    }
}

// Submit Import Wallet Form
async function submitImportWallet(event) {
    event.preventDefault();
    
    const walletName = document.getElementById('importWalletName').value;
    const privateKey = document.getElementById('importPrivateKey').value;
    
    try {
        const response = await fetch(`${API_BASE}/wallet/import`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                wallet_name: walletName,
                private_key: privateKey
            })
        });
        
        if (!response.ok) {
            const error = await response.json();
            throw new Error(error.detail || 'Failed to import wallet');
        }
        
        const result = await response.json();
        showNotification(`Wallet imported: ${result.address.substring(0, 20)}...`, 'success');
        closeModal('importWalletModal');
        
        // Clear sensitive input
        document.getElementById('importPrivateKey').value = '';
        
        // Load the imported wallet
        await switchWallet(walletName);
    } catch (error) {
        console.error('Error importing wallet:', error);
        showNotification(`Import failed: ${error.message}`, 'error');
    }
}

// Modal helpers
function openRuleModal() {
    document.getElementById('ruleModal').style.display = 'block';
    updateRuleParamsForm(); // Initialize with default params
}

function openTransactionModal() {
    document.getElementById('txModal').style.display = 'block';
}

function closeModal(modalId) {
    document.getElementById(modalId).style.display = 'none';
}

// View switching
function switchView(viewName) {
    // Hide all views
    document.querySelectorAll('.view').forEach(view => {
        view.classList.remove('active');
    });
    
    // Show selected view
    const selectedView = document.getElementById(`${viewName}-view`);
    if (selectedView) {
        selectedView.classList.add('active');
    }
    
    // Update navigation
    document.querySelectorAll('.nav-btn').forEach(btn => {
        btn.classList.remove('active');
        if (btn.getAttribute('data-view') === viewName) {
            btn.classList.add('active');
        }
    });
    
    // Load data for specific views
    if (viewName === 'transactions') {
        loadTransactions();
    } else if (viewName === 'rules') {
        loadRules();
    } else if (viewName === 'ai') {
        // AI view is already loaded
    }
}

function clearChat() {
    const messages = document.getElementById('chatMessages');
    messages.innerHTML = '';  // Completely clear the chat history
    showNotification('Chat history cleared', 'success');
}

// Modal Functions
function openTransactionModal() {
    document.getElementById('txModal').classList.add('active');
}

function openRuleModal() {
    document.getElementById('ruleModal').classList.add('active');
}

function closeModal(modalId) {
    document.getElementById(modalId).classList.remove('active');
}

// Submit Transaction
async function submitTransaction(event) {
    event.preventDefault();
    
    const toAddress = document.getElementById('txTo').value;
    const amount = parseFloat(document.getElementById('txAmount').value);
    
    try {
        const response = await fetch(`${API_BASE}/transaction/send`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ to_address: toAddress, value: amount })
        });
        
        if (response.ok) {
            closeModal('txModal');
            document.getElementById('txTo').value = '';
            document.getElementById('txAmount').value = '';
            loadDashboardData();
            alert('Transaction sent successfully!');
        } else {
            const error = await response.json();
            alert(`Error: ${error.detail || 'Transaction failed'}`);
        }
    } catch (error) {
        alert(`Error: ${error.message}`);
    }
}

// Submit Rule
async function submitRule(event) {
    event.preventDefault();
    
    const name = document.getElementById('ruleName').value;
    const type = document.getElementById('ruleType').value;
    const action = document.getElementById('ruleAction').value;
    
    try {
        const response = await fetch(`${API_BASE}/rules/create`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                name,
                rule_type: type,
                parameters: { type: 'daily', amount: 1.0 },
                action,
                enabled: true
            })
        });
        
        if (response.ok) {
            closeModal('ruleModal');
            document.getElementById('ruleName').value = '';
            loadDashboardData();
            loadRules();
            alert('Rule created successfully!');
        } else {
            const error = await response.json();
            alert(`Error: ${error.detail || 'Rule creation failed'}`);
        }
    } catch (error) {
        alert(`Error: ${error.message}`);
    }
}

// Auto Refresh
function startAutoRefresh() {
    refreshInterval = setInterval(() => {
        loadDashboardData();
    }, 2000); // Refresh every 2 seconds for real-time updates
}

// Close modals when clicking outside
window.onclick = function(event) {
    if (event.target.classList.contains('modal')) {
        event.target.classList.remove('active');
    }
}
