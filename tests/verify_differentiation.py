"""Verification script for end-to-end personalization differentiation."""
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from src.data_loader import load_raw_destinations
from src.preprocessing import preprocess_destinations
from src.recommendation import calculate_content_recommendations


df = preprocess_destinations(load_raw_destinations())

# Test 1: Heritage & History lover
p1 = {
    'name': 'Rohan',
    'persona_type': 'Cultural Enthusiast',
    'categories': ['Heritage'],
    'budget_tier': 'Budget',
    'preferred_activities': 'palaces, forts, monuments',
}
r1 = calculate_content_recommendations(df, profile=p1, top_n=3)
print('Test 1 - Heritage profile top 3:')
for i, row in r1.iterrows():
    print(f"  {i+1}. {row['destination']} ({row['category']}) - Cosine: {row['similarity_score']}")

# Test 2: Beach & Water sports lover
p2 = {
    'name': 'Sara',
    'persona_type': 'Solo Backpacker',
    'categories': ['Beach'],
    'budget_tier': 'Moderate',
    'preferred_activities': 'scuba, sunny shores, coastline',
}
r2 = calculate_content_recommendations(df, profile=p2, top_n=3)
print('\nTest 2 - Beach profile top 3:')
for i, row in r2.iterrows():
    print(f"  {i+1}. {row['destination']} ({row['category']}) - Cosine: {row['similarity_score']}")

# Test 3: Nature & Tea estates
p3 = {
    'name': 'Anita',
    'persona_type': 'Family with Kids',
    'categories': ['Nature'],
    'budget_tier': 'Moderate',
    'preferred_activities': 'tea tasting, waterfalls, misty hills',
}
r3 = calculate_content_recommendations(df, profile=p3, top_n=3)
print('\nTest 3 - Nature & Tea profile top 3:')
for i, row in r3.iterrows():
    print(f"  {i+1}. {row['destination']} ({row['category']}) - Cosine: {row['similarity_score']}")

# Assert that different preferences yielded distinct top-1 destinations
assert r1.iloc[0]['destination'] != r2.iloc[0]['destination'], 'Heritage and Beach should recommend different destinations'
assert r2.iloc[0]['destination'] != r3.iloc[0]['destination'], 'Beach and Nature should recommend different destinations'
print('\n[SUCCESS] End-to-end personalization differentiation verified!')
