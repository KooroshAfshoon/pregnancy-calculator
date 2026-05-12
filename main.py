import sys
import jdatetime
import datetime
from PySide6.QtWidgets import *
from PySide6.QtCore import Qt

# -------------------------
# Translation
# -------------------------
translations = {
    "fa": {
        "title": "🤰 محاسبه سن بارداری",
        "lmp": "LMP بر اساس",
        "sono": "بر اساس سونوگرافی",
        "last_period": "تاریخ آخرین پریود",
        "today": "تاریخ امروز",
        "calculate": "محاسبه",
        "back": "بازگشت",
        "sono_age": "سن در سونو (هفته / روز)",
        "sono_date": "تاریخ سونو",
        "weeks_days": "{} هفته و {} روز",
        "error": "خطا",
        "today_btn": "امروز"
    },
    "en": {
        "title": "🤰 Pregnancy Age Calculator",
        "lmp": "Based on LMP",
        "sono": "Based on Sonography",
        "last_period": "Last Menstrual Period",
        "today": "Today",
        "calculate": "Calculate",
        "back": "Back",
        "sono_age": "Age in Sono (weeks / days)",
        "sono_date": "Sonography Date",
        "weeks_days": "{} weeks and {} days",
        "error": "Error",
        "today_btn": "Today"
    }
}

# -------------------------
# Helpers
# -------------------------
def jalali_to_days(y, m, d):
    days = d
    for i in range(1, m):
        days += 31 if i <= 6 else 30 if i <= 11 else 29
    return days + (y * 365)

def create_input(placeholder=""):
    inp = QLineEdit()
    inp.setFixedHeight(36)
    inp.setAlignment(Qt.AlignCenter)
    inp.setPlaceholderText(placeholder)
    inp.setStyleSheet("""
        QLineEdit {
            border: 1px solid #ddd;
            border-radius: 10px;
            background: #fafafa;
            font-size: 14px;
        }
        QLineEdit:focus {
            border: 1px solid #7C4DFF;
            background: #ffffff;
        }
    """)
    return inp

def create_button(text):
    btn = QPushButton(text)
    btn.setCursor(Qt.PointingHandCursor)
    btn.setStyleSheet("""
        QPushButton {
            background: #7C4DFF;
            color: white;
            padding: 10px;
            border-radius: 12px;
            font-size: 14px;
        }
        QPushButton:hover {
            background: #6A3DF0;
        }
    """)
    return btn

def create_small_button(text):
    btn = QPushButton(text)
    btn.setCursor(Qt.PointingHandCursor)
    btn.setFixedHeight(36)
    btn.setStyleSheet("""
        QPushButton {
            background: #EDE7FF;
            color: #7C4DFF;
            border-radius: 10px;
            padding: 5px 10px;
            font-size: 13px;
        }
        QPushButton:hover {
            background: #DCD2FF;
        }
    """)
    return btn

def section_card():
    frame = QFrame()
    frame.setStyleSheet("""
        QFrame {
            background: white;
            border-radius: 16px;
        }
    """)
    layout = QVBoxLayout(frame)
    layout.setContentsMargins(15,15,15,15)
    layout.setSpacing(10)
    return frame, layout

# -------------------------
# App
# -------------------------
class App(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Pregnancy Calculator")
        self.resize(380, 500)
        self.setStyleSheet("background:#F5F3FF;")

        self.lang = "fa"  # "fa" or "en"
        self.calendar = "jalali"  # "jalali" or "gregorian"

        self.stack = QStackedWidget()
        main_layout = QVBoxLayout(self)
        main_layout.addWidget(self.stack)

        # Language & Calendar selectors
        top_bar = QHBoxLayout()
        self.lang_btn = create_small_button("EN" if self.lang=="fa" else "FA")
        self.cal_btn = create_small_button("Gregorian" if self.calendar=="jalali" else "Jalali")
        self.lang_btn.clicked.connect(self.switch_lang)
        self.cal_btn.clicked.connect(self.switch_calendar)
        top_bar.addWidget(self.lang_btn)
        top_bar.addWidget(self.cal_btn)
        main_layout.addLayout(top_bar)

        self.main_page()
        self.lmp_page()
        self.sono_page()

    def switch_lang(self):
        self.lang = "en" if self.lang=="fa" else "fa"
        self.lang_btn.setText("EN" if self.lang=="fa" else "FA")
        self.cal_btn.setText("Gregorian" if self.calendar=="jalali" else "Jalali")
        self.update_ui_texts()

    def switch_calendar(self):
        self.calendar = "gregorian" if self.calendar=="jalali" else "jalali"
        self.cal_btn.setText("Gregorian" if self.calendar=="gregorian" else "Jalali")
        self.update_ui_texts()

    def update_ui_texts(self):
        # update all labels/buttons with current language
        t = translations[self.lang]
        # Main page
        main = self.stack.widget(0)
        main.layout().itemAt(0).widget().setText(t["title"])
        main.layout().itemAt(1).widget().setText(t["lmp"])
        main.layout().itemAt(2).widget().setText(t["sono"])
        # LMP page
        self.calc_lmp_btn.setText(t["calculate"])
        self.back_lmp_btn.setText(t["back"])
        self.today_btn_lmp.setText(t["today_btn"])
        self.lmp_res.setText("")
        # Sono page
        self.calc_sono_btn.setText(t["calculate"])
        self.back_sono_btn.setText(t["back"])
        self.today_btn_sono.setText(t["today_btn"])
        self.sono_res.setText("")

    def switch(self, i):
        self.stack.setCurrentIndex(i)

    # -------------------------
    # MAIN PAGE
    # -------------------------
    def main_page(self):
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.setAlignment(Qt.AlignCenter)
        layout.setSpacing(20)

        title = QLabel(translations[self.lang]["title"])
        title.setStyleSheet("font-size:18px;")

        btn1 = create_button(translations[self.lang]["lmp"])
        btn2 = create_button(translations[self.lang]["sono"])

        btn1.clicked.connect(lambda: self.switch(1))
        btn2.clicked.connect(lambda: self.switch(2))

        layout.addWidget(title)
        layout.addWidget(btn1)
        layout.addWidget(btn2)
        self.stack.addWidget(page)

    # -------------------------
    # LMP PAGE
    # -------------------------
    def lmp_page(self):
        page = QWidget()
        layout = QVBoxLayout(page)
        card, c_layout = section_card()

        title = QLabel(translations[self.lang]["lmp"])
        title.setStyleSheet("font-size:15px;")

        self.l_y = create_input("1403")
        self.l_m = create_input("01")
        self.l_d = create_input("15")

        self.t_y = create_input("1403")
        self.t_m = create_input("02")
        self.t_d = create_input("01")

        def row(label_text, y, m, d, extra_widget=None):
            r = QVBoxLayout()
            lbl = QLabel(label_text)
            h = QHBoxLayout()
            h.addWidget(y)
            h.addWidget(m)
            h.addWidget(d)
            if extra_widget:
                h.addWidget(extra_widget)
            r.addWidget(lbl)
            r.addLayout(h)
            return r

        self.today_btn_lmp = create_small_button(translations[self.lang]["today_btn"])
        self.today_btn_lmp.clicked.connect(self.set_today_lmp)

        c_layout.addLayout(row(translations[self.lang]["last_period"], self.l_y, self.l_m, self.l_d))
        c_layout.addLayout(row(translations[self.lang]["today"], self.t_y, self.t_m, self.t_d, self.today_btn_lmp))

        self.calc_lmp_btn = create_button(translations[self.lang]["calculate"])
        self.back_lmp_btn = create_button(translations[self.lang]["back"])

        self.lmp_res = QLabel("")
        self.lmp_res.setAlignment(Qt.AlignCenter)

        self.calc_lmp_btn.clicked.connect(self.calc_lmp)
        self.back_lmp_btn.clicked.connect(lambda: self.switch(0))

        c_layout.addWidget(self.calc_lmp_btn)
        c_layout.addWidget(self.lmp_res)
        c_layout.addWidget(self.back_lmp_btn)

        layout.addWidget(card)
        self.stack.addWidget(page)

    def set_today_lmp(self):
        if self.calendar == "jalali":
            j = jdatetime.date.today()
            self.t_y.setText(str(j.year))
            self.t_m.setText(str(j.month))
            self.t_d.setText(str(j.day))
        else:
            g = datetime.date.today()
            self.t_y.setText(str(g.year))
            self.t_m.setText(str(g.month))
            self.t_d.setText(str(g.day))

    def calc_lmp(self):
        try:
            ly, lm, ld = int(self.l_y.text()), int(self.l_m.text()), int(self.l_d.text())
            ty, tm, td = int(self.t_y.text()), int(self.t_m.text()), int(self.t_d.text())

            if self.calendar == "jalali":
                diff = jalali_to_days(ty, tm, td) - jalali_to_days(ly, lm, ld)
            else:
                d1 = datetime.date(ly, lm, ld)
                d2 = datetime.date(ty, tm, td)
                diff = (d2 - d1).days

            w, d = diff // 7, diff % 7
            self.lmp_res.setText(translations[self.lang]["weeks_days"].format(w,d))

        except:
            self.lmp_res.setText(translations[self.lang]["error"])
    def sono_page(self):
        page = QWidget()
        layout = QVBoxLayout(page)
        card, c_layout = section_card()

        title = QLabel(translations[self.lang]["sono"])
        title.setStyleSheet("font-size:15px;")

        self.ga_w = create_input("12")
        self.ga_d = create_input("3")

        self.s_y = create_input("1403")
        self.s_m = create_input("01")
        self.s_d = create_input("20")

        self.ty = create_input("1403")
        self.tm = create_input("02")
        self.td = create_input("01")

        def row(label_text, *widgets):
            r = QVBoxLayout()
            lbl = QLabel(label_text)
            h = QHBoxLayout()
            for w in widgets:
                h.addWidget(w)
            r.addWidget(lbl)
            r.addLayout(h)
            return r

        self.today_btn_sono = create_small_button(translations[self.lang]["today_btn"])
        self.today_btn_sono.clicked.connect(self.set_today_sono)

        c_layout.addLayout(row(translations[self.lang]["sono_age"], self.ga_w, self.ga_d))
        c_layout.addLayout(row(translations[self.lang]["sono_date"], self.s_y, self.s_m, self.s_d))
        c_layout.addLayout(row(translations[self.lang]["today"], self.ty, self.tm, self.td, self.today_btn_sono))

        self.calc_sono_btn = create_button(translations[self.lang]["calculate"])
        self.back_sono_btn = create_button(translations[self.lang]["back"])

        self.sono_res = QLabel("")
        self.sono_res.setAlignment(Qt.AlignCenter)

        self.calc_sono_btn.clicked.connect(self.calc_sono)
        self.back_sono_btn.clicked.connect(lambda: self.switch(0))

        c_layout.addWidget(self.calc_sono_btn)
        c_layout.addWidget(self.sono_res)
        c_layout.addWidget(self.back_sono_btn)

        layout.addWidget(card)
        self.stack.addWidget(page)

    def set_today_sono(self):
        if self.calendar == "jalali":
            j = jdatetime.date.today()
            self.ty.setText(str(j.year))
            self.tm.setText(str(j.month))
            self.td.setText(str(j.day))
        else:
            g = datetime.date.today()
            self.ty.setText(str(g.year))
            self.tm.setText(str(g.month))
            self.td.setText(str(g.day))

    def calc_sono(self):
        try:
            gw, gd = int(self.ga_w.text()), int(self.ga_d.text())
            sy, sm, sd = int(self.s_y.text()), int(self.s_m.text()), int(self.s_d.text())
            ty, tm, td = int(self.ty.text()), int(self.tm.text()), int(self.td.text())

            if self.calendar == "jalali":
                diff = jalali_to_days(ty, tm, td) - jalali_to_days(sy, sm, sd)
            else:
                d1 = datetime.date(sy, sm, sd)
                d2 = datetime.date(ty, tm, td)
                diff = (d2 - d1).days

            total = gw * 7 + gd + diff
            w, d = total // 7, total % 7
            self.sono_res.setText(translations[self.lang]["weeks_days"].format(w,d))

        except:
            self.sono_res.setText(translations[self.lang]["error"])
# -------------------------
app = QApplication(sys.argv)
window = App()
window.show()
sys.exit(app.exec())