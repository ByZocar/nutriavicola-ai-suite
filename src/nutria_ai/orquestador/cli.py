"""
Orquestador por consola (chat demostrativo).

Es la prueba viva del Reto 3: un solo punto de entrada que saluda, reconoce la
intencion y enruta al sub-flujo correcto (Certificados RRHH o Soporte TI). Consume
directamente los servicios del extra para funcionar sin depender de la API levantada.

Ejecucion:
    PYTHONPATH=src python -m nutria_ai.orquestador.cli
"""

from __future__ import annotations

from nutria_ai.certificados import generador
from nutria_ai.clasificador import modelo
from nutria_ai.datos import ingesta, limpieza
from nutria_ai.orquestador.enrutador import detectar_intencion
from nutria_ai.tickets import exportador, filtrado

SALUDO = (
    "Hola, soy el asistente interno de Nutriavicola. "
    "Puedo ayudarte con tu certificado laboral o con el estado de tus tickets de soporte. "
    "Cuentame, ¿en que necesitas ayuda? (escribe 'salir' para terminar)"
)


def _flujo_certificado() -> str:
    """Sub-flujo RRHH: pide y valida documento + area, y genera el certificado."""
    documento = input("Agente RRHH > Indicame tu numero de documento: ").strip()
    area = input("Agente RRHH > Indicame tu area: ").strip()
    try:
        ruta = generador.generar_certificado_pdf(documento, area)
        empleado = generador.buscar_empleado(documento, area)
        return (
            f"Listo {empleado['Nombre_Completo']}, genere tu certificado laboral. "
            f"Lo encuentras en: {ruta}"
        )
    except generador.EmpleadoNoEncontrado:
        # Fallback / transferencia a humano cuando la validacion falla
        return (
            "No pude validar tus datos en el sistema. Te transfiero con un agente "
            "humano de Gestion Humana para que revise tu caso."
        )


def _flujo_tickets() -> str:
    """Sub-flujo TI: cuenta los tickets criticos y responde el mensaje del reto."""
    crudo = ingesta.cargar_tickets()
    limpio = limpieza.limpiar_tickets(crudo)
    criticos = filtrado.filtrar_criticos(limpio)
    total = exportador.construir_payload(criticos)["total_criticos"]
    return f"Actualmente tienes {total} tickets criticos pendientes por resolver."


def atender(mensaje: str) -> str:
    """
    Enruta el mensaje del usuario al sub-flujo correcto segun la intencion.

    Si la intencion es desconocida, responde con un fallback que reorienta al usuario.
    """
    resultado = detectar_intencion(mensaje)
    if resultado.intencion == "certificado":
        return _flujo_certificado()
    if resultado.intencion == "tickets":
        return _flujo_tickets()
    return (
        "No estoy seguro de haberte entendido. Puedo ayudarte con tu "
        "certificado laboral o con tus tickets de soporte TI."
    )


def main() -> None:
    """Bucle de conversacion del orquestador."""
    print(SALUDO)
    while True:
        try:
            mensaje = input("Tu > ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\nHasta luego.")
            break
        if mensaje.lower() in {"salir", "exit", "quit"}:
            print("Hasta luego.")
            break
        print("Asistente >", atender(mensaje))


if __name__ == "__main__":
    main()
