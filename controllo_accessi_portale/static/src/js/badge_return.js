/** @odoo-module */
import publicWidget from "@web/legacy/js/public/public_widget";
import { useState, onWillStart, useRef, onMounted, Component, EventBus, mount } from '@odoo/owl';
import { _t } from "@web/core/l10n/translation";
import { templates } from "@web/core/assets";
import { jsonrpc } from "@web/core/network/rpc_service";
import { dataService as dataServiceFactory } from "./read_data_service";

class BadgeReturn extends Component {
    setup() {
        this.texts = {
            badgeReturn: _t("Badge Return"),
            partnerList: _t("Partner List"),
            returnDetails: _t("Return Details"),
            tagCode: _t("Tag Code"),
            enterCodeHere: _t("Enter code here..."),
            pressEnter: _t("Press enter after input to search automatically."),
            selectBadgeLabel: _t("Select Badge"),
            selectBadgePlaceholder: _t("Select a badge..."),
            temporaryOnly: _t("Temporary Only"),
            associatedPartner: _t("Associated Partner"),
            partnerDisplayedHere: _t("The partner will be displayed here..."),
            confirmReturn: _t("Confirm Return"),
            badgeNotFound: _t("Badge non trovato!")
        };

        this.state = useState({
            selectedTag: null,
            selectedPersona: "",
            tag_code: "",
            temp: false,
        });

        this.dataService = this.props.dataService;
        this.tagSelectRef = useRef("tagSelect");
        this.tags = [];

        onWillStart(async () => {
            this.tags = await this.dataService.loadReturnTags();
        });

        onMounted(() => {
            const staticLoader = document.getElementById('static_loader');
            if (staticLoader) {
                staticLoader.remove();
            }

            const $select = $(this.tagSelectRef.el);
            $select.select2({
                placeholder: this.texts.selectBadgePlaceholder,
                allowClear: true,
                width: '100%',
                matcher: function (term, text, opt) {
                    return text.toUpperCase().indexOf(term.toUpperCase()) >= 0
                        || opt.attr("alt").toUpperCase().indexOf(term.toUpperCase()) >= 0;
                }
            });
            $select.on("change.select2", this.OnTagChange.bind(this));
        });
    }

    get tagFiltered() {
        if (this.state.temp) {
            return this.tags.filter(tag => tag.temp === true);
        }
        return this.tags;
    }

    OnTagChange(event) {
        const tagId = parseInt(event.target.value);
        const tag = this.tags.find(tag => tag.id === tagId);
        if (tag && tag.ca_persona_id) {
             this.state.selectedPersona = tag.ca_persona_id[1];
        } else {
             this.state.selectedPersona = "";
        }
        this.state.selectedTag = tag?.id || null;
    }

    OnTempChange(event) {
        this.state.temp = !this.state.temp;
        $(this.tagSelectRef.el).val("").trigger("change");
    }

    onKeyDownTagCode(event) {
        if (event.key === "Enter") {
            event.preventDefault();

            const $select = $(this.tagSelectRef.el);
            const val = event.target.value.trim();
            const tag = this.tags.find(tag => tag.tag_code === val);

            if (tag) {
                $select.val(tag.id).trigger("change");
                this.state.tag_code = ""; 
            } else {
                $select.val("").trigger("change");
                alert(this.texts.badgeNotFound);
            }
            event.target.select();
            return false;
        }
    }
}

BadgeReturn.components = {};
BadgeReturn.template = 'controllo_accessi_portale.BadgeReturn';

publicWidget.registry.BadgeReturnWidget = publicWidget.Widget.extend({
    selector: '#badge_return_app',
    
    start: function () {
        const serviceInstance = dataServiceFactory.start(null, { rpc: jsonrpc });
        
        const env = {
            bus: new EventBus(),
            services: {
                ui: { isSmall: false, size: 2, bus: new EventBus() },
                localization: { direction: 'ltr' },
            }
        };

        return mount(BadgeReturn, this.el, {
            templates: templates,
            props: {
                dataService: serviceInstance
            },
            env: env,
            dev: odoo.debug,
        });
    }
});

export default BadgeReturn;