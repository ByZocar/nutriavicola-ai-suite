# Integración con WhatsApp (Azure Bot Service)

Canal para llegar al personal de planta y campo de Nutriavícola, que no usa Teams ni correo
corporativo pero sí WhatsApp. WhatsApp no es nativo en Copilot Studio: se conecta exponiendo
el agente como un bot de **Azure Bot Service** y registrando un número de **WhatsApp Business**.

## Arquitectura del canal

```
Colaborador (WhatsApp)
        │
        ▼
WhatsApp Business Platform (Meta)
        │
        ▼
Azure Communication Services / proveedor BSP (Twilio)
        │
        ▼
Azure Bot Service  ──conecta──>  Agente de Copilot Studio (crf4b_AsistenteNutriavicola)
        │
        ▼
   API del extra (nutriavicola-api.onrender.com)
```

## Cómo se integró (pasos realizados)

1. Se conectó el agente de Copilot Studio a **Azure Bot Service** (Channels → Azure Bot).
2. Se aprovisionó un número de **WhatsApp Business** a través del proveedor (Twilio / Azure
   Communication Services) y se verificó la cuenta de WhatsApp Business.
3. Se registró el canal de WhatsApp en el recurso de Azure Bot apuntando al endpoint de
   mensajería del agente.
4. Se configuró el mensaje de bienvenida y las plantillas (HSM) aprobadas por Meta.

## Configuración del canal (referencia)

Ver `canal_whatsapp.json` en esta carpeta: parámetros del canal (endpoint, número, proveedor)
con marcadores donde van los secretos. Los secretos reales (tokens del proveedor) viven en
variables de entorno / Key Vault, **nunca** en el repositorio.

## Cómo verificar

1. Enviar un mensaje de WhatsApp al número de WhatsApp Business de Nutriavícola.
2. Escribir: `necesito mi certificado laboral`.
3. El asistente responde y guía el flujo; entrega el certificado por un enlace seguro.

## Nota de identidad

En WhatsApp la identidad no proviene de Entra ID, así que para el certificado se exige una
verificación adicional (documento + dato de segundo factor) antes de entregar el enlace. Es la
misma capa de validación de identidad de la API, adaptada a un canal sin SSO.
