/** @odoo-module */

import {registry} from "@web/core/registry";
import {onMounted, onWillStart, useRef, useState} from '@odoo/owl';
import {useService} from "@web/core/utils/hooks";
import {DateTimeInput} from "@web/core/datetime/datetime_input";
import {_t} from "@web/core/l10n/translation";

const {DateTime} = luxon;

const {Component} = owl;

class BadgeRelease extends Component {
    setup() {
        // ca_persona_parent: [],
        this.csrfToken = odoo.csrf_token;
        this.errors = this.props.errors ?? {};
        this.error_message = this.props.error_message;

        this.state = useState({
            caPersonaParentFiltered: [],
            selectedPersona: null,
            selectedAzienda: null,
            selectedWorkInfo: null,
            isPersonaInternal: false,
            availableTags: [],
            formValues: Object.assign({
                name: "",
                lastname: "",
                fiscalcode: "",
                freshman: "",
                email: "",
                mobile: "",
                ente_azienda: null,
                ca_ente_name: "",
                tipo_ente_azienda_id: null,
                vat: "",
                date_start: DateTime.local(),
                date_end: DateTime.local(),
                ca_tag_id: null,
                ref_domain: "present",
                work_info_type: null,
                ca_title: null,
            }, this.props.values, {
                date_start: this.props.values?.date_start ? DateTime.fromISO(this.props.values.date_start) : null,
                date_end: this.props.values?.date_end ? DateTime.fromISO(this.props.values.date_end) : null,
            }),
            errors: {},
            enteInterno: false,
        });
        this.OnTagChange = this.OnTagChange.bind(this);
        this.onPersonaChange = this.onPersonaChange.bind(this);
        this.loader = $("#loading-rb")
        this.personaSelectRef = useRef("personaSelect");
        this.parentSelectRef = useRef("parentSelect");
        this.tagSelectRef = useRef("tagSelect");
        this.workInfoSelectRef = useRef("wInfoTypeSelect");
        this.caTitleSelectRef = useRef("caTitleSelect");
        this.onDateStartSelect = this.onDateStartSelect.bind(this);
        this.onDateEndSelect = this.onDateEndSelect.bind(this);
        this.dataService = useService("dataService");
        this.notification = useService("notification");
        this.ca_persona = useState([]);
        this.ca_persona_parent = useState([]);
        this.tipo_ente_azienda = useState([]);
        this.ca_ente_azienda = useState([]);
        this.work_info_type = useState([]);
        this.work_info = useState([]);
        this.titolo_persona = useState([]);
        this.tags = useState([]);
        this.tagFilterDomain = useState([]);
        this.datesCtn = useRef("date-ctn")

        onMounted(() => {

            const $select = $(this.personaSelectRef.el);
            $select.select2({
                placeholder: _t("Select a Partner..."),
                allowClear: true,
                width: '100%',
            });
            $select.on("change.select2", this.onPersonaChange.bind(this));

            const $select2 = $(this.parentSelectRef.el);
            $select2.select2({
                placeholder: _t("Select a representative..."),
                allowClear: true,
                width: '100%'
            });

            const $select3 = $(this.tagSelectRef.el);
            $select3.select2({
                placeholder: _t("Select a badge..."),
                allowClear: true,
                width: '100%'
            });
            $select3.on("change.select2", this.OnTagChange.bind(this));

            const $wInfoSelect = $(this.workInfoSelectRef.el);
            $wInfoSelect.select2({
                placeholder: _t("Select a work info type..."),
                allowClear: true,
                width: '100%'
            });
            $wInfoSelect.on("change.select2", this.OnWorkInfoChange.bind(this));

            const $caTitleSelectRef = $(this.caTitleSelectRef.el);
            $caTitleSelectRef.select2({
                placeholder: _t("Select a title..."),
                allowClear: true,
                width: '100%'
            });
            $caTitleSelectRef.on("change.select2", this.onTitleChange.bind(this));

            // Imposta a required i field date, siccome non è previsto dal componente...
            var inputs = this.datesCtn.el.querySelectorAll("input");
            inputs.forEach(input => {
                input.setAttribute("required", true);
                input.classList.add("form-control");
            });
        });

        function sleep(ms) {
            return new Promise(resolve => setTimeout(resolve, ms));
        }

        onWillStart(async () => {
            await sleep(3000);
            const res = await Promise.all([
                this.dataService.loadPersona(),
                this.dataService.loadPersonaParent(),
                this.dataService.loadTipoEntiAzienda(),
                this.dataService.loadTipoEntiAziendaHidden(),
                this.dataService.loadWorkInfoType(),
                this.dataService.loadTitoloPersona(),
                this.dataService.loadEnteAzienda(),
                this.dataService.loadTags(),
                this.dataService.loadWorkInfo(),
                this.dataService.loadTagFilterDomain()
            ]);

            this.ca_persona = res[0];
            this.ca_persona_parent = res[1];
            this.tipo_ente_azienda = res[2];
            this.tipo_ente_azienda_hidden = res[3];
            this.work_info_type = res[4];
            this.titolo_persona = res[5];
            this.ca_ente_azienda = res[6];
            this.tags = res[7];
            this.work_info = res[8];
            this.tag_filter_domain = res[9];

            if (this.props.values.persona_id) {
                this.state.selectedPersona = this.props.values.persona_id;
            }
            if (this.props.values.ca_work_info_type_id) {
                this.state.formValues.work_info_type = this.props.values.ca_work_info_type_id;
            }
            if (this.props.values.ca_title_id) {
                this.state.formValues.ca_title = this.props.values.ca_title_id;
            }
            this.loader.hide();
            // FIXME: C'e un problema con autselezione tag perche viene refreshato credo...

        });
    };

    onPersonaChange(event) {
        const selectedId = parseInt(event.target.value);
        const selectedPersona = this.ca_persona.find(persona => persona.id === selectedId) || false;
        this.populatePersona(selectedPersona);
    }

    onNameChange(event) {
        Object.assign(this.state.formValues, {
            name: event.target.value,
        });
    }

    onLastnameChange(event) {
        Object.assign(this.state.formValues, {
            lastname: event.target.value,
        });
    }

    onEnteNameChange(event) {
        Object.assign(this.state.formValues, {
            ca_ente_name: event.target.value,
        });
    }

    OnTipoEnteChange(event) {
        Object.assign(this.state.formValues, {
            tipo_ente_azienda_id: event.target.value,
        });
    }

    OnFreshmanChange(event) {
        Object.assign(this.state.formValues, {
            freshman: event.target.value,
        });
    }

    onTitleChange(event) {
        this.state.formValues.ca_title = event.target.value ? parseInt(event.target.value) : null;
        this.filterAvailableTags();
    }

    onFiscalcodeChange(event) {
        Object.assign(this.state.formValues, {
            fiscalcode: event.target.value,
        });
        const selectedPersona = this.ca_persona.find(persona => persona.fiscalcode === event.target.value) || "";
        if (selectedPersona) {
            const $select = $(this.personaSelectRef.el);
            $select.val(selectedPersona.id).trigger("change");
        }
    }

    onEmailChange(event) {
        Object.assign(this.state.formValues, {
            email: event.target.value,
        });
        const selectedPersona = this.ca_persona.find(persona => persona.email === event.target.value) || "";
        if (selectedPersona) {
            const $select = $(this.personaSelectRef.el);
            $select.val(selectedPersona.id).trigger("change");
        }
    }

    onMobileChange(event) {
        Object.assign(this.state.formValues, {
            mobile: event.target.value,
        });
    }

    OnWorkInfoChange(event) {
        Object.assign(this.state.formValues, {
            work_info_type: event.target.value,
        });
    }

    // onTagChange(event) {
    //     Object.assign(this.state.formValues, {
    //         ca_tag_id: event.target.value,
    //     });
    // }

    OnTagChange(event) {
        const tagId = parseInt(event.target.value);
        const tag = this.tags.find(tag => tag.id === tagId);
        if (tag?.id !== null && tag.temp) {
            const zone = 'Europe/Rome';
            const now = DateTime.now().setZone(zone);
            const dateStart = now;
            const dateEnd = now.set({
                hour: 19,
                minute: 30,
                second: 0,
                millisecond: 0
            });
            this.state.formValues.date_start = dateStart;
            this.state.formValues.date_end = dateEnd;
        }
    }


    onVatChange(event) {
        this.state.formValues.vat = event.target.value;
        if (this.state.formValues.vat) {
            const targetAzienda = this.ca_ente_azienda.find(azienda => azienda.vat === this.state.formValues.vat)
            if (targetAzienda) {
                this.state.formValues.ca_ente_name = targetAzienda?.name || "";
                this.state.formValues.tipo_ente_azienda_id = targetAzienda?.tipo_ente_azienda_id?.[0] || "";
                this.state.formValues.ente_azienda = targetAzienda.id || "";
            }
            this.setEnteEsterno(targetAzienda);
        }
    }


    onRefDomainChange(ev) {
        this.state.formValues.ref_domain = ev.target.value;
        this.eval_parent_present();
    }

    eval_parent_present() {
        if (this.state.formValues.ref_domain === "present") {
            this.state.caPersonaParentFiltered = this.ca_persona_parent.filter(
                persona => persona.present === "yes");
        } else {
            this.state.caPersonaParentFiltered = this.ca_persona_parent;
        }
    }

    populatePersona(persona) {
        this.state.selectedPersona = persona.id || "";
        this.state.isPersonaInternal = persona.is_internal ?? false;
        const selectedAzienda = this.eval_ente_azienda_id();
        this.state.isPersonaInternal = persona.is_internal ?? false;
        const workInfo = this.work_info.find(wkinfo => wkinfo.ca_persona_id[0] === persona?.ca_workinfo_ids?.[0]);
        let dateStart = this.state.formValues.date_start;
        let dateEnd = this.state.formValues.date_end;
        if (workInfo) {
            dateStart = DateTime.fromISO(workInfo.date_start).set({
                hour: 8,
                minute: 0,
                second: 0
            });
            dateEnd = DateTime.fromISO(workInfo.date_end).set({
                hour: 18,
                minute: 0,
                second: 0
            });
        }
        Object.assign(this.state.formValues, {
            name: persona.name || "",
            lastname: persona.lastname || "",
            fiscalcode: persona.fiscalcode || "",
            freshman: persona.freshman || "",
            email: persona.email || "",
            mobile: persona.mobile || "",
            ente_azienda: selectedAzienda || "",
            ca_ente_name: selectedAzienda?.name || "",
            tipo_ente_azienda_id: selectedAzienda?.tipo_ente_azienda_id?.[0] || "",
            vat: selectedAzienda?.vat || "",
            work_info_type: workInfo?.ca_work_info_type_id?.[0] || "",
            ca_title: workInfo?.ca_title_id?.[0] || "",
            date_start: dateStart || this.state.formValues.date_start,
            date_end: dateEnd || this.state.formValues.date_end,
        });

        const $wInfoSelect = $(this.workInfoSelectRef.el);
        $wInfoSelect.val(this.state.formValues.work_info_type).trigger("change");
        const $caTitleSelect = $(this.caTitleSelectRef.el);
        $caTitleSelect.val(this.state.formValues.ca_title).trigger("change");

        this.state.selectedAzienda = selectedAzienda
        this.state.formValues.ente_azienda = selectedAzienda?.id || "";
        this.filterAvailableTags();
    }

    eval_ente_azienda_id() {
        let selectedAzienda = null;
        const selectedPersona = this.ca_persona.find(persona => persona.id === this.state.selectedPersona);
        if (selectedPersona && selectedPersona.ca_ente_azienda_ids) {
            const azienda_id = selectedPersona.ca_ente_azienda_ids[0];
            if (azienda_id) {
                selectedAzienda = this.ca_ente_azienda.find(azienda => azienda.id === azienda_id) || "";
            }
        }
        this.setEnteEsterno(selectedAzienda);
        return selectedAzienda;
    }

    setEnteEsterno(azienda_id) {
        this.enteInterno = false;
        if (azienda_id) {
            const FilterTypeCompany = this.tipo_ente_azienda_hidden.find(tipo => tipo.id === azienda_id?.tipo_ente_azienda_id?.[0]);
            if (FilterTypeCompany) {
                this.enteInterno = true;
            }
        }
    }

    filterAvailableTags() {
        const ca_title = this.titolo_persona.find(titolo => titolo.id === this.state.formValues.ca_title);
        const selectedPersona = this.ca_persona.find(persona => persona.id === this.state.selectedPersona);
        this.state.availableTags = [];
        if (selectedPersona?.current_tag?.length) {
            this.state.availableTags = this.tags.filter(tag =>
                !tag.in_use &&
                !tag.revoked &&
                tag.ca_proprieta_tag_ids.find(id => this.tag_filter_domain[2].some(tagFilter => tagFilter.id === id))
            );
        } else if (ca_title?.structured === false) {
            this.state.availableTags = this.tags.filter(tag =>
                !tag.in_use &&
                !tag.revoked &&
                tag.temp === true &&
                tag.ca_proprieta_tag_ids.find(id => this.tag_filter_domain[0].some(tagFilter => tagFilter.id === id))
            );
        } else if (selectedPersona?.is_internal) {
            this.state.availableTags = this.tags.filter(tag =>
                !tag.in_use &&
                !tag.revoked &&
                tag.ca_proprieta_tag_ids.find(id => this.tag_filter_domain[1].some(tagFilter => tagFilter.id === id))
            );
        }
    }

    onDateStartSelect(dt) {
        Object.assign(this.state.formValues, {
            date_start: dt,
        });
    }

    onDateEndSelect(dt) {
        this.state.formValues.date_end = dt;
    }

    validateSelectFields() {
        var selectToValidate = ["#parent_id", "#ca_tag_id", "#ca_work_info_type_id", "#ca_title_id"];
        selectToValidate.forEach((selector) => {
            var $tagInput = $(selector);
            if ($tagInput.length !== 0) {
                var $tagSelect2Container = $tagInput
                    .parent()
                    .find('.select2-container');
                $tagSelect2Container.removeClass('is-invalid is-valid');
                if ($tagInput.is(':invalid')) {
                    $tagSelect2Container.addClass('is-invalid');
                } else if ($tagInput.is(':valid')) {
                    $tagSelect2Container.addClass('is-valid');
                }
            }
        });
    }

    onSubmitClick(e) {
        var form = $("form");
        form.addClass('was-validated');

        this.validateSelectFields();
    }
}

BadgeRelease.components = {DateTimeInput};
BadgeRelease.template = 'controllo_accessi_portale.BadgeRelease';
BadgeRelease.props = {
    values: {type: Object, optional: true},
    errors: {type: Object, optional: true},
    error_message: {type: String, optional: true},
};
registry.category("public_components").add("controllo_accessi_portale.BadgeRelease", BadgeRelease);
