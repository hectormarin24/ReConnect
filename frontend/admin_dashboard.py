import argparse
import json
import sys
from functools import partial

from PySide6.QtCore import QCoreApplication, Qt
from PySide6.QtGui import QColor, QFont
from PySide6.QtNetwork import QLocalServer, QLocalSocket
from PySide6.QtWidgets import (
    QApplication,
    QButtonGroup,
    QFrame,
    QGraphicsBlurEffect,
    QGraphicsDropShadowEffect,
    QHBoxLayout,
    QLabel,
    QMainWindow,
    QPushButton,
    QSizePolicy,
    QStackedWidget,
    QVBoxLayout,
    QWidget,
)

from popups.contact_detected import (
    ContactDetectedPopup,
    ContactNotification,
    MinimizedContactNotification,
)

NOTIFICATION_SERVER_NAME = "reconnect-admin-dashboard"


STYLESHEET = """
QWidget {
    background-color: white;
    color: #111111;
    font-family: "Segoe UI";
    font-size: 13px;
}

QFrame#sidebar {
    background-color: #3c467e;
    border: none;
}

QWidget#navContainer {
    background: transparent;
}

QFrame#brandHeader {
    background-color: #101943;
    border-bottom-left-radius: 12px;
    border-bottom-right-radius: 12px;
}

QLabel#brand {
    background: transparent;
    color: white;
    font-weight: 700;
}

QPushButton#navButton {
    background: transparent;
    color: white;
    border: none;
    border-radius: 6px;
    padding: 0;
    text-align: left;
    padding-left: 18px;
}

QPushButton#navButton:hover {
    background-color: #4a558f;
}

QPushButton#navButton:checked {
    background-color: #6074b0;
}

QPushButton#navButton:pressed {
    background-color: #303a70;
}

QPushButton#navButton:focus {
    border: 1px solid #b7bee6;
}

QLabel#pageTitle {
    font-size: 26px;
    font-weight: 700;
}

QLabel#sectionTitle {
    font-size: 24px;
    font-weight: 700;
}

QFrame#card, QFrame#approvalsPanel {
    background-color: white;
    border: 1px solid #eeeeee;
}

QLabel#cardTitle {
    font-size: 16px;
}

QLabel#cardValue {
    color: #00852c;
    font-size: 26px;
    font-weight: 700;
}

QLabel#tableHeader {
    font-size: 11px;
}

QLabel#tableCell {
    font-size: 11px;
}

QLabel#userName {
    font-size: 11px;
    font-weight: 600;
}

QPushButton#approveButton {
    background-color: #008900;
    color: white;
    border: 1px solid #dddddd;
    font-size: 16px;
    font-weight: 600;
}

QPushButton#approveButton:hover {
    background-color: #007000;
}

QPushButton#rejectButton {
    background-color: white;
    color: #d50000;
    border: 1px solid #e4e4e4;
    font-size: 16px;
}

QPushButton#rejectButton:hover {
    background-color: #fff0f0;
}

QPushButton#approveButton:focus,
QPushButton#rejectButton:focus {
    border: 2px solid #3c467e;
}

QLabel#feedback {
    color: #596174;
    font-size: 12px;
}
"""


def create_label(text, object_name):
    label = QLabel(text)
    label.setObjectName(object_name)
    return label


def add_shadow(widget):
    shadow = QGraphicsDropShadowEffect(widget)
    shadow.setBlurRadius(3)
    shadow.setOffset(0, 2)
    shadow.setColor(QColor(0, 0, 0, 90))
    widget.setGraphicsEffect(shadow)


class StatCard(QFrame):
    def __init__(self, title, value):
        super().__init__()
        self.setObjectName("card")
        self.setMinimumHeight(72)
        self.setSizePolicy(
            QSizePolicy.Policy.Expanding,
            QSizePolicy.Policy.Preferred,
        )

        layout = QVBoxLayout(self)
        layout.setContentsMargins(26, 10, 20, 10)
        layout.setSpacing(10)

        layout.addWidget(create_label(title, "cardTitle"))

        self.value_label = create_label(str(value), "cardValue")
        layout.addWidget(self.value_label)

        add_shadow(self)

    def set_value(self, value):
        self.value_label.setText(str(value))


class AdministrationPage(QWidget):
    def __init__(self):
        super().__init__()

        self.user_count = 6
        self.pending_users = [
            {
                "id": 1,
                "name": "Fatima Ali",
                "email": "fatima@example.org",
                "requested": "Sep 29",
            },
            {
                "id": 2,
                "name": "Omar Hasan",
                "email": "omar@example.org",
                "requested": "Sep 30",
            },
        ]

        layout = QVBoxLayout(self)
        self.page_layout = layout
        layout.setContentsMargins(42, 50, 100, 30)
        layout.setSpacing(0)

        layout.addWidget(create_label("Administration", "pageTitle"))
        layout.addSpacing(12)

        description = QLabel(
            "Manage users, approvals, archived contacts, "
            "and administrative activity"
        )
        description.setWordWrap(True)
        layout.addWidget(description)
        layout.addSpacing(23)

        cards_layout = QHBoxLayout()
        self.cards_layout = cards_layout
        cards_layout.setSpacing(34)

        self.users_card = StatCard("Users", self.user_count)
        self.pending_card = StatCard(
            "Pending Approvals", len(self.pending_users)
        )
        self.archived_card = StatCard("Archived Contacts", 0)

        cards_layout.addWidget(self.users_card, 1)
        cards_layout.addWidget(self.pending_card, 1)
        cards_layout.addWidget(self.archived_card, 1)

        layout.addLayout(cards_layout)
        layout.addSpacing(55)

        layout.addWidget(
            create_label("Pending User Approvals", "sectionTitle")
        )
        layout.addSpacing(8)

        panel = QFrame()
        panel.setObjectName("approvalsPanel")
        panel.setMinimumHeight(172)
        add_shadow(panel)

        panel_layout = QVBoxLayout(panel)
        self.panel_layout = panel_layout
        panel_layout.setContentsMargins(32, 8, 32, 22)
        panel_layout.setSpacing(0)

        header = QWidget()
        header_layout = QHBoxLayout(header)
        header_layout.setContentsMargins(0, 0, 0, 0)
        header_layout.setSpacing(12)

        header_layout.addWidget(create_label("User", "tableHeader"), 2)
        header_layout.addWidget(create_label("Email", "tableHeader"), 3)

        requested_header = create_label("Requested", "tableHeader")
        requested_header.setFixedWidth(85)
        header_layout.addWidget(requested_header)

        action_header = create_label("Action", "tableHeader")
        action_header.setFixedWidth(176)
        header_layout.addWidget(action_header)

        panel_layout.addWidget(header)

        self.rows_widget = QWidget()
        self.rows_layout = QVBoxLayout(self.rows_widget)
        self.rows_layout.setContentsMargins(0, 0, 0, 0)
        self.rows_layout.setSpacing(0)

        panel_layout.addWidget(self.rows_widget)

        self.empty_label = QLabel("No pending user approvals.")
        self.empty_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.empty_label.setMinimumHeight(100)
        panel_layout.addWidget(self.empty_label)

        panel_layout.addStretch()

        layout.addWidget(panel)

        self.feedback = create_label("", "feedback")
        layout.addSpacing(12)
        layout.addWidget(self.feedback)
        layout.addStretch()

        self.refresh_rows()

    def resizeEvent(self, event):
        width = self.width()
        horizontal_margin = max(24, min(42, round(width * 0.04)))
        right_margin = max(32, min(100, round(width * 0.1)))
        self.page_layout.setContentsMargins(
            horizontal_margin, 30, right_margin, 24
        )
        self.cards_layout.setSpacing(max(16, min(34, round(width * 0.032))))

        panel_margin = max(16, min(32, round(width * 0.032)))
        self.panel_layout.setContentsMargins(panel_margin, 8, panel_margin, 22)
        super().resizeEvent(event)

    def refresh_rows(self):
        while self.rows_layout.count():
            item = self.rows_layout.takeAt(0)
            widget = item.widget()
            if widget:
                widget.hide()
                widget.deleteLater()

        for user in self.pending_users:
            self.rows_layout.addWidget(self.create_user_row(user))

        self.empty_label.setVisible(not self.pending_users)
        self.pending_card.set_value(len(self.pending_users))

    def create_user_row(self, user):
        row = QWidget()
        row.setFixedHeight(56)

        layout = QHBoxLayout(row)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(12)

        name = create_label(user["name"], "userName")
        name.setToolTip(user["name"])
        layout.addWidget(name, 2)

        email = create_label(user["email"], "tableCell")
        email.setToolTip(user["email"])
        layout.addWidget(email, 3)

        requested = create_label(user["requested"], "tableCell")
        requested.setFixedWidth(85)
        layout.addWidget(requested)

        actions = QWidget()
        actions.setFixedWidth(176)

        actions_layout = QHBoxLayout(actions)
        actions_layout.setContentsMargins(0, 0, 0, 0)
        actions_layout.setSpacing(4)

        approve = QPushButton("Approve")
        approve.setObjectName("approveButton")
        approve.setFixedSize(86, 28)
        approve.setCursor(Qt.CursorShape.PointingHandCursor)
        approve.setAccessibleName(f"Approve {user['name']}")
        approve.clicked.connect(
            lambda checked=False, uid=user["id"]:
            self.resolve_user(uid, approved=True)
        )

        reject = QPushButton("Reject")
        reject.setObjectName("rejectButton")
        reject.setFixedSize(86, 28)
        reject.setCursor(Qt.CursorShape.PointingHandCursor)
        reject.setAccessibleName(f"Reject {user['name']}")
        reject.clicked.connect(
            lambda checked=False, uid=user["id"]:
            self.resolve_user(uid, approved=False)
        )

        actions_layout.addWidget(approve)
        actions_layout.addWidget(reject)

        layout.addWidget(actions)
        return row

    def resolve_user(self, user_id, approved):
        # Demo behavior: updates local data only.
        user = next(
            (u for u in self.pending_users if u["id"] == user_id),
            None,
        )
        if user is None:
            return

        self.pending_users.remove(user)

        if approved:
            self.user_count += 1
            self.users_card.set_value(self.user_count)

        result = "approved" if approved else "rejected"
        self.feedback.setText(f"{user['name']} {result}.")
        self.refresh_rows()


class ReConnectWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("ReConnect — Administration")
        self.resize(1208, 680)
        self.setMinimumSize(900, 560)

        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        root_layout = QVBoxLayout(central_widget)
        root_layout.setContentsMargins(0, 0, 0, 0)
        root_layout.setSpacing(0)

        self.app_content = QWidget(central_widget)
        root_layout.addWidget(self.app_content)
        self.content_blur_effect = QGraphicsBlurEffect(self.app_content)
        self.content_blur_effect.setBlurRadius(5)
        self.content_blur_effect.setEnabled(False)
        self.app_content.setGraphicsEffect(self.content_blur_effect)

        main_layout = QHBoxLayout(self.app_content)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        self.stack = QStackedWidget()
        self.pages = {}

        main_layout.addWidget(self.create_sidebar())
        main_layout.addWidget(self.stack, 1)

        self.add_page("Admin", AdministrationPage())

        for name in (
            "Dashboard", "Contacts", "Cases", "Calendar",
            "To-Do", "Notifications", "Settings",
        ):
            self.add_page(name, self.create_placeholder(name))

        self.notifications_enabled = True
        self.notification_overlay = None
        self.minimized_notifications = []
        self.minimized_stack = QWidget(central_widget)
        self.minimized_stack.setFixedWidth(240)
        self.minimized_stack_layout = QVBoxLayout(self.minimized_stack)
        self.minimized_stack_layout.setContentsMargins(0, 0, 0, 0)
        self.minimized_stack_layout.setSpacing(0)
        self.minimized_stack.hide()
        self.notification_server = QLocalServer(self)
        self.notification_buffers = {}
        self.notification_server.newConnection.connect(
            self.accept_notification_connections
        )
        self.show_page("Admin")

    def start_notification_server(self):
        if not self.notification_server.listen(NOTIFICATION_SERVER_NAME):
            raise RuntimeError(
                "Could not listen for notification test commands: "
                f"{self.notification_server.errorString()}"
            )

    def accept_notification_connections(self):
        while self.notification_server.hasPendingConnections():
            socket = self.notification_server.nextPendingConnection()
            self.notification_buffers[socket] = bytearray()
            socket.readyRead.connect(
                lambda connection=socket:
                self.receive_notification(connection)
            )
            socket.disconnected.connect(
                lambda connection=socket:
                self.notification_buffers.pop(connection, None)
            )
            socket.disconnected.connect(socket.deleteLater)

    def receive_notification(self, socket):
        buffer = self.notification_buffers.get(socket)
        if buffer is None:
            return

        buffer.extend(bytes(socket.readAll()))
        if b"\n" not in buffer:
            return

        message, _, _ = buffer.partition(b"\n")
        try:
            values = json.loads(message.decode("utf-8"))
            notification = ContactNotification(**values)
        except (UnicodeDecodeError, json.JSONDecodeError, TypeError) as error:
            socket.write(f"error: {error}\n".encode("utf-8"))
            socket.flush()
            return

        socket.write(b"ok\n")
        socket.flush()
        self.show_contact_notification(notification)

    def create_sidebar(self):
        sidebar = QFrame()
        self.sidebar = sidebar
        sidebar.setObjectName("sidebar")
        sidebar.setFixedWidth(220)

        layout = QVBoxLayout(sidebar)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        brand_header = QFrame()
        brand_header.setObjectName("brandHeader")
        brand_header.setSizePolicy(
            QSizePolicy.Policy.Expanding,
            QSizePolicy.Policy.Fixed,
        )
        brand_layout = QVBoxLayout(brand_header)
        brand_layout.setContentsMargins(12, 8, 12, 8)
        self.brand = create_label("ReConnect", "brand")
        self.brand.setAlignment(Qt.AlignmentFlag.AlignCenter)
        brand_layout.addWidget(self.brand)
        layout.addWidget(brand_header)
        layout.addSpacing(10)

        nav_container = QWidget()
        nav_container.setObjectName("navContainer")
        self.nav_layout = QVBoxLayout(nav_container)
        self.nav_layout.setContentsMargins(16, 0, 16, 0)
        self.nav_layout.setSpacing(0)
        layout.addWidget(nav_container, 1)

        self.nav_group = QButtonGroup(self)
        self.nav_group.setExclusive(True)
        self.nav_buttons = []

        for name in (
            "Dashboard", "Contacts", "Cases", "Calendar",
            "To-Do", "Notifications", "Admin", "Settings",
        ):
            button = QPushButton(name)
            button.setObjectName("navButton")
            button.setCheckable(True)
            button.setChecked(name == "Admin")
            button.setSizePolicy(
                QSizePolicy.Policy.Expanding,
                QSizePolicy.Policy.Expanding,
            )
            button.setCursor(Qt.CursorShape.PointingHandCursor)
            button.clicked.connect(
                lambda checked=False, page=name: self.show_page(page)
            )

            self.nav_group.addButton(button)
            self.nav_buttons.append(button)
            self.nav_layout.addWidget(button, 1)

        return sidebar

    def resizeEvent(self, event):
        sidebar_width = max(200, min(300, round(self.width() * 0.2)))
        self.sidebar.setFixedWidth(sidebar_width)

        side_margin = max(10, min(18, round(sidebar_width * 0.075)))
        self.nav_layout.setContentsMargins(side_margin, 0, side_margin, 0)
        self.sidebar.layout().setSpacing(max(6, round(sidebar_width * 0.05)))

        brand_font = QFont(self.brand.font())
        brand_font.setPixelSize(max(22, min(34, round(sidebar_width * 0.14))))
        self.brand.setFont(brand_font)

        self.sidebar.layout().activate()
        nav_font = QFont(self.nav_buttons[0].font())
        nav_font.setPixelSize(max(18, min(32, round(sidebar_width * 0.1))))
        for button in self.nav_buttons:
            button.setFont(nav_font)

        super().resizeEvent(event)
        if self.notification_overlay is not None:
            self.notification_overlay.setGeometry(self.centralWidget().rect())
        self.position_minimized_stack()

    def create_placeholder(self, name):
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.setContentsMargins(42, 50, 42, 30)

        layout.addWidget(create_label(name, "pageTitle"))
        layout.addWidget(QLabel("This page is ready for your content."))
        layout.addStretch()

        return page

    def add_page(self, name, widget):
        self.pages[name] = widget
        self.stack.addWidget(widget)

    def show_page(self, name):
        self.stack.setCurrentWidget(self.pages[name])
        title = "Administration" if name == "Admin" else name
        self.setWindowTitle(f"ReConnect — {title}")

    def show_contact_notification(
        self,
        notification: ContactNotification,
    ):
        if not self.notifications_enabled:
            return

        if self.notification_overlay is not None or self.minimized_notifications:
            self.add_minimized_notification(notification)
            return

        self.display_contact_notification(notification)

    def display_contact_notification(self, notification):
        popup = ContactDetectedPopup(notification, self.centralWidget())
        popup.setGeometry(self.centralWidget().rect())
        popup.contact_requested.connect(self.open_contact)
        popup.do_not_disturb_requested.connect(self.disable_notifications)
        popup.dismissed.connect(
            lambda current=popup: self.dismiss_contact_notification(current)
        )
        popup.minimize_requested.connect(
            lambda current=popup: self.minimize_contact_notification(current)
        )
        self.notification_overlay = popup
        self.minimized_stack.hide()
        self.content_blur_effect.setEnabled(True)
        popup.show()
        popup.raise_()

    def dismiss_contact_notification(self, popup):
        if self.notification_overlay is not popup:
            return
        self.finish_contact_notification(popup)
        self.update_minimized_stack()

    def minimize_contact_notification(self, popup):
        if self.notification_overlay is not popup:
            return
        notification = popup.notification
        self.finish_contact_notification(popup)
        self.add_minimized_notification(notification)

    def finish_contact_notification(self, popup):
        self.content_blur_effect.setEnabled(False)
        self.notification_overlay = None
        popup.deleteLater()

    def add_minimized_notification(self, notification):
        chip = MinimizedContactNotification(notification, self.minimized_stack)
        chip.restore_requested.connect(
            lambda current=chip: self.restore_minimized_notification(current)
        )
        self.minimized_notifications.append((notification, chip))
        self.minimized_stack_layout.addWidget(chip)
        self.update_minimized_stack()

    def restore_minimized_notification(self, chip):
        notification = next(
            (
                item
                for item in self.minimized_notifications
                if item[1] is chip
            ),
            None,
        )
        if notification is None:
            return

        self.minimized_notifications.remove(notification)
        self.minimized_stack_layout.removeWidget(chip)
        chip.deleteLater()
        self.update_minimized_stack()
        if self.notification_overlay is None:
            self.display_contact_notification(notification[0])

    def update_minimized_stack(self):
        has_minimized = bool(self.minimized_notifications)
        self.minimized_stack.setVisible(
            has_minimized and self.notification_overlay is None
        )
        self.position_minimized_stack()

    def position_minimized_stack(self):
        if not hasattr(self, "minimized_stack"):
            return
        central = self.centralWidget()
        margins = self.minimized_stack_layout.contentsMargins()
        height = (
            margins.top()
            + margins.bottom()
            + sum(
                chip.height()
                for _, chip in self.minimized_notifications
            )
            + self.minimized_stack_layout.spacing()
            * max(0, len(self.minimized_notifications) - 1)
        )
        self.minimized_stack.setGeometry(
            central.width() - self.minimized_stack.width() - 16,
            16,
            self.minimized_stack.width(),
            height,
        )
        if self.minimized_stack.isVisible():
            self.minimized_stack.raise_()

    def open_contact(self, contact_id: str):
        self.show_page("Contacts")
        contacts_page = self.pages["Contacts"]
        open_contact = getattr(contacts_page, "open_contact", None)
        if callable(open_contact):
            open_contact(contact_id)
        else:
            self.pending_contact_id = contact_id

    def disable_notifications(self):
        self.notifications_enabled = False


def send_notification_to_running_app(notification: ContactNotification):
    socket = QLocalSocket()
    socket.connectToServer(NOTIFICATION_SERVER_NAME)
    if not socket.waitForConnected(1000):
        raise RuntimeError(
            "The ReConnect dashboard is not open, or is not accepting "
            f"notification commands: {socket.errorString()}"
        )

    message = json.dumps(notification.__dict__).encode("utf-8") + b"\n"
    if socket.write(message) != len(message):
        raise RuntimeError(f"Could not send notification: {socket.errorString()}")
    if not socket.waitForBytesWritten(1000):
        raise RuntimeError(f"Could not send notification: {socket.errorString()}")
    if not socket.waitForReadyRead(1000):
        raise RuntimeError(
            f"The dashboard did not acknowledge the notification: "
            f"{socket.errorString()}"
        )

    response = bytes(socket.readAll()).decode("utf-8").strip()
    if response != "ok":
        raise RuntimeError(f"The dashboard rejected the notification: {response}")
    socket.disconnectFromServer()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Run the ReConnect dashboard.")
    parser.add_argument(
        "--test-contact-notification",
        action="store_true",
        help="send a sample contact notification to the already-open dashboard",
    )
    parser.add_argument("--contact-id", default="sample-contact")
    parser.add_argument("--contact-name", default="Sample-name")
    parser.add_argument("--last-interaction", default="Unknown")
    parser.add_argument(
        "--last-topic",
        default="Sample topic",
    )
    parser.add_argument(
        "--direction",
        default="Contact reached out to you",
    )
    args = parser.parse_args()

    if args.test_contact_notification:
        app = QCoreApplication(sys.argv)
        notification = ContactNotification(
            contact_id=args.contact_id,
            contact_name=args.contact_name,
            last_interaction=args.last_interaction,
            last_topic=args.last_topic,
            direction=args.direction,
        )
        try:
            send_notification_to_running_app(notification)
        except RuntimeError as error:
            print(error, file=sys.stderr)
            sys.exit(1)
        print("Contact notification sent to the running dashboard.")
        sys.exit(0)

    app = QApplication(sys.argv)
    app.setStyle("Fusion")
    app.setStyleSheet(STYLESHEET)

    window = ReConnectWindow()
    try:
        window.start_notification_server()
    except RuntimeError as error:
        print(error, file=sys.stderr)
        sys.exit(1)
    window.show()

    sys.exit(app.exec())