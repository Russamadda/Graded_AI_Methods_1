from markov_model import WordState

# Sample test sentences
test_sents = [
    "i like cats",
    "i like dogs",
    "cats like milk"
]

# Create and fit the Markov model
m = WordState()
m.fit_from_sentences(test_sents)

# Display the model's internal state
print("Starts:", m.starts)
for word, nxt in m.transitions.items():
    print(f"{word} -> {dict(nxt)}")
