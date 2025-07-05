def extract_name_from_text(text: str) -> Optional[str]:
    """
    Extract character name from text using strict patterns and context.
    Avoid pronouns, verbs, and common words. Only return if high-confidence.
    """
    if not text:
        return None
    
    text_lower = text.lower()
    logger.debug(f"🔍 Extracting name from text: '{text[:100]}...'")
    
    # Enhanced name extraction patterns - prioritize full names like I do
    name_patterns = [
        # Full name patterns (highest priority)
        r"his name is ([a-z]+ [a-z]+)", r"my character is ([a-z]+ [a-z]+)", 
        r"call me ([a-z]+ [a-z]+)", r"i am ([a-z]+ [a-z]+)",
        r"([a-z]+ [a-z]+) is my name", r"([a-z]+ [a-z]+) is a",
        r"([a-z]+ [a-z]+) was a", r"([a-z]+ [a-z]+) is an",
        r"([a-z]+ [a-z]+) was an",
        
        # Single name patterns (fallback)
        r"my character is ([a-z]+)", r"my name is ([a-z]+)", r"i'm called ([a-z]+)", 
        r"call me ([a-z]+)", r"my character is named ([a-z]+)", r"name me ([a-z]+)",
        r"^i am ([a-z]+)$", r"^i'm ([a-z]+)$", r"my name's ([a-z]+)", r"i go by ([a-z]+)",
        r"my character is ([a-z]+)", r"([a-z]+) is my name", r"name is ([a-z]+)", 
        r"called ([a-z]+)", r"named ([a-z]+)", r"my character's name is ([a-z]+)", 
        r"character name is ([a-z]+)", r"i want to be ([a-z]+)", r"i want to play ([a-z]+)",
        r"([a-z]+) is a", r"([a-z]+) is an", r"([a-z]+) was a", r"([a-z]+) was an"
    ]
    
    for pattern in name_patterns:
        match = re.search(pattern, text_lower)
        if match:
            name = match.group(1).title()
            # Filter out pronouns, verbs, and common words
            if name.lower() in FILTER_WORDS["pronouns"] + FILTER_WORDS["verbs"] + FILTER_WORDS["common_words"]:
                continue
            logger.debug(f"✅ High-confidence name detected: {name}")
            return name
    
    logger.debug(f"⚠️ No high-confidence name detected in text: '{text[:100]}...'")
    return None 