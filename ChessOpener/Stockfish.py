from stockfish import Stockfish

# Set the path to your Stockfish engine executable
stockfish_path = "C:/GitHubRepos/MyPythonScripts/ChessOpener/stockfish/stockfish-windows-x86-64-avx2.exe"

# Initialize the Stockfish engine
stockfish = Stockfish(stockfish_path)
stockfish.set_skill_level(10)  # Adjust skill level as needed

def get_best_move(fen):
    # Set the FEN position
    stockfish.set_fen_position(fen)
    
    # Get the best move from Stockfish
    best_move = stockfish.get_best_move()
    
    if best_move is None:
        return "No move available"
    
    # Split the move into starting and ending coordinates
    start_pos = best_move[:2]
    end_pos = best_move[2:]
    
    return start_pos, end_pos

# Get FEN input from the user
fen_input = input("Enter the FEN string: ")

# Get the best move
start, end = get_best_move(fen_input)
print(f"The best move is from {start} to {end}.")
