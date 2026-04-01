/** @odoo-module */
import publicWidget from "@web/legacy/js/public/public_widget";
import { onWillStart, onWillUnmount, onMounted, useState, useRef, mount, EventBus } from '@odoo/owl';
import { Pager } from "@web/core/pager/pager";
import { _t } from "@web/core/l10n/translation";
import { templates } from "@web/core/assets";
import { jsonrpc } from "@web/core/network/rpc_service"; 
import { dataService as dataServiceFactory } from "./read_data_service"; 

const { Component } = owl;

class PartnersPortal extends Component {
    setup() {
        this.initLimit = 80;
        this.initOffset = 0;
        this.pollInterval = 30000;
        this.pollingTimer = null;
        this.searchTimeout = null;
        this.isComponentAlive = true; 
        this.isFirstLoad = true; 

        this.texts = {
            updatingData: _t("Updating data..."),
            accessLog: _t("Access Log"),
            issueBadge: _t("Issue Badge"),
            returnBadge: _t("Return Badge"),
            searchName: _t("Search Name..."),
            filterVarco: _t("Select an Access Point..."),
            all: _t("All"),
            internals: _t("Internals"),
            externals: _t("Externals"),
            presentOnly: _t("Present Only"),
            name: _t("Name"),
            lastEvent: _t("Last Event"),
            direction: _t("Direction"),
            accessPoint: _t("Access Point"),
            attendanceStatus: _t("Attendance Status"),
            entrance: _t("Entrance"),
            exit: _t("Exit"),
            present: _t("Present"),
            absent: _t("Absent"),
            noResults: _t("No results found with the current filters."),
            autoRefresh: _t("Auto-refresh:")
        };

        this.dataService = this.props.dataService;
        
        this.paCategorySelectRef = useRef("paCategorySelect");    
        this.ca_punto_accesso_category = [];

        this.state = useState({
            isLoading: true, 
            searchValue: "",
            filterCriteria: { internal: null, external: null, is_present: null, pa_category_id: null },
            offset: this.initOffset,
            limit: this.initLimit,
            total: 0,
            ca_persona_data: []
        });

        onWillStart(async () => {
            const categories = await this.dataService.loadPuntoAccessoCategory();
            this.ca_punto_accesso_category = categories || [];
        });

        onMounted(() => {
            const staticLoader = document.getElementById('static_loader');
            if (staticLoader) {
                staticLoader.remove();
            }

            if (this.paCategorySelectRef.el) {
                const $paCategorySelect = $(this.paCategorySelectRef.el);
                $paCategorySelect.select2({ 
                    placeholder: this.texts.filterVarco, 
                    allowClear: true, 
                    width: '100%' 
                });
                $paCategorySelect.on("change.select2", this.onCategoryChange.bind(this));
            }
            this.fetchData(this.state.limit, this.state.offset);
            this.setupPolling();
        });

        onWillUnmount(() => {
            this.isComponentAlive = false;
            this.clearPolling();
            if (this.searchTimeout) clearTimeout(this.searchTimeout);
            if (this.paCategorySelectRef.el) {
                $(this.paCategorySelectRef.el).select2('destroy');
            }
        });
    }

    async fetchData(limit, offset, query = null, filter = null) {
        let loadingTimer = null;
        try {
            if (!this.isFirstLoad) {
                loadingTimer = setTimeout(() => {
                    if (this.isComponentAlive) this.state.isLoading = true;
                }, 300);
            }
            const response = await this.dataService.loadAnagrafiche(limit, offset, query, filter);
            if (this.isComponentAlive && response) {
                this.state.offset = offset;
                this.state.limit = limit;
                this.state.total = response.total || 0;
                this.state.ca_persona_data = response.items || [];
            }
        } catch (error) {
            console.error(error);
        } finally {
            if (loadingTimer) clearTimeout(loadingTimer);
            if (this.isComponentAlive) {
                this.state.isLoading = false;
                this.isFirstLoad = false;
            }
        }
    }

    async onPageChange(event) {
        await this.fetchData(event.limit, event.offset, this.state.searchValue, this.state.filterCriteria);
    }

    async setFilterAll() { this.state.filterCriteria.internal = null; this.state.filterCriteria.external = null; await this._resetAndFetch(); }
    async setFilterInternal() { this.state.filterCriteria.external = null; this.state.filterCriteria.internal = true; await this._resetAndFetch(); }
    async setFilterExternal() { this.state.filterCriteria.internal = null; this.state.filterCriteria.external = true; await this._resetAndFetch(); }
    async setFilterIsPresent(evt) { this.state.filterCriteria.is_present = evt.target.checked ? true : null; await this._resetAndFetch(); }
    
    async onCategoryChange(event) {
        const selectedId = parseInt(event.target.value);
        this.state.filterCriteria.pa_category_id = selectedId || null;
        await this._resetAndFetch();
    }

    updateSearch(event) {
        this.state.searchValue = event.target.value;
        if (this.searchTimeout) clearTimeout(this.searchTimeout);
        this.searchTimeout = setTimeout(async () => { await this._resetAndFetch(); }, 500);
    }

    async _resetAndFetch() {
        this.state.offset = 0; 
        await this.fetchData(this.state.limit, 0, this.state.searchValue, this.state.filterCriteria);
    }

    animateProgressBar() {
        const progressBar = document.getElementById('progressbar');
        if (!progressBar) return;
        const duration = this.pollInterval;
        let startTime = Date.now();
        const update = () => {
            if (!this.isComponentAlive) return;
            const elapsed = Date.now() - startTime;
            if (elapsed > duration) startTime = Date.now();
            const progress = 100 - ((elapsed % duration) / duration * 100);
            progressBar.style.width = progress + '%';
            requestAnimationFrame(update);
        }
        requestAnimationFrame(update);
    }

    setupPolling() {
        this.animateProgressBar();
        const pollLoop = async () => {
            if (!this.isComponentAlive) return;
            await this.fetchData(this.state.limit, this.state.offset, this.state.searchValue, this.state.filterCriteria);
            if (this.isComponentAlive) {
                this.pollingTimer = setTimeout(pollLoop, this.pollInterval);
            }
        };
        this.pollingTimer = setTimeout(pollLoop, this.pollInterval);
    }

    clearPolling() {
        if (this.pollingTimer) { clearTimeout(this.pollingTimer); this.pollingTimer = null; }
    }
}

PartnersPortal.components = { Pager };
PartnersPortal.template = 'controllo_accessi_portale.PartnersPortal';

publicWidget.registry.PartnersPortalWidget = publicWidget.Widget.extend({
    selector: '#partners_portal_app',
    start: async function () {
        const serviceInstance = dataServiceFactory.start(null, { rpc: jsonrpc });
        const env = {
            bus: new EventBus(),
            services: {
                ui: { isSmall: false, size: 2, bus: new EventBus() },
                localization: { direction: 'ltr' },
                hotkey: { add: () => {} }
            }
        };
        return mount(PartnersPortal, this.el, {
            templates: templates,
            props: { dataService: serviceInstance },
            env: env,
            dev: odoo.debug, 
        });
    }
});

export default PartnersPortal;