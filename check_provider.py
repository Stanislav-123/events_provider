
import asyncio

from app.clients.events_provider import EventsProviderClient


async def main() -> None:
    client = EventsProviderClient()

    data = await client.get_events(
        changed_at="2000-01-01",
    )

    events = data.get("results", [])

    print("Events received:", len(events))
    print("Next page exists:", data.get("next") is not None)

    if events:
        event = events[0]

        print("Event fields:", list(event.keys()))
        print("Event ID:", event["id"])
        print("Event name:", event["name"])
        print("Place name:", event["place"]["name"])
        print("Changed at:", event["changed_at"])


if __name__ == "__main__":
    asyncio.run(main())
