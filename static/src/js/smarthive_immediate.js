// Simple immediate SmartHive warning system
(function () {
    'use strict';

    console.log('SmartHive Immediate Warning System starting...');

    // Function to make the warning request
    function checkWarnings() {
        console.log('Making warning request...');

        fetch('/smarthive_client/warning_data', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-Requested-With': 'XMLHttpRequest',
            },
            credentials: 'include',
            body: JSON.stringify({})
        })
            .then(response => {
                console.log('Response received:', response.status);
                if (!response.ok) {
                    throw new Error(`HTTP ${response.status}`);
                }
                return response.json();
            })
            .then(data => {
                console.log('Warning data:', data);
                handleWarningData(data);
            })
            .catch(error => {
                console.error('Warning check failed:', error);
            });
    }

    function handleWarningData(data) {
        console.log('Processing warning data:', JSON.stringify(data));

        // Remove any existing warnings first
        removeExistingWarnings();

        // Force show warnings for testing (remove this line in production)
        if (data && (data.show_warning || data.block_reason || data.message || data.outstanding_amount)) {
            console.log('Detected warning conditions - forcing display');

            // Create test data if needed
            const testData = {
                show_warning: true,
                message: data.message || data.warning_message || 'Payment overdue - please contact administrator',
                outstanding_amount: data.outstanding_amount || '30,000.00',
                payment_status: data.payment_status || 'overdue',
                block_reason: data.block_reason
            };

            if (testData.block_reason) {
                console.log('Creating block screen...');
                createBlockScreen(testData);
            } else {
                console.log('Creating warning banner...');
                createWarningBanner(testData);
            }
        } else {
            console.log('No warning conditions detected');
        }
    }

    function removeExistingWarnings() {
        const banner = document.querySelector('.smarthive-immediate-banner');
        const block = document.querySelector('.smarthive-immediate-block');

        if (banner) banner.remove();
        if (block) block.remove();
    }

    function createWarningBanner(data) {
        const banner = document.createElement('div');
        banner.className = 'smarthive-immediate-banner';
        banner.style.cssText = `
            position: fixed;
            top: 0;
            left: 0;
            right: 0;
            z-index: 10000;
            background: linear-gradient(135deg, #fcf8e3 0%, #f9f2d7 100%);
            border-bottom: 3px solid #f0ad4e;
            padding: 15px;
            box-shadow: 0 2px 8px rgba(0,0,0,0.1);
            display: flex;
            align-items: center;
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
        `;

        banner.innerHTML = `
            <div style="color: #856404; margin-right: 15px; font-size: 1.2em;">⚠️</div>
            <div style="flex-grow: 1; color: #856404;">
                <strong>System Notice:</strong> ${data.message || 'Please check your account status.'}
                ${data.outstanding_amount ? `<br/><strong>Outstanding Amount: ${data.outstanding_amount}</strong>` : ''}
            </div>
            <button onclick="this.parentElement.remove()" style="
                background: none;
                border: none;
                color: #856404;
                font-size: 1.5em;
                cursor: pointer;
                padding: 0;
                margin-left: 15px;
            ">×</button>
        `;

        document.body.insertBefore(banner, document.body.firstChild);
        console.log('Warning banner created and displayed');
    }

    function createBlockScreen(data) {
        const block = document.createElement('div');
        block.className = 'smarthive-immediate-block';
        block.style.cssText = `
            position: fixed;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            background: rgba(0, 0, 0, 0.9);
            z-index: 99999;
            display: flex;
            align-items: center;
            justify-content: center;
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
        `;

        block.innerHTML = `
            <div style="
                background: white;
                border-radius: 8px;
                max-width: 500px;
                margin: 20px;
                box-shadow: 0 10px 30px rgba(0,0,0,0.3);
            ">
                <div style="
                    background: linear-gradient(135deg, #d9534f 0%, #c9302c 100%);
                    color: white;
                    padding: 20px;
                    text-align: center;
                    border-radius: 8px 8px 0 0;
                ">
                    <h3 style="margin: 0; font-size: 1.5em;">
                        🔒 System Access Restricted
                    </h3>
                </div>
                <div style="padding: 30px; text-align: center; color: #333;">
                    <p style="font-size: 1.1em; margin-bottom: 15px;">
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

        document.body.appendChild(block);
        document.body.style.overflow = 'hidden';
        console.log('Block screen created and displayed');
    }

    // Initialize the system
    function init() {
        console.log('Initializing SmartHive warning system...');

        // Check immediately
        setTimeout(checkWarnings, 500);

        // Check periodically
        setInterval(checkWarnings, 60000);

        // Expose for testing
        window.SmartHiveTest = {
            check: checkWarnings,
            remove: removeExistingWarnings,
            forceWarning: function () {
                console.log('Forcing warning display for testing...');
                const testData = {
                    show_warning: true,
                    message: 'TESTING: Payment overdue - please contact administrator',
                    outstanding_amount: '30,000.00',
                    payment_status: 'overdue'
                };
                handleWarningData(testData);
            },
            forceBlock: function () {
                console.log('Forcing block screen for testing...');
                const testData = {
                    show_warning: true,
                    block_reason: 'TESTING: Access blocked by local administrator',
                    local_admin_mode: true
                };
                handleWarningData(testData);
            }
        };

        console.log('SmartHive warning system initialized');
    }

    // Start when page is ready
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', init);
    } else {
        init();
    }

})();