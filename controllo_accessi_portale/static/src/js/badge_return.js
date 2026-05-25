/** @odoo-module */
import publicWidget from "@web/legacy/js/public/public_widget";
import { useState, onWillStart, onMounted, Component, mount } from '@odoo/owl';
import { SelectMenu } from "@web/core/select_menu/select_menu";
import { useService } from "@web/core/utils/hooks";
import { _t } from "@web/core/l10n/translation";
import { getTemplate } from "@web/core/templates";

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

        this.dataService = useService('dataService');
        this.tags = [];

        this.state = useState({
            selectedTag: null,
            selectedPersona: "",
            tag_code: "",
            temp: false,
        });

        onWillStart(async () => {
            this.tags = await this.dataService.loadReturnTags();
        });

        onMounted(() => {
            const staticLoader = document.getElementById('static_loader');
            if (staticLoader) staticLoader.remove();
        });
    }

    get tagFiltered() {
        if (this.state.temp) {
            return this.tags.filter(tag => tag.temp === true || tag.is_jolly === true);
        }
        return this.tags;
    }

    get tagChoices() {
        return this.tagFiltered.map(tag => ({ value: tag.id, label: tag.display_name }));
    }

    onTagSelect(value) {
        const tagId = value || null;
        this.state.selectedTag = tagId;
        const tag = this.tags.find(t => t.id === tagId);
        this.state.selectedPersona = tag?.ca_persona_id?.[1] || "";
    }

    OnTempChange(event) {
        this.state.temp = !this.state.temp;
        this.state.selectedTag = null;
        this.state.selectedPersona = "";
    }

    onKeyDownTagCode(event) {
        if (event.key === "Enter") {
            event.preventDefault();
            const val = event.target.value.trim();
            const tag = this.tags.find(tag => tag.tag_code === val);
            if (tag) {
                this.onTagSelect(tag.id);
                this.state.tag_code = "";
            } else {
                this.onTagSelect(null);
                alert(this.texts.badgeNotFound);
            }
            event.target.select();
            return false;
        }
    }
}

BadgeReturn.components = { SelectMenu };
BadgeReturn.template = 'controllo_accessi_portale.BadgeReturn';

publicWidget.registry.BadgeReturnWidget = publicWidget.Widget.extend({
    selector: '#badge_return_app',

    start: function () {
        return mount(BadgeReturn, this.el, {
            getTemplate: getTemplate,
            props: {},
            env: Component.env,
            dev: odoo.debug,
        });
    }
});

export default BadgeReturn;
