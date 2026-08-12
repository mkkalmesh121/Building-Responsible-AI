def evaluate_response(response):
    if not response or len(response) < 10  :
        return "Poor"
    elif "error" in response.lower():
        return "Review"
    else:
        return "Good"
