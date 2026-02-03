#!/usr/bin/env python3
"""Test script for player data file and group logging."""

import os
import sys
import json
import shutil

# Set environment variables for testing
os.environ['BOT_TOKEN'] = 'test_token'
os.environ['ADMIN_ID'] = '123456'
# Private group logging is optional, so we won't set it for basic tests

# Import bot functions
from bot import (
    save_player_dm_data,
    get_player_dm_data,
    list_player_data_files,
    save_player_profile_snapshot,
    PLAYER_DATA_DIR
)

def test_player_dm_data_saving():
    """Test saving player DM data to files."""
    print("Testing Player DM Data Saving...")
    
    user_id = 99991
    registration_id = 501
    
    # Save a registration request
    message_data = {
        'registration_id': registration_id,
        'game_id': 10,
        'cards_requested': 3,
        'points_paid': 30,
        'game_date': '2026-03-01',
        'game_time': '18:00',
        'game_type': 'classic',
        'pattern': 'single_line',
        'status': 'pending'
    }
    
    filename = save_player_dm_data(user_id, registration_id, 'registration_request', message_data)
    assert filename is not None, "Should return filename"
    assert os.path.exists(filename), "File should exist"
    
    print(f"✓ Saved DM data to {filename}")
    
    # Save an approval
    approval_data = {
        'approved': True,
        'admin_id': 123456,
        'admin_name': 'TestAdmin'
    }
    
    filename2 = save_player_dm_data(user_id, registration_id, 'admin_approval', approval_data)
    assert filename2 == filename, "Should use same file"
    
    print("✓ Added approval to same file")

def test_player_dm_data_retrieval():
    """Test retrieving player DM data from files."""
    print("\nTesting Player DM Data Retrieval...")
    
    user_id = 99991
    registration_id = 501
    
    # Retrieve the data
    data = get_player_dm_data(user_id, registration_id)
    assert data is not None, "Should retrieve data"
    assert data['user_id'] == user_id, "User ID should match"
    assert data['registration_id'] == registration_id, "Registration ID should match"
    assert len(data['messages']) == 2, "Should have 2 messages"
    
    print(f"✓ Retrieved data with {len(data['messages'])} messages")
    
    # Verify message types
    msg_types = [msg['type'] for msg in data['messages']]
    assert 'registration_request' in msg_types, "Should have registration request"
    assert 'admin_approval' in msg_types, "Should have admin approval"
    
    print("✓ Message types verified")

def test_player_profile_snapshot():
    """Test saving player profile snapshots."""
    print("\nTesting Player Profile Snapshot...")
    
    user_id = 99992
    username = "TestPlayer2"
    
    registration_data = {
        'registration_id': 502,
        'game_id': 11,
        'cards_requested': 2,
        'points_paid': 20,
        'status': 'confirmed',
        'game_date': '2026-03-02',
        'game_time': '19:00',
        'game_type': 'dual_action',
        'pattern': 'four_corners'
    }
    
    filename = save_player_profile_snapshot(user_id, username, registration_data)
    assert filename is not None, "Should return filename"
    assert os.path.exists(filename), "File should exist"
    
    print(f"✓ Saved profile snapshot to {filename}")
    
    # Verify file contents
    with open(filename, 'r') as f:
        data = json.load(f)
    
    assert data['user_id'] == user_id, "User ID should match"
    assert data['username'] == username, "Username should match"
    assert len(data['registrations']) == 1, "Should have 1 registration"
    
    print("✓ Profile snapshot contents verified")

def test_list_player_data_files():
    """Test listing player data files."""
    print("\nTesting List Player Data Files...")
    
    # List all files
    all_files = list_player_data_files()
    assert len(all_files) > 0, "Should have at least one file"
    
    print(f"✓ Found {len(all_files)} total files")
    
    # List files for specific user
    user_files = list_player_data_files(user_id=99991)
    assert len(user_files) >= 1, "Should have at least one file for user 99991"
    
    print(f"✓ Found {len(user_files)} files for user 99991")

def test_data_structure():
    """Test the structure of saved data."""
    print("\nTesting Data Structure...")
    
    user_id = 99991
    registration_id = 501
    
    data = get_player_dm_data(user_id, registration_id)
    
    # Check required fields
    required_fields = ['user_id', 'registration_id', 'created_at', 'messages', 'last_updated']
    for field in required_fields:
        assert field in data, f"Should have '{field}' field"
    
    print("✓ All required fields present")
    
    # Check message structure
    if data['messages']:
        msg = data['messages'][0]
        required_msg_fields = ['timestamp', 'type', 'data']
        for field in required_msg_fields:
            assert field in msg, f"Message should have '{field}' field"
        
        print("✓ Message structure verified")

def cleanup_test_data():
    """Clean up test data files."""
    print("\nCleaning up test data...")
    
    # Remove test files
    test_files = [
        'player_99991_reg_501.json',
        'player_99992_reg_502.json',
        'player_99991_profile.json',
        'player_99992_profile.json'
    ]
    
    for filename in test_files:
        filepath = os.path.join(PLAYER_DATA_DIR, filename)
        if os.path.exists(filepath):
            os.remove(filepath)
            print(f"  Removed {filename}")
    
    print("✓ Cleanup complete!")

if __name__ == "__main__":
    print("=" * 60)
    print("PLAYER DATA FILE MANAGEMENT TEST SUITE")
    print("=" * 60)
    
    try:
        test_player_dm_data_saving()
        test_player_dm_data_retrieval()
        test_player_profile_snapshot()
        test_list_player_data_files()
        test_data_structure()
        cleanup_test_data()
        
        print("\n" + "=" * 60)
        print("✓ ALL TESTS PASSED!")
        print("=" * 60)
        print("\nNote: Private group logging requires PLAYER_DATA_GROUP_ID")
        print("to be set and will be tested when the bot is deployed.")
        sys.exit(0)
    except AssertionError as e:
        print(f"\n✗ TEST FAILED: {e}")
        cleanup_test_data()
        sys.exit(1)
    except Exception as e:
        print(f"\n✗ ERROR: {e}")
        import traceback
        traceback.print_exc()
        cleanup_test_data()
        sys.exit(1)
