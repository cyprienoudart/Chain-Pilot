// ChainPilot Dashboard JavaScript

const API_BASE = '/api/v1';

// State
let currentWallet = null;
let transactions = [];
let rules = [];
let wallets = [];

// Initialize Dashboard
document.addEventListener('DOMContentLoaded', () => {
    initializeNavigation();
    initializeModals();
    initializeEventListeners();
    loadDashboardData();
    
    // Refresh data every 10 seconds
    setInterval(loadDashboardData, 10000);
});

// Navigation
function initializeNavigation() {
    const navItems = document.querySelectorAll('.nav-item');
    navItems.forEach(item => {
        item.addEventListener('click', () => {
            const view = item.dataset.view;
            switchView(view);
            
            // Update active state
            navItems.forEach(n => n.classList.remove('active'));
            item.classList.add('active');
        });
    });
}

function switchView(viewName) {
    const views = document.querySelectorAll('.view');
    views.forEach(view => view.classList.remove('active'));
    
    const targetView = document.getElementById(`${viewName}-view`);
    if (targetView) {
        targetView.classList.add('active');
        
        // Load view-specific data
        switch(viewName) {
            case 'transactions':
                loadTransactions();
                break;
            case 'rules':
                loadRules();
                break;
            case 'wallets':
                loadWallets();
                break;
        }
    }
}

// Modals
function initializeModals() {
    // Close buttons
    const closeBtns = document.querySelectorAll('.close, .btn-secondary');
    closeBtns.forEach(btn => {
        btn.addEventListener('click', closeAllModals);
    });
    
    // Click outside to close
    window.addEventListener('click', (e) => {
        if (e.target.classList.contains('modal')) {
            closeAllModals();
        }
    });
}

function showModal(modalId) {
    const modal = document.getElementById(modalId);
    if (modal) {
        modal.classList.add('active');
    }
}

function closeAllModals() {
    const modals = document.querySelectorAll('.modal');
    modals.forEach(modal => modal.classList.remove('active'));
}

// Event Listeners
function initializeEventListeners() {
    // AI Chat
    document.getElementById('sendChatBtn').addEventListener('click', sendAIMessage);
    document.getElementById('chatInput').addEventListener('keypress', (e) => {
        if (e.key === 'Enter') sendAIMessage();
    });
    
    // New Transaction
    document.getElementById('newTransactionBtn').addEventListener('click', () => {
        showModal('newTransactionModal');
    });
    document.getElementById('newTransactionForm').addEventListener('submit', handleNewTransaction);
    
    // New Rule
    document.getElementById('newRuleBtn').addEventListener('click', () => {
        showModal('newRuleModal');
        updateRuleParams();
    });
    document.getElementById('ruleType').addEventListener('change', updateRuleParams);
    document.getElementById('newRuleForm').addEventListener('submit', handleNewRule);
    
    // Create Wallet
    document.getElementById('createWalletBtn').addEventListener('click', () => {
        showModal('createWalletModal');
    });
    document.getElementById('createWalletForm').addEventListener('submit', handleCreateWallet);
}

// Load Dashboard Data
async function loadDashboardData() {
    try {
        // Load network status
        const health = await fetch('/health').then(r => r.json());
        updateNetworkStatus(health);
        
        // Load wallets
        const walletsData = await fetch(`${API_BASE}/wallet/list`).then(r => r.json());
        wallets = walletsData.wallets || [];
        
        // Try to load current wallet balance if wallet is loaded
        try {
            const balance = await fetch(`${API_BASE}/wallet/balance`).then(r => r.json());
            currentWallet = balance;
            updateOverview();
        } catch (e) {
            // No wallet loaded yet
        }
        
        // Load recent transactions
        const txData = await fetch(`${API_BASE}/audit/transactions?limit=10`).then(r => r.json());
        transactions = txData.transactions || [];
        updateRecentTransactions();
        
        // Load rules
        const rulesData = await fetch(`${API_BASE}/rules`).then(r => r.json());
        rules = rulesData || [];
        updateOverview();
        
    } catch (error) {
        console.error('Error loading dashboard data:', error);
    }
}

function updateNetworkStatus(health) {
    const statusEl = document.getElementById('networkStatus');
    const nameEl = document.getElementById('networkName');
    
    if (health.web3_connected) {
        statusEl.style.color = '#10b981';
        nameEl.textContent = health.network || 'Connected';
        
        if (health.sandbox_mode) {
            nameEl.textContent += ' (Sandbox Mode)';
        }
    } else {
        statusEl.style.color = '#ef4444';
        nameEl.textContent = 'Disconnected';
    }
}

function updateOverview() {
    // Current Wallet
    if (currentWallet) {
        document.getElementById('currentWallet').textContent = 
            `${currentWallet.address.substring(0, 6)}...${currentWallet.address.substring(38)}`;
        document.getElementById('walletBalance').textContent = 
            `${parseFloat(currentWallet.balance_ether).toFixed(4)} ETH`;
    }
    
    // Total Transactions
    document.getElementById('totalTransactions').textContent = transactions.length;
    
    // Active Rules
    const activeRules = rules.filter(r => r.enabled).length;
    document.getElementById('activeRules').textContent = activeRules;
}

function updateRecentTransactions() {
    const container = document.getElementById('recentTransactions');
    
    if (transactions.length === 0) {
        container.innerHTML = '<div class="empty-state">No recent transactions</div>';
        return;
    }
    
    const recentTx = transactions.slice(0, 5);
    container.innerHTML = recentTx.map(tx => {
        const time = new Date(tx.timestamp).toLocaleString();
        const statusClass = tx.status.toLowerCase().replace('_', '-');
        
        return `
            <div class="activity-item">
                <div class="activity-info">
                    <div><strong>${tx.to_address.substring(0, 10)}...</strong></div>
                    <div class="activity-time">${time}</div>
                </div>
                <div>
                    <div><strong>${tx.value} ETH</strong></div>
                    <span class="activity-status ${statusClass}">${tx.status}</span>
                </div>
            </div>
        `;
    }).join('');
}

// AI Chat
async function sendAIMessage() {
    const input = document.getElementById('chatInput');
    const message = input.value.trim();
    
    if (!message) return;
    
    // Add user message to chat
    addChatMessage(message, 'user');
    input.value = '';
    
    try {
        // Send to AI API
        const response = await fetch(`${API_BASE}/ai/parse`, {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({
                text: message,
                execute: false // Get confirmation first
            })
        });
        
        const data = await response.json();
        
        // Display AI response
        let aiResponse = formatAIResponse(data);
        addChatMessage(aiResponse, 'bot');
        
        // If it's a valid intent with high confidence, offer to execute
        if (data.parsed && data.confidence > 0.7 && data.api_request) {
            addExecuteButton(data);
        }
        
    } catch (error) {
        addChatMessage('Sorry, I encountered an error processing your request.', 'bot');
        console.error('AI Chat error:', error);
    }
}

function addChatMessage(content, sender) {
    const messagesContainer = document.getElementById('chatMessages');
    const avatar = sender === 'bot' ? '🤖' : '👤';
    
    const messageDiv = document.createElement('div');
    messageDiv.className = `chat-message ${sender}`;
    messageDiv.innerHTML = `
        <div class="message-avatar">${avatar}</div>
        <div class="message-content">${content}</div>
    `;
    
    messagesContainer.appendChild(messageDiv);
    messagesContainer.scrollTop = messagesContainer.scrollHeight;
}

function formatAIResponse(data) {
    if (!data.parsed) {
        return "I'm not sure I understood that. Could you try rephrasing?";
    }
    
    const intent = data.intent;
    const entities = data.entities;
    const confidence = (data.confidence * 100).toFixed(0);
    
    let response = `I understood you want to <strong>${intent}</strong> (${confidence}% confident).<br><br>`;
    
    if (intent === 'send_transaction') {
        response += `Send <strong>${entities.amount} ${entities.currency}</strong> to <strong>${entities.to_address.substring(0, 10)}...</strong>`;
    } else if (intent === 'check_balance') {
        response += 'Check your wallet balance';
    } else if (intent === 'create_rule') {
        response += `Create a <strong>${entities.period}</strong> spending limit of <strong>${entities.amount} ${entities.currency}</strong>`;
    }
    
    return response;
}

function addExecuteButton(parsedData) {
    const messagesContainer = document.getElementById('chatMessages');
    
    const buttonDiv = document.createElement('div');
    buttonDiv.className = 'chat-message bot';
    buttonDiv.innerHTML = `
        <div class="message-avatar">🤖</div>
        <div class="message-content">
            <button class="btn btn-primary" onclick='executeAIAction(${JSON.stringify(parsedData)})'>
                Execute this action
            </button>
        </div>
    `;
    
    messagesContainer.appendChild(buttonDiv);
    messagesContainer.scrollTop = messagesContainer.scrollHeight;
}

async function executeAIAction(parsedData) {
    addChatMessage('Executing...', 'bot');
    
    try {
        const response = await fetch(`${API_BASE}/ai/execute`, {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({
                intent: parsedData.intent,
                entities: parsedData.entities
            })
        });
        
        if (response.ok) {
            const result = await response.json();
            addChatMessage('✅ Action executed successfully!', 'bot');
            
            // Reload data
            loadDashboardData();
        } else {
            const error = await response.json();
            addChatMessage(`❌ Error: ${error.detail.message || error.detail}`, 'bot');
        }
    } catch (error) {
        addChatMessage('❌ Failed to execute action', 'bot');
        console.error('Execute error:', error);
    }
}

// Transactions
async function loadTransactions() {
    try {
        const response = await fetch(`${API_BASE}/audit/transactions?limit=100`);
        const data = await response.json();
        transactions = data.transactions || [];
        
        displayTransactions(transactions);
    } catch (error) {
        console.error('Error loading transactions:', error);
    }
}

function displayTransactions(txs) {
    const tbody = document.getElementById('transactionsTableBody');
    
    if (txs.length === 0) {
        tbody.innerHTML = '<tr><td colspan="6" class="empty-state">No transactions found</td></tr>';
        return;
    }
    
    tbody.innerHTML = txs.map(tx => {
        const time = new Date(tx.timestamp).toLocaleString();
        const statusClass = tx.status.toLowerCase().replace('_', '-');
        
        return `
            <tr>
                <td>${time}</td>
                <td>${tx.from_address.substring(0, 10)}...</td>
                <td>${tx.to_address.substring(0, 10)}...</td>
                <td>${tx.value} ${tx.token_symbol || 'ETH'}</td>
                <td><span class="activity-status ${statusClass}">${tx.status}</span></td>
                <td>
                    <button class="btn btn-secondary" style="padding: 0.25rem 0.75rem; font-size: 0.875rem;" onclick="viewTransaction('${tx.tx_hash}')">
                        View
                    </button>
                </td>
            </tr>
        `;
    }).join('');
}

async function viewTransaction(txHash) {
    try {
        const response = await fetch(`${API_BASE}/transaction/${txHash}`);
        const data = await response.json();
        
        alert(`Transaction Status: ${data.status}\n\nTX Hash: ${txHash}\n\nReceipt: ${JSON.stringify(data.receipt, null, 2)}`);
    } catch (error) {
        alert('Error loading transaction details');
    }
}

async function handleNewTransaction(e) {
    e.preventDefault();
    
    const toAddress = document.getElementById('txToAddress').value;
    const amount = parseFloat(document.getElementById('txAmount').value);
    
    try {
        const response = await fetch(`${API_BASE}/transaction/send`, {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({
                to_address: toAddress,
                value: amount
            })
        });
        
        if (response.ok) {
            alert('✅ Transaction sent successfully!');
            closeAllModals();
            loadDashboardData();
        } else {
            const error = await response.json();
            alert(`❌ Error: ${error.detail.message || error.detail}`);
        }
    } catch (error) {
        alert('❌ Failed to send transaction');
        console.error(error);
    }
}

// Rules
async function loadRules() {
    try {
        const response = await fetch(`${API_BASE}/rules`);
        rules = await response.json();
        
        displayRules(rules);
    } catch (error) {
        console.error('Error loading rules:', error);
    }
}

function displayRules(rulesData) {
    const container = document.getElementById('rulesList');
    
    if (rulesData.length === 0) {
        container.innerHTML = '<div class="empty-state">No rules configured</div>';
        return;
    }
    
    container.innerHTML = rulesData.map(rule => {
        const params = typeof rule.parameters === 'string' ? JSON.parse(rule.parameters) : rule.parameters;
        const paramStr = JSON.stringify(params, null, 2);
        
        return `
            <div class="rule-card">
                <div class="rule-header">
                    <div class="rule-name">${rule.name}</div>
                    <span class="rule-toggle ${rule.enabled ? 'enabled' : 'disabled'}">
                        ${rule.enabled ? 'ENABLED' : 'DISABLED'}
                    </span>
                </div>
                <div class="rule-details">
                    <p><strong>Type:</strong> ${rule.rule_type}</p>
                    <p><strong>Action:</strong> ${rule.action}</p>
                    <p><strong>Risk Level:</strong> ${rule.risk_level}</p>
                    <p><strong>Parameters:</strong></p>
                    <pre style="background: rgba(0,0,0,0.2); padding: 0.5rem; border-radius: 0.25rem; font-size: 0.875rem;">${paramStr}</pre>
                </div>
            </div>
        `;
    }).join('');
}

function updateRuleParams() {
    const ruleType = document.getElementById('ruleType').value;
    const paramsGroup = document.getElementById('ruleParamsGroup');
    
    let html = '';
    
    if (ruleType === 'spending_limit') {
        html = `
            <label>Period:</label>
            <select id="rulePeriod" required>
                <option value="per_transaction">Per Transaction</option>
                <option value="daily">Daily</option>
                <option value="weekly">Weekly</option>
                <option value="monthly">Monthly</option>
            </select>
            <label style="margin-top: 1rem;">Amount (ETH):</label>
            <input type="number" id="ruleAmount" step="0.001" required placeholder="1.0" />
        `;
    } else if (ruleType === 'address_whitelist' || ruleType === 'address_blacklist') {
        html = `
            <label>Addresses (comma-separated):</label>
            <textarea id="ruleAddresses" rows="4" placeholder="0x..., 0x..." style="width: 100%; padding: 0.75rem; background: var(--bg-color); border: 1px solid var(--border-color); border-radius: 0.5rem; color: var(--text-primary);"></textarea>
        `;
    } else if (ruleType === 'time_restriction') {
        html = `
            <label>Allowed Hours (format: HH:MM-HH:MM):</label>
            <input type="text" id="ruleHours" placeholder="09:00-17:00" required />
        `;
    }
    
    paramsGroup.innerHTML = html;
}

async function handleNewRule(e) {
    e.preventDefault();
    
    const name = document.getElementById('ruleName').value;
    const ruleType = document.getElementById('ruleType').value;
    const action = document.getElementById('ruleAction').value;
    
    let parameters = {};
    
    if (ruleType === 'spending_limit') {
        parameters = {
            type: document.getElementById('rulePeriod').value,
            amount: parseFloat(document.getElementById('ruleAmount').value)
        };
    } else if (ruleType === 'address_whitelist' || ruleType === 'address_blacklist') {
        const addresses = document.getElementById('ruleAddresses').value
            .split(',')
            .map(a => a.trim())
            .filter(a => a);
        parameters = {addresses};
    } else if (ruleType === 'time_restriction') {
        parameters = {
            allowed_hours: document.getElementById('ruleHours').value,
            timezone: 'UTC'
        };
    }
    
    try {
        const response = await fetch(`${API_BASE}/rules/create`, {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({
                name,
                rule_type: ruleType,
                parameters,
                action,
                enabled: true
            })
        });
        
        if (response.ok) {
            alert('✅ Rule created successfully!');
            closeAllModals();
            loadRules();
        } else {
            const error = await response.json();
            alert(`❌ Error: ${error.detail}`);
        }
    } catch (error) {
        alert('❌ Failed to create rule');
        console.error(error);
    }
}

// Wallets
async function loadWallets() {
    try {
        const response = await fetch(`${API_BASE}/wallet/list`);
        const data = await response.json();
        wallets = data.wallets || [];
        
        displayWallets(wallets);
    } catch (error) {
        console.error('Error loading wallets:', error);
    }
}

function displayWallets(walletsData) {
    const container = document.getElementById('walletsList');
    
    if (walletsData.length === 0) {
        container.innerHTML = '<div class="empty-state">No wallets found</div>';
        return;
    }
    
    container.innerHTML = walletsData.map(wallet => {
        const isActive = currentWallet && currentWallet.address === wallet.address;
        
        return `
            <div class="wallet-card ${isActive ? 'active' : ''}" onclick="loadWallet('${wallet.name}')">
                <div>
                    <strong>${wallet.name}</strong>
                    ${isActive ? '<span class="rule-toggle enabled" style="margin-left: 1rem;">ACTIVE</span>' : ''}
                </div>
                <div class="wallet-address">${wallet.address}</div>
            </div>
        `;
    }).join('');
}

async function loadWallet(walletName) {
    try {
        const response = await fetch(`${API_BASE}/wallet/load`, {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({wallet_name: walletName})
        });
        
        if (response.ok) {
            alert(`✅ Wallet ${walletName} loaded!`);
            loadDashboardData();
        } else {
            alert('❌ Failed to load wallet');
        }
    } catch (error) {
        alert('❌ Error loading wallet');
        console.error(error);
    }
}

async function handleCreateWallet(e) {
    e.preventDefault();
    
    const walletName = document.getElementById('walletName').value;
    
    try {
        const response = await fetch(`${API_BASE}/wallet/create`, {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({wallet_name: walletName})
        });
        
        if (response.ok) {
            alert('✅ Wallet created successfully!');
            closeAllModals();
            loadWallets();
        } else {
            const error = await response.json();
            alert(`❌ Error: ${error.detail}`);
        }
    } catch (error) {
        alert('❌ Failed to create wallet');
        console.error(error);
    }
}

// Search Transactions
document.getElementById('searchTransactions')?.addEventListener('input', (e) => {
    const searchTerm = e.target.value.toLowerCase();
    const filteredTx = transactions.filter(tx => 
        tx.tx_hash.toLowerCase().includes(searchTerm) ||
        tx.from_address.toLowerCase().includes(searchTerm) ||
        tx.to_address.toLowerCase().includes(searchTerm) ||
        tx.status.toLowerCase().includes(searchTerm)
    );
    displayTransactions(filteredTx);
});

