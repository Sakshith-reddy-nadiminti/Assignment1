#!/usr/bin/env python3
"""Tic-Tac-Toe game with Minimax AI opponent."""

from enum import Enum
from typing import Optional, Tuple, List


class Player(Enum):
    X = "X"
    O = "O"

    def opponent(self) -> "Player":
        return Player.O if self == Player.X else Player.X


class CellState(Enum):
    EMPTY = " "
    X = "X"
    O = "O"


class Board:
    def __init__(self, size: int = 3):
        self.size = size
        self._cells: List[List[CellState]] = [[CellState.EMPTY for _ in range(size)] for _ in range(size)]

    def copy(self) -> "Board":
        new_board = Board(self.size)
        for i in range(self.size):
            for j in range(self.size):
                new_board._cells[i][j] = self._cells[i][j]
        return new_board

    def make_move(self, row: int, col: int, player: Player) -> bool:
        if not (0 <= row < self.size and 0 <= col < self.size):
            return False
        if self._cells[row][col] != CellState.EMPTY:
            return False
        self._cells[row][col] = CellState(player.value)
        return True

    def is_empty(self, row: int, col: int) -> bool:
        return self._cells[row][col] == CellState.EMPTY

    def get_legal_moves(self) -> List[Tuple[int, int]]:
        moves = []
        for r in range(self.size):
            for c in range(self.size):
                if self.is_empty(r, c):
                    moves.append((r, c))
        return moves

    def is_full(self) -> bool:
        return all(self._cells[r][c] != CellState.EMPTY for r in range(self.size) for c in range(self.size))

    def get_winner(self) -> Optional[Player]:
        win_lines = self._get_win_lines()
        for a, b, c in win_lines:
            if self._cells[a[0]][a[1]] != CellState.EMPTY:
                if (self._cells[a[0]][a[1]] == self._cells[b[0]][b[1]] == self._cells[c[0]][c[1]]):
                    return Player(self._cells[a[0]][a[1]].value)
        return None

    def is_draw(self) -> bool:
        return self.is_full() and self.get_winner() is None

    def _get_win_lines(self) -> List[Tuple[Tuple[int, int], Tuple[int, int], Tuple[int, int]]]:
        lines = []
        for i in range(self.size):
            lines.append(((i, 0), (i, 1), (i, 2)))
            lines.append(((0, i), (1, i), (2, i)))
        lines.append(((0, 0), (1, 1), (2, 2)))
        lines.append(((0, 2), (1, 1), (2, 0)))
        return lines

    def __str__(self) -> str:
        lines = []
        for r in range(self.size):
            row_str = " | ".join(self._cells[r][c].value for c in range(self.size))
            lines.append(row_str)
            if r < self.size - 1:
                lines.append("-" * (self.size * 2 + 1))
        return "\n".join(lines)


class MinimaxAI:
    def __init__(self, player: Player):
        self.player = player

    def choose_move(self, board: Board) -> Tuple[int, int]:
        best_score = float("-inf")
        best_moves = []
        for move in board.get_legal_moves():
            new_board = board.copy()
            new_board.make_move(move[0], move[1], self.player)
            score = self._minimax(new_board, 0, False)
            if score > best_score:
                best_score = score
                best_moves = [move]
            elif score == best_score:
                best_moves.append(move)

        # Tie-breaker: prefer center, then corners, then edges
        center = (1, 1)
        corners = [(0, 0), (0, 2), (2, 0), (2, 2)]
        if center in best_moves:
            return center
        for corner in corners:
            if corner in best_moves:
                return corner
        return best_moves[0]

    def _minimax(self, board: Board, depth: int, is_maximizing: bool, alpha: float = float("-inf"), beta: float = float("inf")) -> int:
        winner = board.get_winner()
        if winner == self.player:
            return 10 - depth
        if winner == self.player.opponent():
            return depth - 10
        if board.is_draw():
            return 0

        if is_maximizing:
            best = float("-inf")
            for move in board.get_legal_moves():
                new_board = board.copy()
                new_board.make_move(move[0], move[1], self.player)
                score = self._minimax(new_board, depth + 1, False, alpha, beta)
                best = max(best, score)
                alpha = max(alpha, best)
                if beta <= alpha:
                    break
            return best
        else:
            best = float("inf")
            opponent = self.player.opponent()
            for move in board.get_legal_moves():
                new_board = board.copy()
                new_board.make_move(move[0], move[1], opponent)
                score = self._minimax(new_board, depth + 1, True, alpha, beta)
                best = min(best, score)
                beta = min(beta, best)
                if beta <= alpha:
                    break
            return best


class Game:
    def __init__(self, ai_player: Player = Player.O):
        self.board = Board()
        self.current_player = Player.X
        self.ai = MinimaxAI(ai_player)
        self.game_over = False
        self.winner: Optional[Player] = None

    def play_human_move(self, row: int, col: int) -> bool:
        if self.game_over:
            return False
        if self.current_player == self.ai.player:
            return False

        if self.board.make_move(row, col, self.current_player):
            self._check_game_end()
            if not self.game_over:
                self.current_player = self.current_player.opponent()
                if self.current_player == self.ai.player:
                    self._ai_move()
            return True
        return False

    def _ai_move(self):
        move = self.ai.choose_move(self.board)
        if move:
            self.board.make_move(move[0], move[1], self.ai.player)
            self._check_game_end()
            if not self.game_over:
                self.current_player = self.current_player.opponent()

    def _check_game_end(self):
        winner = self.board.get_winner()
        if winner:
            self.game_over = True
            self.winner = winner
        elif self.board.is_draw():
            self.game_over = True
            self.winner = None

    def is_valid_move(self, row: int, col: int) -> bool:
        if self.game_over:
            return False
        if self.current_player != self.ai.player and self.board.is_empty(row, col):
            return True
        return False

    def get_status(self) -> str:
        if self.game_over:
            if self.winner:
                return f"Game Over! {self.winner.value} wins!"
            return "Game Over! Draw!"
        return f"Current turn: {self.current_player.value}"

    def reset(self):
        self.board = Board()
        self.current_player = Player.X
        self.game_over = False
        self.winner = None

    def display(self) -> str:
        return f"\n{self.board}\n\n{self.get_status()}"


def get_input(prompt: str) -> str:
    try:
        return input(prompt)
    except EOFError:
        return ""


def main():
    print("Welcome to Tic-Tac-Toe!")
    print("You are X, the first player. AI is O.")
    print("Enter moves as 'row col' (0-2 for each). Example: 1 2")
    print("Type 'quit' to exit, 'reset' to restart the game.\n")

    game = Game(ai_player=Player.O)
    print(game.display())

    while True:
        if game.game_over:
            cmd = get_input("\nEnter 'quit' to exit or 'reset' to play again: ").strip().lower()
            if cmd == "quit":
                print("Thanks for playing!")
                break
            elif cmd == "reset":
                game.reset()
                print(game.display())
            continue

        user_input = get_input(f"\n{game.current_player.value}'s turn - Enter move (row col): ").strip().lower()

        if user_input == "quit":
            print("Thanks for playing!")
            break
        elif user_input == "reset":
            game.reset()
            print(game.display())
            continue

        parts = user_input.split()
        if len(parts) != 2:
            print("Invalid input. Use format: row col (e.g., 1 2)")
            continue

        try:
            row, col = int(parts[0]), int(parts[1])
        except ValueError:
            print("Invalid input. Use numbers 0-2.")
            continue

        if game.play_human_move(row, col):
            print(game.display())
        else:
            print("Invalid move. Try again.")


if __name__ == "__main__":
    main()