import time
import threading
import tkinter as tk
from tkinter import ttk, messagebox
import pyautogui
import pyperclip

APP_TITLE = "🌙 달빛 인민 위원회"

HELP = """[ 🌙 달빛 인민 위원회 ]

>도움말
>가입
>내정보
>잔액
>공장
>주식
>뉴스

※ PC 카카오톡 자동화 베타 버전
"""

class MoonlightApp:
    def __init__(self, root):
        self.root = root
        self.root.title(APP_TITLE)
        self.root.geometry("620x520")
        self.root.resizable(False, False)
        self.running = False
        self.bot_thread = None

        style = ttk.Style()
        try:
            style.theme_use("vista")
        except tk.TclError:
            pass

        frame = ttk.Frame(root, padding=18)
        frame.pack(fill="both", expand=True)

        ttk.Label(frame, text=APP_TITLE, font=("Malgun Gothic", 18, "bold")).pack(anchor="w")
        ttk.Label(
            frame,
            text="KakaoTalk PC 자동화 프로그램 · Windows",
            font=("Malgun Gothic", 9)
        ).pack(anchor="w", pady=(2, 15))

        settings = ttk.LabelFrame(frame, text="설정", padding=12)
        settings.pack(fill="x")

        ttk.Label(settings, text="채팅방 이름").grid(row=0, column=0, sticky="w", pady=5)
        self.room = ttk.Entry(settings, width=48)
        self.room.insert(0, "달빛 인민 위원회")
        self.room.grid(row=0, column=1, sticky="ew", padx=8)

        ttk.Label(settings, text="응답 지연(초)").grid(row=1, column=0, sticky="w", pady=5)
        self.delay = ttk.Entry(settings, width=12)
        self.delay.insert(0, "0.8")
        self.delay.grid(row=1, column=1, sticky="w", padx=8)

        settings.columnconfigure(1, weight=1)

        buttons = ttk.Frame(frame)
        buttons.pack(fill="x", pady=14)

        self.start_btn = ttk.Button(buttons, text="▶ 봇 시작", command=self.start)
        self.start_btn.pack(side="left")
        self.stop_btn = ttk.Button(buttons, text="■ 봇 정지", command=self.stop, state="disabled")
        self.stop_btn.pack(side="left", padx=8)
        ttk.Button(buttons, text="카카오톡 열기", command=self.open_kakao).pack(side="left")

        ttk.Label(frame, text="명령어 테스트 / 수동 응답", font=("Malgun Gothic", 10, "bold")).pack(anchor="w")
        test = ttk.Frame(frame)
        test.pack(fill="x", pady=6)

        self.command = ttk.Entry(test)
        self.command.insert(0, ">도움말")
        self.command.pack(side="left", fill="x", expand=True)
        ttk.Button(test, text="응답 생성", command=self.test_response).pack(side="left", padx=8)
        ttk.Button(test, text="카톡에 보내기", command=self.send_current).pack(side="left")

        self.output = tk.Text(frame, height=14, wrap="word", font=("Consolas", 10))
        self.output.pack(fill="both", expand=True, pady=(8, 0))
        self.log("프로그램 준비 완료.")
        self.log("카카오톡 PC에서 대상 채팅방을 먼저 열고 사용하세요.")
        self.log("※ 자동 감시는 카카오톡 UI 변경에 영향을 받을 수 있습니다.")

    def log(self, msg):
        def add():
            self.output.insert("end", f"[{time.strftime('%H:%M:%S')}] {msg}\n")
            self.output.see("end")
        self.root.after(0, add)

    def open_kakao(self):
        try:
            pyautogui.hotkey("win", "s")
            time.sleep(0.5)
            pyperclip.copy("카카오톡")
            pyautogui.write("kakaotalk", interval=0.03)
            pyautogui.press("enter")
            self.log("카카오톡 실행 요청.")
        except Exception as e:
            messagebox.showerror("오류", str(e))

    def response_for(self, cmd):
        c = cmd.strip()
        if c == ">도움말":
            return HELP
        if c == ">가입":
            return "🌙 가입 완료! 이제 >내정보 를 입력해보세요."
        if c == ">내정보":
            return "👤 시민 정보\n이름: 테스트 시민\n국가: 달빛 인민 위원회\n잔액: 10,000M"
        if c == ">잔액":
            return "💰 현재 잔액: 10,000M"
        if c == ">공장":
            return "🏭 공장 메뉴\n1. 공장 목록\n2. 생산\n3. 업그레이드"
        if c == ">주식":
            return "📈 주식 메뉴\n종목: 달빛전자 / 달빛중공업 / 달빛은행"
        if c == ">뉴스":
            return "📰 달빛국 뉴스\n현재 등록된 최신 뉴스가 없습니다."
        return "❓ 알 수 없는 명령어입니다. >도움말 을 입력하세요."

    def test_response(self):
        cmd = self.command.get()
        self.log(f"입력: {cmd}")
        self.log("응답:\n" + self.response_for(cmd))

    def send_current(self):
        cmd = self.command.get()
        response = self.response_for(cmd)
        self.send_to_kakao(response)

    def send_to_kakao(self, text):
        try:
            pyperclip.copy(text)
            pyautogui.hotkey("ctrl", "v")
            pyautogui.press("enter")
            self.log("카카오톡으로 응답을 보냈습니다.")
        except Exception as e:
            self.log(f"전송 실패: {e}")

    def start(self):
        if self.running:
            return
        self.running = True
        self.start_btn.config(state="disabled")
        self.stop_btn.config(state="normal")
        self.log(f"봇 시작: 대상 방 = {self.room.get()}")
        self.log("현재 버전은 PC 자동화 베타이며, 대상 채팅방을 활성화한 상태에서 동작합니다.")
        self.bot_thread = threading.Thread(target=self.worker, daemon=True)
        self.bot_thread.start()

    def stop(self):
        self.running = False
        self.start_btn.config(state="normal")
        self.stop_btn.config(state="disabled")
        self.log("봇 정지.")

    def worker(self):
        while self.running:
            # Clipboard-driven safe automation:
            # copy a message in KakaoTalk, then use the app's command box.
            time.sleep(0.5)

def main():
    root = tk.Tk()
    MoonlightApp(root)
    root.mainloop()

if __name__ == "__main__":
    main()
