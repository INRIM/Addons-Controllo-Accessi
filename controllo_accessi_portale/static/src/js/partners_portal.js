/** @odoo-module */
import publicWidget from "@web/legacy/js/public/public_widget";
import { onWillStart, onWillUnmount, onMounted, useState, mount } from '@odoo/owl';
import { Pager } from "@web/core/pager/pager";
import { SelectMenu } from "@web/core/select_menu/select_menu";
import { useService } from "@web/core/utils/hooks";
import { _t } from "@web/core/l10n/translation";
import { getTemplate } from "@web/core/templates";

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

        this.dataService = useService('dataService');
        
        this.state = useState({
            isLoading: true,
            searchValue: "",
            filterCriteria: { internal: null, external: null, is_present: null, pa_category_id: null },
            sort: { field: "last_event", direction: "desc" },
            offset: this.initOffset,
            limit: this.initLimit,
            total: 0,
            ca_persona_data: [],
            ca_punto_accesso_category: [],
        });

        onWillStart(async () => {
            const categories = await this.dataService.loadPuntoAccessoCategory();
            this.state.ca_punto_accesso_category = categories || [];
        });

        onMounted(() => {
            const staticLoader = document.getElementById('static_loader');
            if (staticLoader) {
                staticLoader.remove();
            }
            this.fetchData(this.state.limit, this.state.offset);
            this.setupPolling();
        });

        onWillUnmount(() => {
            this.isComponentAlive = false;
            this.clearPolling();
            if (this.searchTimeout) clearTimeout(this.searchTimeout);
        });
    }

    get categoryChoices() {
        return this.state.ca_punto_accesso_category.map(cat => ({
            value: cat.id,
            label: cat.display_name,
        }));
    }

    async fetchData(limit, offset, query = null, filter = null, sort = null) {
        let loadingTimer = null;
        try {
            if (!this.isFirstLoad) {
                loadingTimer = setTimeout(() => {
                    if (this.isComponentAlive) this.state.isLoading = true;
                }, 300);
            }
            const currentSort = sort || this.state.sort;
            const response = await this.dataService.loadAnagrafiche(
                limit,
                offset,
                query,
                filter,
                currentSort.field,
                currentSort.direction,
            );
            if (this.isComponentAlive && response) {
                this.state.offset = offset;
                this.state.limit = limit;
                this.state.total = response.total || 0;
                this.state.ca_persona_data = response.items || [];
                this.state.sort.field = currentSort.field;
                this.state.sort.direction = currentSort.direction;
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
    
    async onCategoryChange(value) {
        this.state.filterCriteria.pa_category_id = value || null;
        await this._resetAndFetch();
    }

    updateSearch(event) {
        this.state.searchValue = event.target.value;
        if (this.searchTimeout) clearTimeout(this.searchTimeout);
        this.searchTimeout = setTimeout(async () => { await this._resetAndFetch(); }, 500);
    }

    async toggleNameSort() {
        await this.toggleSort("display_name");
    }

    async toggleLastEventSort() {
        await this.toggleSort("last_event");
    }

    async toggleSort(field) {
        const sameField = this.state.sort.field === field;
        const defaultDirection = field === "display_name" ? "asc" : "desc";
        this.state.sort.field = field;
        this.state.sort.direction = sameField
            ? (this.state.sort.direction === "asc" ? "desc" : "asc")
            : defaultDirection;
        await this._resetAndFetch();
    }

    getSortIconClass(field) {
        if (this.state.sort.field !== field) {
            return "fa fa-sort text-muted ms-2";
        }
        return `fa ${this.state.sort.direction === "asc" ? "fa-sort-up" : "fa-sort-down"} text-primary ms-2`;
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

PartnersPortal.components = { Pager, SelectMenu };
PartnersPortal.template = 'controllo_accessi_portale.PartnersPortal';

publicWidget.registry.PartnersPortalWidget = publicWidget.Widget.extend({
    selector: '#partners_portal_app',
    start: async function () {
        return mount(PartnersPortal, this.el, {
            getTemplate: getTemplate,
            props: {},
            env: Component.env,
            dev: odoo.debug,
        });
    }
});

export default PartnersPortal;
