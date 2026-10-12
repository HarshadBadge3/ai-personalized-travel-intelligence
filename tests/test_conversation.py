"""Unit tests for conversation manager and recommendation integration."""
import sys
from pathlib import Path
import pandas as pd

PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from src.data_loader import load_raw_destinations
from src.preprocessing import preprocess_destinations
from src.conversation_manager import init_conversation_state, process_user_turn


def test_conversation_initialization():
    """Verify clean initialization of conversation state with and without profile."""
    # Without profile
    state1 = init_conversation_state(None)
    assert len(state1["messages"]) == 1
    assert state1["messages"][0]["role"] == "assistant"
    assert state1["preferences"]["budget"] is None

    # With traveler profile
    mock_profile = {
        "name": "Diya",
        "persona_type": "Solo Backpacker",
        "categories": ["Heritage", "Nature"],
        "budget_tier": "Budget (Under ₹5,000/trip)",
    }
    state2 = init_conversation_state(mock_profile)
    assert len(state2["messages"]) == 1
    assert "Diya" in state2["messages"][0]["message"]
    assert state2["preferences"]["categories"] == ["Heritage", "Nature"]
    assert state2["preferences"]["budget"] == 5000
    print("[PASS] test_conversation_initialization passed.")


def test_follow_up_flow_and_recommendation_trigger():
    """Verify conversation progression through clarification until recommendations trigger."""
    df = preprocess_destinations(load_raw_destinations())
    state = init_conversation_state(None)

    # Turn 1: Incomplete input ("I want to plan a trip")
    state = process_user_turn("I want to plan a trip", state, df)
    last_bot_msg = state["messages"][-1]
    assert last_bot_msg["role"] == "assistant"
    assert last_bot_msg["recommendations"] is None
    assert "experience are you looking for" in last_bot_msg["message"].lower()

    # Turn 2: Provide category ("A beach trip")
    state = process_user_turn("A beach trip", state, df)
    last_bot_msg2 = state["messages"][-1]
    assert last_bot_msg2["role"] == "assistant"
    assert "Beach" in state["preferences"]["categories"]
    assert last_bot_msg2["recommendations"] is None
    assert "approximate budget" in last_bot_msg2["message"].lower()


    # Turn 3: Provide budget & duration ("Under 15k for 3 days") -> Triggers recommendations!
    state = process_user_turn("Under 15k for 3 days", state, df)
    last_bot_msg3 = state["messages"][-1]
    assert last_bot_msg3["role"] == "assistant"
    assert last_bot_msg3["recommendations"] is not None
    assert isinstance(last_bot_msg3["recommendations"], pd.DataFrame)
    assert not last_bot_msg3["recommendations"].empty
    assert len(last_bot_msg3["recommendations"]) <= 3

    # Recommendations must come from real dataset and rank beach spots high
    top_dest = last_bot_msg3["recommendations"].iloc[0]["destination"]
    assert top_dest in ["Goa", "Andaman Islands", "Pondicherry"]

    print("[PASS] test_follow_up_flow_and_recommendation_trigger passed.")


def test_conversation_edge_cases():
    """Verify handling of empty messages and reset."""
    df = preprocess_destinations(load_raw_destinations())
    state = init_conversation_state(None)

    # Empty turn does not crash
    state = process_user_turn("", state, df)
    assert len(state["messages"]) == 1

    # Unrelated input triggers polite guidance
    state = process_user_turn("hello who is the president?", state, df)
    assert "specialized in travel planning" in state["messages"][-1]["message"].lower()

    # Reset
    reset_state = init_conversation_state(None)
    assert len(reset_state["messages"]) == 1
    assert reset_state["preferences"]["budget"] is None

    print("[PASS] test_conversation_edge_cases passed.")


if __name__ == "__main__":
    print("==================================================")
    print("RUNNING CONVERSATION MANAGER TESTS")
    print("==================================================")
    test_conversation_initialization()
    test_follow_up_flow_and_recommendation_trigger()
    test_conversation_edge_cases()
    print("==================================================")
    print("SUCCESS: ALL CONVERSATION TESTS PASSED!")
    print("==================================================")
