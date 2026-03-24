import sys
import random
import os
import json
import requests
import wave
import array
import math
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QPushButton, QLabel, 
    QVBoxLayout, QHBoxLayout, QWidget, QTextEdit,
    QDialog, QLineEdit, QMessageBox, QDialogButtonBox,
    QSizePolicy, QSlider, QTabWidget, QGridLayout
)
from PyQt6.QtCore import Qt, QTimer, QSettings
from PyQt6.QtGui import QFont, QIcon, QPixmap, QPainter, QTextCursor
from PyQt6.QtSvg import QSvgRenderer
from sound_manager import SoundManager

# --- KONFIGURACE A KATALOG ---

# Globální katalog všech předmětů ve hře
ITEM_CATALOG = [
    # Zbraně (Weapon) - zvyšují útok
    {"name": "Rusty Dagger", "type": "weapon", "stat": "attack", "bonus": 2, "price": 20, "icon": "rusty_dagger.svg"},
    {"name": "Iron Sword", "type": "weapon", "stat": "attack", "bonus": 5, "price": 50, "icon": "iron_sword.svg"},
    {"name": "Steel Sword", "type": "weapon", "stat": "attack", "bonus": 8, "price": 95, "icon": "steel_sword.svg"},
    {"name": "Knight Blade", "type": "weapon", "stat": "attack", "bonus": 12, "price": 160, "icon": "knight_blade.svg"},
    {"name": "War Axe", "type": "weapon", "stat": "attack", "bonus": 15, "price": 220, "icon": "war_axe.svg"},
    {"name": "Elven Longbow", "type": "weapon", "stat": "attack", "bonus": 18, "price": 280, "icon": "elven_longbow.svg"},
    {"name": "Mythril Spear", "type": "weapon", "stat": "attack", "bonus": 22, "price": 360, "icon": "mythril_spear.svg"},
    {"name": "Dragonfang", "type": "weapon", "stat": "attack", "bonus": 28, "price": 480, "icon": "dragonfang.svg"},
    {"name": "Cursed Blade", "type": "weapon", "stat": "attack", "bonus": 36, "price": 880, "icon": "cursed_blade.svg"},
    {"name": "Hammer of Justice", "type": "weapon", "stat": "attack", "bonus": 43, "price": 1200, "icon": "hammer_of_justice.svg"},
    {"name": "Enchanted Crossbow", "type": "weapon", "stat": "attack", "bonus": 50, "price": 1650, "icon": "enchanted_crossbow.svg"},
    
    # Helmy (Head) - zvyšují obranu
    {"name": "Leather Cap", "type": "head", "stat": "defense", "bonus": 1, "price": 15, "icon": "leather_cap.svg"},
    {"name": "Iron Helmet", "type": "head", "stat": "defense", "bonus": 2, "price": 40, "icon": "iron_helmet.svg"},
    {"name": "Steel Helmet", "type": "head", "stat": "defense", "bonus": 4, "price": 85, "icon": "steel_helmet.svg"},
    {"name": "Knight Great Helm", "type": "head", "stat": "defense", "bonus": 6, "price": 150, "icon": "knight_great_helm.svg"},
    {"name": "Mythril Helm", "type": "head", "stat": "defense", "bonus": 9, "price": 250, "icon": "mythril_helm.svg"},
    
    # Brnění (Torso) - zvyšují obranu
    {"name": "Padded Vest", "type": "torso", "stat": "defense", "bonus": 1, "price": 25, "icon": "padded_vest.svg"},
    {"name": "Leather Armor", "type": "torso", "stat": "defense", "bonus": 2, "price": 60, "icon": "leather_armor.svg"},
    {"name": "Chain Mail", "type": "torso", "stat": "defense", "bonus": 4, "price": 120, "icon": "chain_mail.svg"},
    {"name": "Scale Armor", "type": "torso", "stat": "defense", "bonus": 6, "price": 190, "icon": "scale_armor.svg"},
    {"name": "Plate Armor", "type": "torso", "stat": "defense", "bonus": 8, "price": 270, "icon": "plate_armor.svg"},
    {"name": "Mythril Plate", "type": "torso", "stat": "defense", "bonus": 12, "price": 420, "icon": "mythril_plate.svg"},
    {"name": "Dragonhide Armor", "type": "torso", "stat": "defense", "bonus": 20, "price": 1620, "icon": "dragonhide_armor.svg"},
    {"name": "Colossus Armor", "type": "torso", "stat": "defense", "bonus": 25, "price": 2130, "icon": "colossus_armor.svg"},
    
    # Boty (Legs) - zvyšují obranu
    {"name": "Leather Boots", "type": "legs", "stat": "defense", "bonus": 1, "price": 20, "icon": "leather_boots.svg"},
    {"name": "Iron Greaves", "type": "legs", "stat": "defense", "bonus": 2, "price": 45, "icon": "iron_greaves.svg"},
    {"name": "Steel Greaves", "type": "legs", "stat": "defense", "bonus": 4, "price": 90, "icon": "steel_greaves.svg"},
    {"name": "Plate Greaves", "type": "legs", "stat": "defense", "bonus": 6, "price": 160, "icon": "plate_greaves.svg"},
    {"name": "Mythril Greaves", "type": "legs", "stat": "defense", "bonus": 9, "price": 280, "icon": "mythril_greaves.svg"},
    
    # Lektvary (Consumable)
    {"name": "Health Potion", "type": "consumable", "stat": "potions", "bonus": 1, "price": 15, "icon": "potion.wav"}
]

# Mapa ikon pro rychlejší dohledávání v UI
ICON_MAP = {it['name']: it['icon'] for it in ITEM_CATALOG}
# Přidání výchozích ikon pro prázdné sloty
ICON_MAP.update({
    "": "empty_weapon.svg", # Default pro prázdné jméno
    "empty_head": "empty_head.svg",
    "empty_torso": "empty_torso.svg",
    "empty_legs": "empty_legs.svg",
    "empty_weapon": "empty_weapon.svg"
})

# Globální styly pro moderní tmavý vzhled aplikace (QSS)
APP_QSS = """
/* Stylizace hlavního okna a dialogů */
QMainWindow, QDialog { background: #0f1220; }
QWidget#central { background: #111527; border: 1px solid rgba(255,255,255,0.06); border-radius: 12px; }

/* Záložky v obchodě */
QTabWidget::pane { border: 1px solid #2a315a; background: #111527; border-radius: 8px; margin-top: -1px; }
QTabBar::tab { background: #1a1f3a; color: #9aa0b4; padding: 8px 12px; border-top-left-radius: 6px; border-top-right-radius: 6px; border: 1px solid #2a315a; border-bottom: none; margin-right: 2px; }
QTabBar::tab:selected { background: #2a315a; color: #ffffff; font-weight: bold; }
QTabWidget QWidget { background: #111527; }

/* Textové popisky */
QLabel { color: #e6e9f3; }
QLabel#versionLabel { color: #9aa0b4; font-size: 10px; }
QLabel#goldLabel { font-size: 16px; font-weight: bold; color: #ffd700; margin-bottom: 10px; }

/* Vstupní pole a textové editory */
QLineEdit { background: #171a2a; border: 1px solid rgba(255,255,255,.08); border-radius: 8px; color: #e6e9f3; padding: 6px 8px; }
QTextEdit#log { background: #171a2a; border: 1px solid rgba(255,255,255,.08); border-radius: 10px; color: #e6e9f3; font-family: 'Segoe UI', Arial; font-size: 13px; }

/* Obecná tlačítka */
QPushButton { 
    padding: 8px 14px; 
    border-radius: 10px; 
    border: 1px solid rgba(255,255,255,.08); 
    background: #2a315a; 
    color: #e6e9f3; 
}
QPushButton:hover { background: #33407a; }
QPushButton:pressed { background: #23294d; }

/* Barevné varianty tlačítek pro různé akce */
QPushButton#exploreBtn { background: #4f7cff; border-color: rgba(79,124,255,.4); }
QPushButton#shopBtn { background: #4CAF50; }
QPushButton#restBtn { background: #f2994a; }
QPushButton#returnTownBtn { background: #9bb4ff; color: #0f1220; }
QPushButton#attackBtn { background: #ef4444; }
QPushButton#usePotionBtn { background: #22c55e; }
QPushButton#fleeBtn { background: #a855f7; }
QPushButton:disabled { background: #1a1f3a; color: #4a5068; border-color: #111527; }

/* Malá kruhová tlačítka v záhlaví */
QPushButton#settingsBtn, QPushButton#fullscreenBtn { 
    font-size: 16px; 
    background-color: #1a1f3a; 
    border-radius: 15px; 
    border: 1px solid #2a315a; 
    min-width: 30px; min-height: 30px;
    padding: 0;
}

/* Styl pro Tooltipy (popisky při najetí myší) */
QToolTip {
    background-color: #2a315a;
    color: #ffffff;
    border: 1px solid #4f7cff;
    border-radius: 4px;
    padding: 4px;
    font-weight: bold;
}
"""

class LoginDialog(QDialog):
    """
    Dialogové okno pro přihlášení uživatele.
    Zajišťuje komunikaci se serverem a ověření identity.
    """
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Pcherské Legendy - Přihlášení")
        self.setFixedSize(350, 250)
        
        layout = QVBoxLayout()
        
        # Stav připojení k API serveru
        self.connection_label = QLabel("Kontrola připojení k serveru...")
        self.connection_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        self.username_input = QLineEdit()
        self.username_input.setPlaceholderText("Uživatelské jméno")
        
        self.password_input = QLineEdit()
        self.password_input.setPlaceholderText("Heslo")
        self.password_input.setEchoMode(QLineEdit.EchoMode.Password)
        
        self.login_button = QPushButton("Přihlásit se")
        self.register_button = QPushButton("Registrovat")
        self.retry_button = QPushButton("Zkusit znovu")
        
        layout.addWidget(self.connection_label)
        layout.addWidget(self.username_input)
        layout.addWidget(self.password_input)
        layout.addWidget(self.login_button)
        layout.addWidget(self.register_button)
        layout.addWidget(self.retry_button)
        
        self.setLayout(layout)
        
        # Propojení signálů a slotů
        self.login_button.clicked.connect(self.login)
        self.register_button.clicked.connect(self.register)
        self.retry_button.clicked.connect(self.check_connection)
        
        self.check_connection()
    
    def check_connection(self):
        """Ověří dostupnost API serveru a podle toho povolí/zakáže tlačítka."""
        self.connection_label.setText("Kontrola připojení...")
        if self.test_connection():
            self.connection_label.setText("✅ Připojeno k serveru")
            self.connection_label.setStyleSheet("color: #22c55e;")
            self.login_button.setEnabled(True)
            self.register_button.setEnabled(True)
        else:
            self.connection_label.setText("❌ Nelze se připojit k serveru")
            self.connection_label.setStyleSheet("color: #ef4444;")
            self.login_button.setEnabled(False)
            self.register_button.setEnabled(False)
    
    def test_connection(self):
        """Pokusí se o základní GET požadavek na API."""
        try:
            return requests.get('http://127.0.0.1:5000/api/highscores', timeout=3).status_code == 200
        except:
            return False
    
    def login(self):
        """Odešle přihlašovací údaje na server."""
        username, password = self.username_input.text(), self.password_input.text()
        if not username or not password:
            QMessageBox.warning(self, "Chyba", "Vyplňte všechna pole.")
            return
        
        try:
            res = requests.post('http://127.0.0.1:5000/api/login', json={'username': username, 'password': password}, timeout=5)
            data = res.json()
            if data.get('success'):
                self.user_data = data
                self.accept()
            else:
                QMessageBox.warning(self, "Chyba", data.get('message', "Neplatné údaje."))
        except Exception as e:
            QMessageBox.critical(self, "Chyba", f"Server neodpovídá: {e}")
    
    def register(self):
        """Otevře dialog pro registraci nového účtu."""
        if RegisterDialog(self).exec() == QDialog.DialogCode.Accepted:
            QMessageBox.information(self, "Registrace", "Účet vytvořen! Nyní se můžete přihlásit.")

class RegisterDialog(QDialog):
    """
    Dialog pro registraci nového uživatelského účtu.
    """
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Registrace")
        self.setFixedSize(320, 220)
        
        layout = QVBoxLayout()
        self.username_input = QLineEdit(); self.username_input.setPlaceholderText("Uživatelské jméno")
        self.password_input = QLineEdit(); self.password_input.setPlaceholderText("Heslo")
        self.password_input.setEchoMode(QLineEdit.EchoMode.Password)
        
        self.status_label = QLabel(""); self.status_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        create_btn = QPushButton("Vytvořit účet")
        cancel_btn = QPushButton("Zrušit")
        create_btn.clicked.connect(self.create_account)
        cancel_btn.clicked.connect(self.reject)
        
        layout.addWidget(QLabel("Nová registrace"))
        layout.addWidget(self.username_input)
        layout.addWidget(self.password_input)
        layout.addWidget(self.status_label)
        layout.addWidget(create_btn)
        layout.addWidget(cancel_btn)
        self.setLayout(layout)

    def create_account(self):
        """Odesílá registrační data na server."""
        u, p = self.username_input.text().strip(), self.password_input.text().strip()
        if not u or not p: return
        try:
            res = requests.post('http://127.0.0.1:5000/api/register', json={'username': u, 'password': p}, timeout=5).json()
            if res.get('success'): self.accept()
            else: self.status_label.setText(res.get('message', 'Chyba')); self.status_label.setStyleSheet("color: #ef4444;")
        except: self.status_label.setText("Chyba serveru"); self.status_label.setStyleSheet("color: #ef4444;")

class OptionsDialog(QDialog):
    """
    Dialog pro nastavení zvuků a hudby.
    Ukládá preference do QSettings.
    """
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Nastavení")
        self.settings = QSettings("DungeonExplorer", "RPGGame")
        self.resize(400, 200)
        
        layout = QVBoxLayout()
        # Nastavení hudby
        m_lay = QHBoxLayout(); m_lay.addWidget(QLabel("Hudba:"))
        self.m_slider = QSlider(Qt.Orientation.Horizontal); self.m_slider.setRange(0, 100)
        self.m_slider.setValue(self.settings.value("music_volume", 50, type=int))
        m_lay.addWidget(self.m_slider); layout.addLayout(m_lay)

        # Nastavení efektů
        e_lay = QHBoxLayout(); e_lay.addWidget(QLabel("Efekty:"))
        self.e_slider = QSlider(Qt.Orientation.Horizontal); self.e_slider.setRange(0, 100)
        self.e_slider.setValue(self.settings.value("effects_volume", 50, type=int))
        e_lay.addWidget(self.e_slider); layout.addLayout(e_lay)

        btns = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        btns.accepted.connect(self.save); btns.rejected.connect(self.reject)
        layout.addWidget(btns); self.setLayout(layout)
        
    def save(self):
        """Uloží zvolené hodnoty do QSettings."""
        self.settings.setValue("music_volume", self.m_slider.value())
        self.settings.setValue("effects_volume", self.e_slider.value())
        self.accept()
        
class EventDialog(QDialog):
    """
    Zobrazuje náhodnou událost v dungeonu a umožňuje hráči volbu.
    """
    def __init__(self, event_data, parent=None):
        super().__init__(parent)
        self.setWindowTitle(event_data.get("title", "Událost"))
        self.resize(400, 250); self.event = event_data; self.selected_choice = None
        
        layout = QVBoxLayout()
        title = QLabel(self.event.get("title", "Něco se děje..."))
        title.setFont(QFont("Arial", 12, QFont.Weight.Bold)); layout.addWidget(title)

        desc = QLabel(self.event.get("description", "")); desc.setWordWrap(True); layout.addWidget(desc)

        for choice in self.event.get("choices", []):
            btn = QPushButton(choice.get("label", "Pokračovat"))
            btn.clicked.connect(lambda _, c=choice: self._select(c))
            layout.addWidget(btn)

        self.setLayout(layout)

    def _select(self, choice):
        self.selected_choice = choice; self.accept()

class ShopDialog(QDialog):
    """
    Městský obchod s vybavením a lektvary.
    Používá globální ITEM_CATALOG pro zobrazení předmětů.
    """
    def __init__(self, character, sound_manager, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Obchod")
        self.resize(600, 500)
        self.character, self.sound_manager = character, sound_manager
        self.settings = QSettings("DungeonExplorer", "RPGGame")
        self.char_id = str(self.character.get('id', '0'))

        # Načtení dat o vlastnictví a vybavení
        self._load_player_data()
        self.setup_ui()
        
        # Hudba v obchodě
        self.sound_manager.stop_music()
        if self.settings.value("music_volume", 50, type=int) > 0:
            self.sound_manager.play_music("background_shop.wav", True)

    def _load_player_data(self):
        """Načte seznamy vlastněných předmětů a aktuální vybavení."""
        def load_l(k): return json.loads(self.settings.value(f"{k}_{self.char_id}", "[]", type=str))
        self.owned = {
            'weapon': load_l("owned_weapons"), 'head': load_l("owned_heads"),
            'torso': load_l("owned_torsos"), 'legs': load_l("owned_legs")
        }
        self.equipped = {
            'weapon': self.settings.value(f"equipped_weapon_{self.char_id}", "", type=str),
            'head': self.settings.value(f"equipped_head_{self.char_id}", "", type=str),
            'torso': self.settings.value(f"equipped_torso_{self.char_id}", "", type=str),
            'legs': self.settings.value(f"equipped_legs_{self.char_id}", "", type=str)
        }

    def setup_ui(self):
        """Vytvoří záložkové rozhraní obchodu."""
        layout = QVBoxLayout()
        self.gold_label = QLabel(f"Tvé zlato: {self.character['gold']} g")
        self.gold_label.setObjectName("goldLabel") # Pro QSS styling
        self.gold_label.setAlignment(Qt.AlignmentFlag.AlignCenter); layout.addWidget(self.gold_label)

        self.tabs = QTabWidget()
        self.tabs.setStyleSheet("""
            QTabBar::tab { color: #e6e9f3; font-weight: bold; padding: 10px; }
            QTabBar::tab:selected { background: #2a315a; }
        """)
        self.tab_widgets = {}
        categories = [("weapon", "Zbraně"), ("head", "Hlava"), ("torso", "Trup"), ("legs", "Nohy"), ("consumable", "Lektvary")]
        
        for cat_id, name in categories:
            w = QWidget(); self.tab_widgets[cat_id] = w
            self.tabs.addTab(w, name)

        self._refresh_tabs()
        layout.addWidget(self.tabs)
        
        self.status_label = QLabel(""); self.status_label.setAlignment(Qt.AlignmentFlag.AlignCenter); layout.addWidget(self.status_label)
        
        close_btn = QPushButton("Odejít"); close_btn.clicked.connect(self.accept); layout.addWidget(close_btn)
        self.setLayout(layout)
        self.setStyleSheet("QDialog { background: #0b0e1a; }")

    def _refresh_tabs(self):
        """Překreslí obsah všech záložek obchodu."""
        for cat_id, widget in self.tab_widgets.items():
            if widget.layout():
                # Vyčištění starého obsahu
                while widget.layout().count():
                    item = widget.layout().takeAt(0)
                    if item.widget(): item.widget().deleteLater()
                    elif item.layout():
                        while item.layout().count():
                            sub = item.layout().takeAt(0)
                            if sub.widget(): sub.widget().deleteLater()
            else: widget.setLayout(QVBoxLayout())
            
            # Naplnění záložky předměty z katalogu
            for item in [i for i in ITEM_CATALOG if i['type'] == cat_id]:
                widget.layout().addLayout(self._create_item_row(item))
            widget.layout().addStretch(1)

    def _create_item_row(self, item):
        """Vytvoří řádek s informacemi o předmětu a akčním tlačítkem."""
        row = QHBoxLayout()
        
        # Ikona
        icon = QLabel(); icon.setFixedSize(32, 32)
        try:
            path = os.path.join(os.path.dirname(__file__), "icons", item['icon'])
            if os.path.isfile(path):
                r = QSvgRenderer(path); px = QPixmap(32, 32); px.fill(Qt.GlobalColor.transparent)
                p = QPainter(px); r.render(p); p.end(); icon.setPixmap(px)
        except: pass
        row.addWidget(icon)

        # Informace
        bonus_txt = f"+{item['bonus']} {item['stat']}" if item['type'] != 'consumable' else "Léčení"
        info = QLabel(f"<b>{item['name']}</b> ({bonus_txt}) - {item['price']} g")
        info.setStyleSheet("color: #e6e9f3; font-size: 13px;") # Zlepšená čitelnost textu
        row.addWidget(info); row.addStretch(1)

        # Tlačítko (Koupit / Vybavit / Vybaveno)
        kind = item['type']
        if kind == 'consumable':
            btn = QPushButton("Koupit"); btn.clicked.connect(lambda _, i=item: self._buy_item(i))
        elif item['name'] in self.owned[kind]:
            is_eq = self.equipped[kind] == item['name']
            btn = QPushButton("Vybaveno" if is_eq else "Vybavit")
            btn.setEnabled(not is_eq); btn.clicked.connect(lambda _, i=item: self._equip_item(i))
        else:
            btn = QPushButton("Koupit"); btn.clicked.connect(lambda _, i=item: self._buy_item(i))
        
        row.addWidget(btn); return row

    def _buy_item(self, item):
        """Zpracuje nákup předmětu."""
        if self.character['gold'] < item['price']:
            self.status_label.setText("Nedostatek zlata!"); return
            
        self.character['gold'] -= item['price']
        kind = item['type']
        
        if kind == 'consumable':
            self.character['potions'] += item['bonus']
        else:
            self.owned[kind].append(item['name'])
            # Oprava plurálu pro 'legs' (nohy jsou již v plurálu)
            suffix = "s" if kind != "legs" else ""
            self.settings.setValue(f"owned_{kind}{suffix}_{self.char_id}", json.dumps(self.owned[kind]))
            
        self.gold_label.setText(f"Tvé zlato: {self.character['gold']} g")
        if self.settings.value("effects_volume", 50, type=int) > 0: self.sound_manager.play_sound("buy", True)
        self._refresh_tabs()

    def _equip_item(self, item):
        """Vybaví hráče vybraným předmětem."""
        kind = item['type']
        self.equipped[kind] = item['name']
        self.settings.setValue(f"equipped_{kind}_{self.char_id}", item['name'])
        self.status_label.setText(f"Vybaveno: {item['name']}")
        self._refresh_tabs()

class InnDialog(QDialog):
    """
    Hostinec slouží k léčení postavy a ukládání postupu hry.
    Za poplatek doplní zdraví na maximum.
    """
    def __init__(self, character, sound_manager, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Hostinec")
        self.setFixedSize(450, 300)
        self.character, self.sound_manager = character, sound_manager
        self.settings = QSettings("DungeonExplorer", "RPGGame")
        self.heal_cost = 20

        # Hudební kulisa hostince
        self.sound_manager.stop_music()
        if self.settings.value("music_volume", 50, type=int) > 0:
            self.sound_manager.play_music("background_inn.wav", True)

        layout = QVBoxLayout()
        title = QLabel("U Matěje"); title.setFont(QFont("Arial", 16, QFont.Weight.Bold))
        title.setAlignment(Qt.AlignmentFlag.AlignCenter); layout.addWidget(title)

        self.status_info = QLabel(f"Zlato: {self.character['gold']} | Životy: {self.character['health']}/{self.character['max_health']}")
        self.status_info.setStyleSheet("font-size: 14px; color: #e6e9f3;")
        self.status_info.setAlignment(Qt.AlignmentFlag.AlignCenter); layout.addWidget(self.status_info)

        btns = QHBoxLayout()
        save_btn = QPushButton("Uložit hru"); save_btn.clicked.connect(self.save_game)
        heal_btn = QPushButton(f"Vyléčit a uložit ({self.heal_cost} g)"); heal_btn.clicked.connect(self.heal_and_save)
        btns.addWidget(save_btn); btns.addWidget(heal_btn); layout.addLayout(btns)

        self.msg = QLabel(""); self.msg.setAlignment(Qt.AlignmentFlag.AlignCenter); layout.addWidget(self.msg)
        close_btn = QPushButton("Odejít"); close_btn.clicked.connect(self.accept); layout.addWidget(close_btn)
        self.setLayout(layout)

    def save_game(self):
        """Uloží aktuální stav postavy na server."""
        if self.parent(): self.parent().save_character()
        self.msg.setText("Hra uložena!"); self.msg.setStyleSheet("color: #22c55e;")
        if self.settings.value("effects_volume", 50, type=int) > 0: self.sound_manager.play_sound("save", True)

    def heal_and_save(self):
        """Vyléčí postavu za zlato a následně uloží hru."""
        if self.character['gold'] >= self.heal_cost:
            self.character['gold'] -= self.heal_cost
            self.character['health'] = self.character['max_health']
            self.save_game()
            self.status_info.setText(f"Zlato: {self.character['gold']} | Životy: {self.character['health']}/{self.character['max_health']}")
        else:
            self.msg.setText("Nedostatek zlata!"); self.msg.setStyleSheet("color: #ef4444;")

class CharacterSelectionDialog(QDialog):
    """
    Okno pro výběr existující postavy nebo vytvoření nové po přihlášení.
    """
    def __init__(self, user_id, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Výběr hrdiny"); self.setFixedSize(400, 350)
        self.user_id, self.selected_character = user_id, None
        
        layout = QVBoxLayout()
        self.chars_layout = QVBoxLayout()
        
        self.load_characters()
        
        new_btn = QPushButton("Vytvořit nového hrdinu"); new_btn.clicked.connect(self.create_character)
        layout.addWidget(QLabel("Vyberte si svého hrdinu:"))
        layout.addLayout(self.chars_layout)
        layout.addStretch(1)
        layout.addWidget(new_btn)
        self.setLayout(layout)
    
    def load_characters(self):
        """Načte seznam postav přiřazených k uživateli ze serveru."""
        while self.chars_layout.count():
            w = self.chars_layout.takeAt(0).widget()
            if w: w.deleteLater()
        
        try:
            res = requests.get(f'http://localhost:5000/api/characters?user_id={self.user_id}', timeout=5).json()
            if res.get('success'):
                for char in res['characters']:
                    btn = QPushButton(f"{char['name']} (Lvl {char['level']}, Skóre: {char.get('score', 0)})")
                    btn.clicked.connect(lambda _, c=char: self.select(c))
                    self.chars_layout.addWidget(btn)
        except: pass
    
    def select(self, character):
        self.selected_character = character; self.accept()
    
    def create_character(self):
        """Otevře dialog pro zadání jména nové postavy."""
        name, ok = QLineEdit.getText(self, "Nový hrdina", "Jméno postavy:")
        if ok and name.strip():
            try:
                res = requests.post('http://localhost:5000/api/characters', json={'name': name.strip(), 'user_id': self.user_id}, timeout=5).json()
                if res.get('success'): self.load_characters()
            except: pass

class EndScreenDialog(QDialog):
    """
    Zobrazuje závěrečnou obrazovku (Work in Progress) po poražení finálního bosse.
    """
    def __init__(self, score, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Konec hry")
        self.setFixedSize(400, 300)
        self.setStyleSheet("QDialog { background: #0f1220; } QLabel { color: #e6e9f3; }")
        
        layout = QVBoxLayout()
        layout.setContentsMargins(30, 30, 30, 30)
        layout.setSpacing(20)
        
        title = QLabel("KONEC")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title.setStyleSheet("font-size: 32px; font-weight: bold; color: #4f7cff;")
        layout.addWidget(title)
        
        thanks = QLabel("Děkujeme za zahrání naší hry!")
        thanks.setAlignment(Qt.AlignmentFlag.AlignCenter)
        thanks.setStyleSheet("font-size: 16px;")
        layout.addWidget(thanks)
        
        score_label = QLabel(f"Tvé celkové skóre: {score}")
        score_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        score_label.setStyleSheet("font-size: 18px; font-weight: bold; color: #ffd700;")
        layout.addWidget(score_label)
        
        layout.addStretch(1)
        
        btns = QHBoxLayout()
        town_btn = QPushButton("Zpět do města")
        town_btn.setStyleSheet("background: #4CAF50; padding: 10px;")
        town_btn.clicked.connect(self.accept) # Accept = Návrat do města
        
        exit_btn = QPushButton("Ukončit hru")
        exit_btn.setStyleSheet("background: #ef4444; padding: 10px;")
        exit_btn.clicked.connect(self.reject) # Reject = Vypnutí hry
        
        btns.addWidget(town_btn)
        btns.addWidget(exit_btn)
        layout.addLayout(btns)
        
        self.setLayout(layout)

class RPGGame(QMainWindow):
    """
    Hlavní třída hry Pcherské Legendy. 
    Spravuje herní logiku, uživatelské rozhraní a komunikaci se serverem.
    """
    def __init__(self):
        super().__init__()
        self.sound_manager = SoundManager()
        self.settings = QSettings("DungeonExplorer", "RPGGame")
        
        # Načtení a aplikace nastavení hlasitosti
        mv = self.settings.value("music_volume", 50, type=int)
        ev = self.settings.value("effects_volume", 50, type=int)
        self.sound_manager.set_music_volume(mv / 100.0)
        self.sound_manager.set_effects_volume(ev / 100.0)
        
        # Proces přihlášení
        login = LoginDialog()
        if login.exec() != QDialog.DialogCode.Accepted: sys.exit(0)
        self.user_data = login.user_data
        
        # Výběr hrdiny
        char_sel = CharacterSelectionDialog(self.user_data['user_id'])
        if char_sel.exec() != QDialog.DialogCode.Accepted: sys.exit(0)
        self.character = char_sel.selected_character
        
        # Inicializace herních dat a UI
        self._init_attributes()
        self.setWindowTitle(f"Pcherské Legendy - {self.character['name']}")
        self.resize(1000, 800); self.setMinimumSize(800, 600)
        
        # Herní stav
        self.current_room = "town"
        self.current_enemy = None
        self.dungeon = {"level": 1, "progress": 0, "steps_required": 20}
        self.content = {"events": {}, "enemies": {}, "boss": {}}

        self.setup_ui()
        self._load_game_resources()
        self.play_background_music()

    def _load_game_resources(self):
        """Načte zvuky a externí herní obsah (nepřátelé, události)."""
        self._create_sample_sounds()
        for s in ["attack", "potion", "explore", "click", "buy", "heal", "save"]:
            self.sound_manager.load_sound(s, f"{s}.wav")
        
        try:
            path = os.path.join(os.path.dirname(__file__), "data")
            with open(os.path.join(path, "events.json"), "r", encoding="utf-8") as f:
                self.content["events"] = json.load(f).get("levels", {})
            with open(os.path.join(path, "enemies.json"), "r", encoding="utf-8") as f:
                lvls = json.load(f).get("levels", {})
                self.content["boss"] = lvls.get("boss", {})
                self.content["enemies"] = {k: v for k, v in lvls.items() if k != "boss"}
        except: pass

    def setup_ui(self):
        """Sestaví hlavní rozhraní hry pomocí PyQt6 layoutů."""
        self.game_version = "v0.6.1"
        central = QWidget(); central.setObjectName("central"); self.setCentralWidget(central)
        main_layout = QVBoxLayout(); main_layout.setContentsMargins(15, 15, 15, 15); main_layout.setSpacing(10)
        
        # Horní lišta (Verze + Systémová tlačítka)
        header = QHBoxLayout()
        header.addWidget(QLabel(self.game_version))
        header.addStretch()
        
        self.fs_btn = QPushButton(); self.fs_btn.setObjectName("fullscreenBtn"); self.fs_btn.setFixedSize(30,30)
        self.fs_btn.clicked.connect(self.toggle_fullscreen)
        self._set_svg_icon(self.fs_btn, "fullscreen.svg", "⛶")
        
        set_btn = QPushButton("⚙"); set_btn.setObjectName("settingsBtn"); set_btn.setFixedSize(30,30)
        set_btn.clicked.connect(self.show_options_dialog)
        
        header.addWidget(self.fs_btn); header.addWidget(set_btn); main_layout.addLayout(header)
        
        # Sekce statistik a vybavení
        top_section = QHBoxLayout(); top_section.setSpacing(20)
        
        # 1. Základní statistiky (vlevo)
        self.stats_label = QLabel(); top_section.addWidget(self.stats_label, 1)

        # 2. Vybavení postavy (střed)
        self.equip_layout = QGridLayout(); self.equip_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.equip_layout.setSpacing(10)
        
        self.head_slot = QLabel(); self.torso_slot = QLabel(); self.legs_slot = QLabel(); self.weapon_slot = QLabel()
        for s in [self.head_slot, self.torso_slot, self.legs_slot, self.weapon_slot]:
            s.setFixedSize(50, 50); s.setAlignment(Qt.AlignmentFlag.AlignCenter)
            s.setStyleSheet("background: #1a1f3a; border: 1px solid #2a315a; border-radius: 8px;")

        # Armor vertically aligned (Column 0)
        self.equip_layout.addWidget(self.head_slot, 0, 0)
        self.equip_layout.addWidget(self.torso_slot, 1, 0)
        self.equip_layout.addWidget(self.legs_slot, 2, 0)
        
        # Weapon to the side (Column 1, Row 1 - next to torso)
        self.equip_layout.addWidget(self.weapon_slot, 1, 1)
        
        top_section.addLayout(self.equip_layout, 1)

        # 3. Atributy a body (vpravo)
        attrs_box = QVBoxLayout(); attrs_box.addWidget(QLabel("<b>Vlastnosti</b>"))
        self.attr_label = QLabel(); self.points_label = QLabel()
        r1, r2 = QHBoxLayout(), QHBoxLayout()
        self.str_btn = QPushButton("+ STR"); self.dex_btn = QPushButton("+ DEX")
        self.con_btn = QPushButton("+ CON"); self.int_btn = QPushButton("+ INT")
        for b, a in [(self.str_btn, 'strength'), (self.dex_btn, 'dexterity'), (self.con_btn, 'constitution'), (self.int_btn, 'intelligence')]:
            b.clicked.connect(lambda _, attr=a: self.allocate_point(attr))
        r1.addWidget(self.str_btn); r1.addWidget(self.dex_btn)
        r2.addWidget(self.con_btn); r2.addWidget(self.int_btn)
        attrs_box.addWidget(self.attr_label); attrs_box.addWidget(self.points_label)
        attrs_box.addLayout(r1); attrs_box.addLayout(r2); top_section.addLayout(attrs_box, 1)
        
        main_layout.addLayout(top_section); main_layout.addSpacing(10)

        # Informační oblast (Lokace + Souboj)
        self.location_label = QLabel(""); self.location_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.location_label.setStyleSheet("font-size: 14px; font-weight: bold; color: #9bb4ff;")
        self.combat_label = QLabel(""); self.combat_label.setMinimumHeight(100)
        self.combat_label.setAlignment(Qt.AlignmentFlag.AlignCenter); self.combat_label.setStyleSheet("color: #ef4444;")
        main_layout.addWidget(self.location_label); main_layout.addWidget(self.combat_label)

        # Herní deník (Log)
        log_box = QVBoxLayout(); log_box.addWidget(QLabel("<b>Deník hrdiny</b>"))
        self.log_display = QTextEdit(); self.log_display.setReadOnly(True)
        self.log_display.setObjectName("log") # Důležité pro propojení se stylem v APP_QSS
        log_box.addWidget(self.log_display); main_layout.addLayout(log_box, 1)

        # Ovládací tlačítka (Akce)
        actions = QWidget(); a_layout = QHBoxLayout(actions); a_layout.setContentsMargins(0, 5, 0, 0)
        self.explore_btn = QPushButton("Průzkum"); self.explore_btn.setObjectName("exploreBtn")
        shop_btn = QPushButton("Obchod"); rest_btn = QPushButton("Hostinec")
        self.return_town_btn = QPushButton("Zpět do města"); self.return_town_btn.setObjectName("returnTownBtn")
        att_btn = QPushButton("Útok"); att_btn.setObjectName("attackBtn")
        pot_btn = QPushButton("Lektvar"); pot_btn.setObjectName("usePotionBtn")
        flee_btn = QPushButton("Útěk"); flee_btn.setObjectName("fleeBtn")

        self.explore_btn.clicked.connect(self.explore_dungeon); shop_btn.clicked.connect(self.visit_shop)
        rest_btn.clicked.connect(self.rest_at_inn); self.return_town_btn.clicked.connect(self.return_to_town)
        att_btn.clicked.connect(self.attack_enemy); pot_btn.clicked.connect(self.use_potion)
        flee_btn.clicked.connect(self.flee_combat)

        a_layout.addWidget(self.explore_btn); a_layout.addWidget(shop_btn); a_layout.addWidget(rest_btn)
        a_layout.addStretch(1); a_layout.addWidget(self.return_town_btn)
        a_layout.addWidget(att_btn); a_layout.addWidget(pot_btn); a_layout.addWidget(flee_btn)

        # Seskupení widgetů pro snadné přepínání viditelnosti
        self.town_widgets = [shop_btn, rest_btn]
        self.combat_widgets = [att_btn, pot_btn, flee_btn]

        main_layout.addWidget(actions); central.setLayout(main_layout)
        self.update_stats(); self.update_location(); self.update_actions()

    def _set_svg_icon(self, btn, icon_name, fallback):
        """Pomocná metoda pro nastavení SVG ikony na tlačítko."""
        try:
            path = os.path.join(os.path.dirname(__file__), "icons", icon_name)
            if os.path.isfile(path):
                r = QSvgRenderer(path); px = QPixmap(20,20); px.fill(Qt.GlobalColor.transparent)
                p = QPainter(px); r.render(p); p.end(); btn.setIcon(QIcon(px))
            else: btn.setText(fallback)
        except: btn.setText(fallback)

    def update_stats(self):
        """Přepočítá statistiky a aktualizuje textové popisky v UI."""
        self._recalculate_total_stats()
        c = self.character; next_exp = 10 * max(1, c['level'])
        self.stats_label.setText(f"<b>{c['name']}</b> (Lvl {c['level']})<br>"
                                f"HP: {c['health']}/{c['max_health']}<br>"
                                f"Útok: {c['attack']} | Obrana: {c['defense']}<br>"
                                f"Zlato: {c['gold']} g | Skóre: {c.get('score',0)}<br>"
                                f"EXP: {c['exp']}/{next_exp}<br>"
                                f"Lektvary: {c.get('potions', 0)}")
        
        self.attr_label.setText(f"STR: {c.get('strength',5)} | DEX: {c.get('dexterity',5)}<br>"
                                f"CON: {c.get('constitution',10)} | INT: {c.get('intelligence',5)}")
        
        pts = c.get('stat_points', 0)
        self.points_label.setText(f"Volné body: {pts}" if pts > 0 else "")
        for b in [self.str_btn, self.dex_btn, self.con_btn, self.int_btn]: b.setVisible(pts > 0)
        self._update_equip_ui()
        
    def update_log(self, message):
        """Přidá zprávu do deníku a zajistí odrolování na konec."""
        self.log_display.append(message)
        self.log_display.moveCursor(QTextCursor.MoveOperation.End)
    
    def update_location(self):
        """Aktualizuje název aktuálně navštíveného místa."""
        if self.current_room == "town": 
            text = "Městské náměstí"
        else:
            lvl = self.dungeon['level']
            if lvl == 1:
                name = "Sewers"
            elif lvl == 2:
                name = "Goblin Warrens"
            else:
                name = f"Dungeon Lvl {lvl}"
            
            progress = self.dungeon['progress']
            total = self.dungeon['steps_required']
            text = f"{name} (Krok {progress}/{total})"
        self.location_label.setText(text)

    def update_actions(self):
        """Zobrazuje nebo skrývá tlačítka podle aktuálního herního stavu."""
        is_town = self.current_room == "town"
        in_fight = self.current_enemy is not None
        
        for w in self.town_widgets: w.setVisible(is_town)
        self.explore_btn.setVisible(not in_fight) # Skrýt průzkum během souboje
        self.return_town_btn.setVisible(not is_town and not in_fight)
        for w in self.combat_widgets: w.setVisible(in_fight)
        
        self.update_combat_display()
            
    def save_character(self):
        """Odešle aktuální data postavy na server k uložení."""
        try: requests.put(f'http://localhost:5000/api/characters/{self.character["id"]}', json=self.character, timeout=5)
        except: pass
            
    def toggle_fullscreen(self):
        """Přepíná okno mezi režimem celé obrazovky a normálním zobrazením."""
        if self.isFullScreen(): self.showNormal()
        else: self.showFullScreen()

    def show_options_dialog(self):
        """Otevře nastavení a aplikuje změny hlasitosti."""
        if OptionsDialog(self).exec():
            mv = self.settings.value("music_volume", 50, type=int)
            ev = self.settings.value("effects_volume", 50, type=int)
            self.sound_manager.set_music_volume(mv/100.0)
            self.sound_manager.set_effects_volume(ev/100.0)
            self.play_background_music()

    def play_background_music(self):
        """Spouští hudbu odpovídající aktuální situaci."""
        vol = self.settings.value("music_volume", 50, type=int)
        if vol <= 0: self.sound_manager.stop_music(); return
        
        track = "background.wav"
        if self.current_enemy:
            if self.current_enemy.get('is_boss'):
                # Pokusíme se načíst specifickou boss hudbu z dat nepřítele
                track = self.current_enemy.get('music', "background_boss.wav")
            else:
                track = "background.wav"
        elif self.current_room == "town":
            track = "background.wav"
            
        self.sound_manager.play_music(track, True)

    def _create_sample_sounds(self):
        """Vytvoří základní zvukové soubory, pokud ve složce sounds chybí."""
        os.makedirs('sounds', exist_ok=True)
        # Jednoduchá syntéza sinusových vln pro různé efekty
        sounds = {
            "attack.wav": (8000, 0.2, 220), "potion.wav": (8000, 0.3, 440),
            "explore.wav": (8000, 0.1, 880), "click.wav": (8000, 0.05, 600),
            "background.wav": (8000, 2.0, 330), "background_boss.wav": (8000, 2.0, 110),
            "background_shop.wav": (8000, 2.0, 220), "background_inn.wav": (8000, 2.0, 165),
            "buy.wav": (8000, 0.2, 550), "heal.wav": (8000, 0.4, 440), "save.wav": (8000, 0.3, 330)
        }
        for name, (sr, dur, freq) in sounds.items():
            p = os.path.join('sounds', name)
            if not os.path.exists(p):
                data = array.array('h', [int(16000 * math.sin(2 * math.pi * freq * i / sr)) for i in range(int(dur * sr))])
                with wave.open(p, 'w') as wf:
                    wf.setparams((1, 2, sr, len(data), 'NONE', 'not compressed'))
                    wf.writeframes(data.tobytes())

    def check_level_up(self):
        """Zpracuje postup na novou úroveň, pokud má hráč dostatek EXP."""
        leveled = False
        while self.character['exp'] >= 10 * self.character['level']:
            self.character['exp'] -= 10 * self.character['level']
            self.character['level'] += 1
            self.character['stat_points'] = self.character.get('stat_points', 0) + 3
            leveled = True
        if leveled:
            self.update_log(f"<b>LEVEL UP!</b> Dosáhl jsi úrovně {self.character['level']}.")
            self.update_stats()

    def allocate_point(self, attr):
        """Přidělí volný bod zvolenému atributu a uloží do nastavení."""
        if self.character.get('stat_points', 0) > 0:
            self.character[attr] = self.character.get(attr, 0) + 1
            self.character['stat_points'] -= 1
            cid = str(self.character['id'])
            self.settings.setValue(f"{attr}_{cid}", self.character[attr])
            self.settings.setValue(f"stat_points_{cid}", self.character['stat_points'])
            self._init_attributes()
            self.update_stats()

    def _init_attributes(self):
        """Inicializuje základní i odvozené atributy postavy."""
        cid = str(self.character['id'])
        for a in ['strength', 'dexterity', 'constitution', 'intelligence']:
            self.character[a] = self.settings.value(f"{a}_{cid}", 5 if a != 'constitution' else 10, type=int)
        self.character['stat_points'] = self.settings.value(f"stat_points_{cid}", 0, type=int)
        
        # Odvozené statistiky
        self.character['base_attack'] = self.character['strength'] + self.character['dexterity']
        self.character['base_defense'] = 5
        self.character['max_health'] = self.character['constitution'] * 10
        self.character['health'] = min(self.character.get('health', self.character['max_health']), self.character['max_health'])
        self._recalculate_total_stats()

    def _recalculate_total_stats(self):
        """Přepočítá celkový útok a obranu na základě aktuálního vybavení."""
        self.character['attack'] = self.character['base_attack']
        self.character['defense'] = self.character['base_defense']
        
        cid = str(self.character['id'])
        for k in ['weapon', 'head', 'torso', 'legs']:
            name = self.settings.value(f"equipped_{k}_{cid}", "", type=str)
            self.character[f'equipped_{k}'] = name
            
            # Bonus z katalogu
            bonus = 0
            for it in ITEM_CATALOG:
                if it['name'] == name: bonus = it['bonus']; break
            
            if k == 'weapon': self.character['attack'] += bonus
            else: self.character['defense'] += bonus

    def _update_equip_ui(self):
        """Aktualizuje vizuální sloty vybavení v hlavním okně s tooltipy obsahujícími statistiky."""
        slots = [
            (self.head_slot, 'equipped_head', "empty_head.svg"),
            (self.torso_slot, 'equipped_torso', "empty_torso.svg"),
            (self.legs_slot, 'equipped_legs', "empty_legs.svg"),
            (self.weapon_slot, 'equipped_weapon', "empty_weapon.svg")
        ]
        for label, key, empty_icon in slots:
            name = self.character.get(key, "")
            icon = ICON_MAP.get(name, empty_icon)
            
            # Vyhledání statistik předmětu pro tooltip
            tooltip_text = "Prázdné"
            if name:
                bonus_info = ""
                for it in ITEM_CATALOG:
                    if it['name'] == name:
                        bonus_info = f" (+{it['bonus']} {it['stat']})"
                        break
                tooltip_text = f"{name}{bonus_info}"
            
            self._render_svg_to_label(label, icon, tooltip_text)

    def _render_svg_to_label(self, label, icon_name, tooltip):
        """Vykreslí SVG ikonu do QLabelu."""
        try:
            path = os.path.join(os.path.dirname(__file__), "icons", icon_name)
            r = QSvgRenderer(path); px = QPixmap(40, 40); px.fill(Qt.GlobalColor.transparent)
            p = QPainter(px); r.render(p); p.end()
            label.setPixmap(px); label.setToolTip(tooltip)
        except: pass

    def explore_dungeon(self):
        """Zahájí nebo pokračuje v průzkumu dungeonu."""
        if self.settings.value("effects_volume", 50, type=int) > 0: self.sound_manager.play_sound("explore", True)
        if self.current_room != "dungeon":
            self.current_room = "dungeon"; self.update_location(); self.update_actions()
            self.update_log("Vstupuješ do temných stok...")
        else: self.advance_dungeon()

    def advance_dungeon(self):
        """Posune postavu v dungeonu a vyhodnotí náhodné setkání."""
        self.dungeon["progress"] += 1
        self.update_location()
        
        if self.dungeon["progress"] >= self.dungeon["steps_required"]:
            self.start_boss_battle()
            return
        
        r = random.random()
        if r < 0.35: # Prázdná cesta
            self.update_log(random.choice(["Pokračuješ hlouběji.", "Cesta je klidná.", "Slyšíš jen kapání vody."]))
        elif r < 0.45: # Zlato
            gold = random.randint(5, 15) + (5 * self.dungeon["level"])
            self.character["gold"] += gold
            self.update_log(f"Našel jsi váček zlata (<span style='color: #FFD700;'>+{gold} g</span>)!")
            self.update_stats()
        elif r < 0.55: # Událost
            self.start_event()
        else: # Boj
            self.start_combat()

    def start_event(self):
        """Spustí náhodnou textovou událost."""
        lvl = str(self.dungeon["level"])
        evs = self.content["events"].get(lvl, [])
        if not evs: return
        dlg = EventDialog(random.choice(evs), self)
        if dlg.exec() == QDialog.DialogCode.Accepted and dlg.selected_choice:
            eff = dlg.selected_choice.get("effects", {})
            self.character["gold"] = max(0, self.character.get("gold", 0) + int(eff.get("gold", 0)))
            self.character["health"] = min(self.character["max_health"], max(0, self.character["health"] + int(eff.get("health", 0))))
            self.character["potions"] = max(0, self.character["potions"] + int(eff.get("potions", 0)))
            self.update_stats(); self.update_log(f"Výsledek: {dlg.selected_choice['label']}")

    def start_combat(self):
        """Inicializuje souboj s běžným nepřítelem."""
        lvl = str(self.dungeon["level"])
        enemies = self.content["enemies"].get(lvl, [])
        if not enemies: return
        e = random.choice(enemies)
        self.current_enemy = {
            "name": e["name"], "health": int(e["health"]), "attack": int(e["attack"]),
            "defense": int(e["defense"]), "reward_gold": int(e["reward_gold"]),
            "reward_exp": int(e["reward_exp"]), "is_boss": False
        }
        self.update_log(f"Zpoza rohu vyběhl <b>{e['name']}</b>!")
        if e.get("description"):
            self.update_log(f"<i>'{e['description']}'</i>")
        self.update_actions()

    def start_boss_battle(self):
        """Inicializuje souboj s finálním bossem úrovně."""
        lvl = str(self.dungeon["level"])
        b = self.content["boss"].get(lvl)
        if not b: return
        self.current_enemy = {
            "name": b["name"], "health": int(b["health"]), "attack": int(b["attack"]),
            "defense": int(b["defense"]), "reward_gold": int(b["reward_gold"]),
            "reward_exp": int(b["reward_exp"]), "is_boss": True,
            "music": b.get("music", "background_boss.wav")
        }
        self.update_log(f"<b>POZOR!</b> Před tebou stojí <b>{b['name']}</b>!")
        if b.get("description"):
            self.update_log(f"<i>'{b['description']}'</i>")
        self.update_actions()
        self.play_background_music()

    def return_to_town(self):
        """Ukončí průzkum a vrátí hráče do města. Resetuje úroveň dungeonu."""
        self.current_room = "town"
        self.current_enemy = None
        self.dungeon["level"] = 1      # Reset na Sewers
        self.dungeon["progress"] = 0   # Reset kroků
        self.update_location()
        self.update_actions()
        self.play_background_music()
    
    def visit_shop(self):
        """Otevře okno obchodu."""
        if ShopDialog(self.character, self.sound_manager, self).exec():
            self._init_attributes(); self.update_stats(); self.play_background_music()
    
    def rest_at_inn(self):
        """Otevře okno hostince."""
        if InnDialog(self.character, self.sound_manager, self).exec():
            self.update_stats(); self.play_background_music()
    
    def attack_enemy(self):
        """Provede jedno kolo souboje (útok hráče a protiútok nepřítele)."""
        if not self.current_enemy: return
        if self.settings.value("effects_volume", 50, type=int) > 0: self.sound_manager.play_sound("attack", True)
        
        # 1. Útok hráče
        dmg = max(1, self.character["attack"] - self.current_enemy["defense"])
        self.current_enemy["health"] -= dmg
        self.update_log(f"Zasáhl jsi {self.current_enemy['name']} za <span style='color: #22C55E;'>{dmg} poškození</span>.")

        # Kontrola vítězství
        if self.current_enemy["health"] <= 0:
            self._finish_combat(); return

        # 2. Protiútok nepřítele
        e_dmg = max(1, self.current_enemy["attack"] - self.character["defense"])
        self.character["health"] = max(0, self.character["health"] - e_dmg)
        self.update_log(f"{self.current_enemy['name']} tě zasáhl za <span style='color: #EF4444;'>{e_dmg} poškození</span>.")
        self.update_stats()

        # Kontrola porážky
        if self.character["health"] <= 0:
            self.update_log("Byl jsi poražen! Vracíš se do města se zraněním."); self.return_to_town()
        else: self.update_combat_display()
    
    def _finish_combat(self):
        """Zpracuje odměny po úspěšném souboji."""
        e = self.current_enemy
        g, xp = e["reward_gold"], e["reward_exp"]
        self.character["gold"] += g; self.character["exp"] += xp
        self.character["score"] = self.character.get("score", 0) + xp
        
        self.update_log(f"Vítězství! Získáno <span style='color: #FFD700;'>{g} g</span> a <span style='color: #A855F7;'>{xp} EXP</span>.")
        
        is_boss = e.get('is_boss', False)
        current_lvl = self.dungeon['level']

        if is_boss:
            self.update_log(f"<b>Gratulujeme!</b> Úroveň {current_lvl} dokončena.")
            
            # Kontrola konce hry po 2. úrovni (Goblin Warrens)
            if current_lvl == 2:
                self.update_stats() # Aktualizace skóre před zobrazením konce
                dlg = EndScreenDialog(self.character.get('score', 0), self)
                if dlg.exec() == QDialog.DialogCode.Accepted:
                    # Návrat do města a pokračování
                    self.return_to_town()
                    return
                else:
                    # Ukončení hry
                    sys.exit(0)

            self.dungeon['level'] += 1
            self.dungeon["progress"] = 0 # Reset progress for next level
        
        self.check_level_up(); self.update_stats()
        self.current_enemy = None; self.update_actions()
        self.play_background_music()

    def use_potion(self):
        """Vyléčí část zdraví pomocí lektvaru, pokud nějaké zbývají."""
        potions = self.character.get("potions", 0)
        if potions <= 0:
            self.update_log("<span style='color: #ef4444;'>Nemáš žádné lektvary!</span>")
            return
            
        heal = max(10, self.character["max_health"] // 3)
        self.character["potions"] -= 1
        self.character["health"] = min(self.character["max_health"], self.character["health"] + heal)
        
        self.update_log(f"Vypil jsi lektvar a vyléčil <span style='color: #22C55E;'>{heal} HP</span>.")
        self.update_log(f"Zbývající lektvary: {self.character['potions']}")
        
        if self.settings.value("effects_volume", 50, type=int) > 0: 
            self.sound_manager.play_sound("potion", True)
            
        self.update_stats()
        self.update_combat_display()
    
    def flee_combat(self):
        """Umožní útěk ze souboje za cenu návratu do města."""
        self.update_log("Úspěšně jsi utekl!"); self.return_to_town()

    def update_combat_display(self):
        """Aktualizuje textový stav souboje uprostřed obrazovky."""
        if self.current_enemy:
            e = self.current_enemy
            self.combat_label.setText(f"<b>⚔️ SOUBOJ</b><br>Nepřítel: {e['name']}<br>"
                                     f"Životy: {e['health']} HP<br>"
                                     f"Tvé HP: {self.character['health']}/{self.character['max_health']}")
        else: self.combat_label.setText("")

if __name__ == "__main__":
    app = QApplication(sys.argv); app.setStyleSheet(APP_QSS)
    game = RPGGame(); game.show(); sys.exit(app.exec())
