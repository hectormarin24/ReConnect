
from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QFrame,
    QLabel,
    QVBoxLayout,
    QHBoxLayout,
    QSizePolicy,
)


class MessageCard(QFrame):
    def __init__(self, message):
        super().__init__()

        self.setObjectName("messageCard")
        self.setProperty("unread", message["unread"])
        self.setFrameShape(QFrame.Shape.NoFrame)

        self.setSizePolicy(
            QSizePolicy.Policy.Expanding,
            QSizePolicy.Policy.Minimum,
        )

        card_layout = QVBoxLayout(self)
        card_layout.setContentsMargins(12, 10, 12, 10)
        card_layout.setSpacing(5)

        # Sender and metadata share the top row.
        top_row = QHBoxLayout()
        top_row.setSpacing(10)

        sender_label = QLabel(message["sender"])
        sender_label.setObjectName("senderLabel")
        sender_label.setProperty(
            "unread",
            message["unread"],
        )

        metadata_label = QLabel(
            f'{message["channel"]}  •  {message["timestamp"]}'
        )
        metadata_label.setObjectName("messageMetadata")
        metadata_label.setAlignment(
            Qt.AlignmentFlag.AlignRight
            | Qt.AlignmentFlag.AlignVCenter
        )

        top_row.addWidget(sender_label)
        top_row.addStretch()
        top_row.addWidget(metadata_label)

        # Message preview goes underneath.
        preview_label = QLabel(message["preview"])
        preview_label.setObjectName("messagePreview")
        preview_label.setWordWrap(True)

        card_layout.addLayout(top_row)
        card_layout.addWidget(preview_label)
