# web_asvetec

Módulo Odoo 16 que implementa el sitio web completo de **ASVETEC** (RyS ASVETEC Ltda.), empresa de soluciones industriales en el norte de Chile.

---

## Características

### Sitio web principal
- Página de inicio en `/asvetec` con layout propio y área editable por el editor de Odoo.
- Header y footer personalizados con la identidad visual de ASVETEC.
- Overrides de la tienda (`/shop`) de Odoo para adaptar el diseño al estilo corporativo.

### Snippets reutilizables (8 bloques)
Cada snippet es autocontenido — consulta datos directamente desde la base de datos sin necesidad de contexto adicional desde el controlador.

| Snippet | Descripción |
|---|---|
| `s_asv_hero` | Banner principal con imagen de fondo, título, subtítulo y CTA |
| `s_asv_trust_bar` | Barra de confianza con íconos y cifras clave de la empresa |
| `s_asv_categories` | Grid de categorías de productos con íconos SVG por categoría |
| `s_asv_featured_products` | Carrusel/grid de productos "En stock" con filtro por categoría, precio y botón de cotizar |
| `s_asv_about` | Sección "Quiénes somos" con descripción e imagen |
| `s_asv_brands` | Carrusel automático de marcas representadas |
| `s_asv_services` | Tarjetas de servicios ofrecidos |
| `s_asv_contact` | Formulario de contacto/cotización integrado con CRM |

### Formulario de cotización
- Ruta `POST /asvetec/cotizar` con protección CSRF.
- Crea automáticamente un lead en el módulo **CRM** (`crm.lead`) con los datos del cliente.
- Fallback por email si la creación del lead falla.
- Página de confirmación `asv_cotizar_ok` tras el envío exitoso.

### Modelo extendido — Íconos SVG por categoría
- Extiende `product.public.category` con el campo `asv_svg_icon` (Text).
- Permite asignar un SVG inline a cada categoría de producto.
- Los snippets usan el ícono como fallback cuando un producto no tiene imagen.

### Hook de post-instalación
- Genera automáticamente imágenes PNG de ícono para cada categoría usando **Pillow**, con fondo azul claro y círculo de color de acento personalizado por categoría.

### Datos de referencia incluidos
- 8 categorías de producto preconfiguradas con íconos SVG:
  Limpieza Industrial, Equipos de Taller, Generadores, Arriendo, Hogar y Jardín, Herramientas, Accesorios, Insumos.
- Registro del sitio web ASVETEC (`website.website`).

### Assets frontend
- Sistema de tokens CSS (`asv_tokens.scss`) con variables de color, tipografía y espaciado.
- SCSS modular por snippet y componente de layout.
- JavaScript para: slider del hero, carrusel de marcas y filtro/paginación de productos destacados.

---

## Dependencias

- `website`
- `website_sale`

## Instalación

```bash
# Desde el directorio raíz de Odoo:
python odoo-bin --config=odoo.conf --database=<db> --init=web_asvetec
```

## Actualización

```bash
python odoo-bin --config=odoo.conf --database=<db> --update=web_asvetec
```

---

## Versión

`16.0.1.3.0` — Compatible con **Odoo 16 Community / Enterprise**

## Licencia

LGPL-3 — ver [LICENSE](https://www.gnu.org/licenses/lgpl-3.0.html)

## Autor

**Method** — desarrollo a medida para ASVETEC
