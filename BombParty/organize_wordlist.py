
def organize_wordlist_by_length(input_file, output_file):
    with open(input_file, 'r') as file:
        words = file.read().splitlines()

    # Sort words by length in descending order
    words.sort(key=len, reverse=True)

    with open(output_file, 'w') as file:
        for word in words:
            file.write(word + '\n')

if __name__ == "__main__":
    input_file = 'C:/GitHubRepos/MyPythonScripts/BombParty/merged_wordlist.txt'
    output_file = 'C:/GitHubRepos/MyPythonScripts/BombParty/organized_wordlist.txt'
    organize_wordlist_by_length(input_file, output_file)
    print(f"Word list organized by length and saved to {output_file}")
