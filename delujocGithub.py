import socket
from dataclasses import dataclass


ROBOT_IP = "192.168.125.1"
PORT = 5001
BUFFER_SIZE = 1024


@dataclass
class Pose:
    x: float
    y: float
    z: float
    q1: float
    q2: float
    q3: float
    q4: float


TOCKA_NAD_POBIRANJEM = Pose(
    453.12,
    -224.88,
    470.00,
    0.00045,
    0.23230,
    -0.97265,
    0.00010,
)

TOCKA_POBIRANJE = Pose(
    453.12,
    -224.88,
    346.89,
    0.00045,
    0.23230,
    -0.97265,
    0.00010,
)

TOCKA_NAD_ODLAGANJEM = Pose(
    435.93,
    151.10,
    470.00,
    0.00315,
    -0.23379,
    0.97229,
    -0.00066,
)

TOCKA_ODLAGANJE = Pose(
    435.93,
    151.10,
    362.03,
    0.00315,
    -0.23379,
    0.97229,
    -0.00066,
)


class ABBRobot:
    def __init__(self, robot_ip: str, port: int) -> None:
        self.robot_ip = robot_ip
        self.port = port
        self.sock: socket.socket | None = None

    def connect(self) -> None:
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.settimeout(10)
        self.sock.connect((self.robot_ip, self.port))

        reply = self._recv()
        if reply != "ACK":
            raise RuntimeError(f"Nepricakovan handshake: {reply}")

        print("Povezava z robotom OK")

    def close(self) -> None:
        if self.sock is not None:
            self.sock.close()
            self.sock = None

    def _send(self, msg: str) -> None:
        if self.sock is None:
            raise RuntimeError("Socket ni povezan.")
        print(">>", msg)
        self.sock.sendall(msg.encode("utf-8"))

    def _recv(self) -> str:
        if self.sock is None:
            raise RuntimeError("Socket ni povezan.")

        data = self.sock.recv(BUFFER_SIZE)
        if not data:
            raise RuntimeError("Robot je zaprl povezavo.")

        reply = data.decode("utf-8").strip()
        print("<<", reply)
        return reply

    def _send_expect(self, msg: str, expected: str) -> None:
        self._send(msg)
        reply = self._recv()

        if reply != expected:
            raise RuntimeError(f"Pri {msg!r} sem dobil: {reply}")

    def ping(self) -> None:
        self._send_expect("PING", "PONG")

    def movej(
        self,
        pose: Pose,
        speed: float = 200,
        zone: float = 50,
    ) -> None:
        msg = (
            f"MOVEJ|{pose.x}|{pose.y}|{pose.z}|"
            f"{pose.q1}|{pose.q2}|{pose.q3}|{pose.q4}|"
            f"{speed}|{zone}"
        )
        self._send_expect(msg, "OK")

    def movel(
        self,
        pose: Pose,
        speed: float = 50,
        zone: float = 0,
    ) -> None:
        msg = (
            f"MOVEL|{pose.x}|{pose.y}|{pose.z}|"
            f"{pose.q1}|{pose.q2}|{pose.q3}|{pose.q4}|"
            f"{speed}|{zone}"
        )
        self._send_expect(msg, "OK")

    def grip_close(self) -> None:
        self._send_expect("DO|1", "OK")

    def grip_open(self) -> None:
        self._send_expect("DO|0", "OK")

    def wait(self, seconds: float) -> None:
        self._send_expect(f"WAIT|{seconds}", "OK")

    def finish(self) -> None:
        self._send_expect("END", "BYE")


def run_cycle(robot: ABBRobot) -> None:
    print("Zacetek programa iz Pythona")

    robot.movej(
        TOCKA_NAD_POBIRANJEM,
        speed=200,
        zone=50,
    )

    robot.movel(
        TOCKA_POBIRANJE,
        speed=50,
        zone=0,
    )

    robot.grip_close()
    robot.wait(1)

    robot.movel(
        TOCKA_NAD_POBIRANJEM,
        speed=50,
        zone=50,
    )

    robot.movej(
        TOCKA_NAD_ODLAGANJEM,
        speed=200,
        zone=50,
    )

    robot.movel(
        TOCKA_ODLAGANJE,
        speed=50,
        zone=0,
    )

    robot.grip_open()
    robot.wait(1)

    robot.movel(
        TOCKA_NAD_ODLAGANJEM,
        speed=50,
        zone=10,
    )

    print("Cikel koncan")




def main() -> None:
    gui = GUIRunner()
    gui.run()
    robot = ABBRobot(ROBOT_IP, PORT)

    try:
        robot.connect()
        robot.ping()
        run_cycle(robot)
        robot.finish()
    finally:
        robot.close()



#********************************  GUI APPLICATION ******************************************************+

# ─────────────────────────────────────────────
#  GUI
# ─────────────────────────────────────────────

# Colour / style constants
BG          = "#0d1117"
PANEL_BG    = "#161b22"
BORDER      = "#30363d"
TEXT_DIM    = "#8b949e"
TEXT_MAIN   = "#e6edf3"
ACCENT      = "#58a6ff"
GREEN       = "#3fb950"
YELLOW      = "#d29922"
RED         = "#f85149"
MONO        = ("Consolas", 10)

STEP_PENDING  = ("○", TEXT_DIM,  PANEL_BG)
STEP_RUNNING  = ("◉", YELLOW,    "#1c2030")
STEP_DONE     = ("✓", GREEN,     "#0d1f18")
STEP_ERROR    = ("✗", RED,       "#1f0d0d")


STEPS = [
    "Connect to robot",
    "Ping robot",
    "MOVEJ → nad pobiranjem",
    "MOVEL → pobiranje",
    "Gripper CLOSE",
    "WAIT 1 s",
    "MOVEL ↑ nad pobiranjem",
    "MOVEJ → nad odlaganjem",
    "MOVEL → odlaganje",
    "Gripper OPEN",
    "WAIT 1 s",
    "MOVEL ↑ nad odlaganjem",
    "END",
]


class GUIRunner:
    """
    Launches a tkinter window that tracks each execution step in real time.
    Call  GUIRunner.run()  to start – it blocks until the window is closed.
    """

    def __init__(self) -> None:
        self.root = tk.Tk()
        self.root.title("ABB Robot – Program Runner")
        self.root.configure(bg=BG)
        self.root.resizable(False, False)

        self._step_vars: list[dict] = []   # per-step tkinter variables
        self._build_ui()

    # ── UI construction ───────────────────────────────────────────────────

    def _build_ui(self) -> None:
        root = self.root

        # ── Header ────────────────────────────────────────────────────────
        header = tk.Frame(root, bg=BG, pady=12)
        header.pack(fill="x", padx=20)

        title_font = tkfont.Font(family="Courier New", size=15, weight="bold")
        tk.Label(header, text="ABB ROBOT  //  CYCLE RUNNER",
                 font=title_font, fg=ACCENT, bg=BG).pack(side="left")

        self._status_label = tk.Label(header, text="IDLE",
                                      font=("Courier New", 10, "bold"),
                                      fg=TEXT_DIM, bg=BG)
        self._status_label.pack(side="right")

        tk.Frame(root, bg=BORDER, height=1).pack(fill="x", padx=20)

        # ── Step list ─────────────────────────────────────────────────────
        steps_frame = tk.Frame(root, bg=BG, pady=8)
        steps_frame.pack(fill="x", padx=20)

        for i, label in enumerate(STEPS):
            row = tk.Frame(steps_frame, bg=PANEL_BG,
                           highlightthickness=1,
                           highlightbackground=BORDER,
                           pady=6, padx=10)
            row.pack(fill="x", pady=2)

            icon_var  = tk.StringVar(value=STEP_PENDING[0])
            color_var = tk.StringVar(value=STEP_PENDING[1])

            icon_lbl = tk.Label(row, textvariable=icon_var,
                                font=("Courier New", 12, "bold"),
                                fg=STEP_PENDING[1], bg=PANEL_BG, width=2)
            icon_lbl.pack(side="left")

            num_lbl = tk.Label(row, text=f"{i+1:02d}",
                               font=MONO, fg=TEXT_DIM, bg=PANEL_BG, width=3)
            num_lbl.pack(side="left")

            text_lbl = tk.Label(row, text=label,
                                font=("Courier New", 10), fg=TEXT_DIM,
                                bg=PANEL_BG, anchor="w")
            text_lbl.pack(side="left", fill="x", expand=True)

            self._step_vars.append({
                "row":      row,
                "icon_lbl": icon_lbl,
                "text_lbl": text_lbl,
                "icon_var": icon_var,
            })

        # ── Separator ────────────────────────────────────────────────────
        tk.Frame(root, bg=BORDER, height=1).pack(fill="x", padx=20, pady=(6, 0))

        # ── Log panel ─────────────────────────────────────────────────────
        log_frame = tk.Frame(root, bg=BG, pady=8)
        log_frame.pack(fill="both", expand=True, padx=20)

        tk.Label(log_frame, text="LOG", font=("Courier New", 9, "bold"),
                 fg=TEXT_DIM, bg=BG).pack(anchor="w")

        self._log = tk.Text(log_frame, height=8, bg=PANEL_BG, fg=TEXT_MAIN,
                            font=MONO, relief="flat",
                            highlightthickness=1,
                            highlightbackground=BORDER,
                            insertbackground=ACCENT,
                            state="disabled", wrap="word")
        self._log.pack(fill="both", expand=True)

        # coloured tags for log lines
        self._log.tag_config("INFO",  foreground=TEXT_MAIN)
        self._log.tag_config("OK",    foreground=GREEN)
        self._log.tag_config("ERROR", foreground=RED)
        self._log.tag_config("WARN",  foreground=YELLOW)

        # ── Footer button ─────────────────────────────────────────────────
        footer = tk.Frame(root, bg=BG, pady=10)
        footer.pack(fill="x", padx=20)

        self._run_btn = tk.Button(
            footer, text="▶  RUN CYCLE",
            font=("Courier New", 11, "bold"),
            bg=ACCENT, fg="#0d1117",
            activebackground="#79c0ff", activeforeground="#0d1117",
            relief="flat", padx=20, pady=8,
            cursor="hand2",
            command=self._start_thread,
        )
        self._run_btn.pack(side="left")

        self._quit_btn = tk.Button(
            footer, text="✕  QUIT",
            font=("Courier New", 10),
            bg=PANEL_BG, fg=TEXT_DIM,
            activebackground=RED, activeforeground=TEXT_MAIN,
            relief="flat", padx=16, pady=8,
            highlightthickness=1, highlightbackground=BORDER,
            cursor="hand2",
            command=root.destroy,
        )
        self._quit_btn.pack(side="right")

        root.geometry("520x680")

    # ── Step state helpers ────────────────────────────────────────────────

    def _set_step(self, idx: int, state: str) -> None:
        """state: 'running' | 'done' | 'error'"""
        states = {
            "running": STEP_RUNNING,
            "done":    STEP_DONE,
            "error":   STEP_ERROR,
        }
        icon_ch, fg_col, bg_col = states[state]
        sv = self._step_vars[idx]

        def _apply():
            sv["icon_var"].set(icon_ch)
            sv["icon_lbl"].configure(fg=fg_col)
            sv["text_lbl"].configure(fg=fg_col if state != "running" else TEXT_MAIN)
            sv["row"].configure(bg=bg_col, highlightbackground=fg_col)
            sv["icon_lbl"].configure(bg=bg_col)
            sv["text_lbl"].configure(bg=bg_col)

        self.root.after(0, _apply)

    def _set_status(self, text: str, color: str = TEXT_DIM) -> None:
        self.root.after(0, lambda: self._status_label.configure(text=text, fg=color))

    def _log_line(self, text: str, tag: str = "INFO") -> None:
        def _write():
            self._log.configure(state="normal")
            self._log.insert("end", text + "\n", tag)
            self._log.see("end")
            self._log.configure(state="disabled")
        self.root.after(0, _write)

    def _reset_steps(self) -> None:
        for sv in self._step_vars:
            icon_ch, fg_col, bg_col = STEP_PENDING
            sv["icon_var"].set(icon_ch)
            sv["icon_lbl"].configure(fg=fg_col, bg=bg_col)
            sv["text_lbl"].configure(fg=TEXT_DIM, bg=bg_col)
            sv["row"].configure(bg=bg_col, highlightbackground=BORDER)

    # ── Execution in background thread ────────────────────────────────────

    def _start_thread(self) -> None:
        self._run_btn.configure(state="disabled")
        self._reset_steps()
        self._log_line("─" * 52)
        threading.Thread(target=self._execute, daemon=True).start()

    def _step(self, idx: int, desc: str, fn: Callable) -> None:
        """Mark step as running, call fn(), mark done or error."""
        self._set_step(idx, "running")
        self._set_status(f"STEP {idx+1}/{len(STEPS)}  {desc}", YELLOW)
        self._log_line(f"[{idx+1:02d}] {desc} …", "INFO")
        try:
            fn()
            self._set_step(idx, "done")
            self._log_line(f"     ✓ OK", "OK")
        except Exception as exc:
            self._set_step(idx, "error")
            self._log_line(f"     ✗ {exc}", "ERROR")
            raise  # propagate to _execute so we stop the cycle

    def _execute(self) -> None:
        robot = ABBRobot(ROBOT_IP, PORT)
        self._set_status("RUNNING", YELLOW)

        try:
            self._step(0,  "Connect",                 robot.connect)
            self._step(1,  "Ping",                    robot.ping)
            self._step(2,  "MOVEJ nad pobiranjem",    lambda: robot.movej(TOCKA_NAD_POBIRANJEM, speed=200, zone=50))
            self._step(3,  "MOVEL pobiranje",         lambda: robot.movel(TOCKA_POBIRANJE, speed=50, zone=0))
            self._step(4,  "Gripper CLOSE",           robot.grip_close)
            self._step(5,  "WAIT 1 s",                lambda: robot.wait(1))
            self._step(6,  "MOVEL ↑ nad pobiranjem",  lambda: robot.movel(TOCKA_NAD_POBIRANJEM, speed=50, zone=50))
            self._step(7,  "MOVEJ nad odlaganjem",    lambda: robot.movej(TOCKA_NAD_ODLAGANJEM, speed=200, zone=50))
            self._step(8,  "MOVEL odlaganje",         lambda: robot.movel(TOCKA_ODLAGANJE, speed=50, zone=0))
            self._step(9,  "Gripper OPEN",            robot.grip_open)
            self._step(10, "WAIT 1 s",                lambda: robot.wait(1))
            self._step(11, "MOVEL ↑ nad odlaganjem",  lambda: robot.movel(TOCKA_NAD_ODLAGANJEM, speed=50, zone=10))
            self._step(12, "END",                     robot.finish)

            self._set_status("DONE ✓", GREEN)
            self._log_line("Cikel uspešno končan.", "OK")

        except Exception:
            self._set_status("ERROR ✗", RED)
            self._log_line("Cikel prekinjen zaradi napake.", "ERROR")

        finally:
            robot.close()
            self.root.after(0, lambda: self._run_btn.configure(state="normal"))

    # ── Entry point ──────────────────────────────────────────────────────

    def run(self) -> None:
        """Block until the GUI window is closed."""
        self.root.mainloop()


# ─────────────────────────────────────────────
#  Main
# ────────────────────────────────────────────







if __name__ == "__main__":
    main()