/** @odoo-module */

import { registry } from "@web/core/registry";
import { useState, onWillStart, useRef, onMounted } from '@odoo/owl';
import { useService } from "@web/core/utils/hooks";
import { _t } from "@web/core/l10n/translation";

const { Component } = owl;

class BadgeReturn extends Component {
    setup() {
        this.state = useState({
            selectedTag: null,
            selectedPersona: "",
            temp : false,
        })
        this.OnTagChange = this.OnTagChange.bind(this);
        this.dataService = useService("dataService");
        this.tagSelectRef = useRef("tagSelect");
        this.ca_persona = useState([]);
        this.tags = useState([]);

        onMounted(() => {
            const $select = $(this.tagSelectRef.el);
            $select.select2({
                placeholder: _t("Select a badge..."),
                allowClear: true,
                width: '100%',
            });
            $select.on("change.select2", this.OnTagChange.bind(this));

        });
        
        onWillStart(async () => {
            this.ca_persona = await this.dataService.loadPersona();
            this.tags = await this.dataService.loadReturnTags();
        });
    }
    
    get tagFiltered() { 
        let tagFilter = this.tags;
        if (this.state.temp) {
            tagFilter = this.tags.filter(tag => tag.temp === true);
        }
        return tagFilter;
    }

    OnTagChange(event) {
        const tagId = parseInt(event.target.value);
        const tag = this.tags.find(tag => tag.id === tagId);
        this.state.selectedPersona = tag?.ca_persona_id[1] || "";
        this.state.selectedTag = tag?.id || null;
    }

    OnTempChange(event) {
        this.state.temp = !this.state.temp;
    }
}

BadgeReturn.components = {};
BadgeReturn.template = 'controllo_accessi_portale.BadgeReturn';
registry.category("public_components").add("controllo_accessi_portale.BadgeReturn", BadgeReturn);