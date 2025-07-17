import httpx

TNE_API_URL = "http://localhost:5001"

async def send_event_to_tne(event: dict) -> dict:
    """
    Sends a character action event from SoloHeart to the TNE memory engine.

    Args:
        event (dict): Structured event containing character ID, action type,
                      timestamp, emotion tags, and narrative context.

    Returns:
        dict: Response from TNE containing success status and event details.

    Raises:
        httpx.HTTPStatusError: If the request fails or TNE returns an error.
    """
    async with httpx.AsyncClient() as client:
        response = await client.post(f"{TNE_API_URL}/memory/inject", json=event)
        response.raise_for_status()
        return response.json()

async def fetch_goal_alignment(character_id: str) -> dict:
    """
    Retrieves current goal alignment status for a character from TNE.

    Args:
        character_id (str): Unique ID of the SoloHeart character.

    Returns:
        dict: Symbolic insight including alignment/conflict with character's goals.

    Raises:
        httpx.HTTPStatusError: If the request fails or TNE returns an error.
    """
    async with httpx.AsyncClient() as client:
        response = await client.get(f"{TNE_API_URL}/symbolic/goal_alignment/{character_id}")
        response.raise_for_status()
        return response.json() 