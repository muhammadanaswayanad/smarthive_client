/** @odoo-module **/

import { Component, onWillStart, onMounted } from "@odoo/owl";
import { registry } from "@web/core/registry";
import { useService } from "@web/core/utils/hooks";

class SmartHiveCrmWarningService {
    setup() {
        this.orm = useService("orm");
        this.action = useService("action");
        this.notification = useService("notification");
    }

    async checkAndShowWarnings() {
        try {
            // Check for SmartHive warnings when CRM views are loaded
            const result = await this.orm.call(
                'smarthive.client.config',
                'get_active_config',
                []
            );

            if (!result) return;

            // Get warning data
            const warningData = await this.orm.call(
                'smarthive.client.config',
                'get_warning_data',
                [result.id]
            );

            if (warningData) {
                if (warningData.block_reason) {
                    // Show block wizard
                    await this.action.doAction({
                        type: 'ir.actions.act_window',
                        name: 'System Access Restricted',
                        res_model: 'smarthive.block.wizard',
                        view_mode: 'form',
                        target: 'new',
                        context: {
                            default_block_reason: warningData.block_reason,
                            default_local_admin_mode: warningData.local_admin_mode || false,
                        },
                    });
                } else if (warningData.show_warning) {
                    // Check if user has already seen this warning today
                    const lastWarningKey = `smarthive_warning_${result.id}_${new Date().toDateString()}`;
                    if (!localStorage.getItem(lastWarningKey)) {
                        // Show warning wizard
                        await this.action.doAction({
                            type: 'ir.actions.act_window',
                            name: 'System Notice',
                            res_model: 'smarthive.crm.warning.wizard',
                            view_mode: 'form',
                            target: 'new',
                            context: {
                                default_warning_message: warningData.message,
                                default_payment_status: warningData.payment_status || 'paid',
                                default_outstanding_amount: warningData.outstanding_amount || 0,
                                default_local_admin_mode: warningData.local_admin_mode || false,
                            },
                        });

                        // Mark as seen for today
                        localStorage.setItem(lastWarningKey, 'seen');
                    }
                }
            }
        } catch (error) {
            console.error("SmartHive CRM warning check failed:", error);
        }
    }

    async showWarningBanner(warningData) {
        // Show a dismissible banner at the top
        const bannerHtml = `
            <div class="alert alert-warning alert-dismissible d-flex align-items-center" role="alert" style="margin: 0; border-radius: 0;">
                <i class="fa fa-exclamation-triangle me-2"></i>
                <div class="flex-grow-1">
                    <strong>System Notice:</strong> ${warningData.message || 'Please check your account status.'}
                    ${warningData.outstanding_amount ? `<br/><strong>Outstanding Amount: ${warningData.outstanding_amount}</strong>` : ''}
                </div>
                <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button>
            </div>
        `;

        // Insert banner at top of page
        const existingBanner = document.querySelector('.smarthive-warning-banner');
        if (existingBanner) {
            existingBanner.remove();
        }

        const banner = document.createElement('div');
        banner.className = 'smarthive-warning-banner';
        banner.innerHTML = bannerHtml;

        const navbar = document.querySelector('.o_main_navbar');
        if (navbar) {
            navbar.parentNode.insertBefore(banner, navbar.nextSibling);
        } else {
            document.body.insertBefore(banner, document.body.firstChild);
        }
    }
}

// Register the service
registry.category("services").add("smartHiveCrmWarning", {
    dependencies: ["orm", "action", "notification"],
    start(env, { orm, action, notification }) {
        const service = new SmartHiveCrmWarningService();
        service.orm = orm;
        service.action = action;
        service.notification = notification;
        return service;
    },
});

// Hook into CRM lead list view to show warnings
const originalCrmLeadListView = registry.category("views").get("list");

class SmartHiveCrmLeadListView extends originalCrmLeadListView.Controller {
    setup() {
        super.setup();
        this.smartHiveWarning = useService("smartHiveCrmWarning");

        onMounted(async () => {
            // Only show warnings on CRM lead views
            if (this.props.resModel === 'crm.lead') {
                await this.smartHiveWarning.checkAndShowWarnings();
            }
        });
    }
}

// Register the enhanced CRM view
registry.category("views").add("smarthive_crm_list", {
    ...originalCrmLeadListView,
    Controller: SmartHiveCrmLeadListView,
});

export { SmartHiveCrmWarningService };