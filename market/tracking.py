"""Reklam piksel olaylari: view'lar olay ekler, sonraki sayfada tarayici kodu (bbTrack) tetikler."""


def bb_event(request, name, params=None, custom=False):
    try:
        events = request.session.get("bb_events", [])
        events.append([name, params or {}, bool(custom)])
        request.session["bb_events"] = events[-8:]
    except Exception:
        pass
