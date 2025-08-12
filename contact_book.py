import json
import os
import tkinter as tk
import customtkinter as ctk
from tkinter import messagebox
from typing import Dict, List, Optional, Callable

class Contact:
    """Represents a single contact with all their information."""
    def __init__(self, name: str, phone: str, email: str = "", address: str = ""):
        self.name = name
        self.phone = phone
        self.email = email
        self.address = address

    def to_dict(self) -> Dict:
        return {
            "name": self.name,
            "phone": self.phone,
            "email": self.email,
            "address": self.address,
        }

    @classmethod
    def from_dict(cls, data: Dict) -> "Contact":
        return cls(
            name=data.get("name", ""),
            phone=data.get("phone", ""),
            email=data.get("email", ""),
            address=data.get("address", ""),
        )


class ContactManager:
    """Manages all contact operations including storage and retrieval."""
    def __init__(self, filename: str = "contacts.json"):
        self.filename = filename
        self.contacts: List[Contact] = []
        self.load_contacts()

    def load_contacts(self):
        if os.path.exists(self.filename):
            try:
                with open(self.filename, "r") as f:
                    data = json.load(f)
                    self.contacts = [Contact.from_dict(c) for c in data]
            except (json.JSONDecodeError, FileNotFoundError):
                self.contacts = []

    def save_contacts(self):
        try:
            with open(self.filename, "w") as f:
                json.dump([c.to_dict() for c in self.contacts], f, indent=2)
        except Exception as e:
            print(f"Error saving contacts: {e}")

    def add_contact(self, name: str, phone: str, email: str = "", address: str = "") -> bool:
        if not name.strip() or not phone.strip():
            return False
        if self.find_contact_by_name(name):
            return False
        contact = Contact(name.strip(), phone.strip(), email.strip(), address.strip())
        self.contacts.append(contact)
        self.save_contacts()
        return True

    def search_contacts(self, query: str) -> List[Contact]:
        query = query.lower()
        results: List[Contact] = []
        for c in self.contacts:
            if query in c.name.lower() or query in c.phone or query in c.email.lower():
                results.append(c)
        return results

    def find_contact_by_name(self, name: str) -> Optional[Contact]:
        for c in self.contacts:
            if c.name.lower() == name.lower():
                return c
        return None

    def update_contact(self, old_name: str, name: str, phone: str, email: str = "", address: str = "") -> bool:
        contact = self.find_contact_by_name(old_name)
        if not contact:
            return False
        if not name.strip() or not phone.strip():
            return False
        contact.name = name.strip()
        contact.phone = phone.strip()
        contact.email = email.strip()
        contact.address = address.strip()
        self.save_contacts()
        return True

    def delete_contact(self, name: str) -> bool:
        contact = self.find_contact_by_name(name)
        if not contact:
            return False
        self.contacts.remove(contact)
        self.save_contacts()
        return True


class ContactCard(ctk.CTkFrame):
    """Single contact card used in the scrollable list."""
    def __init__(
        self,
        master: ctk.CTkBaseClass,
        contact: Contact,
        on_select: Callable[[Contact], None],
        is_selected: bool = False,
        **kwargs,
    ):
        super().__init__(master, corner_radius=10, fg_color=("#F5F6F8", "#1F1F1F"), **kwargs)
        self.contact = contact
        self.on_select = on_select
        self.configure(border_width=0)
        self._update_selected_ui(is_selected)
        self.grid_columnconfigure(0, weight=1)

        name_label = ctk.CTkLabel(self, text=contact.name, font=("Segoe UI", 14, "bold"))
        phone_label = ctk.CTkLabel(self, text=contact.phone, font=("Segoe UI", 12))
        email_label = ctk.CTkLabel(self, text=contact.email or "No email", font=("Segoe UI", 12))
        name_label.grid(row=0, column=0, sticky="w", padx=12, pady=(4, 0))
        phone_label.grid(row=1, column=0, sticky="w", padx=12)
        email_label.grid(row=2, column=0, sticky="w", padx=12, pady=(0, 4))

        for widget in (self, name_label, phone_label, email_label):
            widget.bind("<Button-1>", self._handle_click)

    def _handle_click(self, _event=None):
        self.on_select(self.contact)

    def _update_selected_ui(self, is_selected: bool):
        if is_selected:
            self.configure(border_width=2, border_color=("#3B8ED0", "#1F6AA5"))
        else:
            self.configure(border_width=0)


class ContactDialog(ctk.CTkToplevel):
    """Dialog window for adding/updating contacts."""
    def __init__(self, parent, title: str, contact: Optional[Contact] = None):
        super().__init__(parent)
        self.title(title)
        self.geometry("420x380")
        self.resizable(False, False)
        self.grab_set()
        self.result = None

        self.update_idletasks()
        if parent is not None:
            x = parent.winfo_rootx() + (parent.winfo_width() // 2) - (420 // 2)
            y = parent.winfo_rooty() + (parent.winfo_height() // 2) - (380 // 2)
            self.geometry(f"+{x}+{y}")

        container = ctk.CTkFrame(self, corner_radius=12)
        container.pack(fill="both", expand=True, padx=20, pady=20)

        self.name_var = ctk.StringVar(value=contact.name if contact else "")
        self.phone_var = ctk.StringVar(value=contact.phone if contact else "")
        self.email_var = ctk.StringVar(value=contact.email if contact else "")
        self.address_var = ctk.StringVar(value=contact.address if contact else "")

        ctk.CTkLabel(container, text="Name").grid(row=0, column=0, sticky="w")
        name_entry = ctk.CTkEntry(container, textvariable=self.name_var, width=260)
        name_entry.grid(row=1, column=0, sticky="we", pady=(0, 10))
        name_entry.focus()

        ctk.CTkLabel(container, text="Phone").grid(row=2, column=0, sticky="w")
        phone_entry = ctk.CTkEntry(container, textvariable=self.phone_var, width=260)
        phone_entry.grid(row=3, column=0, sticky="we", pady=(0, 10))

        ctk.CTkLabel(container, text="Email").grid(row=4, column=0, sticky="w")
        email_entry = ctk.CTkEntry(container, textvariable=self.email_var, width=260)
        email_entry.grid(row=5, column=0, sticky="we", pady=(0, 10))

        ctk.CTkLabel(container, text="Address").grid(row=6, column=0, sticky="w")
        self.address_entry = ctk.CTkEntry(container, textvariable=self.address_var, width=260)
        self.address_entry.grid(row=7, column=0, sticky="we", pady=(0, 12))

        btns = ctk.CTkFrame(container)
        btns.grid(row=8, column=0, pady=(4, 0), sticky="we")
        btns.grid_columnconfigure(0, weight=1)
        btns.grid_columnconfigure(1, weight=1)
        ctk.CTkButton(btns, text="Save", command=self._save).grid(row=0, column=0, padx=(0, 6), sticky="we")
        ctk.CTkButton(btns, text="Cancel", fg_color=("#E5E7EB", "#2b2b2b"), text_color=("#111827", "#F3F4F6"), command=self._cancel).grid(row=0, column=1, sticky="we")

        container.grid_columnconfigure(0, weight=1)

        self.bind("<Return>", lambda e: self._save())
        self.bind("<Escape>", lambda e: self._cancel())
        self.wait_visibility()
        self.wait_window(self)

    def _save(self):
        name = self.name_var.get().strip()
        phone = self.phone_var.get().strip()
        email = self.email_var.get().strip()
        address = self.address_var.get().strip()
        if not name or not phone:
            messagebox.showerror("Error", "Name and phone number are required!")
            return
        self.result = (name, phone, email, address)
        self.destroy()

    def _cancel(self):
        self.destroy()


class ContactApp:
    """Main GUI application (CustomTkinter)."""

    def __init__(self):
        # Theming
        ctk.set_appearance_mode("System")
        ctk.set_default_color_theme("blue")

        self.root = ctk.CTk()
        self.root.title("Contact Management System")
        self.root.geometry("900x650")
        self.root.resizable(False, False)

        self.manager = ContactManager()
        self.selected_contact_name: Optional[str] = None
        self.card_widgets: Dict[str, ContactCard] = {}

        self.root.grid_columnconfigure(1, weight=1)
        self.root.grid_rowconfigure(1, weight=1)

        header = ctk.CTkFrame(self.root, corner_radius=0, fg_color=("#FFFFFF", "#101010"), height=64)
        header.grid(row=0, column=0, columnspan=2, sticky="nsew")
        header.grid_columnconfigure(0, weight=1)
        title = ctk.CTkLabel(header, text="Contact Management System", font=("Segoe UI", 20, "bold"))
        title.grid(row=0, column=0, padx=20, pady=16, sticky="w")

        self.theme_selector = ctk.CTkSegmentedButton(
            header,
            values=["System", "Light", "Dark"],
            command=self._on_theme_change,
        )
        self.theme_selector.set("System")
        self.theme_selector.grid(row=0, column=1, padx=20)

        controls = ctk.CTkFrame(self.root, corner_radius=12)
        controls.grid(row=1, column=0, sticky="nsew", padx=(16, 8), pady=(12, 12))
        controls.grid_rowconfigure(3, weight=0)
        controls.grid_rowconfigure(6, weight=1)
        controls.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(controls, text="Search").grid(row=0, column=0, sticky="w", padx=8, pady=(8, 4))
        self.search_var = ctk.StringVar()
        self.search_entry = ctk.CTkEntry(controls, textvariable=self.search_var, placeholder_text="Search by name, phone, email")
        self.search_entry.grid(row=1, column=0, sticky="we", padx=8, pady=(0, 12))
        self.search_entry.bind("<KeyRelease>", self.on_search_change)

        btn_add = ctk.CTkButton(controls, text="Add Contact", command=self.add_contact_dialog)
        btn_update = ctk.CTkButton(controls, text="Update Contact", command=self.update_contact_dialog)
        btn_delete = ctk.CTkButton(controls, text="Delete Contact", command=self.delete_contact_dialog, fg_color="#C24141")
        btn_clear = ctk.CTkButton(controls, text="Clear Search", command=self.clear_search, fg_color="gray")

        btn_add.grid(row=2, column=0, sticky="we", padx=8, pady=(0, 8))
        btn_update.grid(row=3, column=0, sticky="we", padx=8, pady=(0, 8))
        btn_delete.grid(row=4, column=0, sticky="we", padx=8, pady=(0, 8))
        btn_clear.grid(row=5, column=0, sticky="we", padx=8)

        list_frame = ctk.CTkFrame(self.root, corner_radius=12)
        list_frame.grid(row=1, column=1, sticky="nsew", padx=(8, 16), pady=(12, 12))
        list_frame.grid_rowconfigure(1, weight=1)
        list_frame.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(list_frame, text="Contacts", font=("Segoe UI", 14, "bold")).grid(row=0, column=0, sticky="w", padx=12, pady=(10, 0))
        self.scroll = ctk.CTkScrollableFrame(list_frame, corner_radius=12)
        self.scroll.grid(row=1, column=0, sticky="nsew", padx=10, pady=6)
        self.scroll.grid_columnconfigure(0, weight=1)

        details = ctk.CTkFrame(self.root, corner_radius=12)
        details.grid(row=2, column=0, columnspan=2, sticky="we", padx=16, pady=(0, 16))
        details.grid_columnconfigure(1, weight=1)

        ctk.CTkLabel(details, text="Name:").grid(row=0, column=0, sticky="w")
        self.detail_name = ctk.CTkLabel(details, text="", font=("Segoe UI", 12, "bold"))
        self.detail_name.grid(row=0, column=1, sticky="w")

        ctk.CTkLabel(details, text="Phone:").grid(row=1, column=0, sticky="w")
        self.detail_phone = ctk.CTkLabel(details, text="")
        self.detail_phone.grid(row=1, column=1, sticky="w")

        ctk.CTkLabel(details, text="Email:").grid(row=2, column=0, sticky="w")
        self.detail_email = ctk.CTkLabel(details, text="")
        self.detail_email.grid(row=2, column=1, sticky="w")

        ctk.CTkLabel(details, text="Address:").grid(row=3, column=0, sticky="w")
        self.detail_address = ctk.CTkLabel(details, text="", wraplength=700, justify="left")
        self.detail_address.grid(row=3, column=1, sticky="w")

        self.refresh_contact_list()

    def _on_theme_change(self, value: str):
        ctk.set_appearance_mode(value)

    def _select_contact(self, contact: Contact):
        previous = self.selected_contact_name
        self.selected_contact_name = contact.name
        # update details
        self.show_contact_details(contact)
        # update cards highlight
        for name, card in self.card_widgets.items():
            card._update_selected_ui(name == self.selected_contact_name)

    def refresh_contact_list(self, contacts: Optional[List[Contact]] = None):
        # clear
        for child in list(self.scroll.children.values()):
            child.destroy()
        self.card_widgets.clear()

        if contacts is None:
            contacts = self.manager.contacts

        for idx, contact in enumerate(contacts):
            card = ContactCard(self.scroll, contact, on_select=self._select_contact)
            card.grid(row=idx, column=0, sticky="we", padx=4, pady=4)
            self.card_widgets[contact.name] = card

    def show_contact_details(self, contact: Contact):
        self.detail_name.configure(text=contact.name)
        self.detail_phone.configure(text=contact.phone)
        self.detail_email.configure(text=contact.email or "Not provided")
        self.detail_address.configure(text=contact.address or "Not provided")

    def clear_details(self):
        self.detail_name.configure(text="")
        self.detail_phone.configure(text="")
        self.detail_email.configure(text="")
        self.detail_address.configure(text="")
        self.selected_contact_name = None

    def on_search_change(self, _event=None):
        query = self.search_var.get()
        if query.strip():
            results = self.manager.search_contacts(query)
            self.refresh_contact_list(results)
        else:
            self.refresh_contact_list()

    def clear_search(self):
        self.search_var.set("")
        self.refresh_contact_list()

    def add_contact_dialog(self):
        dialog = ContactDialog(self.root, "Add Contact")
        if dialog.result:
            name, phone, email, address = dialog.result
            if self.manager.add_contact(name, phone, email, address):
                self.refresh_contact_list()
                messagebox.showinfo("Success", f"Contact '{name}' added successfully!")
            else:
                if self.manager.find_contact_by_name(name):
                    messagebox.showerror("Error", f"Contact with name '{name}' already exists!")
                else:
                    messagebox.showerror("Error", "Name and phone number are required!")

    def update_contact_dialog(self):
        if not self.selected_contact_name:
            messagebox.showwarning("Warning", "Please select a contact to update.")
            return
        contact = self.manager.find_contact_by_name(self.selected_contact_name)
        if not contact:
            messagebox.showerror("Error", "Contact not found!")
            return
        dialog = ContactDialog(self.root, "Update Contact", contact)
        if dialog.result:
            name, phone, email, address = dialog.result
            if self.manager.update_contact(self.selected_contact_name, name, phone, email, address):
                self.refresh_contact_list()
                self.clear_details()
                messagebox.showinfo("Success", "Contact updated successfully!")
            else:
                messagebox.showerror("Error", "Name and phone number are required!")

    def delete_contact_dialog(self):
        if not self.selected_contact_name:
            messagebox.showwarning("Warning", "Please select a contact to delete.")
            return
        name = self.selected_contact_name
        result = messagebox.askyesno("Confirm Delete", f"Are you sure you want to delete contact '{name}'?")
        if result:
            if self.manager.delete_contact(name):
                self.refresh_contact_list()
                self.clear_details()
                messagebox.showinfo("Success", f"Contact '{name}' deleted successfully!")
            else:
                messagebox.showerror("Error", "Failed to delete contact!")

    def run(self):
        self.root.mainloop()


def main():
    try:
        app = ContactApp()
        app.run()
    except Exception as e:
        messagebox.showerror("Error", f"An error occurred: {e}")


if __name__ == "__main__":
    main()


