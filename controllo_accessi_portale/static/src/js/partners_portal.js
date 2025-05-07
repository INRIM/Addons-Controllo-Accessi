/** @odoo-module */

import {registry} from "@web/core/registry";
import {onWillStart, onWillUnmount, onMounted, useState, useRef} from '@odoo/owl';
import {useService} from "@web/core/utils/hooks";
import {Pager} from "@web/core/pager/pager";
import {_t} from "@web/core/l10n/translation";

const {Component} = owl;

class PartnersPortal extends Component {
    setup() {
        this.initLimit = 80;
        this.initOffset = 0;
        this.pollInterval = 10 * 1000; // 30 seconds
        // Setup polling timer reference
        this.pollingTimer = null;

        this.dataService = useService("dataService");
        this.paCategorySelectRef = useRef("paCategorySelect");
        this.state = useState({
            searchValue: "",
            filterCriteria: {
                internal: null,
                external: null,
                is_present: null,
                pa_category_id: null
            },
            offset: this.initOffset,
            limit: this.initLimit,
            total: 0,
            ca_persona_data: []
        });
        this.ca_punto_accesso_category = useState([])

        onWillStart(async () => {
            this.ca_punto_accesso_category = await this.dataService.loadPuntoAccessoCategory();
            await this.fetchData(this.state.limit, this.state.offset);
        });

        onMounted(() => {
            const $paCategorySelect = $(this.paCategorySelectRef.el);
            $paCategorySelect.select2({
                placeholder: _t("Select an Access Point..."),
                allowClear: true,
                width: '100%',
            });
            $paCategorySelect.on("change.select2", this.onCategoryChange.bind(this));
            this.setupPolling();
        })

        // Clean up on component unmount
        onWillUnmount(() => {
            this.clearPolling();
        });
    };

    async fetchData(limit, offset, query = null, filter = null) {
        const response = await this.dataService.loadAnagrafiche(limit, offset, query, filter);
        this.state.offset = offset;
        this.state.limit = limit;
        this.state.total = response.total;
        this.state.ca_persona_data = response.items;
        return response.items;
    }

    async onPageChange(event) {
        await this.fetchData(event.limit, event.offset, this.state.searchValue, this.state.filterCriteria);
    }

    async setFilterAll() {
        this.state.filterCriteria.internal = null;
        this.state.filterCriteria.external = null;
        await this.fetchData(this.initLimit, this.initOffset, this.state.searchValue, this.state.filterCriteria);
    }

    async setFilterInternal() {
        this.state.filterCriteria.external = null;
        this.state.filterCriteria.internal = true;
        await this.fetchData(this.initLimit, this.initOffset, this.state.searchValue, this.state.filterCriteria);
    }

    async setFilterExternal() {
        this.state.filterCriteria.internal = null;
        this.state.filterCriteria.external = true;
        await this.fetchData(this.initLimit, this.initOffset, this.state.searchValue, this.state.filterCriteria);
    }

    async setFilterIsPresent(evt) {
        const value = evt.target.checked;
        if (value === true) {
            this.state.filterCriteria.is_present = true;
        } else {
            this.state.filterCriteria.is_present = null;
        }
        await this.fetchData(this.initLimit, this.initOffset, this.state.searchValue, this.state.filterCriteria);
    }

    async updateSearch(event) {
        this.state.searchValue = event.target.value;
        await this.fetchData(this.initLimit, this.initOffset, this.state.searchValue, this.state.filterCriteria);
    }

    async onCategoryChange(event) {
        const selectedId = parseInt(event.target.value);
        this.state.filterCriteria.pa_category_id = selectedId;
        await this.fetchData(this.initLimit, this.initOffset, this.state.searchValue, this.state.filterCriteria);
    }

    animateProgressBar() {
        const progressBar = document.getElementById('progressbar');
        const duration = this.pollInterval; // 5 seconds
        const startTime = Date.now();

        function update() {
            const elapsed = Date.now() - startTime;
            const progress = 100 - ((elapsed % duration) / duration * 100);

            progressBar.style.width = progress + '%';

            requestAnimationFrame(update);
        }

        update();
    }

    setupPolling() {
        this.animateProgressBar();

        this.pollingTimer = setInterval(async () => {
            await this.fetchData(this.state.limit, this.state.offset, this.state.searchValue, this.state.filterCriteria);
        }, this.pollInterval);

    }

    clearPolling() {
        if (this.pollingTimer) {
            clearInterval(this.pollingTimer);
            this.pollingTimer = null;
        }
    }
}

PartnersPortal.components = {Pager};
PartnersPortal.template = 'controllo_accessi_portale.PartnersPortal';
registry.category("public_components").add("controllo_accessi_portale.PartnersPortal", PartnersPortal);
