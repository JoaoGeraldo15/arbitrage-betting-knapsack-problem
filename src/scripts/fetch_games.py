from src.service import EventService, GameService

if __name__ == '__main__':
    event_service = EventService()
    events = event_service.get_events_utc_date()

    if len(events):
        game_service = GameService()
        leagues = {event.sport_key for event in events}
        game_service.fetch_games(list(leagues))
