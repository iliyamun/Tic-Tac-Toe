import tkinter as tk
from tkinter import font


class TicTacToe(tk.Tk):
    """Simple yet polished Tic-Tac-Toe mini-game with a friendly GUI."""

    WIN_PATTERNS = (
        (0, 1, 2),
        (3, 4, 5),
        (6, 7, 8),
        (0, 3, 6),
        (1, 4, 7),
        (2, 5, 8),
        (0, 4, 8),
        (2, 4, 6),
    )

    def __init__(self) -> None:
        super().__init__()
        self.title("Tic-Tac-Toe Deluxe")
        self.resizable(False, False)
        self.configure(bg="#252525")

        self.board_state = [""] * 9
        self.current_player = "X"
        self.score = {"X": 0, "O": 0, "Draw": 0}
        self.buttons: list[tk.Button] = []
        self.preview_index: int | None = None
        self.status_pulse_job: str | None = None

        # Fonts for consistent styling
        self.board_font = font.Font(family="Segoe UI", size=32, weight="bold")
        self.info_font = font.Font(family="Segoe UI", size=12)
        self.title_font = font.Font(family="Segoe UI", size=14, weight="bold")

        self._build_layout()
        self._update_status("Player X's turn", accent="#79d279")

    def _build_layout(self) -> None:
        """Create the static layout widgets."""
        outer = tk.Frame(self, bg="#252525", padx=20, pady=20)
        outer.pack()

        info_panel = tk.Frame(outer, bg="#252525")
        info_panel.grid(row=0, column=0, sticky="ew")
        info_panel.columnconfigure(0, weight=1)

        tk.Label(
            info_panel,
            text="Tic-Tac-Toe",
            fg="#f2f2f2",
            bg="#252525",
            font=self.title_font,
        ).grid(row=0, column=0, sticky="w")

        self.status_label = tk.Label(
            info_panel,
            text="",
            fg="#dedede",
            bg="#252525",
            font=self.info_font,
        )
        self.status_label.grid(row=1, column=0, sticky="w", pady=(4, 12))

        self.score_labels = {}
        scores_frame = tk.Frame(outer, bg="#252525")
        scores_frame.grid(row=1, column=0, sticky="ew", pady=(0, 10))
        for idx, player in enumerate(("X", "O", "Draw")):
            lbl = tk.Label(
                scores_frame,
                text=f"{player}: 0",
                fg="#f2f2f2",
                bg="#3a3a3a",
                font=self.info_font,
                padx=10,
                pady=6,
                width=10,
                relief="ridge",
                bd=1,
            )
            lbl.grid(row=0, column=idx, padx=4)
            self.score_labels[player] = lbl

        self.board_frame = tk.Frame(
            outer, bg="#252525", highlightbackground="#444", highlightthickness=2
        )
        self.board_frame.grid(row=2, column=0)

        for idx in range(9):
            btn = tk.Button(
                self.board_frame,
                text="",
                width=3,
                height=1,
                font=self.board_font,
                fg="#f7f7f7",
                bg="#1f1f1f",
                activebackground="#333333",
                activeforeground="#b3f0b3",
                relief="flat",
                command=lambda i=idx: self._handle_move(i),
            )
            btn.grid(row=idx // 3, column=idx % 3, ipadx=10, ipady=10, padx=3, pady=3)
            btn.bind("<Enter>", lambda e, i=idx: self._preview_move(i))
            btn.bind("<Leave>", lambda e, i=idx: self._clear_preview(i))
            self.buttons.append(btn)

        controls = tk.Frame(outer, bg="#252525")
        controls.grid(row=3, column=0, pady=(15, 0), sticky="ew")
        tk.Button(
            controls,
            text="New Round",
            command=self._reset_board,
            bg="#79d279",
            activebackground="#6ecb6e",
            fg="#101010",
            font=self.info_font,
            width=12,
            relief="flat",
            cursor="hand2",
        ).grid(row=0, column=0, padx=5)
        tk.Button(
            controls,
            text="Reset Score",
            command=self._reset_scores,
            bg="#f25f5c",
            activebackground="#d94f4c",
            fg="#101010",
            font=self.info_font,
            width=12,
            relief="flat",
            cursor="hand2",
        ).grid(row=0, column=1, padx=5)

    def _handle_move(self, index: int) -> None:
        """Handle a player's tap on a board cell."""
        if self.board_state[index] or self._board_locked():
            return

        self.board_state[index] = self.current_player
        btn = self.buttons[index]
        btn.config(text=self.current_player, fg="#f7f7f7", bg="#303030")

        winner = self._find_winner()
        if winner:
            self._finish_round(winner)
            return

        if "" not in self.board_state:
            self._finish_round("Draw")
            return

        self.current_player = "O" if self.current_player == "X" else "X"
        self._update_status(f"Player {self.current_player}'s turn", accent="#79d279")

    def _preview_move(self, index: int) -> None:
        """Show a subtle preview of the move while hovering."""
        if self.board_state[index] or self._board_locked():
            return
        btn = self.buttons[index]
        btn.config(text=self.current_player, fg="#6d6d6d")
        self.preview_index = index

    def _clear_preview(self, index: int) -> None:
        if self.preview_index != index:
            return
        btn = self.buttons[index]
        if self.board_state[index]:
            btn.config(fg="#f7f7f7")
        else:
            btn.config(text="", fg="#f7f7f7", bg="#1f1f1f")
        self.preview_index = None

    def _find_winner(self) -> str | None:
        """Return 'X' or 'O' if there's a winner, None otherwise."""
        for a, b, c in self.WIN_PATTERNS:
            first = self.board_state[a]
            if first and first == self.board_state[b] == self.board_state[c]:
                for idx in (a, b, c):
                    self.buttons[idx].config(bg="#4caf50")
                return first
        return None

    def _finish_round(self, result: str) -> None:
        """Handle end-of-round updates."""
        if result == "Draw":
            self._update_status("It's a draw! Hit New Round to play again.", accent="#f2c94c")
        else:
            self._update_status(f"Player {result} wins!", accent="#79d279")
        self.score[result] += 1
        self._board_lock(True)
        self._refresh_score_labels()

    def _refresh_score_labels(self) -> None:
        for key, lbl in self.score_labels.items():
            lbl.config(text=f"{key}: {self.score[key]}")

    def _reset_board(self) -> None:
        """Start a new round but keep the score."""
        self.board_state = [""] * 9
        self.current_player = "X"
        self.preview_index = None
        for btn in self.buttons:
            btn.config(text="", state="normal", bg="#1f1f1f", fg="#f7f7f7")
        self._board_lock(False)
        self._update_status("Player X's turn", accent="#79d279")

    def _reset_scores(self) -> None:
        self.score = {"X": 0, "O": 0, "Draw": 0}
        self._refresh_score_labels()
        self._reset_board()

    def _board_lock(self, locked: bool) -> None:
        for btn in self.buttons:
            btn.config(state="disabled" if locked else "normal")

    def _board_locked(self) -> bool:
        # All buttons share the same state, so checking the first is enough.
        return bool(self.buttons and self.buttons[0]["state"] == "disabled")

    def _update_status(self, text: str, accent: str = "#dedede") -> None:
        """Update and animate the status message."""
        if self.status_pulse_job:
            self.after_cancel(self.status_pulse_job)
        self.status_label.config(text=text, fg=accent)

        def pulse(alpha: float = 0.15, direction: int = 1) -> None:
            # Provide a subtle glow/opacity effect using color blending.
            blend = int(222 + (255 - 222) * alpha)
            color = f"#{blend:02x}{blend:02x}{blend:02x}"
            self.status_label.config(bg=color)
            next_alpha = alpha + direction * 0.05
            if next_alpha > 0.45 or next_alpha < 0.1:
                direction *= -1
            self.status_pulse_job = self.after(60, pulse, next_alpha, direction)

        self.status_pulse_job = self.after(0, pulse)


if __name__ == "__main__":
    app = TicTacToe()
    app.mainloop()
