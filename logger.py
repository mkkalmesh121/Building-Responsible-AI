import datetime

def log_interaction(user, response, quality, time_taken):
    with open("logs.txt", "a",encoding="utf-8") as f:
        f.write(f"\n[{datetime.datetime.now()}]\n")
        f.write(f"User : {user}\n")
        f.write(f"AI : {response}\n")
        f.write(f"Quality : {quality}\n")
        f.write(f"Time: {time_taken:.2f}s\n")
        f.write("-" * 40)
       