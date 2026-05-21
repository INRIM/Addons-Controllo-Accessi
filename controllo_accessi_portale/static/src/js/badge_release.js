/** @odoo-module */
import publicWidget from "@web/legacy/js/public/public_widget";
import { onMounted, onWillStart, onWillUnmount, useRef, useState, Component, EventBus, mount } from '@odoo/owl';
import { _t } from "@web/core/l10n/translation";
import { getTemplate } from "@web/core/templates";
import { rpc as jsonrpc } from "@web/core/network/rpc";
import { dataService as dataServiceFactory } from "./read_data_service";

const { DateTime } = luxon;

class BadgeRelease extends Component {
    setup() {
        this.csrfToken = odoo.csrf_token;
        this.values = this.props.values || {};
        this.errors = this.props.errors || {};
        this.errorMessage = this.props.error_message || "";
        this.dataService = this.props.dataService;

        this.texts = {
            issueBadge: _t("Issue Badge"),
            partnerList: _t("Partner List"),
            findInSystem: _t("Find in System"),
            existingPartner: _t("Existing Partner"),
            selectPartnerHelp: _t("Select a partner to pre-fill data or leave blank to create a new one."),
            personalDetails: _t("Personal Details"),
            lastName: _t("Last Name *"),
            firstName: _t("First Name *"),
            fiscalCode: _t("Fiscal Code *"),
            vatNumber: _t("VAT Number"),
            companyName: _t("Company Name / Entity *"),
            entityType: _t("Entity Type"),
            email: _t("Email"),
            mobile: _t("Mobile"),
            idNumber: _t("ID Number"),
            internalContact: _t("Internal Contact"),
            searchDomain: _t("Search Domain"),
            presentToday: _t("Present Today"),
            all: _t("All"),
            referencePerson: _t("Reference Person"),
            accessDetails: _t("Access Details"),
            workType: _t("Work Type *"),
            titleQualification: _t("Title / Qualification *"),
            assignBadge: _t("Assign Badge *"),
            startDate: _t("Start Date"),
            endDate: _t("End Date"),
            selectPartner: _t("Select a Partner..."),
            selectRepresentative: _t("Select a representative..."),
            selectBadge: _t("Select a badge..."),
            selectWorkInfo: _t("Select a work info type..."),
            selectTitle: _t("Select a title...")
        };

        this.ca_persona = [];
        this.ca_persona_parent = [];
        this.tipo_ente_azienda = [];
        this.tipo_ente_azienda_hidden = [];
        this.work_info_type = [];
        this.titolo_persona = [];
        this.ca_ente_azienda = [];
        this.tags = [];
        
        this.store = {
            workInfosMap: {}, 
            entiMap: {},      
            entiVatMap: {},   
            titoliMap: {},    
            personasMap: {},  
            tagDomains: {},   
        };

        this.state = useState({
            csrfToken: odoo.csrf_token,
            selectedPersonaId: null,
            caPersonaParentFiltered: [],
            availableTags: [], 
            enteInterno: false,
            isPersonaInternal: false, 

            formValues: {
                name: "", lastname: "", fiscalcode: "", freshman: "", email: "", mobile: "",
                ente_azienda: null, ca_ente_name: "", tipo_ente_azienda_id: null, vat: "",
                date_start: this.values.date_start ? DateTime.fromISO(this.values.date_start) : DateTime.local(),
                date_end: this.values.date_end ? DateTime.fromISO(this.values.date_end) : DateTime.local(),
                ca_tag_id: null, ref_domain: "present", work_info_type: null, ca_title: null,
                ...this.values
            },
            errors: this.errors,
            errorMessage: this.errorMessage
        });

        this.refs = {
            persona: useRef("personaSelect"),
            parent: useRef("parentSelect"),
            tag: useRef("tagSelect"),
            workInfo: useRef("wInfoTypeSelect"),
            title: useRef("caTitleSelect")
        };

        this.onPersonaChange = this.onPersonaChange.bind(this);
        this.onTagChange = this.onTagChange.bind(this);
        this.onTitleChange = this.onTitleChange.bind(this);
        this.onDateStartChange = this.onDateStartChange.bind(this);
        this.onDateEndChange = this.onDateEndChange.bind(this);
        this.onSubmitClick = this.onSubmitClick.bind(this);

        onWillStart(async () => {
            const [initData, personas] = await Promise.all([
                this.dataService.loadBadgeReleaseInitData(),
                this.dataService.loadPersona()
            ]);

            const safeInit = initData || {};
            const safePersonas = personas || [];

            this.ca_persona = safePersonas;
            this.ca_persona_parent = safeInit.persona_parent || [];
            this.tipo_ente_azienda = safeInit.tipo_enti || [];
            this.tipo_ente_azienda_hidden = safeInit.tipo_enti_hidden_ids || [];
            this.work_info_type = safeInit.work_info_types || [];
            this.titolo_persona = safeInit.titoli || [];
            this.ca_ente_azienda = safeInit.enti_aziende || [];
            this.tags = safeInit.tags || [];
            this.store.tagDomains = safeInit.tag_domains || {}; 
            
            this.store.personasMap = Object.fromEntries(safePersonas.map(p => [p.id, p]));
            this.store.titoliMap = Object.fromEntries(this.titolo_persona.map(t => [t.id, t]));
            this.store.entiMap = Object.fromEntries(this.ca_ente_azienda.map(e => [e.id, e]));
            
            this.ca_ente_azienda.forEach(e => { if(e.vat) this.store.entiVatMap[e.vat] = e; });
            (safeInit.work_infos || []).forEach(w => { 
                if(w.ca_persona_id) this.store.workInfosMap[w.ca_persona_id[0]] = w; 
            });

            if (this.values.persona_id) this.state.selectedPersonaId = parseInt(this.values.persona_id);
            if (this.values.ca_work_info_type_id) this.state.formValues.work_info_type = parseInt(this.values.ca_work_info_type_id);
            if (this.values.ca_title_id) this.state.formValues.ca_title = parseInt(this.values.ca_title_id);
            if (this.values.ca_tag_id) this.state.formValues.ca_tag_id = parseInt(this.values.ca_tag_id);

            this.evalParentPresent();
            
            this.filterAvailableTagsSimple();
        });

        onMounted(() => {
            const staticLoader = document.getElementById('static_loader');
            if (staticLoader) staticLoader.remove();
            this.initSelect2();
        });

        onWillUnmount(() => {
            Object.values(this.refs).forEach(ref => { 
                if(ref.el) $(ref.el).select2('destroy'); 
            });
        });
    }

    initSelect2() {
        const init = (ref, ph, handler) => {
            if (!ref.el) return;
            const $el = $(ref.el);
            $el.select2({ placeholder: ph, allowClear: true, width: '100%' });
            if (handler) $el.on("change.select2", handler);
            
            const initialVal = $el.val(); 
            if(initialVal) $el.trigger('change.select2');
        };

        init(this.refs.persona, this.texts.selectPartner, this.onPersonaChange);
        init(this.refs.parent, this.texts.selectRepresentative);
        init(this.refs.tag, this.texts.selectBadge, this.onTagChange);
        init(this.refs.workInfo, this.texts.selectWorkInfo, (e) => { 
            this.state.formValues.work_info_type = e.target.value ? parseInt(e.target.value) : null; 
        });
        init(this.refs.title, this.texts.selectTitle, this.onTitleChange);
    }

    onPersonaChange(ev) {
        const id = parseInt(ev.target.value);
        this.state.selectedPersonaId = id || null;
        this.state.formValues.persona_id = id || null; 
        
        if (!id) {
            this.state.isPersonaInternal = false;
            this.filterAvailableTagsSimple();
            return;
        }
        const persona = this.store.personasMap[id];
        if (persona) this.populatePersona(persona);
    }

    populatePersona(persona) {
        const wInfo = this.store.workInfosMap[persona.id];
        let ente = null;
        if (persona.ca_ente_azienda_ids?.[0]) {
            ente = this.store.entiMap[persona.ca_ente_azienda_ids[0]];
        }

        this.state.isPersonaInternal = persona.is_internal || false;
        this.checkEnteInterno(ente);
        
        let dStart = this.state.formValues.date_start;
        let dEnd = this.state.formValues.date_end;
        if (wInfo) {
            if(wInfo.date_start) dStart = DateTime.fromISO(wInfo.date_start).set({hour: 8, minute: 0, second: 0});
            if(wInfo.date_end) dEnd = DateTime.fromISO(wInfo.date_end).set({hour: 18, minute: 0, second: 0});
        }

        Object.assign(this.state.formValues, {
            name: persona.name || "", 
            lastname: persona.lastname || "", 
            fiscalcode: persona.fiscalcode || "",
            freshman: persona.freshman || "", 
            email: persona.email || "", 
            mobile: persona.mobile || "",
            ente_azienda: ente?.id || "", 
            ca_ente_name: ente?.name || "",
            tipo_ente_azienda_id: ente?.tipo_ente_azienda_id?.[0] || "", 
            vat: ente?.vat || "",
            work_info_type: wInfo?.ca_work_info_type_id?.[0] || "", 
            ca_title: wInfo?.ca_title_id?.[0] || "",
            date_start: dStart, 
            date_end: dEnd
        });

        $(this.refs.workInfo.el).val(this.state.formValues.work_info_type).trigger("change");
        $(this.refs.title.el).val(this.state.formValues.ca_title).trigger("change");
        
        this.filterAvailableTagsSimple(); 
    }

    onVatChange(ev) {
        const vat = ev.target.value;
        this.state.formValues.vat = vat;
        const ente = this.store.entiVatMap[vat];
        if (ente) {
             Object.assign(this.state.formValues, {
                ca_ente_name: ente.name, 
                ente_azienda: ente.id, 
                tipo_ente_azienda_id: ente.tipo_ente_azienda_id?.[0]
             });
             this.checkEnteInterno(ente);
        }
    }

    checkEnteInterno(ente) {
        this.state.enteInterno = false;
        if (ente?.tipo_ente_azienda_id?.[0]) {
             if (this.tipo_ente_azienda_hidden.includes(ente.tipo_ente_azienda_id[0])) {
                 this.state.enteInterno = true;
             }
        }
    }

    onTitleChange(ev) {
        this.state.formValues.ca_title = ev.target.value ? parseInt(ev.target.value) : null;
        // this.filterAvailableTags();
    }

    filterAvailableTagsSimple() {
        const persona = this.store.personasMap[this.state.selectedPersonaId];
        const domains = this.store.tagDomains; 

        if (!persona || !persona.current_tag || persona.current_tag.length === 0) {
            this.state.availableTags = this.tags.filter(t => !t.in_use && !t.revoked);
            return;
        }

        const neededIds = persona.current_tag_temp === false
            ? (domains.temp || [])
            : (domains.visitor || []);

        this.state.availableTags = this.tags.filter(tag =>
            !tag.in_use &&
            !tag.revoked &&
            tag.ca_proprieta_tag_ids.some(id => neededIds.includes(id))
        );
    }

    filterAvailableTags() {
        const titleId = this.state.formValues.ca_title;
        const title = this.store.titoliMap[titleId];
        const persona = this.store.personasMap[this.state.selectedPersonaId];
        const domains = this.store.tagDomains; 
        let neededIds = [];

        if (persona?.current_tag?.length) neededIds = domains.visitor; 
        else if (title?.structured === false) neededIds = domains.temp; 
        else if (persona?.is_internal) neededIds = domains.internal; 
        else {
            this.state.availableTags = this.tags.filter(t => !t.in_use && !t.revoked);
            return;
        }

        if (neededIds && neededIds.length > 0) {
            this.state.availableTags = this.tags.filter(t => 
                !t.in_use && !t.revoked && t.ca_proprieta_tag_ids.some(id => neededIds.includes(id))
            );
        } else {
            this.state.availableTags = [];
        }
    }

    onTagChange(ev) {
        const id = parseInt(ev.target.value);
        this.state.formValues.ca_tag_id = id;
        const tag = this.tags.find(t => t.id === id);
        if (tag?.temp) {
             const now = DateTime.now().setZone('Europe/Rome');
             this.state.formValues.date_start = now;
             this.state.formValues.date_end = now.set({hour: 19, minute: 30, second: 0});
        }
    }

    onRefDomainChange(ev) {
        this.state.formValues.ref_domain = ev.target.value;
        this.evalParentPresent();
    }

    evalParentPresent() {
        if (this.state.formValues.ref_domain === "present") {
            this.state.caPersonaParentFiltered = this.ca_persona_parent.filter(p => p.present === "yes");
        } else {
            this.state.caPersonaParentFiltered = this.ca_persona_parent || [];
        }
    }

    formatDateForInput(luxonDate) {
        if (!luxonDate || !luxonDate.isValid) return "";
        return luxonDate.toFormat("yyyy-MM-dd'T'HH:mm");
    }

    onDateStartChange(ev) {
        const val = ev.target.value;
        this.state.formValues.date_start = val ? DateTime.fromISO(val) : null;
    }

    onDateEndChange(ev) {
        const val = ev.target.value;
        this.state.formValues.date_end = val ? DateTime.fromISO(val) : null;
    }

    onNameChange(e) { this.state.formValues.name = e.target.value; }
    onLastnameChange(e) { this.state.formValues.lastname = e.target.value; }
    onEnteNameChange(e) { this.state.formValues.ca_ente_name = e.target.value; }
    OnTipoEnteChange(e) { this.state.formValues.tipo_ente_azienda_id = e.target.value; }
    OnFreshmanChange(e) { this.state.formValues.freshman = e.target.value; }
    onEmailChange(e) { 
        this.state.formValues.email = e.target.value; 
        const found = Object.values(this.store.personasMap).find(p => p.email === e.target.value);
        if(found) $(this.refs.persona.el).val(found.id).trigger("change");
    }
    onMobileChange(e) { this.state.formValues.mobile = e.target.value; }
    onFiscalcodeChange(ev) {
        const val = ev.target.value;
        this.state.formValues.fiscalcode = val;
        const found = Object.values(this.store.personasMap).find(p => p.fiscalcode === val);
        if(found) $(this.refs.persona.el).val(found.id).trigger("change");
    }

    onSubmitClick(e) {
        const form = document.querySelector("form");
        if (form) {
            form.classList.add('was-validated');
            if (!form.checkValidity()) {
                e.preventDefault();
                e.stopPropagation();
                const invalid = form.querySelector(":invalid");
                if(invalid) invalid.scrollIntoView({behavior: "smooth", block: "center"});
            }
        }
    }
}

BadgeRelease.components = {};
BadgeRelease.template = 'controllo_accessi_portale.BadgeRelease';
BadgeRelease.props = {
    values: {type: Object, optional: true},
    errors: {type: Object, optional: true},
    error_message: {type: String, optional: true},
    dataService: {type: Object}
};

publicWidget.registry.BadgeReleaseWidget = publicWidget.Widget.extend({
    selector: '#badge_release_app',
    
    start: function () {
        const serviceInstance = dataServiceFactory.start(null, { rpc: jsonrpc });
        const serverData = window.odoo_badge_release_data || {};

        const env = {
            bus: new EventBus(),
            services: {
                ui: { isSmall: false, size: 2, bus: new EventBus() },
                localization: { direction: 'ltr' },
            }
        };

        return mount(BadgeRelease, this.el, {
            getTemplate: getTemplate,
            props: {
                dataService: serviceInstance,
                values: serverData.values || {},
                errors: serverData.errors || {},
                error_message: serverData.error_message || ""
            },
            env: env,
            dev: odoo.debug,
        });
    }
});

export default BadgeRelease;
