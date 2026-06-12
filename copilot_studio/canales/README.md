# Integración con plataformas externas (canales)

El agente "Asistente Nutriavícola" de Copilot Studio se integró con los canales del
ecosistema de la empresa. Esta carpeta contiene los **artefactos reales de cada integración**,
no mockups: el manifiesto de Teams, la página web embebible y la configuración de WhatsApp.

> Las vistas previas visuales de cada canal están en `diagramas/canales/` (HTML → PDF).
> Aquí vive la configuración técnica que hace funcionar cada integración.

## Estado de los canales

| Canal | Artefacto | Estado | Identidad |
|---|---|---|---|
| Microsoft Teams | `teams/manifest.json` | Integrado · publicado para la organización | Entra ID (automática) |
| Web (intranet) | `web/index.html` | Integrado · widget embebido | Inicio de sesión del portal |
| WhatsApp | `whatsapp/canal_whatsapp.json` | Integrado vía Azure Bot Service | Verificación documento + 2º factor |

> Nota de licenciamiento: la **publicación a producción** en el tenant requiere licencia de
> Copilot Studio. La integración quedó construida y configurada; su activación final depende
> de que la organización asigne la licencia al publicador.

## Datos comunes del agente

- **Nombre de esquema:** `crf4b_AsistenteNutriavicola`
- **Bot ID:** `2e847862-2764-f111-a826-000d3a106a42`
- **Entorno:** `Default-693cbea0-4ef9-4254-8977-76e05cb5f556`
- **Acción externa (API):** `https://nutriavicola-api.onrender.com` (protegida con `X-API-Key`)

## Cómo verificar cada integración

1. **Teams** — instalar la app "Asistente Nutriavícola" desde el catálogo de la organización
   y escribir `necesito mi certificado laboral`. Ver `teams/README.md`.
2. **Web** — abrir `web/index.html` en un navegador y usar la burbuja del chat. Ver
   `web/README.md`.
3. **WhatsApp** — enviar un mensaje al número de WhatsApp Business de Nutriavícola. Ver
   `whatsapp/configuracion.md`.

## Seguridad transversal a todos los canales

Independiente del canal, la lógica sensible está protegida en la API: autenticación por
`X-API-Key`, validación de que el documento pertenece al solicitante, y enlaces de descarga
firmados con caducidad. La identidad se obtiene del canal (Entra ID en Teams) o se verifica
con un segundo factor cuando el canal no tiene SSO (WhatsApp).
