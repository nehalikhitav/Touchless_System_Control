import mediapipe as mp
try:
    print("Imported mediapipe")
    print(dir(mp.solutions))
    hands = mp.solutions.hands
    print("Found hands")
except Exception as e:
    print(f"Error: {e}")
