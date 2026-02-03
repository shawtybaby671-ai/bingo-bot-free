#!/usr/bin/env python3
"""Test script for inline menu and player management."""

import sqlite3
import os
import sys

# Set environment variables for testing
os.environ['BOT_TOKEN'] = 'test_token'
os.environ['ADMIN_ID'] = '123456'

# Import bot functions
from bot import (
    get_or_create_player,
    update_player_points,
    create_scheduled_game,
    register_for_game,
    get_registration,
    approve_registration,
    get_scheduled_games
)

def test_player_management():
    """Test player profile creation and management."""
    print("Testing Player Management...")
    
    # Create a player
    player = get_or_create_player(12345, "TestUser")
    assert player[0] == 12345, "User ID should match"
    assert player[1] == "TestUser", "Username should match"
    assert player[2] == 100, "Starting points should be 100"
    assert player[3] == 0, "Starting cards should be 0"
    
    # Get existing player
    player2 = get_or_create_player(12345, "TestUser")
    assert player2[0] == 12345, "Should retrieve same player"
    
    # Update points
    update_player_points(12345, 50)
    player3 = get_or_create_player(12345, "TestUser")
    assert player3[2] == 150, "Points should be updated to 150"
    
    # Deduct points
    update_player_points(12345, -30)
    player4 = get_or_create_player(12345, "TestUser")
    assert player4[2] == 120, "Points should be 120 after deduction"
    
    print("✓ Player management works!")

def test_game_scheduling():
    """Test game scheduling."""
    print("\nTesting Game Scheduling...")
    
    # Create a scheduled game
    game_id = create_scheduled_game(
        game_date="2026-02-15",
        game_time="18:00",
        game_type="classic",
        pattern="single_line",
        max_players=50,
        entry_cost=10
    )
    
    assert game_id > 0, "Game ID should be positive"
    
    # Get scheduled games
    games = get_scheduled_games()
    assert len(games) > 0, "Should have at least one game"
    
    found = False
    for game in games:
        if game[0] == game_id:
            found = True
            assert game[3] == "classic", "Game type should match"
            assert game[4] == "single_line", "Pattern should match"
            assert game[6] == 10, "Entry cost should match"
    
    assert found, "Should find the created game"
    
    print("✓ Game scheduling works!")

def test_registration_workflow():
    """Test game registration and approval workflow."""
    print("\nTesting Registration Workflow...")
    
    # Create a player with sufficient points
    player = get_or_create_player(99999, "RegTestUser")
    update_player_points(99999, 50)  # Give extra points
    
    # Create a game
    game_id = create_scheduled_game(
        game_date="2026-02-20",
        game_time="20:00",
        game_type="dual_action",
        pattern="blackout",
        entry_cost=15
    )
    
    # Register for game
    reg_id = register_for_game(game_id, 99999, "RegTestUser", 3)
    assert reg_id > 0, "Registration ID should be positive"
    
    # Get registration
    registration = get_registration(reg_id)
    assert registration is not None, "Should retrieve registration"
    assert registration[3] == "RegTestUser", "Username should match"
    assert registration[4] == 3, "Cards requested should be 3"
    assert registration[5] == 45, "Points paid should be 45 (15*3)"
    assert registration[7] == "pending", "Status should be pending"
    
    # Check player points before approval (should not be deducted yet)
    player_before = get_or_create_player(99999, "RegTestUser")
    points_before = player_before[2]
    
    # Approve registration
    success = approve_registration(reg_id)
    assert success, "Approval should succeed"
    
    # Check registration status after approval
    registration_after = get_registration(reg_id)
    assert registration_after[7] == "approved", "Should be approved"
    assert registration_after[6] == "confirmed", "Status should be confirmed"
    
    # Check player points after approval (should be deducted)
    player_after = get_or_create_player(99999, "RegTestUser")
    points_after = player_after[2]
    assert points_after == points_before - 45, "Points should be deducted after approval"
    
    print("✓ Registration workflow works!")

def cleanup_test_data():
    """Clean up test data from database."""
    print("\nCleaning up test data...")
    conn = sqlite3.connect('game.db')
    c = conn.cursor()
    
    # Delete test players
    c.execute("DELETE FROM player_profiles WHERE user_id IN (12345, 99999)")
    
    # Delete test registrations
    c.execute("DELETE FROM game_registrations WHERE username IN ('TestUser', 'RegTestUser')")
    
    # Delete test games (keep real ones)
    c.execute("DELETE FROM scheduled_games WHERE game_date >= '2026-02-15'")
    
    conn.commit()
    conn.close()
    print("✓ Cleanup complete!")

if __name__ == "__main__":
    print("=" * 60)
    print("INLINE MENU & PLAYER MANAGEMENT TEST SUITE")
    print("=" * 60)
    
    try:
        test_player_management()
        test_game_scheduling()
        test_registration_workflow()
        cleanup_test_data()
        
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
