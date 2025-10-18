/** @odoo-module **/

import { Component, onWillStart, useState, onMounted } from "@odoo/owl";
import { registry } from "@web/core/registry";
import { useService } from "@web/core/utils/hooks";

class SmartHiveWarningBanner extends Component {
    setup() {
        this.orm = useService("orm");
        this.rpc = useService("rpc");

        this.state = useState({
            warningData: null,
            showBanner: false,
            showBlockScreen: false,
        });

        onWillStart(async () => {
            await this.loadWarningData();
        });

        onMounted(() => {
            // Check for warnings periodically
            this.warningInterval = setInterval(() => {
                this.loadWarningData();
            }, 60000); // Check every minute
        });
    }

    async loadWarningData() {
        try {
            const result = await this.rpc('/smarthive_client/warning_data');

            if (result.show_warning) {
                this.state.warningData = result;
                this.state.showBanner = true;

                // If client is blocked, show block screen
                if (result.block_reason) {
                    this.state.showBlockScreen = true;
                    this.showBlockScreen(result);
                }
            } else {
                this.state.showBanner = false;
                this.state.showBlockScreen = false;
            }
        } catch (error) {
            console.error("Failed to load SmartHive warning data:", error);
        }
    }

    showBlockScreen(data) {
        // Create and show block screen overlay
        if (document.querySelector('.smarthive_block_overlay')) {
            return; // Already showing
        }

        const overlay = document.createElement('div');
        overlay.className = 'smarthive_block_overlay';
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

        const card = document.createElement('div');
        card.style.cssText = `
            max-width: 500px;
            margin: 20px;
            background: white;
            border-radius: 8px;
            box-shadow: 0 10px 30px rgba(0,0,0,0.3);
        `;

        card.innerHTML = `
            <div style="background: linear-gradient(135deg, #d9534f 0%, #c9302c 100%); color: white; padding: 20px; text-align: center; border-radius: 8px 8px 0 0;">
                <h3 style="margin: 0; font-size: 1.5em;">
                    <i class="fa fa-lock" style="margin-right: 10px;"></i>
                    System Access Restricted
                </h3>
            </div>
            <div style="padding: 30px; text-align: center;">
                <p style="font-size: 1.1em; margin-bottom: 15px;">
                    ${data.block_reason || 'System access has been temporarily restricted.'}
                </p>
                <p>Please contact your system administrator for assistance.</p>
                <hr style="margin: 20px 0;"/>
                <p style="color: #666; font-size: 0.9em;">
                    If you believe this is an error, please contact support.
                </p>
            </div>
        `;

        overlay.appendChild(card);
        document.body.appendChild(overlay);

        // Prevent interaction with underlying page
        document.body.style.overflow = 'hidden';
    }

    dismissBanner() {
        this.state.showBanner = false;
    }

    getWarningClass() {
        if (!this.state.warningData) return 'alert-warning';

        switch (this.state.warningData.payment_status) {
            case 'overdue':
            case 'blocked':
                return 'alert-danger';
            case 'pending':
                return 'alert-warning';
            default:
                return 'alert-info';
        }
    }

    willUnmount() {
        if (this.warningInterval) {
            clearInterval(this.warningInterval);
        }

        // Clean up block screen if exists
        const overlay = document.querySelector('.smarthive_block_overlay');
        if (overlay) {
            overlay.remove();
            document.body.style.overflow = '';
        }
    }
}

SmartHiveWarningBanner.template = "smarthive_client.WarningBanner";

// Register as a service that can be used throughout the application
const smartHiveWarningService = {
    dependencies: ["rpc"],

    start(env, { rpc }) {
        let warningBanner = null;

        // Check for warnings on app start
        const checkWarnings = async () => {
            try {
                const result = await rpc('/smarthive_client/warning_data');

                if (result.show_warning && !warningBanner) {
                    // Create warning banner
                    warningBanner = new SmartHiveWarningBanner();
                    // Mount to appropriate container
                    const container = document.querySelector('.o_main_navbar') || document.body;
                    container.after(warningBanner.el);
                }
            } catch (error) {
                console.error("SmartHive warning check failed:", error);
            }
        };

        // Initial check
        checkWarnings();

        // Periodic checks
        setInterval(checkWarnings, 60000);

        return {
            checkWarnings,
        };
    },
};

registry.category("services").add("smartHiveWarning", smartHiveWarningService);

// Auto-initialize warning system
document.addEventListener('DOMContentLoaded', () => {
    const warningScript = document.createElement('script');
    warningScript.textContent = `
        (function() {
            function checkSmartHiveWarnings() {
                fetch('/smarthive_client/warning_data', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                        'X-Requested-With': 'XMLHttpRequest',
                    },
                    body: JSON.stringify({})
                })
                .then(response => response.json())
                .then(data => {
                    if (data.show_warning) {
                        showSmartHiveWarning(data);
                    }
                    if (data.block_reason) {
                        showSmartHiveBlockScreen(data);
                    }
                })
                .catch(error => console.error('SmartHive warning check failed:', error));
            }
            
            function showSmartHiveWarning(data) {
                let banner = document.querySelector('.smarthive_warning_banner');
                if (banner) return;
                
                banner = document.createElement('div');
                banner.className = 'smarthive_warning_banner alert alert-warning';
                banner.style.cssText = 'margin: 0; border-radius: 0; text-align: center; position: sticky; top: 0; z-index: 9999;';
                
                banner.innerHTML = \`
                    <div class="container">
                        <strong><i class="fa fa-exclamation-triangle"></i> System Notice:</strong>
                        \${data.message || 'Please check your account status.'}
                        \${data.outstanding_amount ? '<br/><strong>Outstanding Amount: ' + data.outstanding_amount + '</strong>' : ''}
                        <button type="button" class="close" style="float: right;" onclick="this.parentElement.parentElement.remove()">
                            <span aria-hidden="true">&times;</span>
                        </button>
                    </div>
                \`;
                
                document.body.insertBefore(banner, document.body.firstChild);
            }
            
            function showSmartHiveBlockScreen(data) {
                if (document.querySelector('.smarthive_block_overlay')) return;
                
                const overlay = document.createElement('div');
                overlay.className = 'smarthive_block_overlay';
                overlay.style.cssText = \`
                    position: fixed; top: 0; left: 0; width: 100%; height: 100%;
                    background-color: rgba(0, 0, 0, 0.9); z-index: 999999;
                    display: flex; align-items: center; justify-content: center;
                \`;
                
                overlay.innerHTML = \`
                    <div style="max-width: 500px; margin: 20px; background: white; border-radius: 8px; box-shadow: 0 10px 30px rgba(0,0,0,0.3);">
                        <div style="background: linear-gradient(135deg, #d9534f 0%, #c9302c 100%); color: white; padding: 20px; text-align: center; border-radius: 8px 8px 0 0;">
                            <h3 style="margin: 0; font-size: 1.5em;">
                                <i class="fa fa-lock" style="margin-right: 10px;"></i>
                                System Access Restricted
                            </h3>
                        </div>
                        <div style="padding: 30px; text-align: center;">
                            <p style="font-size: 1.1em; margin-bottom: 15px;">
                                \${data.block_reason || 'System access has been temporarily restricted.'}
                            </p>
                            <p>Please contact your system administrator for assistance.</p>
                        </div>
                    </div>
                \`;
                
                document.body.appendChild(overlay);
                document.body.style.overflow = 'hidden';
            }
            
            // Initial check
            checkSmartHiveWarnings();
            
            // Periodic checks
            setInterval(checkSmartHiveWarnings, 60000);
        })();
    `;

    document.head.appendChild(warningScript);
});