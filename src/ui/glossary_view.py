"""Glossary with key terms used in the application."""
from __future__ import annotations

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QLabel, QScrollArea, QVBoxLayout, QWidget


def _build_glossary_html() -> str:
    definitions = [
        (
            "Stake",
            "Cantidad que se arriesga en la apuesta principal. En BetLedger se "
            "bloquea de la cuenta de origen cuando el origen es en efectivo.",
        ),
        (
            "Cuotas (odds)",
            "Multiplicadores ofrecidos por las casas de apuestas. La cuota A se "
            "aplica a la apuesta de origen y la cuota B a la cobertura.",
        ),
        (
            "Cobertura",
            "Importe y selección que se coloca en la casa de la contra-apuesta "
            "para asegurar el resultado. El sistema calcula automáticamente la "
            "cantidad óptima (stake B) y la exposición necesaria.",
        ),
        (
            "Exposición B",
            "Fondos que quedan bloqueados en la cuenta de cobertura al crear una "
            "operación. Corresponde al riesgo máximo asumido en la contra-apuesta.",
        ),
        (
            "Comisión",
            "Porcentaje que la casa de intercambio descuenta de los beneficios de "
            "la contra-apuesta.",
        ),
        (
            "Modos",
            "\n<ul>\n"
            "<li><b>Calificación</b>: operación destinada a liberar un bono, suele "
            "asumir una pequeña pérdida controlada.</li>\n"
            "<li><b>Crédito no retorno</b>: se busca retener beneficios en la "
            "cobertura; el stake de origen puede estar financiado por la casa.</li>\n"
            "</ul>\n",
        ),
        (
            "Origen del stake",
            "Indica de dónde procede el stake de la apuesta A. <b>Efectivo</b> "
            "bloquea fondos de la cuenta de origen; <b>Crédito</b> supone que la "
            "casa lo financia y no requiere bloqueo inicial.",
        ),
        (
            "Resultado de la operación",
            "Estado final registrado tras el evento: Gana A, Gana B o Anulada. "
            "Determina cómo se liberan y registran los movimientos en las cuentas.",
        ),
        (
            "Rating",
            "Indicador del valor de la operación calculado por la herramienta de "
            "comparación y la calculadora.",
        ),
        (
            "Notas",
            "Campo libre para anotar información adicional relevante de la "
            "operación.",
        ),
    ]

    entries = "".join(
        f"<dt><b>{term}</b></dt><dd>{definition}</dd>" for term, definition in definitions
    )
    return (
        "<h1>Glosario</h1>"
        "<p>Este glosario resume los conceptos clave utilizados en BetLedger para "
        "gestionar y hacer seguimiento de las operaciones de apuestas.</p>"
        f"<dl>{entries}</dl>"
    )


class GlossaryView(QWidget):
    """Simple scrollable view with glossary definitions."""

    def __init__(self) -> None:
        super().__init__()
        layout = QVBoxLayout(self)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)

        container = QWidget()
        container_layout = QVBoxLayout(container)

        label = QLabel()
        label.setTextFormat(Qt.RichText)
        label.setWordWrap(True)
        label.setText(_build_glossary_html())

        container_layout.addWidget(label)
        container_layout.addStretch(1)

        scroll.setWidget(container)
        layout.addWidget(scroll)

        self.setLayout(layout)
