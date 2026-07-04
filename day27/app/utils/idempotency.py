_seen_requests = set()  #private set to track seen request IDs

def is_duplicate(request_id: str) -> bool:
    if request_id in _seen_requests:
        return True
    
    _seen_requests.add(request_id)
    return False