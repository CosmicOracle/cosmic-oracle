// public/js/admin/dashboard.js
/**
 * Handles logic for the administrative monitoring dashboard.
 * Fetches data and renders it into charts and tables.
 */
import { api } from '../api/index.js';
import Chart from 'chart.js/auto'; // Uses Chart.js for visualization

// --- DOM Element Selectors for the Admin Page ---
const metricsContainer = document.getElementById('admin-metrics-container');
const alertsContainer = document.getElementById('admin-alerts-container');
const chartsContainer = document.getElementById('admin-charts-container');

let metricsChart = null; // To hold the chart instance

function renderMetrics(metrics) {
    const status = metrics.current_status;
    const performance = metrics.performance_metrics;
    
    metricsContainer.innerHTML = `
        <div class="metric-card">
            <h3>Active Subs</h3>
            <p>${status.active}</p>
        </div>
        <div class="metric-card">
            <h3>Trialing</h3>
            <p>${status.trialing}</p>
        </div>
        <div class="metric-card">
            <h3>Churn Rate (30d)</h3>
            <p>${performance.churn_rate_percent}%</p>
        </div>
        <div class="metric-card">
            <h3>New Subs (30d)</h3>
            <p>${performance.new_subscriptions}</p>
        </div>
    `;
}

function renderAlerts(alerts) {
    if (alerts.total_alerts === 0) {
        alertsContainer.innerHTML = '<div class="alert alert-success">System health is nominal. No active alerts.</div>';
        return;
    }

    let alertsHTML = alerts.alerts.map(alert => `
        <div class="alert alert-${alert.level}">
            <strong>${alert.type.replace('_', ' ').toUpperCase()}:</strong> ${alert.message}
        </div>
    `).join('');
    alertsContainer.innerHTML = alertsHTML;
}

function renderCharts(metrics) {
    const paymentData = metrics.payment_health;
    const perfData = metrics.performance_metrics;
    
    if (metricsChart) {
        metricsChart.destroy(); // Destroy old chart before creating a new one
    }

    const ctx = document.createElement('canvas');
    chartsContainer.innerHTML = '';
    chartsContainer.appendChild(ctx);

    metricsChart = new Chart(ctx, {
        type: 'bar',
        data: {
            labels: ['New Subs', 'Cancellations', 'Payment Failures'],
            datasets: [{
                label: 'Count (Last 30 Days)',
                data: [
                    perfData.new_subscriptions,
                    perfData.cancellations,
                    paymentData.total_failures
                ],
                backgroundColor: [
                    'rgba(75, 192, 192, 0.6)',
                    'rgba(255, 99, 132, 0.6)',
                    'rgba(255, 206, 86, 0.6)'
                ],
                borderColor: [
                    'rgba(75, 192, 192, 1)',
                    'rgba(255, 99, 132, 1)',
                    'rgba(255, 206, 86, 1)'
                ],
                borderWidth: 1
            }]
        },
        options: {
            scales: {
                y: {
                    beginAtZero: true
                }
            },
            responsive: true,
            maintainAspectRatio: false
        }
    });
}

async function fetchAndRenderDashboard() {
    try {
        const [metrics, alerts] = await Promise.all([
            api.getMonitoringMetrics(),
            api.getMonitoringAlerts()
        ]);
        
        renderMetrics(metrics);
        renderAlerts(alerts);
        renderCharts(metrics);

    } catch (error) {
        metricsContainer.innerHTML = `<div class="alert alert-danger">Failed to load dashboard data: ${error.message}</div>`;
    }
}

/**
 * Initializes the admin dashboard.
 */
export function initializeAdminDashboard() {
    if (metricsContainer && alertsContainer && chartsContainer) {
        console.log("Admin Dashboard Initializing...");
        fetchAndRenderDashboard();
        // Set up an interval to refresh the data every 5 minutes
        setInterval(fetchAndRenderDashboard, 300000); 
    }
}