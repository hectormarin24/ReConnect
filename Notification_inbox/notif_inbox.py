import customtkinter as ctk

ctk.set_appearance_mode("light")
ctk.set_default_color_theme("blue")

class Notif_Inbox(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("Notification Inbox")
        self.geometry("1100x700")
        self.minsize(850, 550)

        self.messages = [
            {"sender": "Alice", 
             "channel": "Email",
            "preview": "Hello! How are you doing today?",
            "timestamp": "10:30 AM",
            "unread": True,
            },

            {"sender": "Sam", 
            "channel": "WhatsApp",
            "preview": "Can I can get an update?",
            "timestamp": "10:45 AM",
            "unread": False,
            },

            {"sender": "Alice", 
            "channel": "SMS",
            "preview": "I appreciate the help.",
            "timestamp": "11:00 AM",
            "unread": True,
            },

       ]

        self.selected_message_index = "All"
        self.selected_message = None
        
        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        self.create_sidebar()
        self.create_inbox()
        self.show_messages()

    def create_sidebar(self):
        sidebar = ctk.CTkFrame(
            self, width=200, corner_radius=0,
            fg_color="transparent")

        sidebar.grid(row=0, column=0, sticky="nsew")
        sidebar.grid_propagate(False)

        ctk.CTkLabel(
            sidebar, 
            text="Notification Inbox",
            font=("Arial", 20, "bold"),
            text_color="black", ).pack(padx=15, pady=(25,30))

        for channel in ["All", "Email", "WhatsApp", "SMS"]:
            label = "Inbox" if channel == "All" else channel

            ctk.CTkButton(
                sidebar,
                text=label,
                anchor="w",
                height=40,
                fg_color="black" if channel == "All" else "transparent",
                text_color="black" if channel == "All" else "gray",
                hover_color="gray" if channel == "All" else "lightgray",
                command=lambda c=channel: self.filter_channel(c),
            ).pack(fill="x", padx=15, pady=5)

    def create_inbox(self):
        self.content = ctk.CTkFrame(self, corner_radius=0)
            
        self.content.grid(row=0, column=1, sticky="nsew", padx=25, pady=25)

        self.content.grid_columnconfigure(0, weight=1) 
        self.content.grid_rowconfigure(2, weight=1)

        ctk.CTkLabel(
                self.content,
                text="Messages",
                font=("Arial", 20, "bold"),
                text_color="black",
            ).grid(row=0, column=0, sticky="w", pady=(5, 15))

        self.search = ctk.CTkEntry(
                self.content,
                placeholder_text="Search messages...",
                height=30,
        
            )

        self.search.grid(row=1, column=0, sticky="ew", pady=(0, 15))
        self.search.bind("<KeyRelease>", lambda event: self.show_messages())

        self.message_frame = ctk.CTkScrollableFrame(
                self.content,
                fg_color="transparent",
                corner_radius=12,
            )
        self.message_frame.grid(row=2, column=0, sticky="nsew")

    def filter_channel(self, channel):
        self.selected_message_index = channel
        self.show_messages()

    def show_messages(self):
        for widget in self.message_frame.winfo_children():
            widget.destroy()

        query = self.search.get().lower()

        filtered = [
            message for message in self.messages
            if (
                self.selected_message_index == "All"
                or message["channel"] == self.selected_message_index
            )
            and (
                query in message["sender"].lower()
                or query in message["preview"].lower()
                or query in message["channel"].lower()
            )
        ]

        if not filtered:
            ctk.CTkLabel(
                self.message_frame,
                text="No messages found.",
                text_color="gray",
            ).pack(pady=20)
            return
        for message in filtered:
            self.create_message_card(message)

    def create_message_card(self, message):
        card = ctk.CTkFrame(
            self.message_frame,
            fg_color="lightgray" if message["unread"] else "white",
            corner_radius=9,
            border_width=1,
            border_color="gray",
        )
        card.pack(fill="x", padx=10, pady=5)

        card.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(
                card,
                text=message["sender"],
                font=("Arial", 14, "bold" if message["unread"] else "normal", ),
                text_color="black",
        ).grid(row=0, column=0, sticky="w", padx=(10, 5), pady=(10, 0))

        ctk.CTkLabel(
                card,
                text=message["channel"],
                font=("Arial", 12),
                text_color="gray",
        ).grid(row=1, column=0, sticky="w", padx=(10, 5), pady=(0, 10))

        ctk.CTkLabel(
                card,
                text=message["preview"],
                font=("Arial", 12),
                text_color="black",
        ).grid(row=2, column=0, sticky="ew", padx=(10, 5), pady=(0, 10))

if __name__ == "__main__":
    app = Notif_Inbox()
    app.mainloop()

           
                


