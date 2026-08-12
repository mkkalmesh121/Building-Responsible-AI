BLOCKED_WORDS = ["hack", "attack", "illegal", "steal"]

def is_safe(user_input):
    return not any(word in user_input.lower() for word in BLOCKED_WORDS)