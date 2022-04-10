from re import S
from database import read_database, get_database
import os


class Board:
    """
    Defines a abstract board for Termoo, Wardle etc.
    """

    def __init__(self, n_letters):
        # Loading database
        path_data = os.path.join(os.environ["TEMP"], "data_TD.csv")
        if not os.path.exists(path_data):
            get_database()

        self.df = read_database(path_data, n_letters)
        self.plays = []
        self.excluded_letters = []
        self.included_letters = []
        self.known_letters = []
        self.unknown_indexes = []
        self.answer = "_" * n_letters

    def make_input(self, word):
        indexes = []
        for i, letter in enumerate(word):
            guess = int(input(f"{letter.upper()} : "))
            # Letters that are not in the word
            if guess == 0:
                self.excluded_letters.append(letter)

            # Letters that are in the word, but wrong position
            elif guess == 1:
                self.included_letters.append((letter, i))

            # Letters that are in the word, and right position
            else:
                self.known_letters.append((letter, i))
                self.answer = self.answer[:i] + letter + self.answer[i + 1 :]

            indexes.append(guess)

        # Unkoown indexes
        self.unknown_indexes = [
            i for i, letter in enumerate(self.answer) if letter == "_"
        ]

        self.plays.append((word, indexes))

    def build_query(self):
        """Explanation of the algorithm:
        We have three lists:
        1. known_letters    - list of known letters and their position (e.g. [('a', 1), ('b', 2), ('c', 3)])
        2. excluded_letters - list of excluded letters (e.g. ['a', 'b', 'c'])
        3. included_letters - list of letters that are in the word but wrong place (e.g. [('a', 1), ('b', 2), ('c', 3)])
        4. unknown_indexes  - list of indexes that are unknown (e.g. [1, 2, 4])

        To build the query, we must start with known letters:
        - For each known letter, add "id.str[<index>] == <letter>"

        Then, we must exclude letters that are NOT in the word:
        - None of the unknown indexes should contain letters that are in excluded_letters
        - So, we must iterate over unknown_indexes and add "id.str[<unknown_index>] != <letter>"

        Finally, we must include letters that are in the word but wrong place:
        - First, iterate over included_letters, deconstructing then into (letter, index)
        - Then, remove the index from unknown_indexes
        - Iterate over unknown_indexes
        - One of this indexes must contain the letter, so we must use the "or" operator
        - e.g. "id.str[1] == "a or id.str[0] == 'b'
        """
        query = []

        # Adding known letters to the query
        tmp = []
        for letter, index in self.known_letters:
            tmp.append(f"id.str[{index}] == '{letter}'")
        query.append(" and ".join(tmp))

        # Adding excluded letters to the query
        tmp = []
        for index in self.unknown_indexes:
            tmp.append(f"id.str[{index}] not in {self.excluded_letters}")
        query.append(" and ".join(tmp))

        # Adding included letters to the query
        tmp = []
        for letter, index in self.included_letters:
            tmp.append(f"id.str[{index}] != '{letter}'")
        query.append(" and ".join(tmp))

        # Adding letter that must be in the word
        tmp = []
        for letter, index in self.included_letters:
            index_tmp = self.unknown_indexes.copy()
            if index_tmp.index(index) in index_tmp:
                index_tmp.remove(index_tmp.index(index))
            for i in index_tmp:
                tmp.append(f"id.str[{i}] == '{letter}'")
        tmp = " or ".join(tmp)
        if tmp != "":
            query.append("(" + tmp + ")")
        query = list(filter(lambda x: x != "", query))
        print(query)
        return " and ".join(query)

    def guess_word(self):
        query = self.build_query()
        self.df = self.df.query(query)


class Game:
    def __init__(self):
        self.n_games = input("How many games? ")
        self.n_letters = input("How many letters? ")
        self.n_chances = input("How many chances? ")
        self.boards = []
        print("Initializing the game")
        for _ in range(int(self.n_games)):
            self.boards.append(Board(int(self.n_letters)))

        self.play()

    def play(self):
        for _ in range(int(self.n_chances)):
            for board in self.boards:
                word = board.df.sample(1)["id"].iloc[0]
                print(f"Try: {word}")
                board.make_input(word)
                board.guess_word()
                print(board.df)
                # win = int(input("Win (1|0)? "))
                # if bool(win):
                #     print("We won!")
                #     break
                print(f"Answer: {board.answer}")


if __name__ == "__main__":
    Game()
