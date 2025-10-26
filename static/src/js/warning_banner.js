/** @odoo-module **/

import { Component, onWillStart, useState, onMounted } from "@odoo/owl";
import { registry } from "@web/core/registry";
import { useService } from "@web/core/utils/hooks";

class SmartHiveWarningBanner extends Component {
    setup() {
        this.orm = useService("orm");
        this.rpc = useService("rpc");
        this.action = useService("action");

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

                // If client is blocked, show block modal immediately
                if (result.block_reason) {
                    this.state.showBlockScreen = true;
                    this.showBlockModal(result);
                } else {
                    // Show warning banner
                    this.showWarningBanner(result);
                }
            } else {
                this.state.showBanner = false;
                this.state.showBlockScreen = false;
                this.hideWarningBanner();
            }
        } catch (error) {
            console.error("Failed to load SmartHive warning data:", error);
        }
    }

    async showBlockModal(data) {
        // Show block modal using action service
        try {
            await this.action.doAction({
                type: 'ir.actions.act_window',
                name: 'System Access Restricted',
                res_model: 'smarthive.block.wizard',
                view_mode: 'form',
                target: 'new',
                context: {
                    default_block_reason: data.block_reason,
                    default_local_admin_mode: data.local_admin_mode || false,
                },
            });
        } catch (error) {
            console.error("Failed to show block modal:", error);
            // Fallback to simple alert
            alert(`System Access Restricted: ${data.block_reason}`);
        }
    }

    showWarningBanner(data) {
        // Remove existing banner first
        this.hideWarningBanner();

        const warningClass = this.getWarningClass(data.payment_status);
        const bannerHtml = `
            <div class="smarthive-warning-banner alert ${warningClass} alert-dismissible d-flex align-items-center" role="alert" style="margin: 0; border-radius: 0; position: sticky; top: 0; z-index: 9999;">
                <i class="fa fa-exclamation-triangle me-2"></i>
                <div class="flex-grow-1">
                    <strong>System Notice:</strong> ${data.message || 'Please check your account status.'}
                    ${data.outstanding_amount ? `<br/><strong>Outstanding Amount: ${data.outstanding_amount}</strong>` : ''}
                </div>
                <button type="button" class="btn-close" onclick="this.parentElement.remove()" aria-label="Close"></button>
            </div>
        `;

        // Insert banner at top of page
        const banner = document.createElement('div');
        banner.innerHTML = bannerHtml;

        const body = document.body;
        body.insertBefore(banner, body.firstChild);
    }

    hideWarningBanner() {
        const existingBanner = document.querySelector('.smarthive-warning-banner');
        if (existingBanner) {
            existingBanner.remove();
        }
    }

    getWarningClass(paymentStatus) {
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

    willUnmount() {
        if (this.warningInterval) {
            clearInterval(this.warningInterval);
        }
        this.hideWarningBanner();
    }
}

SmartHiveWarningBanner.template = "smarthive_client.WarningBanner";

// Register as a service that can be used throughout the application
const smartHiveWarningService = {
    dependencies: ["rpc", "action"],

    start(env, { rpc, action }) {
        let warningBanner = null;

        // Check for warnings on app start
        const checkWarnings = async () => {
            try {
                const result = await rpc('/smarthive_client/warning_data');

                if (result.show_warning) {
                    // Create warning banner instance if not exists
                    if (!warningBanner) {
                        warningBanner = new SmartHiveWarningBanner();
                        warningBanner.setup();
                    }

                    // Show appropriate warning
                    if (result.block_reason) {
                        // Show block modal
                        await action.doAction({
                            type: 'ir.actions.act_window',
                            name: 'System Access Restricted',
                            res_model: 'smarthive.block.wizard',
                            view_mode: 'form',
                            target: 'new',
                            context: {
                                default_block_reason: result.block_reason,
                                default_local_admin_mode: result.local_admin_mode || false,
                            },
                        });
                    } else {
                        // Show warning banner
                        showSimpleWarningBanner(result);
                    }
                }
            } catch (error) {
                console.error("SmartHive warning check failed:", error);
            }
        };

        // Simple banner function
        function showSimpleWarningBanner(data) {
            // Remove existing banner
            const existingBanner = document.querySelector('.smarthive-warning-banner');
            if (existingBanner) {
                existingBanner.remove();
            }

            const warningClass = getWarningClass(data.payment_status);
            const bannerHtml = `
                <div class="smarthive-warning-banner alert ${warningClass} alert-dismissible d-flex align-items-center" role="alert" style="margin: 0; border-radius: 0; position: sticky; top: 0; z-index: 9999;">
                    <i class="fa fa-exclamation-triangle me-2"></i>
                    <div class="flex-grow-1">
                        <strong>System Notice:</strong> ${data.message || 'Please check your account status.'}
                        ${data.outstanding_amount ? `<br/><strong>Outstanding Amount: ${data.outstanding_amount}</strong>` : ''}
                    </div>
                    <button type="button" class="btn-close" onclick="this.parentElement.remove()" aria-label="Close">×</button>
                </div>
            `;

            const banner = document.createElement('div');
            banner.innerHTML = bannerHtml;

            document.body.insertBefore(banner, document.body.firstChild);
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