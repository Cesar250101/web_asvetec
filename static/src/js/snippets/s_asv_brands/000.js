/** @odoo-module **/

import publicWidget from "@web/legacy/js/public/public_widget";

// El marquee de marcas usa animación CSS pura.
// Este widget sólo pausa la animación en modo edición de Odoo.
publicWidget.registry.sAsvBrands = publicWidget.Widget.extend({
    selector: ".s_asv_brands",

    start() {
        if (this.editableMode) {
            const track = this.el.querySelector(".asv-brands-track");
            if (track) {
                track.style.animationPlayState = "paused";
            }
        }
        return this._super(...arguments);
    },
});

export default publicWidget.registry.sAsvBrands;
