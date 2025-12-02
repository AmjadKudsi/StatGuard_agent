import pickle

def load_data():
    # Untrusted pickle load can lead to code execution
    with open("user_uploaded.pkl", "rb") as f:
        data = pickle.load(f)
    return data
