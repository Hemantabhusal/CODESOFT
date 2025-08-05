from pathlib import Path
from tkinter import Tk, Canvas, Toplevel, Entry, Button, PhotoImage

ASSETS_PATH = Path(__file__).parent / "assets"

MAX_ROWS = 4

class TodoApp:
    def __init__(self):
        self.window = Tk()
        self.window.title("To-Do-List")
        self.window.geometry("350x421")
        self.window.configure(bg="#778DA9")
        self.window.resizable(False, False)

        # load optional logo
        logo_path = ASSETS_PATH / "logo.png"
        if logo_path.is_file():
            icon_img = PhotoImage(master=self.window, file=logo_path)
            self.window.iconphoto(True, icon_img)

        # — State —
        self.items = []  
        self._id_counter = 0
        self.today_offset = 0
        self.comp_offset = 0
        self.active_section = None 
        self.popup_open = False

        def R(fn):  return ASSETS_PATH / fn
        self.images = {
            "bg1":  PhotoImage(master=self.window, file=R("entry_1.png")),
            "bg2":  PhotoImage(master=self.window, file=R("entry_2.png")),
            "box":  PhotoImage(master=self.window, file=R("minibox.png")),
            "tick": PhotoImage(master=self.window, file=R("tick.png")),
            "bin":  PhotoImage(master=self.window, file=R("dustbin.png")),
            "plus": PhotoImage(master=self.window, file=R("plus.png")),
            "input_bg": PhotoImage(master=self.window, file=R("new_input.png")),
            "enter":    PhotoImage(master=self.window, file=R("Enter.png")),
            "cancel":   PhotoImage(master=self.window, file=R("Cancel.png")),
        }
        self._build_main_canvas()
        self.redraw_items()
        self.window.bind_all("<MouseWheel>", self._on_mousewheel)

    def _new_id(self):
        i = self._id_counter
        self._id_counter += 1
        return i

    def add_item(self, text, state="today"):
        self.items.append({"id": self._new_id(), "text": text, "state": state})

    def delete_item(self, item_id):
        self.items = [i for i in self.items if i["id"] != item_id]
        self._clamp_offsets()
        self.redraw_items()

    def toggle_item(self, item_id):
        for i in self.items:
            if i["id"] == item_id:
                i["state"] = "completed" if i["state"] == "today" else "today"
                break
        self._clamp_offsets()
        self.redraw_items()

    def _clamp_offsets(self):
        tcount = sum(1 for i in self.items if i["state"] == "today")
        dcount = sum(1 for i in self.items if i["state"] == "completed")
        self.today_offset = max(0, min(self.today_offset, max(0, tcount - MAX_ROWS)))
        self.comp_offset  = max(0, min(self.comp_offset,  max(0, dcount - MAX_ROWS)))

    # ─── MAIN CANVAS ────────────────────────────────────────────
    def _build_main_canvas(self):
        c = self.window
        self.canvas = Canvas(c, bg="#778DA9", width=350, height=421,
                             bd=0, highlightthickness=0, relief="ridge")
        self.canvas.place(x=0, y=0)

        self.canvas.create_text(26, 17,  anchor="nw",
                                text="TODAY", fill="#000000",
                                font=("Inter Medium", -20))
        self.canvas.create_text(26, 177, anchor="nw",
                                text="COMPLETED", fill="#000000",
                                font=("Inter Medium", -20))

        self.bg1_id = self.canvas.create_image(175, 105.5, image=self.images["bg1"])
        self.bg2_id = self.canvas.create_image(175, 271.5, image=self.images["bg2"])

        self.canvas.tag_bind(self.bg1_id, "<Button-1>",
                             lambda e: self._set_active("today"))
        self.canvas.tag_bind(self.bg2_id, "<Button-1>",
                             lambda e: self._set_active("completed"))

        plus_id = self.canvas.create_image(175, 378, image=self.images["plus"])
        self.canvas.tag_bind(plus_id, "<Button-1>",
                             lambda e: self._open_popup())

        self.drawn_ids = []

    def redraw_items(self):
        for cid in self.drawn_ids:
            self.canvas.delete(cid)
        self.drawn_ids.clear()

        # layout constants
        R1T, R1O, R1B = 46, 14, 26
        R2T, R2O, R2B = 212, 10, 21
        SP = 26
        CX = 45.5
        LX1, LX2 = 59, 65
        DX = 299

        today = [i for i in self.items if i["state"] == "today"]
        done  = [i for i in self.items if i["state"] == "completed"]

        # TODAY slice
        for idx, item in enumerate(today[self.today_offset:self.today_offset+MAX_ROWS]):
            y_txt = R1T + R1O + idx*SP
            y_box = R1T + R1B + idx*SP

            bid = self.canvas.create_image(CX, y_box,
                                           image=self.images["box"],
                                           tags=(f"box_{item['id']}",))
            lid = self.canvas.create_text(LX1, y_txt,
                                          anchor="nw",
                                          text=item["text"],
                                          fill="#000000",
                                          font=("Inter", -20))
            did = self.canvas.create_image(DX, y_box,
                                           image=self.images["bin"],
                                           tags=(f"del_{item['id']}",))

            self.drawn_ids += [bid, lid, did]

            self.canvas.tag_bind(f"box_{item['id']}", "<Button-1>",
                                 lambda e, i=item["id"]: self.toggle_item(i))
            self.canvas.tag_bind(f"del_{item['id']}", "<Button-1>",
                                 lambda e, i=item["id"]: self.delete_item(i))

        # COMPLETED slice
        for idx, item in enumerate(done[self.comp_offset:self.comp_offset+MAX_ROWS]):
            y_txt = R2T + R2O + idx*SP
            y_box = R2T + R2B + idx*SP

            bid0 = self.canvas.create_image(CX, y_box,
                                            image=self.images["box"],
                                            tags=(f"box_{item['id']}",))
            bid1 = self.canvas.create_image(CX, y_box,
                                            image=self.images["tick"],
                                            tags=(f"box_{item['id']}",))
            lid  = self.canvas.create_text(LX2, y_txt,
                                           anchor="nw",
                                           text=item["text"],
                                           fill="#000000",
                                           font=("Inter", -20))
            did  = self.canvas.create_image(DX, y_box,
                                            image=self.images["bin"],
                                            tags=(f"del_{item['id']}",))

            self.drawn_ids += [bid0, bid1, lid, did]

            self.canvas.tag_bind(f"box_{item['id']}", "<Button-1>",
                                 lambda e, i=item["id"]: self.toggle_item(i))
            self.canvas.tag_bind(f"del_{item['id']}", "<Button-1>",
                                 lambda e, i=item["id"]: self.delete_item(i))

    def _set_active(self, section):
        self.active_section = section

    def _open_popup(self):
        if self.popup_open:
            return
        self.popup_open = True

        pop = Toplevel(self.window)
        pop.title("")
        pop.geometry("229x160")
        pop.configure(bg="#778DA9")
        pop.resizable(False, False)

        def close_popup():
            self.popup_open = False
            pop.destroy()

        pop.protocol("WM_DELETE_WINDOW", close_popup)

        c2 = Canvas(pop, bg="#778DA9",
                    width=229, height=160,
                    bd=0, highlightthickness=0, relief="ridge")
        c2.place(x=0, y=0)
        c2.create_image(114.5, 69.5, image=self.images["input_bg"])
        c2.create_text(22, 20,
                       anchor="nw",
                       text="Input New Task",
                       fill="#000000",
                       font=("Inter SemiBold", -20))

        entry = Entry(pop,
                      bd=0,
                      bg="#EDEAE5",
                      fg="#000716",
                      highlightthickness=0,
                      font=("Inter", 14))
        entry.place(x=27, y=56, width=175, height=25)
        entry.focus_set()

        def do_add(event=None):
            txt = entry.get().strip()
            if txt:
                self.add_item(txt, "today")
                total = sum(1 for i in self.items if i["state"] == "today")
                if total > MAX_ROWS:
                    self.today_offset = total - MAX_ROWS
                self._clamp_offsets()
                self.redraw_items()
            close_popup()

        entry.bind("<Return>", do_add)

        b1 = Button(pop,
                    image=self.images["enter"],
                    borderwidth=0,
                    highlightthickness=0,
                    relief="flat",
                    bg="#778DA9", activebackground="#778DA9",
                    command=do_add)
        b1.place(x=22, y=103, width=82, height=24)

        b2 = Button(pop,
                    image=self.images["cancel"],
                    borderwidth=0,
                    highlightthickness=0,
                    relief="flat",
                    bg="#778DA9", activebackground="#778DA9",
                    command=close_popup)
        b2.place(x=124, y=103, width=82, height=24)

    def _scroll(self, delta):
        sec = self.active_section
        if sec == "today":
            count = sum(1 for i in self.items if i["state"] == "today")
            if delta < 0 and self.today_offset + MAX_ROWS < count:
                self.today_offset += 1
                self.redraw_items()
            elif delta > 0 and self.today_offset > 0:
                self.today_offset -= 1
                self.redraw_items()

        elif sec == "completed":
            count = sum(1 for i in self.items if i["state"] == "completed")
            if delta < 0 and self.comp_offset + MAX_ROWS < count:
                self.comp_offset += 1
                self.redraw_items()
            elif delta > 0 and self.comp_offset > 0:
                self.comp_offset -= 1
                self.redraw_items()

    def _on_mousewheel(self, e):
        self._scroll(e.delta / 120)

    def run(self):
        self.window.mainloop()

if __name__ == "__main__":
    app = TodoApp()
    app.run()
