/** @odoo-module **/

import publicWidget from "@web/legacy/js/public/public_widget";

// El hero de ASVETEC es un layout estático split-panel (no carousel).
// Este widget solo maneja el comportamiento del scroll-anchor del CTA "Contáctanos".
publicWidget.registry.sAsvHero = publicWidget.Widget.extend({
    selector: ".s_asv_hero",

    start() {
        this._bindSmoothScroll();
        return this._super(...arguments);
    },

    _bindSmoothScroll() {
        this.el.querySelectorAll('a[href^="#"]').forEach((anchor) => {
            anchor.addEventListener("click", (e) => {
                const target = document.querySelector(anchor.getAttribute("href"));
                if (target) {
                    e.preventDefault();
                    target.scrollIntoView({ behavior: "smooth" });
                }
            });
        });
    },
});

export default publicWidget.registry.sAsvHero;
