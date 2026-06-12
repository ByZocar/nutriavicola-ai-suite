# Integración Web (intranet)

Página del Portal del Colaborador con el Asistente Nutriavícola embebido como widget
conversacional (canal "Custom website" de Copilot Studio).

## Qué contiene esta carpeta

- `index.html`: página web real y autocontenida que incrusta el agente publicado mediante un
  `<iframe>`. Es la integración tal como va en la intranet de Nutriavícola.

## Cómo se integró (pasos realizados)

1. En Copilot Studio: **Channels → Custom website**.
2. Se copió el código de inserción (`<iframe>`) que apunta al agente publicado
   `crf4b_AsistenteNutriavicola` del entorno de Nutriavícola.
3. Se incrustó en el portal con un lanzador flotante (burbuja inferior derecha), igual que un
   widget de soporte.

## Cómo verificar

1. Abrir `index.html` en un navegador (o publicarlo en la intranet).
2. Hacer clic en la burbuja inferior derecha: se abre el chat del agente publicado.
3. Probar: `¿cuántos tickets críticos hay?`.

> Para el certificado (dato sensible) la intranet debe exigir inicio de sesión corporativo;
> la consulta de tickets es información operativa no personal y puede ir en el portal general.

## URL del canal

```
https://copilotstudio.microsoft.com/environments/Default-693cbea0-4ef9-4254-8977-76e05cb5f556/bots/crf4b_AsistenteNutriavicola/webchat?__version__=2
```
