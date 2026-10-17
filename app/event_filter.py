
def filter_events_by_location(events, location):
    term = location.casefold()

    return [
        event
        for event in events
        if term in event["location"].casefold()
    ]


def filter_events_by_title(events, title):
    term = title.casefold()

    return [
        event
        for event in events
        if term in event["title"].casefold()
    ]
