
def merge_wordlists(file1, file2, output_file):
    words = set()

    # Read words from the first file
    with open(file1, 'r') as f1:
        for line in f1:
            word = line.strip().upper()
            if len(word) >= 3:
                words.add(word)

    # Read words from the second file
    with open(file2, 'r') as f2:
        for line in f2:
            word = line.strip().upper()
            if len(word) >= 3:
                words.add(word)

    # Write the merged words to the output file
    with open(output_file, 'w') as out:
        for word in sorted(words):
            out.write(word + '\n')

if __name__ == "__main__":
    file1 = 'C:/GitHubRepos/MyPythonScripts/BombParty/dict.txt'
    file2 = 'C:/GitHubRepos/MyPythonScripts/BombParty/wordlist.txt'
    output_file = 'C:/GitHubRepos/MyPythonScripts/BombParty/merged_wordlist.txt'
    merge_wordlists(file1, file2, output_file)
    print(f"Merged word list saved to {output_file}")
