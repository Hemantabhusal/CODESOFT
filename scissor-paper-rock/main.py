import random
from pathlib import Path
import tkinter as tk
from tkinter import Canvas, Button, Label, PhotoImage

class GameGUI:
    def __init__(self, root, assets_path):
        self.root = root
        self.assets_path = Path(assets_path)
        self.busy = False
        self._load_images()
        self._setup_canvas()
        self._init_scores()
        self._create_widgets()

    def relative_to_assets(self, filename: str) -> Path:
        return self.assets_path / filename

    def _load_images(self):
        # Must have called Tk() first
        self.scissor_img = PhotoImage(master=self.root,
                                      file=self.relative_to_assets("scissor.png"))
        # You’re already using logo.png instead of paper.png
        self.paper_img   = PhotoImage(master=self.root,
                                      file=self.relative_to_assets("paper.png"))
        self.rock_img    = PhotoImage(master=self.root,
                                      file=self.relative_to_assets("rock.png"))
        self.restart_img = PhotoImage(master=self.root,
                                      file=self.relative_to_assets("restart.png"))
        # blank placeholder for the bot slot
        self.blank_img   = PhotoImage(master=self.root, width=63, height=63)

        self.IMAGES = {
            "scissor": self.scissor_img,
            "paper":   self.paper_img,
            "rock":    self.rock_img,
        }

    def _setup_canvas(self):
        self.canvas = Canvas(self.root,
                             bg="#333333",
                             height=369,
                             width=374,
                             bd=0,
                             highlightthickness=0,
                             relief="ridge")
        self.canvas.place(x=0, y=0)

        # exact Figma positions, pixel fonts
        self.canvas.create_text(123, 98,
                                anchor="nw",
                                text="Pick One",
                                fill="#FFFFFF",
                                font=("Inter", -28))
        self.canvas.create_text(111, 216,
                                anchor="nw",
                                text="Bot Picked",
                                fill="#FFFFFF",
                                font=("Inter", -28))

    def _init_scores(self):
        self.wins = self.losses = self.draws = 0
        self.won_text = self.canvas.create_text(21,  262,
                                                anchor="nw",
                                                text="Won: 0",
                                                fill="#FFFFFF",
                                                font=("Inter", -28))
        self.lost_text = self.canvas.create_text(138, 262,
                                                 anchor="nw",
                                                 text="Lost: 0",
                                                 fill="#FFFFFF",
                                                 font=("Inter", -28))
        self.draw_text = self.canvas.create_text(252, 262,
                                                 anchor="nw",
                                                 text="Draw: 0",
                                                 fill="#FFFFFF",
                                                 font=("Inter", -28))

    def _create_widgets(self):
        # Bot’s pick display (blank initially)
        self.bot_label = Label(self.root, image=self.blank_img, bg="#333333")
        self.bot_label.image = self.blank_img
        self.bot_label.place(x=145, y=146, width=63, height=63)

        # Scissor / Paper(logo) / Rock buttons
        for name, img, x in (
            ("scissor", self.scissor_img, 33),
            ("paper",   self.paper_img,   146),
            ("rock",    self.rock_img,    263),
        ):
            btn = Button(
                self.root,
                image=img,
                borderwidth=0,
                highlightthickness=0,
                relief="flat",
                overrelief="flat",
                activebackground="#333333",
                command=lambda choice=name: self.play(choice)
            )
            btn.image = img
            btn.place(x=x, y=28, width=63, height=63)
            setattr(self, f"btn_{name}", btn)

        # Restart button, same flat styling
        self.btn_restart = Button(
            self.root,
            image=self.restart_img,
            borderwidth=0,
            highlightthickness=0,
            relief="flat",
            overrelief="flat",
            activebackground="#333333",
            command=self.reset
        )
        self.btn_restart.image = self.restart_img
        self.btn_restart.place(x=159, y=315, width=38, height=38)

    def update_score(self, user_choice, bot_choice):
        if user_choice == bot_choice:
            self.draws += 1
        elif (user_choice, bot_choice) in (
            ("scissor","paper"),
            ("paper",  "rock"),
            ("rock",   "scissor"),
        ):
            self.wins += 1
        else:
            self.losses += 1

        self.canvas.itemconfig(self.won_text,  text=f"Won: {self.wins}")
        self.canvas.itemconfig(self.lost_text, text=f"Lost: {self.losses}")
        self.canvas.itemconfig(self.draw_text, text=f"Draw: {self.draws}")

    def play(self, user_choice):
        if self.busy:
            return
        self.busy = True

        bot_choice = random.choice(list(self.IMAGES.keys()))
        sequence = ["scissor", "rock", "paper"] * 2

        def animate(i=0):
            if i < len(sequence):
                img = self.IMAGES[sequence[i]]
                self.bot_label.config(image=img)
                self.bot_label.image = img
                self.root.after(120, lambda: animate(i+1))
            else:
                final = self.IMAGES[bot_choice]
                self.bot_label.config(image=final)
                self.bot_label.image = final
                self.update_score(user_choice, bot_choice)
                self.busy = False

        animate()

    def reset(self):
        self.wins = self.losses = self.draws = 0
        self.canvas.itemconfig(self.won_text,  text="Won: 0")
        self.canvas.itemconfig(self.lost_text, text="Lost: 0")
        self.canvas.itemconfig(self.draw_text, text="Draw: 0")
        self.bot_label.config(image=self.blank_img)
        self.bot_label.image = self.blank_img


if __name__ == "__main__":
    assets_folder = Path(__file__).parent / "assets"

    root = tk.Tk()
    root.title("Scissor-Paper-Rock")

    # ─── Sets a custom icon if logo.png actually exists ───────────────
    logo_path = assets_folder / "logo.png"
    if logo_path.is_file():
        icon_img = PhotoImage(file=logo_path)
        root.iconphoto(True, icon_img)
    root.geometry("374x369")
    root.configure(bg="#333333")
    root.resizable(False, False)

    app = GameGUI(root, assets_folder)
    root.mainloop()
