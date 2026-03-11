/** @odoo-module */
import {registry} from "@web/core/registry";
import {onMounted, onWillStart, useRef, useState} from '@odoo/owl';
import {useService} from "@web/core/utils/hooks";
import {DateTimeInput} from "@web/core/datetime/datetime_input";
import {_t} from "@web/core/l10n/translation";

const {DateTime} = luxon;
const {Component} = owl;

class BadgeReleaseDocs extends Component {
    setup() {
        this.personaId = this.props.persona_id ?? {};
        this.errors = this.props.errors ?? {};
        this.error_message = this.props.error_message;
        this.csrfToken = odoo.csrf_token;

        this.state = useState({
            formValues: Object.assign({
                persona_id: this.personaId,
                tipo_documento_id: null,
                validity_start_date: null,
                validity_end_date: null,
                document_code: "",
                issued_by: ""
            }, this.props.values, {
                validity_start_date: this.props.values?.validity_start_date ? DateTime.fromISO(this.props.values.validity_start_date) : null,
                validity_end_date: this.props.values?.validity_end_date ? DateTime.fromISO(this.props.values.validity_end_date) : null,
            })
        });
        
        this.personaSelectRef = useRef("personaSelect");
        this.dataService = useService("dataService");
        
        this.ca_persona = [];
        this.tipo_documento = [];
        this.datesCtn = useRef("date-ctn")
        this.onDateStartSelect = this.onDateStartSelect.bind(this);
        this.onDateEndSelect = this.onDateEndSelect.bind(this);

        onMounted(() => {
            const $select = $(this.personaSelectRef.el);
            $select.select2({ placeholder: _t("Select a Partner..."), allowClear: true, width: '100%' });
            $select.select2("readonly", true);
            
            if(this.datesCtn.el){
                var inputs = this.datesCtn.el.querySelectorAll("input");
                inputs.forEach(input => {
                    input.setAttribute("required", true);
                    input.classList.add("form-control");
                })
            }
        });

        onWillStart(async () => {
            const res = await Promise.all([
                this.dataService.loadPersona(),
                this.dataService.loadTipoDocumento()
            ]);
            this.ca_persona = res[0] || [];
            this.tipo_documento = res[1] || [];
        });
    };

    onDateStartSelect(dt) { this.state.formValues.validity_start_date = dt; }
    onDateEndSelect(dt) { this.state.formValues.validity_end_date = dt; }

    onSubmitClick(e) {
        var form = $("form");
        form.addClass('was-validated');
    }
}

BadgeReleaseDocs.components = {DateTimeInput};
BadgeReleaseDocs.template = 'controllo_accessi_portale.BadgeReleaseDocs';
BadgeReleaseDocs.props = {
    persona_id: Number,
    values: {type: Object, optional: true},
    errors: {type: Object, optional: true},
    error_message: {type: String, optional: true},
};
registry.category("public_components").add("controllo_accessi_portale.BadgeReleaseDocs", BadgeReleaseDocs);