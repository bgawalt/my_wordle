"""Wordle Mean: Render your average Wordle board.

Reads in a collection of Wordle boards (as saved to a text file) and generates
a picture of your "average" Wordle grid -- the average color you've left each
square of the puzzle.
"""

import enum
import sys

from enum import Enum
from typing import Iterator, List, Tuple
from PIL import Image, ImageDraw


# Edge length of a letter-square, in pixels
SQUARE_PX = 120
# Width of the borders between squares, in pixels
BORDER_PX = 15
# Width of the border surrounding the grid overall.
OUTER_EDGE_PX = 3 * BORDER_PX
# Distance from corner-to-corresponding-corner of neighboring grid squares.
SQUARE_AND_BORDER_PX = SQUARE_PX + BORDER_PX


# Width of the overall image
IMG_WIDTH_PX = (OUTER_EDGE_PX
                + (5 * SQUARE_AND_BORDER_PX)
                + OUTER_EDGE_PX - BORDER_PX)
# Height of the overall image
IMG_HEIGHT_PX = (OUTER_EDGE_PX
                 + (6 * SQUARE_AND_BORDER_PX)
                 + OUTER_EDGE_PX - BORDER_PX)


def char_rect(row: int, col: int) -> Tuple[Tuple[int, int], Tuple[int, int]]:
    """Returns ((upper_left, lower_right)) pixel corners of a grid point."""
    if row > 5:
        raise ValueError("row is too big (%d)" % (row,))
    if col > 4:
        raise ValueError("col is too big (%d)" % (col,))
    y0 = OUTER_EDGE_PX + (row * SQUARE_AND_BORDER_PX)
    y1 = y0 + SQUARE_PX
    x0 = OUTER_EDGE_PX + (col * SQUARE_AND_BORDER_PX)
    x1 = x0 + SQUARE_PX
    return ((x0, y0), (x1, y1))



@enum.unique
class WordleColor(Enum):
    GREY = '787C7E'
    YELLOW = 'CAB459'
    GREEN = '6AAA64'
    WHITE = 'FFFFFF'

    def to_rgb(self):
        # TODO: Save some time by making this a property?
        return (int(self.value[:2], 16),
                int(self.value[2:4], 16),
                int(self.value[4:], 16))


# Every five-letter guess is converted into five corresponding colors.
GuessColors = (
    Tuple[WordleColor, WordleColor, WordleColor, WordleColor, WordleColor])


# Unused guesses (e.g., the fourth row for a Wordle solved in two) is all white.
ALL_WHITE: GuessColors = (
    WordleColor.WHITE, WordleColor.WHITE, WordleColor.WHITE,
    WordleColor.WHITE, WordleColor.WHITE)


def word_to_colors(guess: str, answer: str) -> GuessColors:
    if len(guess) != 5:
        raise ValueError('Guesses are 5 characters (not %d)' % (len(guess)))
    if len(answer) != 5:
        raise ValueError('Answers are 5 characters (not %d)' % (len(answer)))
    colors = []
    for g_ch, a_ch in zip(guess, answer):
        if g_ch == a_ch:
            colors.append(WordleColor.GREEN)
        elif g_ch in answer:
            colors.append(WordleColor.YELLOW)
        else:
            colors.append(WordleColor.GREY)
    return tuple(colors)


class WordleGrid():
    """TODO: Describe."""

    def __init__(self, words: List[str]):
        if len(words) > 7:
            raise ValueError('Too many words (%d)' % (len(words),))
        answer = words[-1]
        guesses = words[:6]
        guess_colors = [word_to_colors(guess, answer) for guess in guesses]
        while len(guess_colors) < 6:
            guess_colors.append(ALL_WHITE)
        self.guesses = tuple(guess_colors)


def grids_from_lines(lines: Iterator[str]) -> List[WordleGrid]:
    current_words = []
    grids = []
    for line in lines:
        # Allow for comments (e.g., for date-stamping)
        if line.startswith('--'):
            continue
        if line == '\n' and current_words:
            grids.append(WordleGrid(current_words))
            current_words = []
        else:
            current_words.append(line.strip().upper())
    grids.append(WordleGrid(current_words))
    return grids


class AggregateGrid():
    """TODO: Describe."""

    def __init__(self, grids: List[WordleGrid]):
        # Accumulate RGB totals per grid-point.
        self._acc = [[[0, 0, 0] for ch in range(5)] for word in range(6)]
        for grid in grids:
            for gid, guess_chars in enumerate(grid.guesses):
                for cid, char_color in enumerate(guess_chars):
                    r, g, b = char_color.to_rgb()
                    self._acc[gid][cid][0] += r
                    self._acc[gid][cid][1] += g
                    self._acc[gid][cid][2] += b
        # Normalize by grid count to get the mean RGB value per grid-point.
        for row in range(6):
            for col in range(5):
                for channel in range(3):
                    self._acc[row][col][channel] = int(round(
                        self._acc[row][col][channel] / len(grids)))

    def save_png(self, filename: str) -> None:
        # Initialize an all-white image.
        img = Image.new('RGB', size=(IMG_WIDTH_PX, IMG_HEIGHT_PX),
                        color=(255, 255, 255))
        drw = ImageDraw.Draw(img)
        for row in range(6):
            for col in range(5):
                rgb = tuple(self._acc[row][col])
                rect_coords = char_rect(row, col)
                drw.rectangle(rect_coords, fill=rgb, outline=rgb)
        img.save(filename, 'PNG')


def main():
    infilename = sys.argv[1]
    outfilename = sys.argv[2]
    with open(infilename, 'rt') as infile:
        grids = grids_from_lines(infile.readlines())
    agg = AggregateGrid(grids)
    agg.save_png(outfilename)


if __name__ == '__main__':
    main()
