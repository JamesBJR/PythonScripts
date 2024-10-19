import customtkinter as ctk
from tkinter import messagebox

class ModernPokedexGUI:
    def __init__(self, root):
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")
        
        self.root = root
        self.root.title("Modern Pokédex")
        self.root.geometry("500x700")

        self.pokedex = {}

        # Frame for Entries and Buttons
        self.frame = ctk.CTkFrame(self.root)
        self.frame.pack(pady=20, padx=20, fill="both", expand=True)

        # Labels and entry fields
        self.label_num = ctk.CTkLabel(self.frame, text="Pokémon Number:")
        self.label_num.pack(pady=5)
        self.entry_num = ctk.CTkEntry(self.frame)
        self.entry_num.pack(pady=5)

        self.label_name = ctk.CTkLabel(self.frame, text="Pokémon Name:")
        self.label_name.pack(pady=5)
        self.entry_name = ctk.CTkEntry(self.frame)
        self.entry_name.pack(pady=5)

        self.label_type1 = ctk.CTkLabel(self.frame, text="Pokémon Type 1:")
        self.label_type1.pack(pady=5)
        self.entry_type1 = ctk.CTkEntry(self.frame)
        self.entry_type1.pack(pady=5)

        self.label_type2 = ctk.CTkLabel(self.frame, text="Pokémon Type 2 (Optional):")
        self.label_type2.pack(pady=5)
        self.entry_type2 = ctk.CTkEntry(self.frame)
        self.entry_type2.pack(pady=5)

        # Buttons
        self.add_button = ctk.CTkButton(self.frame, text="Add Pokémon", command=self.add_pokemon)
        self.add_button.pack(pady=10)

        self.search_button = ctk.CTkButton(self.frame, text="Search Pokémon", command=self.search_pokemon)
        self.search_button.pack(pady=10)

        self.display_button = ctk.CTkButton(self.frame, text="Display Pokédex", command=self.display_pokedex)
        self.display_button.pack(pady=10)

        # Textbox for Displaying Pokédex
        self.textbox = ctk.CTkTextbox(self.root, width=450, height=250)
        self.textbox.pack(pady=20)

    def add_pokemon(self):
        number = self.entry_num.get()
        name = self.entry_name.get()
        type1 = self.entry_type1.get()
        type2 = self.entry_type2.get() if self.entry_type2.get() else "None"

        if number and name and type1:
            self.pokedex[number] = {
                "name": name,
                "type1": type1,
                "type2": type2
            }
            messagebox.showinfo("Success", f"{name} added to the Pokédex!")
        else:
            messagebox.showerror("Error", "Please fill in all required fields.")

    def search_pokemon(self):
        number = self.entry_num.get()
        if number in self.pokedex:
            pokemon = self.pokedex[number]
            result = f"#{number}: {pokemon['name']} (Type: {pokemon['type1']}, {pokemon['type2']})"
            messagebox.showinfo("Pokédex Search", result)
        else:
            messagebox.showerror("Not Found", f"Pokémon with number {number} not found.")

    def display_pokedex(self):
        self.textbox.delete("1.0", "end")  # Clear the textbox

        if not self.pokedex:
            self.textbox.insert("1.0", "The Pokédex is empty.")
        else:
            for number, pokemon in self.pokedex.items():
                text = f"#{number}: {pokemon['name']} (Type: {pokemon['type1']}, {pokemon['type2']})\n"
                self.textbox.insert("end", text)

# Main
if __name__ == "__main__":
    root = ctk.CTk()
    app = ModernPokedexGUI(root)
    root.mainloop()
