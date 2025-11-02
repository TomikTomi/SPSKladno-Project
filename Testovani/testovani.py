import sys
import random
import os
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QPushButton, QLabel, 
    QVBoxLayout, QHBoxLayout, QWidget, QTextEdit, QProgressBar
)
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QPixmap, QFont

class RPGGame(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Dungeon Explorer")
        self.resize(600, 700)
        
        # Player stats
        self.player = {
            "level": 1,
            "exp": 0,
            "exp_to_level": 100,
            "health": 100,
            "max_health": 100,
            "attack": 10,
            "defense": 5,
            "gold": 50,
            "potions": 3
        }
        
        # Game state
        self.current_room = "town"
        self.current_enemy = None
        self.game_log = ["Welcome to Dungeon Explorer!", "You are in the town square."]
        
        # Initialize UI components first
        self.health_bar = None
        self.stats_label = None
        self.log_display = None
        self.location_label = None
        self.combat_label = None
        
        # Setup UI
        self.init_ui()
        
    def init_ui(self):
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout()
        
        # Title
        title = QLabel("Dungeon Explorer")
        title.setFont(QFont("Arial", 16, QFont.Weight.Bold))
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        # Player stats
        stats_layout = QHBoxLayout()
        
        self.stats_label = QLabel()
        
        self.health_bar = QProgressBar()
        self.health_bar.setMaximum(100)
        self.health_bar.setValue(100)
        self.health_bar.setStyleSheet("QProgressBar::chunk { background-color: red; }")
        
        stats_layout.addWidget(self.stats_label)
        stats_layout.addWidget(self.health_bar)
        
        # Game log
        self.log_display = QTextEdit()
        self.log_display.setMaximumHeight(150)
        self.log_display.setReadOnly(True)
        
        # Location display
        self.location_label = QLabel()
        self.location_label.setFont(QFont("Arial", 12, QFont.Weight.Bold))
        
        # Action buttons
        self.action_buttons_layout = QHBoxLayout()
        
        # Combat display (hidden initially)
        self.combat_label = QLabel()
        self.combat_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        # Combat buttons (hidden initially)
        self.combat_buttons_layout = QHBoxLayout()
        self.attack_button = QPushButton("Attack")
        self.defend_button = QPushButton("Defend")
        self.potion_button = QPushButton("Use Potion")
        self.flee_button = QPushButton("Flee")
        
        self.attack_button.clicked.connect(self.player_attack)
        self.defend_button.clicked.connect(self.player_defend)
        self.potion_button.clicked.connect(self.use_potion)
        self.flee_button.clicked.connect(self.flee_combat)
        
        self.combat_buttons_layout.addWidget(self.attack_button)
        self.combat_buttons_layout.addWidget(self.defend_button)
        self.combat_buttons_layout.addWidget(self.potion_button)
        self.combat_buttons_layout.addWidget(self.flee_button)
        
        # Add widgets to main layout
        layout.addWidget(title)
        layout.addLayout(stats_layout)
        layout.addWidget(self.location_label)
        layout.addWidget(self.log_display)
        layout.addLayout(self.action_buttons_layout)
        layout.addWidget(self.combat_label)
        layout.addLayout(self.combat_buttons_layout)
        
        central_widget.setLayout(layout)
        
        # Initialize game state after UI is built
        self.update_stats()
        self.update_log()
        self.update_location()
        self.update_actions()
        
        # Hide combat UI initially
        self.hide_combat_ui()
    
    def update_stats(self):
        if self.stats_label and self.health_bar:
            self.stats_label.setText(
                f"Level: {self.player['level']}\n"
                f"EXP: {self.player['exp']}/{self.player['exp_to_level']}\n"
                f"Attack: {self.player['attack']}\n"
                f"Defense: {self.player['defense']}\n"
                f"Gold: {self.player['gold']}\n"
                f"Potions: {self.player['potions']}"
            )
            self.health_bar.setMaximum(self.player['max_health'])
            self.health_bar.setValue(self.player['health'])
    
    def update_log(self):
        if self.log_display:
            self.log_display.clear()
            for message in self.game_log[-10:]:  # Show last 10 messages
                self.log_display.append(message)
            self.log_display.verticalScrollBar().setValue(
                self.log_display.verticalScrollBar().maximum()
            )
    
    def update_location(self):
        if self.location_label:
            location_names = {
                "town": "🏠 Town Square",
                "forest": "🌲 Dark Forest", 
                "cave": "🕳️ Deep Cave",
                "boss": "🐉 Dragon's Lair"
            }
            self.location_label.setText(f"Location: {location_names.get(self.current_room, self.current_room)}")
    
    def update_actions(self):
        # Clear existing buttons
        for i in reversed(range(self.action_buttons_layout.count())): 
            widget = self.action_buttons_layout.itemAt(i).widget()
            if widget:
                widget.setParent(None)
        
        # Add location-specific actions
        if self.current_room == "town":
            self.add_action_button("Go to Forest", lambda: self.change_location("forest"))
            self.add_action_button("Visit Shop", self.visit_shop)
            self.add_action_button("Rest", self.rest)
            
        elif self.current_room == "forest":
            self.add_action_button("Return to Town", lambda: self.change_location("town"))
            self.add_action_button("Explore", self.explore_forest)
            self.add_action_button("Go Deeper", lambda: self.change_location("cave"))
            
        elif self.current_room == "cave":
            self.add_action_button("Return to Forest", lambda: self.change_location("forest"))
            self.add_action_button("Explore Cave", self.explore_cave)
            if self.player["level"] >= 3:
                self.add_action_button("Face the Dragon", lambda: self.change_location("boss"))
                
        elif self.current_room == "boss":
            self.add_action_button("Flee to Cave", lambda: self.change_location("cave"))
            self.add_action_button("Fight Dragon", self.start_boss_fight)
    
    def add_action_button(self, text, callback):
        button = QPushButton(text)
        button.clicked.connect(callback)
        self.action_buttons_layout.addWidget(button)
    
    def add_log_message(self, message):
        self.game_log.append(message)
        self.update_log()
    
    def change_location(self, new_location):
        self.current_room = new_location
        self.add_log_message(f"You travel to {new_location}.")
        self.update_location()
        self.update_actions()
        self.hide_combat_ui()
    
    def rest(self):
        heal_amount = self.player["max_health"] // 2
        self.player["health"] = min(self.player["max_health"], self.player["health"] + heal_amount)
        self.add_log_message(f"You rest and recover {heal_amount} health.")
        self.update_stats()
    
    def visit_shop(self):
        if self.player["gold"] >= 30:
            self.player["gold"] -= 30
            self.player["potions"] += 1
            self.add_log_message("You bought a health potion for 30 gold.")
        else:
            self.add_log_message("Not enough gold for a potion (30 gold needed).")
        self.update_stats()
    
    def explore_forest(self):
        encounters = [
            ("You find a treasure chest!", self.find_treasure),
            ("A wild goblin appears!", lambda: self.start_combat("Goblin", 30, 8, 3, 25)),
            ("You find a healing herb.", self.find_herb),
            ("Nothing interesting happens.", lambda: None)
        ]
        message, action = random.choice(encounters)
        self.add_log_message(message)
        if action:
            action()
    
    def explore_cave(self):
        encounters = [
            ("An orc warrior blocks your path!", lambda: self.start_combat("Orc Warrior", 50, 12, 6, 40)),
            ("You discover a hidden treasure!", self.find_cave_treasure),
            ("Bats fly past you harmlessly.", lambda: None),
            ("A skeleton rises from the ground!", lambda: self.start_combat("Skeleton", 40, 10, 4, 35))
        ]
        message, action = random.choice(encounters)
        self.add_log_message(message)
        if action:
            action()
    
    def find_treasure(self):
        gold = random.randint(10, 30)
        self.player["gold"] += gold
        self.add_log_message(f"You found {gold} gold!")
        self.update_stats()
    
    def find_cave_treasure(self):
        gold = random.randint(30, 60)
        self.player["gold"] += gold
        if random.random() < 0.3:  # 30% chance for potion
            self.player["potions"] += 1
            self.add_log_message(f"You found {gold} gold and a health potion!")
        else:
            self.add_log_message(f"You found {gold} gold!")
        self.update_stats()
    
    def find_herb(self):
        heal = random.randint(10, 25)
        self.player["health"] = min(self.player["max_health"], self.player["health"] + heal)
        self.add_log_message(f"The healing herb restores {heal} health.")
        self.update_stats()
    
    def start_combat(self, enemy_name, enemy_health, enemy_attack, enemy_defense, exp_reward):
        self.current_enemy = {
            "name": enemy_name,
            "health": enemy_health,
            "max_health": enemy_health,
            "attack": enemy_attack,
            "defense": enemy_defense,
            "exp_reward": exp_reward
        }
        self.show_combat_ui()
        self.add_log_message(f"A {enemy_name} appears! Combat started!")
    
    def start_boss_fight(self):
        self.start_combat("Ancient Dragon", 150, 20, 10, 200)
    
    def show_combat_ui(self):
        if self.combat_label:
            self.combat_label.show()
        self.attack_button.show()
        self.defend_button.show()
        self.potion_button.show()
        self.flee_button.show()
        self.update_combat_display()
    
    def hide_combat_ui(self):
        if self.combat_label:
            self.combat_label.hide()
        self.attack_button.hide()
        self.defend_button.hide()
        self.potion_button.hide()
        self.flee_button.hide()
        self.current_enemy = None
    
    def update_combat_display(self):
        if self.current_enemy and self.combat_label:
            enemy = self.current_enemy
            self.combat_label.setText(
                f"⚔️ COMBAT ⚔️\n"
                f"{enemy['name']}: {enemy['health']}/{enemy['max_health']} HP\n"
                f"Player: {self.player['health']}/{self.player['max_health']} HP"
            )
    
    def player_attack(self):
        if not self.current_enemy:
            return
        
        # Player attack
        player_damage = max(1, self.player["attack"] - self.current_enemy["defense"] // 2)
        self.current_enemy["health"] -= player_damage
        self.add_log_message(f"You attack for {player_damage} damage!")
        
        if self.current_enemy["health"] <= 0:
            self.win_combat()
            return
        
        # Enemy attack
        self.enemy_attack()
    
    def player_defend(self):
        if not self.current_enemy:
            return
        
        # Player defends (take half damage this turn)
        self.add_log_message("You brace for impact!")
        
        # Enemy attack with reduced damage
        enemy_damage = max(1, (self.current_enemy["attack"] - self.player["defense"]) // 2)
        self.player["health"] -= enemy_damage
        self.add_log_message(f"The {self.current_enemy['name']} attacks for {enemy_damage} damage!")
        
        self.check_combat_status()
    
    def enemy_attack(self):
        enemy_damage = max(1, self.current_enemy["attack"] - self.player["defense"])
        self.player["health"] -= enemy_damage
        self.add_log_message(f"The {self.current_enemy['name']} attacks for {enemy_damage} damage!")
        
        self.check_combat_status()
    
    def use_potion(self):
        if self.player["potions"] > 0:
            heal_amount = 40
            self.player["health"] = min(self.player["max_health"], self.player["health"] + heal_amount)
            self.player["potions"] -= 1
            self.add_log_message(f"You use a potion and heal {heal_amount} health!")
            self.update_stats()
            
            # Enemy still attacks
            self.enemy_attack()
        else:
            self.add_log_message("You have no potions left!")
    
    def flee_combat(self):
        if random.random() < 0.7:  # 70% chance to flee
            self.add_log_message("You successfully flee from combat!")
            self.hide_combat_ui()
        else:
            self.add_log_message("You failed to flee!")
            self.enemy_attack()
    
    def check_combat_status(self):
        if self.player["health"] <= 0:
            self.game_over()
        else:
            self.update_combat_display()
            self.update_stats()
    
    def win_combat(self):
        exp = self.current_enemy["exp_reward"]
        gold = random.randint(10, 30)
        
        self.player["exp"] += exp
        self.player["gold"] += gold
        
        self.add_log_message(f"You defeated the {self.current_enemy['name']}!")
        self.add_log_message(f"Gained {exp} EXP and {gold} gold!")
        
        self.check_level_up()
        self.hide_combat_ui()
    
    def check_level_up(self):
        if self.player["exp"] >= self.player["exp_to_level"]:
            self.player["level"] += 1
            self.player["exp"] = 0
            self.player["exp_to_level"] = int(self.player["exp_to_level"] * 1.5)
            self.player["max_health"] += 20
            self.player["health"] = self.player["max_health"]
            self.player["attack"] += 3
            self.player["defense"] += 2
            
            self.add_log_message(f"⭐ Level Up! You are now level {self.player['level']}!")
            self.add_log_message("Health, attack, and defense increased!")
        
        self.update_stats()
    
    def game_over(self):
        self.add_log_message("💀 YOU DIED! Game Over!")
        self.add_log_message("Restart the game to play again.")
        self.hide_combat_ui()
        # Disable all action buttons
        for i in range(self.action_buttons_layout.count()):
            widget = self.action_buttons_layout.itemAt(i).widget()
            if widget:
                widget.setEnabled(False)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    game = RPGGame()
    game.show()
    sys.exit(app.exec())