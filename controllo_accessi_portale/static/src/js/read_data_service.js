/** @odoo-module */

import { registry } from "@web/core/registry";
import { memoize } from "@web/core/utils/functions";

export const dataService = {
    dependencies: ["rpc"],
    async: ["loadAnagrafiche",
        "loadPersona",
        "loadTipoEntiAzienda",
        "loadTipoEntiAziendaHidden",
        "loadPersonaParent",
        "loadWorkInfoType",
        "loadTitoloPersona",
        "loadTags",
        "loadEnteAzienda",
        "loadWorkInfo",
        "loadTagFilterDomain",
        "loadReturnTags",
        "loadTipoDocumento"
    ],
    start(env, { rpc }) {
        return {
            loadAnagrafiche: () => rpc("/get/anagrafiche"),
            loadPersona: () => rpc("/get/badge_release/ca_persona"),
            loadPersonaParent: () => rpc("/get/badge_release/ca_persona_parent"),
            loadTipoEntiAzienda: () => rpc("/get/badge_release/tipo_enti_azienda"),
            loadTipoEntiAziendaHidden: () => rpc("/get/badge_release/tipo_enti_azienda_hidden"),
            loadWorkInfoType: () => rpc("/get/badge_release/work_info_type"),
            loadTitoloPersona: () => rpc("/get/badge_release/titolo_persona"),
            loadTags: () => rpc("/get/badge_release/tags"),
            loadEnteAzienda: () => rpc("/get/badge_release/ente_azienda"),
            loadWorkInfo: () => rpc("/get/badge_release/work_info"),
            loadTagFilterDomain: () => rpc("/get/badge_release/tag_filter_domain"),
            loadReturnTags: () => rpc("/get/badge_return/tags"),
            loadTipoDocumento: () => rpc("/get/badge_release_docs/tipo_documento")
        };
    },
};

registry.category("services").add("dataService", dataService);