/** @odoo-module **/

// Simple global warning system that loads immediately
(function () {
    'use strict';

    console.log('SmartHive Global Warning System Loading...');

    // Function to check warnings
    async function checkSmartHiveWarnings() {
        try {
            console.log('Checking SmartHive warnings...');

            const response = await fetch('/smarthive_client/warning_data', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-Requested-With': 'XMLHttpRequest',
                },
                credentials: 'include',
                body: JSON.stringify({})
            });

            if (!response.ok) {
                console.log('Warning check response not OK:', response.status);
                return;
            }

            const data = await response.json();
            console.log('Warning data received:', data);

            // Remove existing banners first
            removeExistingWarnings();

            if (data.show_warning) {
                console.log('Showing warning banner');
                showWarningBanner(data);
            }

            if (data.block_reason) {
                console.log('Showing block screen');
                showBlockScreen(data);
            }
        } catch (error) {
            console.error('SmartHive warning check failed:', error);
        }
    }

    function removeExistingWarnings() {
        // Remove existing banners
        const existingBanner = document.querySelector('.smarthive-warning-banner');
        if (existingBanner) {
            existingBanner.remove();
        }

        // Remove existing block screen
        const existingBlock = document.querySelector('.smarthive-block-overlay');
        if (existingBlock) {
            existingBlock.remove();
            document.body.style.overflow = '';
        }
    }

    function showWarningBanner(data) {
        console.log('Creating warning banner with data:', data);

        const warningClass = getWarningClass(data.payment_status);

        const banner = document.createElement('div');
        banner.className = `smarthive-warning-banner alert ${warningClass} alert-dismissible`;
        banner.style.cssText = `
            margin: 0;
            border-radius: 0;
            position: sticky;
            top: 0;
            z-index: 9999;
            display: flex;
            align-items: center;
            padding: 15px;
            border: none;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        `;

        banner.innerHTML = `
            <i class="fa fa-exclamation-triangle" style="margin-right: 10px; font-size: 1.2em;"></i>
            <div style="flex-grow: 1;">
                <strong>System Notice:</strong> ${data.message || 'Please check your account status.'}
                ${data.outstanding_amount ? `<br/><strong>Outstanding Amount: ${data.outstanding_amount}</strong>` : ''}
            </div>
            <button type="button" class="btn-close" style="background: none; border: none; font-size: 1.5em; cursor: pointer; margin-left: 15px;" onclick="this.parentElement.remove()">×</button>
        `;

        // Insert at the top of the body
        document.body.insertBefore(banner, document.body.firstChild);

        console.log('Warning banner created and inserted');
    }

    function showBlockScreen(data) {
        console.log('Creating block screen with data:', data);

        const overlay = document.createElement('div');
        overlay.className = 'smarthive-block-overlay';
        overlay.style.cssText = `
            position: fixed;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            background-color: rgba(0, 0, 0, 0.9);
            z-index: 999999;
            display: flex;
            align-items: center;
            justify-content: center;
        `;

        overlay.innerHTML = `
            <div style="max-width: 500px; margin: 20px; background: white; border-radius: 8px; box-shadow: 0 10px 30px rgba(0,0,0,0.3);">
                <div style="background: linear-gradient(135deg, #d9534f 0%, #c9302c 100%); color: white; padding: 20px; text-align: center; border-radius: 8px 8px 0 0;">
                    <h3 style="margin: 0; font-size: 1.5em;">
                        <i class="fa fa-lock" style="margin-right: 10px;"></i>
                        System Access Restricted
                    </h3>
                </div>
                <div style="padding: 30px; text-align: center;">
                    <p style="font-size: 1.1em; margin-bottom: 15px; color: #333;">
                        ${data.block_reason || 'System access has been temporarily restricted.'}
                    </p>
                    <p style="color: #666;">Please contact your system administrator for assistance.</p>
                    <hr style="margin: 20px 0; border: 1px solid #eee;"/>
                    <p style="color: #999; font-size: 0.9em;">
                        If you believe this is an error, please contact support.
                    </p>
                </div>
            </div>
        `;

        document.body.appendChild(overlay);
        document.body.style.overflow = 'hidden';

        console.log('Block screen created and displayed');
    }

    function getWarningClass(paymentStatus) {
        switch (paymentStatus) {
            case 'overdue':
            case 'blocked':
                return 'alert-danger';
            case 'pending':
                return 'alert-warning';
            default:
                return 'alert-info';
        }
    }

    // Wait for page to load, then check warnings
    function initializeWarningSystem() {
        console.log('Initializing SmartHive warning system...');

        // Initial check
        setTimeout(checkSmartHiveWarnings, 1000);

        // Periodic checks every minute
        setInterval(checkSmartHiveWarnings, 60000);

        console.log('SmartHive warning system initialized');
    }

    // Multiple ways to ensure initialization
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', initializeWarningSystem);
    } else {
        initializeWarningSystem();
    }

    // Also try after a short delay to catch late-loading pages
    setTimeout(initializeWarningSystem, 2000);

    // Expose for manual testing
    window.SmartHiveWarnings = {
        check: checkSmartHiveWarnings,
        remove: removeExistingWarnings
    };

})();