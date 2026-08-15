/** @odoo-module **/

import publicWidget from "@web/legacy/js/public/public_widget";

// Las páginas editadas con el constructor de Odoo almacenan una copia del
// HTML del snippet. Este widget mantiene esas copias sincronizadas con la
// imagen definida actualmente en product.public.category.
publicWidget.registry.sAsvCategoriesImages = publicWidget.Widget.extend({
    selector: ".s_asv_categories",
    disabledInEditableMode: false,

    start() {
        // En los widgets legacy de Odoo, _super sólo existe durante la llamada
        // síncrona. La carga remota se lanza después para no romper el editor.
        const result = this._super.apply(this, arguments);
        this._replaceIconsWithCategoryImages();
        return result;
    },

    async _replaceIconsWithCategoryImages() {
        let imageUrls;
        try {
            imageUrls = await this._rpc({route: "/asvetec/category-images"});
        } catch (_) {
            return;
        }

        for (const card of this.el.querySelectorAll(".asv-cat-card")) {
            const href = card.getAttribute("href");
            if (!href) continue;

            const categoryId = new URL(href, window.location.origin)
                .searchParams.get("category");
            const imageUrl = imageUrls[categoryId];
            const icon = card.querySelector(".asv-cat-icon");
            if (!imageUrl || !icon) continue;

            const image = document.createElement("img");
            image.className = "asv-cat-image";
            image.src = imageUrl;
            image.alt = card.querySelector(".asv-cat-name")?.textContent.trim() || "";
            image.loading = "lazy";
            icon.replaceChildren(image);
        }
    },
});

export default publicWidget.registry.sAsvCategoriesImages;
