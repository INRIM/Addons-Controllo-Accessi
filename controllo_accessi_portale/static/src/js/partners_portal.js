/** @odoo-module */

import { registry } from "@web/core/registry";
import { useState, onWillStart } from '@odoo/owl';
import { useService } from "@web/core/utils/hooks";
import { Pager } from "@web/core/pager/pager";
const { DateTime } = luxon;

const { Component } = owl;

class PartnersPortal extends Component {
    setup() { 
        this.state = useState({
            searchValue: "",
            filterCriteria: { is_external: null, is_internal: null },
            offset: 0,
            limit: 80,
        });
        this.dataService = useService("dataService");
        this.ca_persona_data = useState([]);

        onWillStart(async () => {
            const response = await this.dataService.loadAnagrafiche();
            this.ca_persona_data = response;
        });
    };  

    get filteredData() {
        const { searchValue, filterCriteria } = this.state;

        return this.ca_persona_data.filter((record) => {
            const name = record.display_name.toLowerCase();
            const matchesSearch = !searchValue || name.includes(searchValue);

            const matchesFilter =
                (filterCriteria.is_external === null || filterCriteria.is_external === record.is_external) &&
                (filterCriteria.is_internal === null || filterCriteria.is_internal === record.is_internal);

            return matchesSearch && matchesFilter;
        });
    }

    get caPersonaCount() {
        return this.filteredData.length;
    }

    onPageChange(event) {
        this.state.offset = event.offset;
        this.state.limit = event.limit;
    }

    get PagedData() {
        let filteredData = this.filteredData;
        return filteredData.slice(this.state.offset, this.state.offset+this.state.limit);
    }

    setFilterAll() {
        this.state.filterCriteria = { is_external: null, is_internal: null };
    }

    setFilterInternal() {
        this.state.filterCriteria = { is_external: false, is_internal: true };
    }

    setFilterExternal() {
        this.state.filterCriteria = { is_external: true, is_internal: false };
    }

    updateSearch(event) {
        this.state.searchValue = event.target.value.toLowerCase();
    }
}

PartnersPortal.components = {Pager};
PartnersPortal.template = 'controllo_accessi_portale.PartnersPortal';
registry.category("public_components").add("controllo_accessi_portale.PartnersPortal", PartnersPortal);
