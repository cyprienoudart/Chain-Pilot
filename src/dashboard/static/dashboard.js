// ChainPilot Dashboard - Modern Black & White with Charts
const API_BASE = '/api/v1';
let activityChart = null;
let typeChart = null;
let refreshInterval = null;

// Initialize dashboard
document.addEventListener('DOMContentLoaded', () => {
    console.log('ChainPilot Dashboard initializing...');
    initializeNavigation();
    initializeCharts();
    loadDashboardData();
    startAutoRefresh();
});

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
                    data: [1, 0, 0],
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
}

// Load Dashboard Data
async function loadDashboardData() {
    try {
        // Load health status
        const health = await fetch('/health').then(r => r.json());
        updateNetworkStatus(health);
        
        // Load wallet list
        const walletList = await fetch(`${API_BASE}/wallet/list`).then(r => r.json());
        updateWalletSelector(walletList);
        
        // Load balance
        try {
            const balance = await fetch(`${API_BASE}/wallet/balance`).then(r => r.json());
            updateBalance(balance);
        } catch (e) {
            console.log('No wallet loaded');
        }
        
        // Load transactions
        const transactions = await fetch(`${API_BASE}/audit/transactions?limit=100`).then(r => r.json());
        updateTransactionStats(transactions);
        updateRecentActivity(transactions);
        updateCharts(transactions);
        
        // Load rules
        const rules = await fetch(`${API_BASE}/rules`).then(r => r.json());
        updateRulesCount(rules);
        
    } catch (error) {
        console.error('Error loading dashboard data:', error);
    }
}

// Update Network Status
function updateNetworkStatus(health) {
    const networkName = document.getElementById('networkName');
    const networkValue = document.getElementById('networkValue');
    const chainId = document.getElementById('chainId');
    
    if (health.network && typeof health.network === 'object') {
        networkName.textContent = health.network.name || 'Unknown';
        networkValue.textContent = health.network.name || 'Unknown';
        chainId.textContent = `Chain ID: ${health.network.chain_id || 'N/A'}`;
    } else {
        networkName.textContent = health.network || 'Unknown';
        networkValue.textContent = health.network || 'Unknown';
        chainId.textContent = `Chain ID: ${health.chain_id || 'N/A'}`;
    }
}

// Update Wallet Selector
function updateWalletSelector(walletList) {
    const dropdown = document.getElementById('walletDropdown');
    dropdown.innerHTML = '<option value="">No Wallet</option>';
    
    const wallets = walletList.wallets || walletList || [];
    wallets.forEach(wallet => {
        const option = document.createElement('option');
        option.value = wallet.name || wallet;
        option.textContent = wallet.name || wallet;
        dropdown.appendChild(option);
    });
    
    dropdown.addEventListener('change', async (e) => {
        if (e.target.value) {
            await fetch(`${API_BASE}/wallet/load`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ wallet_name: e.target.value })
            });
            loadDashboardData();
        }
    });
}

// Update Balance
function updateBalance(balance) {
    const balanceValue = document.getElementById('balanceValue');
    if (balance && balance.balance_ether !== undefined) {
        balanceValue.textContent = `${parseFloat(balance.balance_ether).toFixed(4)} ETH`;
    }
}

// Update Transaction Stats
function updateTransactionStats(transactions) {
    const txCountValue = document.getElementById('txCountValue');
    const txs = transactions.transactions || [];
    txCountValue.textContent = txs.length;
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
    
    activityList.innerHTML = txs.slice(0, 5).map(tx => `
        <div class="activity-item">
            <div class="left">
                <span class="icon">💸</span>
                <div>
                    <div><strong>${tx.to_address.substring(0, 10)}...</strong></div>
                    <div class="time">${new Date(tx.timestamp).toLocaleString()}</div>
                </div>
            </div>
            <div class="right">
                <div><strong>${parseFloat(tx.value_ether || 0).toFixed(4)} ETH</strong></div>
                <div class="status-${tx.status.toLowerCase()}">${tx.status}</div>
            </div>
        </div>
    `).join('');
}

// Update Charts
function updateCharts(transactions) {
    const txs = transactions.transactions || [];
    
    // Update activity chart (last 7 days)
    const last7Days = Array(7).fill(0);
    const today = new Date();
    
    txs.forEach(tx => {
        const txDate = new Date(tx.timestamp);
        const daysDiff = Math.floor((today - txDate) / (1000 * 60 * 60 * 24));
        if (daysDiff >= 0 && daysDiff < 7) {
            last7Days[6 - daysDiff]++;
        }
    });
    
    if (activityChart) {
        activityChart.data.datasets[0].data = last7Days;
        activityChart.update();
    }
    
    // Update type chart
    const nativeCount = txs.filter(tx => !tx.token_address).length;
    const tokenCount = txs.filter(tx => tx.token_address).length;
    
    if (typeChart) {
        typeChart.data.datasets[0].data = [nativeCount || 1, tokenCount, 0];
        typeChart.update();
    }
}

// Load Transactions
async function loadTransactions() {
    try {
        const transactions = await fetch(`${API_BASE}/audit/transactions?limit=50`).then(r => r.json());
        const tbody = document.getElementById('transactionsTableBody');
        const txs = transactions.transactions || [];
        
        if (txs.length === 0) {
            tbody.innerHTML = '<tr><td colspan="6" class="empty-message">No transactions</td></tr>';
            return;
        }
        
        tbody.innerHTML = txs.map(tx => `
            <tr>
                <td>${new Date(tx.timestamp).toLocaleString()}</td>
                <td title="${tx.tx_hash}">${tx.tx_hash.substring(0, 10)}...</td>
                <td title="${tx.from_address}">${tx.from_address.substring(0, 10)}...</td>
                <td title="${tx.to_address}">${tx.to_address.substring(0, 10)}...</td>
                <td>${parseFloat(tx.value_ether || 0).toFixed(4)} ETH</td>
                <td class="status-${tx.status.toLowerCase()}">${tx.status}</td>
            </tr>
        `).join('');
    } catch (error) {
        console.error('Error loading transactions:', error);
    }
}

// Load Rules
async function loadRules() {
    try {
        const rules = await fetch(`${API_BASE}/rules`).then(r => r.json());
        const grid = document.getElementById('rulesGrid');
        const rulesList = rules.rules || [];
        
        if (rulesList.length === 0) {
            grid.innerHTML = '<div class="empty-message">No rules configured</div>';
            return;
        }
        
        grid.innerHTML = rulesList.map(rule => `
            <div class="rule-card">
                <h4>${rule.name}</h4>
                <div class="rule-type">${rule.rule_type.replace('_', ' ').toUpperCase()}</div>
                <div class="rule-status">${rule.enabled ? 'Active' : 'Inactive'}</div>
            </div>
        `).join('');
    } catch (error) {
        console.error('Error loading rules:', error);
    }
}

// Chat Functions
async function sendChat() {
    const input = document.getElementById('chatInput');
    const messages = document.getElementById('chatMessages');
    const text = input.value.trim();
    
    if (!text) return;
    
    // Add user message
    messages.innerHTML += `
        <div class="message user">
            <div class="message-content">
                <div class="message-text">
                    <p>${text}</p>
                </div>
            </div>
        </div>
    `;
    
    input.value = '';
    messages.scrollTop = messages.scrollHeight;
    
    try {
        // Send to AI
        const response = await fetch(`${API_BASE}/ai/parse`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ text, execute: true })
        });
        
        const result = await response.json();
        
        // Add bot response
        messages.innerHTML += `
            <div class="message bot">
                <div class="message-content">
                    <div class="message-text">
                        <strong>ChainPilot AI</strong>
                        <p><strong>Intent:</strong> ${result.intent}</p>
                        <p><strong>Confidence:</strong> ${(result.confidence * 100).toFixed(0)}%</p>
                        ${result.execution_result ? `<p><strong>Result:</strong> ${JSON.stringify(result.execution_result)}</p>` : ''}
                    </div>
                </div>
            </div>
        `;
        
        messages.scrollTop = messages.scrollHeight;
        
        // Refresh data if transaction was executed
        if (result.execution_result) {
            setTimeout(() => loadDashboardData(), 1000);
        }
    } catch (error) {
        console.error('Chat error:', error);
        messages.innerHTML += `
            <div class="message bot">
                <div class="message-content">
                    <div class="message-text">
                        <strong>Error</strong>
                        <p>${error.message}</p>
                    </div>
                </div>
            </div>
        `;
    }
}

function handleChatKeyPress(event) {
    if (event.key === 'Enter') {
        sendChat();
    }
}

function clearChat() {
    const messages = document.getElementById('chatMessages');
    messages.innerHTML = `
        <div class="message bot">
            <div class="message-content">
                <div class="message-text">
                    <strong>ChainPilot AI</strong>
                    <p>Try: "Send 0.01 ETH to 0x742d..." or "What's my balance?"</p>
                </div>
            </div>
        </div>
    `;
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
    }, 10000); // Refresh every 10 seconds
}

// Close modals when clicking outside
window.onclick = function(event) {
    if (event.target.classList.contains('modal')) {
        event.target.classList.remove('active');
    }
}
