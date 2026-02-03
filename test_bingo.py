#!/usr/bin/env python3
"""Test script for bingo logic."""

import sys
import random

# Mock the bot-related dependencies
class MockBot:
    def __init__(self):
        pass

# Import after mocking
sys.path.insert(0, '.')

# Set mock values before importing bot
import os
os.environ['BOT_TOKEN'] = 'test_token'
os.environ['ADMIN_ID'] = '1'

# Now we can import and test the core logic
from bot import (
    generate_classic_card, 
    generate_dual_action_card,
    is_cell_marked,
    check_pattern,
    get_marked_cells,
    format_card,
    get_bingo_letter,
    PATTERNS,
    COLUMN_RANGES
)

def test_card_generation():
    """Test card generation."""
    print("Testing Classic Card Generation...")
    classic_card = generate_classic_card()
    
    # Check dimensions
    assert len(classic_card) == 5, "Card should have 5 rows"
    assert all(len(row) == 5 for row in classic_card), "Each row should have 5 cells"
    
    # Check free space
    assert classic_card[2][2] is None, "Center should be free space"
    
    # Check column ranges
    for col in range(5):
        min_num, max_num = COLUMN_RANGES[col]
        for row in range(5):
            if classic_card[row][col] is not None:
                assert min_num <= classic_card[row][col] <= max_num, \
                    f"Number {classic_card[row][col]} at ({row},{col}) not in range {min_num}-{max_num}"
    
    print("✓ Classic card generation works!")
    
    print("\nTesting Dual Action Card Generation...")
    dual_card = generate_dual_action_card()
    
    # Check dimensions
    assert len(dual_card) == 5, "Card should have 5 rows"
    assert all(len(row) == 5 for row in dual_card), "Each row should have 5 cells"
    
    # Check free space
    assert dual_card[2][2] is None, "Center should be free space"
    
    # Check column ranges and tuple structure
    for col in range(5):
        min_num, max_num = COLUMN_RANGES[col]
        for row in range(5):
            cell = dual_card[row][col]
            if cell is not None:
                assert isinstance(cell, tuple), f"Cell at ({row},{col}) should be tuple"
                assert len(cell) == 2, f"Cell at ({row},{col}) should have 2 numbers"
                assert min_num <= cell[0] <= max_num, f"First number {cell[0]} not in range"
                assert min_num <= cell[1] <= max_num, f"Second number {cell[1]} not in range"
    
    print("✓ Dual action card generation works!")

def test_marking():
    """Test cell marking logic."""
    print("\nTesting Cell Marking...")
    
    # Classic marking
    assert is_cell_marked(5, [1, 2, 3, 4, 5], "classic"), "Classic: Should mark when number is called"
    assert not is_cell_marked(5, [1, 2, 3, 4], "classic"), "Classic: Should not mark when number not called"
    assert is_cell_marked(None, [], "classic"), "Free space should always be marked"
    
    # Dual action marking
    assert is_cell_marked((5, 10), [5], "dual_action"), "Dual: Should mark if first number called"
    assert is_cell_marked((5, 10), [10], "dual_action"), "Dual: Should mark if second number called"
    assert is_cell_marked((5, 10), [5, 10], "dual_action"), "Dual: Should mark if both called"
    assert not is_cell_marked((5, 10), [1, 2], "dual_action"), "Dual: Should not mark if neither called"
    
    print("✓ Cell marking works correctly!")

def test_patterns():
    """Test pattern checking."""
    print("\nTesting Pattern Checking...")
    
    # Create a simple card
    card = [[1, 16, 31, 46, 61],
            [2, 17, 32, 47, 62],
            [3, 18, None, 48, 63],  # Center is free
            [4, 19, 34, 49, 64],
            [5, 20, 35, 50, 65]]
    
    # Test horizontal line (top row)
    called = [1, 16, 31, 46, 61]
    marked = get_marked_cells(card, called, "classic")
    assert check_pattern(card, marked, PATTERNS["single_line"]), "Should detect horizontal line"
    
    # Test vertical line (first column)
    called = [1, 2, 3, 4, 5]
    marked = get_marked_cells(card, called, "classic")
    assert check_pattern(card, marked, PATTERNS["single_line"]), "Should detect vertical line"
    
    # Test diagonal (with free space)
    called = [1, 17, 49, 65]  # Free space is auto-marked
    marked = get_marked_cells(card, called, "classic")
    assert check_pattern(card, marked, PATTERNS["single_line"]), "Should detect diagonal"
    
    # Test four corners
    called = [1, 61, 5, 65]
    marked = get_marked_cells(card, called, "classic")
    assert check_pattern(card, marked, PATTERNS["four_corners"]), "Should detect four corners"
    
    print("✓ Pattern checking works correctly!")

def test_bingo_letters():
    """Test BINGO letter assignment."""
    print("\nTesting BINGO Letters...")
    
    assert get_bingo_letter(1) == 'B', "1 should be B"
    assert get_bingo_letter(15) == 'B', "15 should be B"
    assert get_bingo_letter(16) == 'I', "16 should be I"
    assert get_bingo_letter(30) == 'I', "30 should be I"
    assert get_bingo_letter(31) == 'N', "31 should be N"
    assert get_bingo_letter(45) == 'N', "45 should be N"
    assert get_bingo_letter(46) == 'G', "46 should be G"
    assert get_bingo_letter(60) == 'G', "60 should be G"
    assert get_bingo_letter(61) == 'O', "61 should be O"
    assert get_bingo_letter(75) == 'O', "75 should be O"
    
    print("✓ BINGO letter assignment works!")

def test_card_formatting():
    """Test card formatting."""
    print("\nTesting Card Formatting...")
    
    card = [[1, 16, 31, 46, 61],
            [2, 17, 32, 47, 62],
            [3, 18, None, 48, 63],
            [4, 19, 34, 49, 64],
            [5, 20, 35, 50, 65]]
    
    marked = {(0, 0), (1, 1), (2, 2)}  # Mark a few cells
    text = format_card(card, "classic", marked)
    
    assert "B    I    N    G    O" in text, "Should have BINGO header"
    assert "FREE" in text, "Should show FREE for center"
    assert "[" in text, "Should have brackets for marked cells"
    
    print("✓ Card formatting works!")

if __name__ == "__main__":
    print("=" * 60)
    print("BINGO LOGIC TEST SUITE")
    print("=" * 60)
    
    try:
        test_card_generation()
        test_marking()
        test_patterns()
        test_bingo_letters()
        test_card_formatting()
        
        print("\n" + "=" * 60)
        print("✓ ALL TESTS PASSED!")
        print("=" * 60)
        sys.exit(0)
    except AssertionError as e:
        print(f"\n✗ TEST FAILED: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"\n✗ ERROR: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
