/** @odoo-module **/

import publicWidget from "@web/legacy/js/public/public_widget";

const PER_PAGE = 4;

publicWidget.registry.sAsvFeaturedProducts = publicWidget.Widget.extend({
    selector: ".s_asv_featured_products",
    events: {
        "click .asv-filter-btn": "_onFilter",
        "click [data-asv-prod-prev]": "_onPrev",
        "click [data-asv-prod-next]": "_onNext",
    },

    start() {
        this._filter = "Todos";
        this._page = 0;
        this._cards = Array.from(this.el.querySelectorAll(".asv-prod-card"));
        this._curEl = this.el.querySelector(".asv-prod-page-cur");
        this._totEl = this.el.querySelector(".asv-prod-page-tot");
        this._prevBtn = this.el.querySelector("[data-asv-prod-prev]");
        this._nextBtn = this.el.querySelector("[data-asv-prod-next]");
        this._render();
        return this._super(...arguments);
    },

    // Returns category names for a card; supports both data-categories (JSON array)
    // and legacy data-category (single string).
    _cardCategories(card) {
        try {
            const raw = card.dataset.categories;
            if (raw) return JSON.parse(raw);
        } catch (_) {}
        return card.dataset.category ? [card.dataset.category] : [];
    },

    _filtered() {
        if (this._filter === "Todos") return this._cards;
        return this._cards.filter(c => this._cardCategories(c).includes(this._filter));
    },

    _render() {
        const filtered = this._filtered();
        const total = Math.max(1, Math.ceil(filtered.length / PER_PAGE));
        this._page = Math.min(this._page, total - 1);

        this._cards.forEach(c => { c.style.display = "none"; });
        const visible = filtered.slice(this._page * PER_PAGE, this._page * PER_PAGE + PER_PAGE);
        visible.forEach(c => { c.style.display = "flex"; });

        if (this._curEl) this._curEl.textContent = this._page + 1;
        if (this._totEl) this._totEl.textContent = total;

        if (this._prevBtn) this._prevBtn.disabled = this._page === 0;
        if (this._nextBtn) this._nextBtn.disabled = this._page >= total - 1;
    },

    _onFilter(ev) {
        const btn = ev.currentTarget;
        this.el.querySelectorAll(".asv-filter-btn").forEach(b => b.classList.remove("active"));
        btn.classList.add("active");
        this._filter = btn.dataset.asvFilter;
        this._page = 0;
        this._render();
    },

    _onPrev() {
        if (this._page > 0) {
            this._page--;
            this._render();
        }
    },

    _onNext() {
        const total = Math.ceil(this._filtered().length / PER_PAGE);
        if (this._page < total - 1) {
            this._page++;
            this._render();
        }
    },
});

export default publicWidget.registry.sAsvFeaturedProducts;
