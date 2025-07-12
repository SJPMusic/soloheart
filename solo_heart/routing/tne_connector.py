import requests

# TNE API endpoint (update as needed)
TNE_API_URL = "http://localhost:8000/api/symbolic"


def get_symbolic_analysis(text, context=None):
    """
    Call TNE API for symbolic analysis (archetype detection, chaos/order, etc.)
    Args:
        text (str): User or narrative input
        context (dict): Optional context for analysis
    Returns:
        dict: Symbolic analysis results from TNE
    """
    payload = {"text": text}
    if context:
        payload["context"] = context
    try:
        response = requests.post(f"{TNE_API_URL}/analyze", json=payload, timeout=10)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        # Fallback: return empty symbolic result
        return {"archetypal_tags": [], "chaos_order_tension": 0.5, "narrative_decay": 0.0, "symbolic_coherence": 1.0, "error": str(e)}


def get_symbolic_summary(character_id):
    """
    Call TNE API for a summary of symbolic state for a character.
    Args:
        character_id (str): Unique character identifier
    Returns:
        dict: Symbolic summary from TNE
    """
    try:
        response = requests.get(f"{TNE_API_URL}/summary/{character_id}", timeout=10)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        return {"archetypal_tags": [], "chaos_order_tension": 0.5, "narrative_decay": 0.0, "symbolic_coherence": 1.0, "error": str(e)}

# Add more TNE symbolic API calls as needed for the demo layer
