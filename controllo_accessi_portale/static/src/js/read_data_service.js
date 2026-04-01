/** @odoo-module */
import {registry} from "@web/core/registry";

export const dataService = {
    dependencies: ["rpc"],
    start(env, {rpc}) {
        return {
            loadAnagrafiche: (limit, offset, query, filter) => rpc("/get/anagrafiche", {limit, offset, query, filter}),
            loadPuntoAccessoCategory: () => rpc("/get/anagrafiche/ca_punto_accesso_category"),
            loadTipoDocumento: () => rpc("/get/badge_release_docs/tipo_documento"),
            loadBadgeReleaseInitData: () => rpc("/get/badge_release/init_data"),
            loadPersona: () => rpc("/get/badge_release/ca_persona"), 
            loadReturnTags: () => rpc("/get/badge_return/tags"),

        };
    },
};
registry.category("services").add("dataService", dataService);