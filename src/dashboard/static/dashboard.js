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
    initializeWalletSelector();
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
        
        // Load wallet list - use enhanced loading for selector
        await loadWalletsEnhanced();
        
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
    
    // Update type chart - REAL DATA ONLY
    const nativeCount = txs.filter(tx => !tx.token_address).length;
    const tokenCount = txs.filter(tx => tx.token_address).length;
    
    if (typeChart) {
        // Show actual counts, no fake data
        typeChart.data.datasets[0].data = [nativeCount, tokenCount, 0];
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
        const container = document.getElementById('rulesList');
        const rulesList = rules.rules || [];
        
        if (rulesList.length === 0) {
            container.innerHTML = '<div class="empty-state">No rules configured</div>';
            return;
        }
        
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
        try {
            const balanceResponse = await fetch(`${API_BASE}/wallet/balance`);
            if (balanceResponse.ok) {
                const balanceData = await balanceResponse.json();
                currentWalletAddress = balanceData.address;
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
                            <span class="value">${balance} ETH</span>
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
        showNotification('Failed to load wallets', 'error');
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
        
        showNotification(`Switched to wallet: ${walletName}`, 'success');
        await loadWalletsEnhanced();
        await loadDashboardData();
    } catch (error) {
        console.error('Error switching wallet:', error);
        showNotification('Failed to switch wallet', 'error');
    }
}

// Notification System
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
