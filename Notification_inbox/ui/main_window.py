
from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QMainWindow,
    QWidget,
    QFrame,
    QLabel,
    QPushButton,
    QLineEdit,
    QScrollArea,
    QVBoxLayout,
    QHBoxLayout,
)

from data.sample_messages import SAMPLE_MESSAGES
from ui.message_card import MessageCard


class NotificationInbox(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Notification Inbox")
        self.resize(1100, 700)
        self.setMinimumSize(850, 550)

        # Load the sample message data.
        self.messages = [
            message.copy() for message in SAMPLE_MESSAGES
        ]

        self.selected_channel = "All"
        self.nav_buttons = {}

        self.setStyleSheet("""
            QMainWindow {
                background-color: #FFFFFF;
            }

            QFrame#sidebar {
                background-color: #F0F0F0;
                border: none;
            }

            QLabel#appTitle {
                color: #111111;
                font-size: 20px;
                font-weight: bold;
            }

            QPushButton#navButton {
                background-color: transparent;
                color: #555555;
                border: none;
                border-radius: 7px;
                text-align: left;
                padding: 10px 12px;
                font-size: 14px;
            }

            QPushButton#navButton:hover {
                background-color: #E5E7EB;
            }

            QPushButton#navButton[selected="true"] {
                background-color: #D9E8FF;
                color: #111111;
                font-weight: bold;
            }

            QLabel#pageTitle {
                color: #111111;
                font-size: 26px;
                font-weight: bold;
            }

            QLineEdit#searchInput {
                background-color: #FFFFFF;
                color: #111111;
                border: 1px solid #D1D5DB;
                border-radius: 8px;
                padding: 8px 12px;
                font-size: 14px;
            }

            QLineEdit#searchInput:focus {
                border: 1px solid #6495ED;
            }

            QFrame#messageCard {
                background-color: #FFFFFF;
                border: 1px solid #D1D5DB;
                border-radius: 9px;
            }

            QFrame#messageCard[unread="true"] {
                background-color: #EAF2FF;
            }

            QLabel#senderLabel {
                color: #111111;
                font-size: 14px;
                font-weight: bold;
                background-color: transparent;
                border: none;
            }

            QLabel#senderLabel[unread="false"] {
                font-weight: normal;
            }

            QLabel#messageMetadata {
                color: #777777;
                font-size: 11px;
                background-color: transparent;
                border: none;
            }

            QLabel#messagePreview {
                color: #111111;
                font-size: 12px;
                background-color: transparent;
                border: none;
            }

            QScrollArea {
                background-color: transparent;
                border: none;
            }

            QWidget#messageList {
                background-color: transparent;
            }

            QLabel#emptyLabel {
                color: #777777;
                font-size: 14px;
                background-color: transparent;
            }
        """)

        self.create_ui()
        self.show_messages()

    # Build the main interface.
    def create_ui(self):
        root = QWidget()
        self.setCentralWidget(root)

        root_layout = QHBoxLayout(root)
        root_layout.setContentsMargins(0, 0, 0, 0)
        root_layout.setSpacing(0)

        self.create_sidebar(root_layout)
        self.create_inbox(root_layout)

    # Create the sidebar and channel filters.
    def create_sidebar(self, parent_layout):
        sidebar = QFrame()
        sidebar.setObjectName("sidebar")
        sidebar.setFixedWidth(200)

        sidebar_layout = QVBoxLayout(sidebar)
        sidebar_layout.setContentsMargins(15, 25, 15, 15)
        sidebar_layout.setSpacing(5)

        title = QLabel("Notification Inbox")
        title.setObjectName("appTitle")
        title.setWordWrap(True)

        sidebar_layout.addWidget(title)
        sidebar_layout.addSpacing(20)

        for channel in ["All", "Email", "WhatsApp", "SMS"]:
            label = "Inbox" if channel == "All" else channel

            button = QPushButton(label)
            button.setObjectName("navButton")
            button.setCursor(Qt.CursorShape.PointingHandCursor)
            button.setMinimumHeight(40)

            button.setProperty(
                "selected",
                channel == self.selected_channel,
            )

            button.clicked.connect(
                lambda checked=False, c=channel:
                self.filter_messages(c)
            )

            sidebar_layout.addWidget(button)
            self.nav_buttons[channel] = button

        sidebar_layout.addStretch()
        parent_layout.addWidget(sidebar)

    # Create the main inbox area.
    def create_inbox(self, parent_layout):
        content = QWidget()
        content_layout = QVBoxLayout(content)

        content_layout.setContentsMargins(25, 25, 25, 25)
        content_layout.setSpacing(0)

        title = QLabel("Messages")
        title.setObjectName("pageTitle")

        content_layout.addWidget(title)
        content_layout.addSpacing(15)

        self.search = QLineEdit()
        self.search.setObjectName("searchInput")
        self.search.setPlaceholderText("Search messages...")
        self.search.setMinimumHeight(38)

        self.search.textChanged.connect(self.show_messages)

        content_layout.addWidget(self.search)
        content_layout.addSpacing(15)

        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setHorizontalScrollBarPolicy(
            Qt.ScrollBarPolicy.ScrollBarAlwaysOff
        )

        self.message_frame = QWidget()
        self.message_frame.setObjectName("messageList")

        self.message_layout = QVBoxLayout(self.message_frame)
        self.message_layout.setContentsMargins(0, 0, 5, 0)
        self.message_layout.setSpacing(5)
        self.message_layout.setAlignment(
            Qt.AlignmentFlag.AlignTop
        )

        self.scroll_area.setWidget(self.message_frame)

        content_layout.addWidget(self.scroll_area, 1)
        parent_layout.addWidget(content, 1)

    # Filter messages by channel.
    def filter_messages(self, channel):
        self.selected_channel = channel

        for name, button in self.nav_buttons.items():
            button.setProperty(
                "selected",
                name == self.selected_channel,
            )

            # Refresh the style after changing the property.
            button.style().unpolish(button)
            button.style().polish(button)
            button.update()

        self.show_messages()

    # Search and display matching messages.
    def show_messages(self, text=None):
        # Remove the previously displayed widgets.
        while self.message_layout.count():
            item = self.message_layout.takeAt(0)
            widget = item.widget()

            if widget is not None:
                widget.deleteLater()

        query = self.search.text().lower().strip()

        filtered_messages = [
            message
            for message in self.messages
            if (
                self.selected_channel == "All"
                or message["channel"] == self.selected_channel
            )
            and (
                query in message["sender"].lower()
                or query in message["preview"].lower()
                or query in message["channel"].lower()
            )
        ]

        if not filtered_messages:
            empty_label = QLabel("No messages found.")
            empty_label.setObjectName("emptyLabel")
            empty_label.setAlignment(
                Qt.AlignmentFlag.AlignCenter
            )

            self.message_layout.addWidget(empty_label)
            return

        for message in filtered_messages:
            card = MessageCard(message)
            self.message_layout.addWidget(card)

        self.message_layout.addStretch()
