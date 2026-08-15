/** @odoo-module **/

import publicWidget from "@web/legacy/js/public/public_widget";

// El carrusel se alimenta con las marcas configuradas desde el backend.
// Así también actualiza las copias del snippet que ya existen en páginas.
publicWidget.registry.sAsvBrands = publicWidget.Widget.extend({
    selector: ".s_asv_brands",

    start() {
        const result = this._super.apply(this, arguments);
        if (this.editableMode) {
            const track = this.el.querySelector(".asv-brands-track");
            if (track) {
                track.style.animationPlayState = "paused";
            }
        }
        this._loadBrands();
        return result;
    },

    async _loadBrands() {
        let brands;
        try {
            const response = await this._rpc({ route: "/asvetec/brands" });
            brands = response.brands || [];
        } catch (_) {
            return;
        }
        const track = this.el.querySelector(".asv-brands-track");
        if (!track) {
            return;
        }
        track.replaceChildren();
        if (!brands.length) {
            return;
        }
        for (const brand of [...brands, ...brands]) {
            track.append(this._brandTile(brand));
        }
        if (this.editableMode) {
            track.style.animationPlayState = "paused";
        }
    },

    _brandTile(brand) {
        const tile = brand.website_url
            ? document.createElement("a")
            : document.createElement("div");
        tile.className = "asv-brand-tile";
        if (brand.website_url) {
            tile.href = brand.website_url;
            tile.target = "_blank";
            tile.rel = "noopener noreferrer";
        }

        if (brand.image_url) {
            const image = document.createElement("img");
            image.className = "asv-brand-logo";
            image.src = brand.image_url;
            image.alt = brand.name;
            image.loading = "lazy";
            tile.append(image);
        } else {
            const name = document.createElement("span");
            const slug = brand.name.normalize("NFD")
                .replace(/[\u0300-\u036f]/g, "")
                .toLowerCase()
                .replace(/[^a-z0-9]/g, "");
            name.className = `asv-brand-${slug || "name"}`;
            name.textContent = brand.name;
            tile.append(name);
        }
        return tile;
    },
});

export default publicWidget.registry.sAsvBrands;
