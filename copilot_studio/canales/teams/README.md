# Integración con Microsoft Teams

Canal principal del personal administrativo de Nutriavícola. Es el despliegue donde la
identidad de Entra ID fluye de forma automática, por lo que la validación de identidad del
certificado opera al 100%.

## Qué contiene esta carpeta

- `manifest.json`: manifiesto de la app de Teams (formato oficial v1.16). Es el paquete que
  Copilot Studio genera al publicar el agente en Teams. Junto con los íconos `color.png`
  (192x192) y `outline.png` (32x32) forma el `.zip` que se sube a la organización.

## Cómo se integró (pasos realizados)

1. En Copilot Studio: **Settings → Security → Authentication → "Authenticate with Microsoft"**
   y se activó **"Require users to sign in"** (Entra ID).
2. Se **publicó** el agente (botón *Publish*).
3. **Channels → Microsoft Teams → Add channel → Turn on Teams**.
4. Se generó el paquete de la app (`manifest.json` + íconos) y se envió a
   **"Submit for admin approval"** para publicarlo en el catálogo de apps de la organización.
5. Los colaboradores instalan "Asistente Nutriavícola" desde la tienda de apps de Teams.

## Cómo verificar

1. Abrir Microsoft Teams con una cuenta del tenant de Nutriavícola.
2. Buscar la app **"Asistente Nutriavícola"** en *Apps* y abrir el chat.
3. Escribir: `necesito mi certificado laboral`.
4. Verificar que la identidad llega autenticada (el agente saluda con el nombre del usuario
   y solo entrega el certificado a su titular).

## Datos del agente

- **Bot ID:** `2e847862-2764-f111-a826-000d3a106a42`
- **Nombre de esquema:** `crf4b_AsistenteNutriavicola`
- **Entorno:** `Default-693cbea0-4ef9-4254-8977-76e05cb5f556`
