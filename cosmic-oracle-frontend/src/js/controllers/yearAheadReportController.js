// D:\my_projects\cosmic-oracle\cosmic-oracle-frontend\public\js\yearAheadReportController.js

import { apiService } from './apiService.js';
import { showLoading, hideLoading, displayError, displaySuccess } from './uiUpdate.js';

const yearAheadReportController = {
    container: null,
    generateBtn: null,
    statusContainer: null,
    reportsListContainer: null, // To list generated reports

    initialize(containerId = 'year-ahead-report-content') {
        this.container = document.getElementById(containerId);
        if (!this.container) {
            console.warn('Year Ahead Report container not found.');
            return;
        }
        this.renderBaseUI();
        this.addEventListeners();
        this.loadUserReports(); // Load previously generated reports
    },

    renderBaseUI() {
        this.container.innerHTML = `
            <h3>Year Ahead Astrological Report (Premium)</h3>
            <p>Gain deep insights into your upcoming year with a personalized astrological report covering major transits and progressions.</p>
            <div class="report-controls">
                <label for="report-start-date">Report Start Date (optional, defaults to today):</label>
                <input type="date" id="report-start-date" name="report-start-date">
                <button id="generate-year-ahead-report-btn" class="btn btn-premium">Generate New Report</button>
            </div>
            <div id="year-ahead-report-status" class="report-status"></div>
            <h4>Your Generated Reports:</h4>
            <div id="year-ahead-reports-list" class="reports-list">
                <p>Loading your reports...</p>
            </div>
        `;
        this.generateBtn = document.getElementById('generate-year-ahead-report-btn');
        this.statusContainer = document.getElementById('year-ahead-report-status');
        this.reportsListContainer = document.getElementById('year-ahead-reports-list');
        document.getElementById('report-start-date').value = new Date().toISOString().split('T')[0];
    },

    addEventListeners() {
        this.generateBtn?.addEventListener('click', () => this.handleGenerateReport());
        // Event delegation for download buttons if reports are loaded dynamically
        this.reportsListContainer?.addEventListener('click', async (event) => {
            if (event.target.classList.contains('download-report-btn')) {
                const reportId = event.target.dataset.reportId;
                if (reportId) {
                    await this.downloadReport(reportId, event.target);
                }
            } else if (event.target.classList.contains('refresh-report-status-btn')) {
                const reportId = event.target.dataset.reportId;
                if (reportId) {
                    await this.refreshReportStatus(reportId);
                }
            }
        });
    },

    async loadUserReports() {
        // This endpoint doesn't exist yet, you'll need to create one:
        // GET /api/v1/forecasting/reports/year-ahead (lists reports for the current user)
        // For now, we'll simulate or leave it empty.
        // Example:
        // try {
        //     showLoading(this.reportsListContainer);
        //     const response = await apiService.listYearAheadReports(); // You'll need to create this API call
        //     this.renderReportsList(response.data.reports);
        // } catch (error) {
        //     displayError('Could not load your reports.', this.reportsListContainer);
        // } finally {
        //     hideLoading(this.reportsListContainer);
        // }
        this.reportsListContainer.innerHTML = "<p>Functionality to list existing reports will be added. Please generate a new report.</p>";
    },

    renderReportsList(reports) {
        if (!reports || reports.length === 0) {
            this.reportsListContainer.innerHTML = "<p>You haven't generated any Year Ahead reports yet.</p>";
            return;
        }
        this.reportsListContainer.innerHTML = reports.map(report => `
            <div class="report-list-item" id="report-item-${report.id}">
                <p><strong>Report ID:</strong> ${report.id.substring(0,8)}...</p>
                <p><strong>Generated:</strong> ${new Date(report.generated_at).toLocaleString()}</p>
                <p><strong>Period:</strong> ${report.start_date_covered} to ${report.end_date_covered}</p>
                <p><strong>Status:</strong> <span class="status-${report.status.toLowerCase()}">${report.status}</span></p>
                ${report.status === 'completed' ?
                    `<button class="btn download-report-btn" data-report-id="${report.id}">Download PDF</button>` : ''}
                ${report.status === 'pending' || report.status === 'processing' ?
                    `<button class="btn refresh-report-status-btn" data-report-id="${report.id}">Refresh Status</button>` : ''}
                ${report.status === 'failed' ? `<p class="error-msg">Error: ${report.error_message || 'Unknown error'}</p>` : ''}
            </div>
        `).join('');
    },

    async handleGenerateReport() {
        const targetStartDateInput = document.getElementById('report-start-date');
        const targetStartDate = targetStartDateInput ? targetStartDateInput.value : null;
        
        showLoading(this.statusContainer);
        displaySuccess('Initiating report generation...', this.statusContainer);

        try {
            const response = await apiService.generateYearAheadReport({ target_start_date: targetStartDate });
            if (response.status === 'success' && response.data) {
                displaySuccess(`Report generation started (ID: ${response.data.id.substring(0,8)}...). Status: ${response.data.status}`, this.statusContainer);
                // Add to list or refresh list
                this.loadUserReports(); // Reload to show the new pending report
                // Optionally poll for status or ask user to refresh
                this.pollReportStatus(response.data.id);
            } else {
                displayError(response.message || 'Could not start report generation.', this.statusContainer);
            }
        } catch (error) {
            console.error("Error generating report:", error);
            const errorMsg = error.responseJSON?.message || error.message || 'An unknown error occurred.';
            if (error.status === 403) { // Example for premium check
                displayError('This is a premium feature. Please subscribe to generate reports.', this.statusContainer);
            } else {
                displayError(`Failed to generate report: ${errorMsg}`, this.statusContainer);
            }
        } finally {
            // hideLoading for statusContainer might be too quick if polling starts
        }
    },

    async pollReportStatus(reportId, attempts = 5, delay = 5000) {
        if (attempts <= 0) {
            displayError(`Stopped checking status for report ${reportId.substring(0,8)}. Please refresh manually.`, this.statusContainer);
            hideLoading(this.statusContainer); // For main status
            // Update specific item status
            const reportItemDiv = document.getElementById(`report-item-${reportId}`);
            if (reportItemDiv) {
                const statusSpan = reportItemDiv.querySelector(`span[class^="status-"]`);
                 if (statusSpan) {
                    statusSpan.className = `status-timed_out_polling`;
                    statusSpan.textContent = "timed_out_polling";
                }
            }
            return;
        }

        try {
            const response = await apiService.getYearAheadReportStatus(reportId);
            const report = response.data;
            
            // Update the general status container
            displaySuccess(`Report ${reportId.substring(0,8)} status: ${report.status}`, this.statusContainer);

            // Update the specific report item in the list
            const reportItemDiv = document.getElementById(`report-item-${report.id}`);
            if (reportItemDiv) {
                // More robustly update status class and text
                const statusSpan = reportItemDiv.querySelector(`span[class^="status-"]`); // Find any span starting with "status-"
                if (statusSpan) {
                    statusSpan.className = `status-${report.status.toLowerCase()}`; // Set the new class
                    statusSpan.textContent = report.status;
                }


                if (report.status === 'completed' && !reportItemDiv.querySelector('.download-report-btn')) {
                    const downloadBtn = document.createElement('button');
                    downloadBtn.className = 'btn download-report-btn';
                    downloadBtn.dataset.reportId = report.id;
                    downloadBtn.textContent = 'Download PDF';
                    // Append after status paragraph or in a specific actions div if you have one
                    const statusP = reportItemDiv.querySelector(`p strong:contains('Status:')`)?.parentElement;
                    if (statusP) {
                        statusP.insertAdjacentElement('afterend', downloadBtn);
                    } else {
                        reportItemDiv.appendChild(downloadBtn);
                    }
                }
                
                const refreshBtn = reportItemDiv.querySelector('.refresh-report-status-btn');
                if(refreshBtn) {
                    refreshBtn.style.display = (report.status === 'pending' || report.status === 'processing') ? 'inline-block' : 'none';
                }

            } else { // If item not yet in list, refresh list
                this.loadUserReports();
            }


            if (report.status === 'completed' || report.status === 'failed') {
                hideLoading(this.statusContainer); // For main status
                if (report.status === 'failed') {
                    displayError(`Report generation failed: ${report.error_message || 'Unknown error'}`, this.statusContainer);
                }
                this.loadUserReports(); // Refresh the list to reflect final status
            } else { // Still pending or processing
                setTimeout(() => this.pollReportStatus(reportId, attempts - 1, delay), delay);
            }
        } catch (error) {
            console.error(`Error polling status for report ${reportId}:`, error);
            // Don't stop polling immediately on a network error, try a few more times
            setTimeout(() => this.pollReportStatus(reportId, attempts - 1, delay), delay);
        }
    },
    
    async refreshReportStatus(reportId) {
        const reportItemDiv = document.getElementById(`report-item-${reportId}`);
        if (reportItemDiv) {
            const statusSpan = reportItemDiv.querySelector(`span[class^="status-"]`);
            if (statusSpan) statusSpan.textContent = 'checking...';
        }
        // This will re-initiate polling or just fetch once:
        await this.pollReportStatus(reportId, 1, 100); // Check once quickly
    },

    async downloadReport(reportId, buttonElement) {
        if (buttonElement) buttonElement.textContent = 'Preparing...';
        if (buttonElement) buttonElement.disabled = true;

        try {
            // This directly triggers a download via the apiService making a GET request
            // that results in a file. The browser handles the download.
            await apiService.downloadYearAheadReport(reportId); 
            // No specific success message here as browser handles it,
            // but you could re-enable the button after a short delay.
            setTimeout(() => {
                if (buttonElement) buttonElement.textContent = 'Download PDF';
                if (buttonElement) buttonElement.disabled = false;
            }, 3000);
        } catch (error) {
            console.error("Error downloading report:", error);
            const errorMsg = error.responseJSON?.message || error.message || 'Could not download report.';
            if (buttonElement) buttonElement.textContent = 'Download PDF'; // Reset button text
            if (buttonElement) buttonElement.disabled = false;
            displayError(`Download failed: ${errorMsg}`, this.statusContainer); // Show error near generate button or on item
        }
    }
};
window.yearAheadReportController = yearAheadReportController;