import re
import sys

from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import (
    QApplication,
    QWidget,
    QFrame,
    QLabel,
    QLineEdit,
    QPushButton,
    QHBoxLayout,
    QVBoxLayout,
)


class RecoveryEmailWindow(QWidget):
    # Connect these signals to your application's navigation and backend.
    recovery_requested = Signal(str)
    cancel_requested = Signal()
    create_account_requested = Signal()

    def __init__(self):
        super().__init__()

        self.setWindowTitle("Recovery Email | ReConnect")
        self.setObjectName("recoveryEmailWindow")
        self.resize(1030, 580)
        self.setMinimumSize(1030, 580)

        # Main layout: branding on the left, recovery form on the right.
        main_layout = QHBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        branding = QFrame()
        branding.setObjectName("branding")

        right_panel = QFrame()
        right_panel.setObjectName("rightPanel")

        main_layout.addWidget(branding, 474)
        main_layout.addWidget(right_panel, 526)

        # Branding panel
        branding_layout = QVBoxLayout(branding)
        branding_layout.setContentsMargins(55, 82, 40, 17)
        branding_layout.setSpacing(0)

        brand_title = QLabel("ReConnect")
        brand_title.setObjectName("brandTitle")

        tagline = QLabel("Stay connected. Never let a\nrelationship fall through the cracks.")
        tagline.setObjectName("tagline")

        organization = QLabel("Tarbiya Institute")
        organization.setObjectName("organization")

        branding_layout.addWidget(brand_title)
        branding_layout.addWidget(tagline)
        branding_layout.addStretch()
        branding_layout.addWidget(organization)

        # Center the recovery card inside the right panel.
        right_layout = QVBoxLayout(right_panel)
        right_layout.setContentsMargins(35, 35, 35, 35)

        card = QFrame()
        card.setObjectName("loginCard")
        card.setFixedSize(377, 461)

        right_layout.addWidget(card, alignment=Qt.AlignmentFlag.AlignCenter)

        card_layout = QVBoxLayout(card)
        card_layout.setContentsMargins(25, 33, 33, 22)
        card_layout.setSpacing(0)

        heading = QLabel("Recovery Email")
        heading.setObjectName("heading")
        heading.setFixedHeight(43)

        subtitle = QLabel("Please enter the email that is\nlinked to your account.")
        subtitle.setObjectName("subtitle")
        subtitle.setContentsMargins(8, 0, 0, 0)
        subtitle.setFixedHeight(44)

        card_layout.addWidget(heading)
        card_layout.addSpacing(7)
        card_layout.addWidget(subtitle)
        card_layout.addSpacing(43)

        # Email field
        email_label = QLabel("Email Address")
        email_label.setObjectName("fieldLabel")
        email_label.setContentsMargins(8, 0, 0, 0)
        email_label.setFixedHeight(18)