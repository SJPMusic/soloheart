"""
DnD 5E AI-Powered Game - GUI Interface
=====================================

A basic GUI window for interactive DnD gameplay
"""

import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox
import threading
import queue
from datetime import datetime
import sys
import os

# Add the project root to the path so we can import our modules
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from main import DnDCampaignManager
from core.character_manager import Character

class DnDGameGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("DnD 5E AI-Powered Solo Game")
        self.root.geometry("800x600")
        self.root.minsize(600, 400)
        
        # Initialize game systems
        self.campaign = None
        self.current_character = None
        self.message_queue = queue.Queue()
        
        # Create GUI elements
        self.create_widgets()
        
        # Start message processing
        self.process_messages()
    
    def create_widgets(self):
        """Create and arrange GUI widgets"""
        # Main frame
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Configure grid weights for resizing
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
        main_frame.rowconfigure(1, weight=1)
        
        # Title
        title_label = ttk.Label(main_frame, text="DnD 5E AI-Powered Solo Game", 
                               font=("Arial", 16, "bold"))
        title_label.grid(row=0, column=0, columnspan=3, pady=(0, 10))
        
        # Game output area
        output_frame = ttk.LabelFrame(main_frame, text="Game Output", padding="5")
        output_frame.grid(row=1, column=0, columnspan=3, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(0, 10))
        output_frame.columnconfigure(0, weight=1)
        output_frame.rowconfigure(0, weight=1)
        
        self.output_text = scrolledtext.ScrolledText(output_frame, wrap=tk.WORD, 
                                                    width=70, height=20, state=tk.DISABLED)
        self.output_text.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Input area
        input_frame = ttk.Frame(main_frame)
        input_frame.grid(row=2, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(0, 10))
        input_frame.columnconfigure(0, weight=1)
        
        self.input_entry = ttk.Entry(input_frame, font=("Arial", 12))
        self.input_entry.grid(row=0, column=0, sticky=(tk.W, tk.E), padx=(0, 5))
        self.input_entry.bind("<Return>", self.handle_input)
        
        send_button = ttk.Button(input_frame, text="Send", command=self.handle_input)
        send_button.grid(row=0, column=1)
        
        # Control buttons
        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=3, column=0, columnspan=3, pady=(0, 10))
        
        ttk.Button(button_frame, text="New Character", command=self.new_character).grid(row=0, column=0, padx=5)
        ttk.Button(button_frame, text="Start Session", command=self.start_session).grid(row=0, column=1, padx=5)
        ttk.Button(button_frame, text="End Session", command=self.end_session).grid(row=0, column=2, padx=5)
        ttk.Button(button_frame, text="Clear Output", command=self.clear_output).grid(row=0, column=3, padx=5)
        
        # Status bar
        self.status_var = tk.StringVar()
        self.status_var.set("Ready - Type 'help' for commands")
        status_bar = ttk.Label(main_frame, textvariable=self.status_var, relief=tk.SUNKEN)
        status_bar.grid(row=4, column=0, columnspan=3, sticky=(tk.W, tk.E))
        
        # Focus on input
        self.input_entry.focus()
        
        # Welcome message
        self.add_message("Welcome to DnD 5E AI-Powered Solo Game!")
        self.add_message("Type 'help' to see available commands.")
        self.add_message("Type 'new character' to create a character and start playing!")
        self.add_message("")
    
    def add_message(self, message, message_type="info"):
        """Add a message to the output area"""
        self.message_queue.put((message, message_type))
    
    def process_messages(self):
        """Process messages from the queue"""
        try:
            while True:
                message, message_type = self.message_queue.get_nowait()
                
                # Enable text widget for editing
                self.output_text.config(state=tk.NORMAL)
                
                # Add timestamp
                timestamp = datetime.now().strftime("%H:%M:%S")
                
                # Format message based on type
                if message_type == "error":
                    formatted_message = f"[{timestamp}] ERROR: {message}\n"
                elif message_type == "success":
                    formatted_message = f"[{timestamp}] ✓ {message}\n"
                elif message_type == "ai":
                    formatted_message = f"[{timestamp}] AI: {message}\n"
                elif message_type == "player":
                    formatted_message = f"[{timestamp}] You: {message}\n"
                else:
                    formatted_message = f"[{timestamp}] {message}\n"
                
                # Insert message
                self.output_text.insert(tk.END, formatted_message)
                
                # Auto-scroll to bottom
                self.output_text.see(tk.END)
                
                # Disable text widget
                self.output_text.config(state=tk.DISABLED)
                
        except queue.Empty:
            pass
        
        # Schedule next check
        self.root.after(100, self.process_messages)
    
    def handle_input(self, event=None):
        """Handle user input"""
        command = self.input_entry.get().strip()
        if not command:
            return
        
        # Clear input
        self.input_entry.delete(0, tk.END)
        
        # Echo player input
        self.add_message(command, "player")
        
        # Process command
        self.process_command(command)
    
    def process_command(self, command):
        """Process user commands"""
        command_lower = command.lower()
        
        # Game management commands
        if command_lower == "help":
            self.show_help()
        elif command_lower == "new character":
            self.new_character()
        elif command_lower == "start session":
            self.start_session()
        elif command_lower == "end session":
            self.end_session()
        elif command_lower == "clear":
            self.clear_output()
        # Handle all other input as conversation with AI DM
        else:
            self.handle_ai_conversation(command)
    
    def show_help(self):
        """Show help information"""
        help_text = """
Welcome to DnD 5E AI-Powered Solo Game!
========================================

This is a conversational AI DM that remembers everything about your adventures.

How to Play:
-----------
1. **Create your character naturally** - Just tell me about yourself:
   "I'm a half-elf wizard named Gandalf who specializes in fire magic"
   "My name is Thorin, I'm a dwarf fighter with a mysterious past"

2. **Start playing** - Just describe what you want to do:
   "I explore the dark forest"
   "I talk to the innkeeper about rumors"
   "I cast fireball at the goblins"
   "What do I see around me?"

3. **The AI remembers everything** - Your character, locations, NPCs, and story progress are all saved.

Commands:
---------
start session    - Start a new game session
end session      - End the current session
clear            - Clear the output
help             - Show this help

Just type naturally and the AI DM will respond!
        """
        self.add_message(help_text)
    
    def new_character(self):
        """Create a new character - now handled conversationally"""
        self.add_message("Tell me about your character! For example:", "info")
        self.add_message("'I'm a half-elf wizard named Gandalf'", "info")
        self.add_message("'My name is Thorin, I'm a dwarf fighter'", "info")
        self.add_message("Just describe who you are and what kind of adventurer you want to be!", "info")
    
    def start_session(self):
        """Start a new session"""
        if not self.campaign:
            self.campaign = DnDCampaignManager("Interactive Campaign")
            self.add_message("Campaign created! Now tell me about your character.", "success")
            return
        
        try:
            session = self.campaign.start_session()
            self.add_message(f"Session started: {session.session_id}", "success")
            self.add_message("You find yourself at the edge of a mysterious forest...", "ai")
            self.add_message("What would you like to do?", "ai")
            
        except Exception as e:
            self.add_message(f"Error starting session: {str(e)}", "error")
    
    def end_session(self):
        """End the current session"""
        if not self.campaign:
            self.add_message("No active session to end.", "error")
            return
        
        try:
            session_summary = self.campaign.end_session()
            self.add_message(f"Session ended. Duration: {session_summary.duration_minutes} minutes", "success")
            self.add_message("Session summary saved.", "info")
            
        except Exception as e:
            self.add_message(f"Error ending session: {str(e)}", "error")
    
    def clear_output(self):
        """Clear the output area"""
        self.output_text.config(state=tk.NORMAL)
        self.output_text.delete(1.0, tk.END)
        self.output_text.config(state=tk.DISABLED)
        self.add_message("Output cleared.", "info")

    def handle_ai_conversation(self, message):
        """Handle conversation with the AI DM"""
        try:
            self.status_var.set("AI is thinking...")
            self.root.update()
            
            # Ensure campaign exists
            if not self.campaign:
                self.campaign = DnDCampaignManager("Interactive Campaign")
            
            # Process the message through the AI DM engine
            response = self.campaign.process_player_action(message, self.current_character)
            
            # Update current character if one was created
            if not self.current_character and self.campaign.player_characters:
                self.current_character = list(self.campaign.player_characters.values())[0]
            
            # Display AI response
            self.add_message(response, "ai")
            
            # Update status
            if self.current_character:
                self.status_var.set(f"Session active - Character: {self.current_character.name}")
            else:
                self.status_var.set("Tell me about your character to begin!")
            
        except Exception as e:
            self.add_message(f"Error processing message: {str(e)}", "error")
            self.status_var.set("Error occurred")

def main():
    """Main function to start the GUI"""
    root = tk.Tk()
    app = DnDGameGUI(root)
    root.mainloop()

if __name__ == "__main__":
    main() 