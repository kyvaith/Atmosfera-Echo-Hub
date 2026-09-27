class AtmosferaTileEditor extends HTMLElement {
  constructor() {
    super();
    this.attachShadow({ mode: "open" });
    this._loaded = false;
    this._data = null;
    this._entryId = "";
  }

  set hass(value) {
    this._hass = value;
    if (this.isConnected && !this._loaded) this.load();
  }

  set panel(value) {
    this._panel = value;
  }

  connectedCallback() {
    this.renderLoading();
    this.load();
  }

  async load() {
    if (!this._hass || this._loading) return;
    this._loading = true;
    try {
      this._data = await this._hass.callWS({ type: "atmosfera_echo_hub/tiles/get" });
      this._entryId = this._entryId || this._data.entries[0]?.entry_id || "";
      this._loaded = true;
      this.render();
    } catch (error) {
      this.renderError(error);
    } finally {
      this._loading = false;
    }
  }

  escape(value) {
    return String(value ?? "")
      .replaceAll("&", "&amp;")
      .replaceAll('"', "&quot;")
      .replaceAll("<", "&lt;")
      .replaceAll(">", "&gt;");
  }

  renderLoading() {
    this.shadowRoot.innerHTML = `<style>${this.styles()}</style><main><p>Loading Atmosfera cards...</p></main>`;
  }

  renderError(error) {
    const message = this.errorText(error);
    this.shadowRoot.innerHTML = `<style>${this.styles()}</style><main><h1>Atmosfera</h1><p class="error">${this.escape(message || "Unknown panel error")}</p></main>`;
  }

  errorText(error) {
    const seen = new Set();
    const visit = (value) => {
      if (typeof value === "string" && value) return value;
      if (value === null || value === undefined || typeof value !== "object") return "";
      if (seen.has(value)) return "";
      seen.add(value);
      for (const key of ["message", "code", "error", "body"]) {
        const text = visit(value[key]);
        if (text) return text;
      }
      try {
        return JSON.stringify(value);
      } catch (_ignored) {
        return "Unknown panel error";
      }
    };
    return visit(error);
  }

  entityOptions() {
    const domains = new Set(this._data.domains);
    return Object.values(this._hass.states)
      .filter((state) => domains.has(state.entity_id.split(".")[0]))
      .sort((a, b) => {
        const aName = a.attributes.friendly_name || a.entity_id;
        const bName = b.attributes.friendly_name || b.entity_id;
        return aName.localeCompare(bName);
      })
      .map((state) => {
        const name = state.attributes.friendly_name || state.entity_id;
        return `<option value="${this.escape(state.entity_id)}">${this.escape(name)}</option>`;
      })
      .join("");
  }

  render() {
    const entry = this._data.entries.find((item) => item.entry_id === this._entryId);
    if (!entry) {
      this.shadowRoot.innerHTML = `<style>${this.styles()}</style><main><h1>Atmosfera</h1><p>No configured display was found.</p></main>`;
      return;
    }
    const entries = this._data.entries
      .map((item) => `<option value="${this.escape(item.entry_id)}" ${item.entry_id === this._entryId ? "selected" : ""}>${this.escape(item.title)}</option>`)
      .join("");
    const iconOptions = (selected) => this._data.icons
      .map((icon) => `<option ${icon === selected ? "selected" : ""}>${this.escape(icon)}</option>`)
      .join("");
    const paletteOptions = (selected) => this._data.palettes
      .map((palette) => `<option ${palette === selected ? "selected" : ""}>${this.escape(palette)}</option>`)
      .join("");
    const cards = entry.cards
      .map((card) => `
        <section class="card" data-slot="${card.slot}">
          <header><span>Slot ${card.slot + 1}</span><label class="visible"><input name="visible" type="checkbox" ${card.visible ? "checked" : ""}> Visible</label></header>
          <label>Entity<input name="entity_id" list="ha-entities" value="${this.escape(card.entity_id)}" placeholder="light.living_room"></label>
          <div class="columns">
            <label>Title<input name="title" value="${this.escape(card.title)}" maxlength="40"></label>
            <label>Service<input name="service" value="${this.escape(card.service)}" placeholder="Optional domain.service"></label>
          </div>
          <div class="columns">
            <label>Icon<select name="icon">${iconOptions(card.icon)}</select></label>
            <label>Palette<select name="palette">${paletteOptions(card.palette)}</select></label>
          </div>
        </section>`)
      .join("");
    this.shadowRoot.innerHTML = `
      <style>${this.styles()}</style>
      <main>
        <div class="title-row"><div><h1>Atmosfera cards</h1><p>Fixed LVGL surfaces, live Home Assistant state.</p></div><button id="save">Save</button></div>
        <label class="device">Display<select id="entry">${entries}</select></label>
        <datalist id="ha-entities">${this.entityOptions()}</datalist>
        <div class="grid">${cards}</div>
        <div id="status" role="status"></div>
      </main>`;
    this.shadowRoot.getElementById("entry").addEventListener("change", (event) => {
      this._entryId = event.target.value;
      this.render();
    });
    this.shadowRoot.getElementById("save").addEventListener("click", () => this.save());
  }

  async save() {
    const status = this.shadowRoot.getElementById("status");
    const button = this.shadowRoot.getElementById("save");
    button.disabled = true;
    status.textContent = "Saving...";
    const cards = [...this.shadowRoot.querySelectorAll(".card")].map((row) => ({
      slot: Number(row.dataset.slot),
      entity_id: row.querySelector('[name="entity_id"]').value.trim(),
      title: row.querySelector('[name="title"]').value.trim(),
      service: row.querySelector('[name="service"]').value.trim(),
      icon: row.querySelector('[name="icon"]').value,
      palette: row.querySelector('[name="palette"]').value,
      visible: row.querySelector('[name="visible"]').checked,
    }));
    try {
      const result = await this._hass.callWS({
        type: "atmosfera_echo_hub/tiles/save",
        entry_id: this._entryId,
        cards,
      });
      const entry = this._data.entries.find((item) => item.entry_id === this._entryId);
      entry.cards = result.cards;
      status.textContent = "Saved. The display will refresh changed cards.";
    } catch (error) {
      status.textContent = `Save failed: ${this.errorText(error)}`;
      status.className = "error";
    } finally {
      button.disabled = false;
    }
  }

  styles() {
    return `
      :host { color: var(--primary-text-color); font-family: var(--paper-font-body1_-_font-family, sans-serif); }
      main { box-sizing: border-box; max-width: 1180px; margin: 0 auto; padding: 28px 24px 64px; }
      h1 { margin: 0 0 4px; font-size: 28px; } p { margin: 0; color: var(--secondary-text-color); }
      .title-row { display: flex; align-items: center; justify-content: space-between; gap: 24px; margin-bottom: 28px; }
      button { border: 0; border-radius: 20px; padding: 11px 24px; color: #210f48; background: #e9ddff; font-weight: 700; cursor: pointer; }
      button:disabled { opacity: .55; cursor: wait; }
      label { display: grid; gap: 7px; color: var(--secondary-text-color); font-size: 13px; }
      input, select { box-sizing: border-box; width: 100%; min-height: 42px; border: 1px solid var(--divider-color); border-radius: 8px; padding: 8px 11px; color: var(--primary-text-color); background: var(--card-background-color); }
      .device { max-width: 440px; margin-bottom: 22px; }
      .grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(310px, 1fr)); gap: 14px; }
      .card { border-radius: 8px; padding: 16px; background: var(--card-background-color); box-shadow: var(--ha-card-box-shadow, none); }
      .card header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 14px; font-size: 15px; font-weight: 700; }
      .visible { display: flex; grid-template-columns: auto 1fr; align-items: center; gap: 7px; font-weight: 400; }
      .visible input { width: 18px; min-height: 18px; }
      .columns { display: grid; grid-template-columns: 1fr 1fr; gap: 12px; margin-top: 12px; }
      #status { min-height: 24px; margin-top: 18px; color: var(--success-color, #4caf50); }
      .error { color: var(--error-color, #db4437) !important; }
      @media (max-width: 620px) { main { padding: 20px 12px 48px; } .columns { grid-template-columns: 1fr; } }
    `;
  }
}

customElements.define("atmosfera-tile-editor", AtmosferaTileEditor);
