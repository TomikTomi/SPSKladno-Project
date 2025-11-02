import sys
import random
import os
import json
import requests
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QPushButton, QLabel, 
    QVBoxLayout, QHBoxLayout, QWidget, QTextEdit, QProgressBar,
    QDialog, QLineEdit, QMessageBox, QCheckBox, QDialogButtonBox
)
from PyQt6.QtCore import Qt, QTimer, QSettings
from PyQt6.QtGui import QFont, QIcon
from sound_manager import SoundManager

class LoginDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("RPG Game - Login")
        self.resize(350, 250)
        
        layout = QVBoxLayout()
        
        # Connection status
        self.connection_label = QLabel("Checking server connection...")
        self.connection_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        self.username_input = QLineEdit()
        self.username_input.setPlaceholderText("Username")
        
        self.password_input = QLineEdit()
        self.password_input.setPlaceholderText("Password")
        self.password_input.setEchoMode(QLineEdit.EchoMode.Password)
        
        self.login_button = QPushButton("Login")
        self.register_button = QPushButton("Register")
        self.retry_button = QPushButton("Retry Connection")
        
        layout.addWidget(self.connection_label)
        layout.addWidget(self.username_input)
        layout.addWidget(self.password_input)
        layout.addWidget(self.login_button)
        layout.addWidget(self.register_button)
        layout.addWidget(self.retry_button)
        
        self.setLayout(layout)
        
        self.login_button.clicked.connect(self.login)
        self.register_button.clicked.connect(self.register)
        self.retry_button.clicked.connect(self.check_connection)
        
        # Check connection on startup
        self.check_connection()
    
    def check_connection(self):
        """Check and display connection status"""
        self.connection_label.setText("Checking server connection...")
        
        if self.test_connection():
            self.connection_label.setText("✅ Connected to server")
            self.connection_label.setStyleSheet("color: green;")
            self.login_button.setEnabled(True)
            self.register_button.setEnabled(True)
        else:
            self.connection_label.setText("❌ Cannot connect to server")
            self.connection_label.setStyleSheet("color: red;")
            self.login_button.setEnabled(False)
            self.register_button.setEnabled(False)
    
    def test_connection(self):
        """Test connection to Flask server"""
        try:
            response = requests.get('http://127.0.0.1:5000/api/highscores', timeout=5)
            return response.status_code == 200
        except:
            return False
    
    def login(self):
        if not self.test_connection():
            self.check_connection()
            return
        
        username = self.username_input.text()
        password = self.password_input.text()
        
        if not username or not password:
            QMessageBox.warning(self, "Error", "Please enter username and password")
            return
        
        try:
            response = requests.post(
                'http://127.0.0.1:5000/api/login', 
                json={'username': username, 'password': password},
                timeout=10
            )
            
            if response.json().get('success'):
                self.user_data = response.json()
                self.accept()
            else:
                QMessageBox.warning(self, "Error", "Invalid credentials")
                
        except requests.exceptions.ConnectionError:
            QMessageBox.critical(self, "Connection Error", "Lost connection to server")
            self.check_connection()
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Login failed: {str(e)}")
    
    def register(self):
        # Similar robust implementation for register
        pass
class OptionsDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Game Options")
        self.settings = QSettings("DungeonExplorer", "RPGGame")
        self.setup_ui()
        
    def setup_ui(self):
        layout = QVBoxLayout()
        
        # Title
        title = QLabel("Game Options")
        title.setFont(QFont("Arial", 14, QFont.Weight.Bold))
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title)
        
        # Sound effects option
        self.sound_effects_checkbox = QCheckBox("Enable Sound Effects")
        self.sound_effects_checkbox.setChecked(self.settings.value("sound_effects", False, type=bool))
        layout.addWidget(self.sound_effects_checkbox)
        
        # Background music option
        self.music_checkbox = QCheckBox("Enable Background Music")
        self.music_checkbox.setChecked(self.settings.value("background_music", False, type=bool))
        layout.addWidget(self.music_checkbox)
        
        # Add some spacing
        layout.addSpacing(10)
        
        # Dialog buttons
        button_box = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        button_box.accepted.connect(self.save_settings)
        button_box.rejected.connect(self.reject)
        layout.addWidget(button_box)
        
        self.setLayout(layout)
        
    def save_settings(self):
        # Save settings
        self.settings.setValue("sound_effects", self.sound_effects_checkbox.isChecked())
        self.settings.setValue("background_music", self.music_checkbox.isChecked())
        self.accept()
        
class ShopDialog(QDialog):
    def __init__(self, character, sound_manager, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Town Shop")
        self.resize(500, 400)
        self.character = character
        self.sound_manager = sound_manager
        self.purchased_items = []
        self.settings = QSettings("DungeonExplorer", "RPGGame")
        
        # Shop items with their stats and prices
        self.shop_items = [
            {"name": "Iron Sword", "type": "weapon", "stat": "attack", "bonus": 5, "price": 50},
            {"name": "Steel Sword", "type": "weapon", "stat": "attack", "bonus": 10, "price": 120},
            {"name": "Leather Armor", "type": "armor", "stat": "defense", "bonus": 3, "price": 40},
            {"name": "Chain Mail", "type": "armor", "stat": "defense", "bonus": 7, "price": 100},
            {"name": "Health Potion", "type": "consumable", "stat": "potions", "bonus": 1, "price": 15}
        ]
        
        # Play shop music (ensure no overlap)
        self.sound_manager.stop_music()
        self.sound_manager.play_music("background_shop.wav", 
                                     self.settings.value("background_music", False, type=bool))
        
        self.setup_ui()
        
    def setup_ui(self):
        layout = QVBoxLayout()
        
        # Title
        title = QLabel("Town Shop")
        title.setFont(QFont("Arial", 16, QFont.Weight.Bold))
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title)
        
        # Player gold
        self.gold_label = QLabel(f"Your Gold: {self.character['gold']}")
        self.gold_label.setFont(QFont("Arial", 12))
        self.gold_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.gold_label)
        
        # Items for sale
        items_layout = QVBoxLayout()
        
        for item in self.shop_items:
            item_layout = QHBoxLayout()
            
            # Item name and description
            item_info = QLabel(f"{item['name']} - {item['bonus']} {item['stat'].capitalize()}")
            item_info.setFont(QFont("Arial", 11))
            
            # Price
            price_label = QLabel(f"{item['price']} gold")
            
            # Buy button
            buy_button = QPushButton("Buy")
            buy_button.setFixedWidth(60)
            buy_button.clicked.connect(lambda checked, i=item: self.buy_item(i))
            
            item_layout.addWidget(item_info)
            item_layout.addStretch()
            item_layout.addWidget(price_label)
            item_layout.addWidget(buy_button)
            
            items_layout.addLayout(item_layout)
        
        layout.addLayout(items_layout)
        
        # Status message
        self.status_label = QLabel("")
        self.status_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.status_label)
        
        # Close button
        close_button = QPushButton("Close")
        close_button.clicked.connect(self.close_shop)
        layout.addWidget(close_button)
        
        self.setLayout(layout)
    
    def buy_item(self, item):
        # Check if player has enough gold
        if self.character['gold'] >= item['price']:
            # Play buy sound
            self.sound_manager.play_sound("buy", 
                                         self.settings.value("sound_effects", False, type=bool))
            
            # Deduct gold
            self.character['gold'] -= item['price']
            
            # Update stats based on item type
            if item['stat'] == 'attack':
                self.character['attack'] += item['bonus']
            elif item['stat'] == 'defense':
                self.character['defense'] += item['bonus']
            elif item['stat'] == 'potions':
                self.character['potions'] += item['bonus']
            
            # Add to purchased items
            self.purchased_items.append(item)
            
            # Update gold display
            self.gold_label.setText(f"Your Gold: {self.character['gold']}")
            
            # Show success message
            self.status_label.setText(f"Purchased {item['name']}!")
            self.status_label.setStyleSheet("color: green;")
        else:
            # Show error message
            self.status_label.setText("Not enough gold!")
            self.status_label.setStyleSheet("color: red;")
    
    def close_shop(self):
         # Stop shop music and return to regular music
         self.sound_manager.stop_music()
         # Just accept the dialog, the parent will handle music
         self.accept()

class InnDialog(QDialog):
    def __init__(self, character, sound_manager, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Town Inn")
        self.resize(500, 300)
        self.character = character
        self.sound_manager = sound_manager
        self.settings = QSettings("DungeonExplorer", "RPGGame")
        # Healing cost (small gold price)
        self.heal_cost = 20

        # Play inn music (ensure no overlap)
        self.sound_manager.stop_music()
        self.sound_manager.play_music("background_inn.wav",
                                      self.settings.value("background_music", False, type=bool))

        self.setup_ui()

    def setup_ui(self):
        layout = QVBoxLayout()

        title = QLabel("Town Inn")
        title.setFont(QFont("Arial", 16, QFont.Weight.Bold))
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title)

        # Player status
        self.gold_label = QLabel(f"Your Gold: {self.character['gold']}")
        self.gold_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.gold_label)

        self.health_label = QLabel(f"Health: {self.character['health']}/{self.character['max_health']}")
        self.health_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.health_label)

        # Actions
        actions_layout = QHBoxLayout()

        save_btn = QPushButton("Save Game")
        save_btn.clicked.connect(self.save_game)

        heal_save_btn = QPushButton(f"Heal and Save ({self.heal_cost} gold)")
        heal_save_btn.clicked.connect(self.heal_and_save)

        actions_layout.addWidget(save_btn)
        actions_layout.addWidget(heal_save_btn)
        layout.addLayout(actions_layout)

        # Status message
        self.status_label = QLabel("")
        self.status_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.status_label)

        # Close
        close_btn = QPushButton("Close")
        close_btn.clicked.connect(self.close_inn)
        layout.addWidget(close_btn)

        self.setLayout(layout)

    def save_game(self):
        # Play save sound
        if self.settings.value("sound_effects", False, type=bool):
            self.sound_manager.play_sound("save")
        # Call parent save
        parent = self.parent()
        if parent:
            parent.save_character()
            self.status_label.setText("Game saved!")
            self.status_label.setStyleSheet("color: green;")

    def heal_and_save(self):
        if self.character['gold'] >= self.heal_cost:
            # Deduct gold and heal to max
            self.character['gold'] -= self.heal_cost
            self.character['health'] = self.character['max_health']
            # Play heal sound
            if self.settings.value("sound_effects", False, type=bool):
                self.sound_manager.play_sound("heal")
            # Save game
            parent = self.parent()
            if parent:
                parent.save_character()
            # Update UI labels
            self.gold_label.setText(f"Your Gold: {self.character['gold']}")
            self.health_label.setText(f"Health: {self.character['health']}/{self.character['max_health']}")
            self.status_label.setText("You are fully healed and saved!")
            self.status_label.setStyleSheet("color: green;")
        else:
            self.status_label.setText("Not enough gold to heal!")
            self.status_label.setStyleSheet("color: red;")

    def close_inn(self):
        self.sound_manager.stop_music()
        self.accept()


class CharacterSelectionDialog(QDialog):
    def __init__(self, user_id, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Select Character")
        self.resize(400, 300)
        self.user_id = user_id
        self.selected_character = None
        
        layout = QVBoxLayout()
        self.characters_layout = QVBoxLayout()
        
        self.load_characters()
        
        new_char_button = QPushButton("Create New Character")
        new_char_button.clicked.connect(self.create_character)
        
        layout.addWidget(QLabel("Select Your Character:"))
        layout.addLayout(self.characters_layout)
        layout.addWidget(new_char_button)
        
        self.setLayout(layout)
    
    def load_characters(self):
        # Clear existing characters
        for i in reversed(range(self.characters_layout.count())): 
            widget = self.characters_layout.itemAt(i).widget()
            if widget:
                widget.setParent(None)
        
        response = requests.get(f'http://localhost:5000/api/characters?user_id={self.user_id}')
        if response.json().get('success'):
            characters = response.json()['characters']
            
            if not characters:
                self.characters_layout.addWidget(QLabel("No characters found. Create one!"))
                return
            
            for char in characters:
                char_button = QPushButton(
                    f"{char['name']} (Level {char['level']}, {char['gold']} gold)"
                )
                char_button.clicked.connect(lambda checked, c=char: self.select_character(c))
                self.characters_layout.addWidget(char_button)
    
    def select_character(self, character):
        self.selected_character = character
        self.accept()
    
    def create_character(self):
        name, ok = QLineEdit.getText(self, "New Character", "Enter character name:")
        if ok and name:
            response = requests.post('http://localhost:5000/api/characters', json={
                'name': name,
                'user_id': self.user_id
            })
            
            if response.json().get('success'):
                self.load_characters()
            else:
                QMessageBox.warning(self, "Error", "Failed to create character")

class RPGGame(QMainWindow):
    def __init__(self):
        super().__init__()
        
        # Initialize sound manager
        self.sound_manager = SoundManager()
        
        # Show login dialog first
        login_dialog = LoginDialog()
        if login_dialog.exec() != QDialog.DialogCode.Accepted:
            sys.exit(0)
        
        self.user_data = login_dialog.user_data
        
        # Show character selection
        char_dialog = CharacterSelectionDialog(self.user_data['user_id'])
        if char_dialog.exec() != QDialog.DialogCode.Accepted:
            sys.exit(0)
        
        self.character = char_dialog.selected_character

        self.setWindowTitle(f"Dungeon Explorer - {self.character['name']}")
        self.resize(600, 700)
        
        # Game state
        self.current_room = "town"
        self.current_enemy = None
        self.game_log = [f"Welcome {self.character['name']}!", "You are in the town square."]

        # Dungeon state
        self.dungeon = {
            "level": 1,
            "progress": 0,
            "steps_required": 20,
            "state": "idle"  # idle | event | combat | completed
        }

        # Content loaded from JSON
        self.content = {
            "events": {},   # { level: [event, ...] }
            "enemies": {},  # { level: [enemy, ...] }
            "boss": {}      # { level: boss_enemy }
        }
        
        # Initialize UI
        self.health_bar = None
        self.stats_label = None
        self.log_display = None
        self.location_label = None
        self.combat_label = None
        
        self.setup_ui()
        # Disable autosave: saving is only available at the Inn
        self.autosave_timer = None

        # Load sound effects
        self.load_sounds()

        # Load external content (events/enemies) from JSON
        self.load_content()

        # Play background music if enabled
        self.play_background_music()

        # Initialize EXP threshold meta
        # Ensure level/exp keys exist and set exp_to_level for display
        self.character.setdefault('level', 1)
        self.character.setdefault('exp', 0)
        self.character['exp_to_level'] = self.exp_needed_for_next(self.character['level'])
    
    def setup_ui(self):
        # Set game version
        self.game_version = "v0.0.1"
        
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout()
        
        # Header with version and settings (center title removed to free space)
        header_layout = QHBoxLayout()
        
        # Right side container for version and settings
        right_container = QVBoxLayout()
        
        # Version in top right
        version_label = QLabel(self.game_version)
        version_label.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignTop)
        version_label.setStyleSheet("color: #666; font-size: 10px;")
        right_container.addWidget(version_label)
        
        # Settings button (cogwheel)
        settings_button = QPushButton("⚙")
        settings_button.setFixedSize(30, 30)
        settings_button.setStyleSheet("""
            QPushButton {
                font-size: 16px;
                background-color: #f0f0f0;
                border-radius: 15px;
                border: 1px solid #ccc;
            }
            QPushButton:hover {
                background-color: #e0e0e0;
            }
        """)
        settings_button.clicked.connect(self.show_options_dialog)
        
        settings_container = QHBoxLayout()
        settings_container.addStretch()
        settings_container.addWidget(settings_button)
        right_container.addLayout(settings_container)
        
        header_layout.addLayout(right_container, 0)
        
        layout.addLayout(header_layout)
        
        # Player stats
        stats_layout = QHBoxLayout()
        
        self.stats_label = QLabel()
        
        # Remove visual health bar; keep compact stats only
        stats_layout.addWidget(self.stats_label)
        layout.addLayout(stats_layout)
        
        # Location info
        location_box = QVBoxLayout()
        self.location_label = QLabel("Current Location")
        self.location_label.setFont(QFont("Arial", 12, QFont.Weight.Bold))
        self.location_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        location_box.addWidget(self.location_label)
        layout.addLayout(location_box)
        
        # Game log
        log_box = QVBoxLayout()
        log_title = QLabel("Adventure Log")
        log_title.setFont(QFont("Arial", 12, QFont.Weight.Bold))
        self.log_display = QTextEdit()
        self.log_display.setReadOnly(True)
        # Increase height and allow much longer play history
        self.log_display.setMinimumHeight(300)
        self.log_display.setUndoRedoEnabled(False)
        log_box.addWidget(log_title)
        log_box.addWidget(self.log_display)
        layout.addLayout(log_box)
        
        # Action buttons
        action_box = QVBoxLayout()
        action_title = QLabel("Actions")
        action_title.setFont(QFont("Arial", 12, QFont.Weight.Bold))
        action_box.addWidget(action_title)
        
        # Town actions
        town_actions = QHBoxLayout()
        explore_btn = QPushButton("Explore Dungeon")
        # Keep a reference for visibility control in both town and dungeon
        self.explore_btn = explore_btn
        shop_btn = QPushButton("Visit Shop")
        rest_btn = QPushButton("Rest at Inn")
        
        explore_btn.clicked.connect(self.explore_dungeon)
        shop_btn.clicked.connect(self.visit_shop)
        rest_btn.clicked.connect(self.rest_at_inn)
        
        town_actions.addWidget(explore_btn)
        town_actions.addWidget(shop_btn)
        town_actions.addWidget(rest_btn)
        action_box.addLayout(town_actions)
        
        # Dungeon actions (only visible in dungeon)
        dungeon_actions = QHBoxLayout()
        self.return_town_btn = QPushButton("Return to Town")
        # Attach icon if available
        try:
            base_dir = os.path.dirname(os.path.abspath(__file__))
            icon_path = os.path.join(base_dir, "icons", "return_to_town.svg")
            if os.path.isfile(icon_path):
                self.return_town_btn.setIcon(QIcon(icon_path))
        except Exception:
            pass
        self.return_town_btn.clicked.connect(self.return_to_town)
        dungeon_actions.addWidget(self.return_town_btn)
        action_box.addLayout(dungeon_actions)
        
        # Store town and dungeon action widgets for visibility management
        # Explore button belongs to town widgets, and we explicitly show it in dungeon
        self.town_action_widgets = [explore_btn, shop_btn, rest_btn]
        self.dungeon_action_widgets = [self.return_town_btn]
        
        # Combat section (initially hidden)
        combat_box = QVBoxLayout()
        self.combat_label = QLabel("Combat")
        self.combat_label.setFont(QFont("Arial", 12, QFont.Weight.Bold))
        
        combat_buttons = QHBoxLayout()
        attack_btn = QPushButton("Attack")
        use_potion_btn = QPushButton("Use Potion")
        flee_btn = QPushButton("Flee")
        
        attack_btn.clicked.connect(self.attack_enemy)
        use_potion_btn.clicked.connect(self.use_potion)
        flee_btn.clicked.connect(self.flee_combat)
        
        combat_buttons.addWidget(attack_btn)
        combat_buttons.addWidget(use_potion_btn)
        combat_buttons.addWidget(flee_btn)
        
        combat_box.addWidget(self.combat_label)
        combat_box.addLayout(combat_buttons)
        
        # Store combat widgets for hiding/showing
        self.combat_widgets = [self.combat_label, attack_btn, use_potion_btn, flee_btn]
        
        action_box.addLayout(combat_box)
        layout.addLayout(action_box)
        
        central_widget.setLayout(layout)
        
        # Initialize game state
        self.update_stats()
        self.update_log("Úspěšné přihlášení")
        self.update_location()
        self.update_actions()
        self.hide_combat_ui()
    
    def update_stats(self):
        """Update character stats in the UI"""
        exp_to_level = self.character.get('exp_to_level', 'N/A')  # Use 'N/A' if the key is missing
        stats = (
            f"Name: {self.character['name']}\n"
            f"Level: {self.character['level']}\n"
            f"EXP: {self.character['exp']}/{exp_to_level}\n"
            f"Gold: {self.character['gold']}\n"
            f"Health: {self.character['health']}/{self.character['max_health']}\n"
            f"Attack: {self.character['attack']}\n"
            f"Defense: {self.character['defense']}\n"
            f"Potions: {self.character['potions']}"
        )
        self.stats_label.setText(stats)
        
    def update_log(self, message):
        """Add a message to the game log"""
        self.game_log.append(message)
        if hasattr(self, 'log_display') and self.log_display is not None:
            # Append incrementally and auto-scroll to bottom
            self.log_display.append(message)
            sb = self.log_display.verticalScrollBar()
            if sb is not None:
                sb.setValue(sb.maximum())
        else:
            print(f"Game Log: {message}")  # Fallback if log_display is not initialized
    
    def update_location(self):
        """Update the player's location in the UI."""
        if self.current_room == "town":
            location_text = "Town Square"
        elif self.current_room == "dungeon":
            # Level names mapping
            level_names = {
                1: "Sewers"
                # Add more levels later: 2: "Cellars", etc.
            }
            level_name = level_names.get(self.dungeon['level'], f"Unknown Level {self.dungeon['level']}")
            location_text = f"Lvl {self.dungeon['level']} - {level_name}"
        elif self.current_room == "shop":
            location_text = "Town Shop"
        elif self.current_room == "inn":
            location_text = "Town Inn"
        else:
            location_text = self.current_room.capitalize()
            
        if hasattr(self, 'location_label') and self.location_label is not None:
            self.location_label.setText(location_text)
        else:
            print(f"Current location: {location_text}")

    def update_actions(self):
        """Update the available actions in the UI."""
        # This method is now handled by the buttons in the UI
        print(f"Available actions: Explore Dungeon, Visit Shop, Rest at Inn")
        
        # Show/hide action buttons based on current room
        if self.current_room == "town":
            # Show town actions, hide dungeon actions
            for widget in self.town_action_widgets:
                widget.show()
            for widget in self.dungeon_action_widgets:
                widget.hide()
        elif self.current_room == "dungeon":
            # Hide non-dungeon town actions, show Return + Explore when not in combat/event
            for widget in self.town_action_widgets:
                widget.hide()
            if self.current_enemy is None and self.dungeon.get("state") not in ("event", "combat"):
                for widget in self.dungeon_action_widgets:
                    widget.show()
                # Show explore in dungeon as "Advance"
                if hasattr(self, "explore_btn"):
                    self.explore_btn.show()
            else:
                for widget in self.dungeon_action_widgets:
                    widget.hide()
                if hasattr(self, "explore_btn"):
                    self.explore_btn.hide()
        
        # Show/hide combat UI based on current room
        if self.current_room == "dungeon" and self.current_enemy is not None:
            self.show_combat_ui()
        else:
            self.hide_combat_ui()
            
    def show_combat_ui(self):
        """Show combat-related UI elements."""
        if hasattr(self, 'combat_widgets'):
            for widget in self.combat_widgets:
                widget.show()
        else:
            print("Combat UI shown")

    def hide_combat_ui(self):
        """Hide combat-related UI elements."""
        if hasattr(self, 'combat_widgets'):  # Assuming there's a list of combat-related widgets
            for widget in self.combat_widgets:
                widget.hide()  # Hide each combat-related widget
        else:
            print("Combat UI hidden")  # Fallback to a simple message
            
    def save_character(self):
        """Save character data to the server"""
        try:
            response = requests.put(
                f'http://localhost:5000/api/characters/{self.character["id"]}',
                json=self.character
            )
            if response.status_code == 200:
                self.update_log("Character saved successfully")
            else:
                self.update_log(f"Error saving character: {response.status_code}")
        except Exception as e:
            self.update_log(f"Error saving character: {str(e)}")
            # Continue game even if save fails
            
    def show_options_dialog(self):
        """Show the options dialog"""
        dialog = OptionsDialog(self)
        if dialog.exec():
            # Apply settings if needed
            settings = QSettings("DungeonExplorer", "RPGGame")
            sound_enabled = settings.value("sound_effects", False, type=bool)
            music_enabled = settings.value("background_music", False, type=bool)
            
            # Log the settings changes
            self.update_log(f"Settings updated: Sound {'enabled' if sound_enabled else 'disabled'}, Music {'enabled' if music_enabled else 'disabled'}")
            
            # Apply sound settings
            if music_enabled:
                self.play_background_music()
            else:
                self.sound_manager.stop_music()
                
    def load_sounds(self):
        """Load all game sound effects"""
        # Create sample sound files if they don't exist
        self.create_sample_sounds()
        
        # Load sound effects
        self.sound_manager.load_sound("attack", "attack.wav")
        self.sound_manager.load_sound("potion", "potion.wav")
        self.sound_manager.load_sound("explore", "explore.wav")
        self.sound_manager.load_sound("click", "click.wav")
        self.sound_manager.load_sound("buy", "buy.wav")
        self.sound_manager.load_sound("heal", "heal.wav")
        self.sound_manager.load_sound("save", "save.wav")
    
    def play_background_music(self):
        """Play background music if enabled"""
        settings = QSettings("DungeonExplorer", "RPGGame")
        music_enabled = settings.value("background_music", False, type=bool)
        
        if music_enabled:
            self.sound_manager.play_music("background.wav", True)

    def play_boss_music(self):
        """Play boss background music if enabled (placeholder file)."""
        settings = QSettings("DungeonExplorer", "RPGGame")
        music_enabled = settings.value("background_music", False, type=bool)
        if music_enabled:
            # Use a dedicated boss track; user can replace/edit this file
            self.sound_manager.play_music("background_boss.wav", True)
    
    def create_sample_sounds(self):
        """Create sample sound files if they don't exist"""
        import os
        import wave
        import struct
        import array
        import math
        
        # Create sounds directory if it doesn't exist
        os.makedirs('sounds', exist_ok=True)
        
        # Only create files if they don't exist
        sound_files = {
            "attack.wav": (8000, 0.3, 220.0),  # Attack sound (lower pitch)
            "potion.wav": (8000, 0.3, 440.0),  # Potion sound (medium pitch)
            "explore.wav": (8000, 0.3, 880.0), # Explore sound (higher pitch)
            "click.wav": (8000, 0.1, 660.0),   # Click sound (short)
            "background.wav": (8000, 2.0, 330.0),  # Background music (longer)
            "background_boss.wav": (8000, 2.5, 110.0)  # Boss music (lower ominous tone)
        }
        
        for filename, (sample_rate, duration, frequency) in sound_files.items():
            file_path = os.path.join('sounds', filename)
            if not os.path.exists(file_path):
                # Create a simple sine wave as a placeholder sound
                samples = int(duration * sample_rate)
                audio_data = array.array('h', [
                    max(-32767, min(32767, int(32767 * 0.3 * 
                    math.sin(2 * math.pi * frequency * i / sample_rate))))
                    for i in range(samples)])
                
                with wave.open(file_path, 'w') as wave_file:
                    wave_file.setparams((1, 2, sample_rate, samples, 'NONE', 'not compressed'))
                    wave_file.writeframes(audio_data.tobytes())

    def exp_needed_for_next(self, level):
        """Return EXP needed to reach the next level."""
        # Simple linear progression: 10 * current level
        return 10 * max(1, int(level))

    def check_level_up(self):
        """Check if EXP meets threshold; level up without changing stats."""
        exp_to_level = self.exp_needed_for_next(self.character['level'])
        # Keep rollover EXP into next level(s)
        leveled_up = False
        while self.character['exp'] >= exp_to_level:
            self.character['exp'] -= exp_to_level
            self.character['level'] += 1
            leveled_up = True
            exp_to_level = self.exp_needed_for_next(self.character['level'])
        # Update displayed threshold
        self.character['exp_to_level'] = exp_to_level
        if leveled_up:
            self.update_log(f"Level Up! You reached Level {self.character['level']}.")
            self.update_stats()

# Action methods with sound effects
    def explore_dungeon(self):
        """Enter or advance through the dungeon with placeholder outcomes."""
        settings = QSettings("DungeonExplorer", "RPGGame")
        if settings.value("sound_effects", False, type=bool):
            self.sound_manager.play_sound("explore")

        # Enter dungeon from town
        if self.current_room != "dungeon":
            self.current_room = "dungeon"
            self.update_location()
            self.update_actions()  # Update button visibility
            self.update_log("You step into the dungeon sewers...")
            return

        # If in dungeon, attempt to advance
        self.advance_dungeon()

    def load_content(self):
        """Load events and enemies from JSON files with basic validation."""
        base_dir = os.path.dirname(os.path.abspath(__file__))
        data_dir = os.path.join(base_dir, "data")
        # Events
        events_path = os.path.join(data_dir, "events.json")
        enemies_path = os.path.join(data_dir, "enemies.json")
        try:
            if os.path.isfile(events_path):
                with open(events_path, "r", encoding="utf-8") as f:
                    events = json.load(f)
                self.content["events"] = events.get("levels", {})
            else:
                self.content["events"] = {}
            if os.path.isfile(enemies_path):
                with open(enemies_path, "r", encoding="utf-8") as f:
                    enemies = json.load(f)
                levels = enemies.get("levels", {})
                # Separate boss mapping if present
                boss = levels.get("boss", {}) if isinstance(levels.get("boss", {}), dict) else {}
                self.content["boss"] = boss
                # Remove boss from regular enemies
                if "boss" in levels:
                    levels = {k: v for k, v in levels.items() if k != "boss"}
                self.content["enemies"] = levels
            else:
                self.content["enemies"] = {}
                self.content["boss"] = {}
        except Exception as e:
            self.update_log(f"Error loading content: {e}")

    def advance_dungeon(self):
        """Advance one step in the dungeon and handle outcome."""
        # Block if in event or combat state
        if self.dungeon["state"] in ("event", "combat"):
            self.update_log("You must resolve your current situation before advancing.")
            return

        # Warning 3, 2, 1 steps before boss encounter
        steps_left = self.dungeon["steps_required"] - self.dungeon["progress"]
        if steps_left in (3, 2, 1):
            self.update_log("You feel a terrible presence ahead...")

        # If next step reaches boss, start boss combat
        if steps_left == 1:
            self.dungeon["state"] = "combat"
            self.start_boss_battle()
            return

        # Roll outcome
        outcome = self.roll_outcome()
        if outcome == "nothing":
            # Random "nothing happens" messages for variety
            nothing_messages = [
                "You advance cautiously. Nothing happens.",
                "You examine ancient dungeon engravings. You can't make anything of them.",
                "Your footsteps echo in the empty hallway ahead.",
                "You search thoroughly but come up empty-handed this time.",
                "The stone walls seem to whisper ancient secrets, but reveal nothing.",
                "You navigate through a maze of empty chambers.",
                "Every shadow could hide danger, but this time... nothing stirs.",
                "You explore a series of abandoned rooms, finding nothing of value.",
                "Ancient murals line the walls, but no treasures await here.",
                "The darkness ahead seems to watch you, but nothing emerges."
            ]
            message = random.choice(nothing_messages)
            self.update_log(message)
            self.dungeon["progress"] += 1
        elif outcome == "treasure":
            # Simple treasure scaled by level
            reward = random.randint(10, 25) + 5 * self.dungeon["level"]
            self.character["gold"] += reward
            self.update_log(f"You find a small stash of gold (+{reward}).")
            self.dungeon["progress"] += 1
            self.update_stats()
        elif outcome == "event":
            self.dungeon["state"] = "event"
            self.start_event_placeholder()
            # Resolve immediately for now
            self.dungeon["state"] = "idle"
            self.dungeon["progress"] += 1
        elif outcome == "enemy":
            # Enter combat; progress increases upon victory
            self.dungeon["state"] = "combat"
            self.start_enemy_placeholder()

        # Check completion
        if self.dungeon["progress"] >= self.dungeon["steps_required"]:
            self.dungeon["state"] = "completed"
            self.complete_level()

    def roll_outcome(self):
        """Weighted random outcome for dungeon advance."""
        probs = {
            "nothing": 0.3,
            "event": 0.3,
            "enemy": 0.3,
            "treasure": 0.1
        }
        r = random.random()
        cumulative = 0.0
        for outcome, p in probs.items():
            cumulative += p
            if r <= cumulative:
                return outcome
        return "nothing"

    def start_event_placeholder(self):
        """Show a simple placeholder for events. Content to be filled via JSON later."""
        QMessageBox.information(self, "Event", "An event occurs (placeholder). Fill details in data/events.json.")

    def start_enemy_placeholder(self):
        """Start a simple enemy encounter using loaded content when available."""
        lvl = str(self.dungeon["level"])
        enemies_for_level = self.content.get("enemies", {}).get(lvl, [])
        if enemies_for_level:
            enemy = random.choice(enemies_for_level)
            self.current_enemy = {
                "id": enemy.get("id"),
                "name": enemy.get("name", "Enemy"),
                "health": int(enemy.get("health", 10)),
                "attack": int(enemy.get("attack", 3)),
                "defense": int(enemy.get("defense", 1)),
                "reward_gold": int(enemy.get("reward_gold", 5)),
                "reward_exp": int(enemy.get("reward_exp", 3)),
                "is_boss": False,
            }
            self.update_log(f"A {self.current_enemy['name']} appears! Combat started.")
        else:
            self.current_enemy = {
                "id": "placeholder",
                "name": "Training Dummy",
                "health": 10,
                "attack": 0,
                "defense": 0,
                "reward_gold": 0,
                "reward_exp": 0,
                "is_boss": False,
            }
            self.update_log("An enemy appears (placeholder).")
        self.update_actions()
        self.update_combat_display()

    def start_boss_battle(self):
        """Start a boss encounter using loaded boss content when available."""
        lvl = str(self.dungeon["level"])
        boss = self.content.get("boss", {}).get(lvl)
        if boss:
            self.current_enemy = {
                "id": boss.get("id", f"boss_{lvl}"),
                "name": boss.get("name", "Boss"),
                "health": int(boss.get("health", 30)),
                "attack": int(boss.get("attack", 6)),
                "defense": int(boss.get("defense", 2)),
                "reward_gold": int(boss.get("reward_gold", 25)),
                "reward_exp": int(boss.get("reward_exp", 20)),
                "is_boss": True,
            }
            self.update_log(f"A powerful foe awaits: {self.current_enemy['name']}! Boss battle begins.")
        else:
            # Fallback boss
            self.current_enemy = {
                "id": f"boss_{lvl}",
                "name": "Sewer Abomination",
                "health": 35,
                "attack": 7,
                "defense": 2,
                "reward_gold": 20,
                "reward_exp": 18,
                "is_boss": True,
            }
            self.update_log("A powerful presence looms... A boss emerges!")

        # Switch to boss music
        self.play_boss_music()
        self.update_actions()
        self.update_combat_display()

    def handle_boss_placeholder(self):
        """Boss encounter placeholder at the final step of the level."""
        lvl = str(self.dungeon["level"])
        boss = self.content.get("boss", {}).get(lvl)
        if boss:
            self.update_log(f"A powerful foe awaits: {boss.get('name', 'Boss')} (placeholder).")
        else:
            self.update_log("A powerful presence looms... Boss battle is coming (placeholder).")

    def complete_level(self):
        """Handle level completion and move to next level."""
        self.update_log(f"You find stairs to Level {self.dungeon['level'] + 1}.")
        # Advance level
        self.dungeon["level"] += 1
        self.dungeon["progress"] = 0
        self.dungeon["state"] = "idle"
        self.update_location()

    def return_to_town(self):
        """Return to town from the dungeon."""
        if self.current_room == "dungeon":
            # Reset dungeon state
            self.dungeon["state"] = "idle"
            self.dungeon["progress"] = 0
            self.current_enemy = None
            
            # Return to town
            self.current_room = "town"
            self.update_location()
            self.update_actions()
            
            # Log the return
            steps_required = self.dungeon.get("steps_required", 0)
            self.update_log(f"You return to the safety of town. Dungeon progress reset (0/{steps_required}).")
            
            # Play sound effect
            if hasattr(self, 'sound_manager'):
                self.sound_manager.play_sound('click')
    
    def visit_shop(self):
        """Handle shop visit action with sound"""
        self.update_log("You visit the shop...")
        settings = QSettings("DungeonExplorer", "RPGGame")
        if settings.value("sound_effects", False, type=bool):
            self.sound_manager.play_sound("click")
            
        # Open shop dialog
        shop_dialog = ShopDialog(self.character, self.sound_manager, self)
        if shop_dialog.exec() == QDialog.DialogCode.Accepted:
            # Update character stats display after shopping
            self.update_stats()
            
            # Log purchases
            if shop_dialog.purchased_items:
                items_text = ", ".join([item["name"] for item in shop_dialog.purchased_items])
                self.update_log(f"You purchased: {items_text}")
            else:
                self.update_log("You leave the shop without buying anything.")
            
            # Restart background music
            self.play_background_music()
    
    def rest_at_inn(self):
        """Handle rest at inn action: open Inn dialog for save/heal"""
        self.update_log("You rest at the inn...")
        self.current_room = "inn"
        self.update_location()
        settings = QSettings("DungeonExplorer", "RPGGame")
        if settings.value("sound_effects", False, type=bool):
            self.sound_manager.play_sound("click")

        inn_dialog = InnDialog(self.character, self.sound_manager, self)
        if inn_dialog.exec() == QDialog.DialogCode.Accepted:
            # Update stats after potential healing
            self.update_stats()
            # Restart normal background music when leaving inn
            self.current_room = "town"
            self.update_location()
            self.play_background_music()
    
    def attack_enemy(self):
        """Simple combat: player attacks, enemy counterattacks if alive."""
        if not self.current_enemy:
            return
        settings = QSettings("DungeonExplorer", "RPGGame")
        if settings.value("sound_effects", False, type=bool):
            self.sound_manager.play_sound("attack")

        # Player attacks
        player_damage = max(1, self.character["attack"] - self.current_enemy["defense"])
        self.current_enemy["health"] -= player_damage
        self.update_log(f"You hit the {self.current_enemy['name']} for {player_damage} damage.")

        # Victory check
        if self.current_enemy["health"] <= 0:
            gold = self.current_enemy.get("reward_gold", 0)
            exp = self.current_enemy.get("reward_exp", 0)
            self.character["gold"] += gold
            self.character["exp"] += exp
            # Check for level up without stat increases
            self.check_level_up()
            self.update_stats()
            self.update_log(f"You defeated the {self.current_enemy['name']}! +{gold} gold, +{exp} EXP.")

            # If boss, complete the level and restore normal music
            if self.current_enemy.get("is_boss"):
                self.current_enemy = None
                self.dungeon["state"] = "completed"
                # Stop boss music and resume normal background
                self.sound_manager.stop_music()
                self.play_background_music()
                self.complete_level()
                return

            # Regular enemy victory: advance progress
            self.current_enemy = None
            self.dungeon["state"] = "idle"
            self.dungeon["progress"] += 1
            self.update_actions()
            return

        # Enemy counterattacks
        enemy_damage = max(1, self.current_enemy["attack"] - self.character["defense"])
        self.character["health"] = max(0, self.character["health"] - enemy_damage)
        self.update_log(f"The {self.current_enemy['name']} hits you for {enemy_damage} damage.")
        self.update_stats()

        # Defeat check
        if self.character["health"] <= 0:
            self.update_log("You are defeated! You wake up back in town.")
            # Minimal defeat handling
            self.current_enemy = None
            self.dungeon["state"] = "idle"
            self.current_room = "town"
            self.dungeon["progress"] = 0
            self.character["health"] = self.character["max_health"] // 2
            self.update_location()
            # Stop any boss music and resume normal town music
            self.sound_manager.stop_music()
            self.play_background_music()
            self.update_actions()
        else:
            self.update_combat_display()
    
    def use_potion(self):
        """Restore health if a potion is available."""
        settings = QSettings("DungeonExplorer", "RPGGame")
        if self.character.get("potions", 0) <= 0:
            self.update_log("No potions left!")
            return
        heal_amount = max(10, self.character["max_health"] // 4)
        self.character["potions"] -= 1
        self.character["health"] = min(self.character["max_health"], self.character["health"] + heal_amount)
        self.update_log(f"You use a potion and heal {heal_amount} HP.")
        if settings.value("sound_effects", False, type=bool):
            self.sound_manager.play_sound("potion")
        self.update_stats()
        self.update_combat_display()
    
    def flee_combat(self):
        """Attempt to flee: exit combat; progress doesn't change."""
        settings = QSettings("DungeonExplorer", "RPGGame")
        self.update_log("You attempt to flee!")
        if settings.value("sound_effects", False, type=bool):
            self.sound_manager.play_sound("explore")
        if self.current_enemy:
            self.update_log("You successfully flee from combat.")
            # If fleeing from a boss, restore normal music
            if self.current_enemy.get("is_boss"):
                self.sound_manager.stop_music()
                self.play_background_music()
        self.current_enemy = None
        self.dungeon["state"] = "idle"
        self.update_actions()
        self.update_combat_display()

    def update_combat_display(self):
        """Update combat label with current stats."""
        if not self.combat_label:
            return
        if self.current_enemy:
            self.combat_label.setText(
                f"⚔️ COMBAT\nEnemy: {self.current_enemy['name']}\n"
                f"Enemy HP: {self.current_enemy['health']}\n"
                f"Your HP: {self.character['health']}/{self.character['max_health']}"
            )
        else:
            self.combat_label.setText("Combat")

# Main application execution
if __name__ == "__main__":
    app = QApplication(sys.argv)
    game = RPGGame()
    game.show()
    sys.exit(app.exec())