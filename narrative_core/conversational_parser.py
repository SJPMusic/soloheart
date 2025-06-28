"""
Conversational Parser for Natural Language Style Switching
Handles natural language input to detect and process narration style changes
"""

import re
from typing import Dict, List, Optional, Tuple, Any
from .rules import DMNarrationStyle

class ConversationalParser:
    """Parses natural language input to detect style change requests and other conversational commands"""
    
    def __init__(self, dm_style: DMNarrationStyle):
        self.dm_style = dm_style
        self.style_patterns = self._build_style_patterns()
        self.feedback_patterns = self._build_feedback_patterns()
        self.discovery_patterns = self._build_discovery_patterns()
    
    def _build_style_patterns(self) -> Dict[str, List[Tuple[str, str]]]:
        """Build regex patterns for detecting style change requests"""
        return {
            "epic": [
                (r"\b(?:more\s+)?epic\b", "epic"),
                (r"\b(?:more\s+)?heroic\b", "epic"),
                (r"\b(?:more\s+)?grand\b", "epic"),
                (r"\b(?:more\s+)?legendary\b", "epic"),
                (r"\b(?:more\s+)?dramatic\b", "epic"),
                (r"\b(?:more\s+)?cinematic\b", "epic"),
                (r"\b(?:more\s+)?thunderous\b", "epic"),
                (r"\b(?:more\s+)?mighty\b", "epic"),
            ],
            "gritty": [
                (r"\b(?:more\s+)?gritty\b", "gritty"),
                (r"\b(?:more\s+)?dark\b", "gritty"),
                (r"\b(?:more\s+)?harsh\b", "gritty"),
                (r"\b(?:more\s+)?realistic\b", "gritty"),
                (r"\b(?:more\s+)?brutal\b", "gritty"),
                (r"\b(?:more\s+)?grim\b", "gritty"),
                (r"\b(?:more\s+)?bleak\b", "gritty"),
                (r"\b(?:more\s+)?visceral\b", "gritty"),
            ],
            "comedic": [
                (r"\b(?:more\s+)?funny\b", "comedic"),
                (r"\b(?:more\s+)?humorous\b", "comedic"),
                (r"\b(?:more\s+)?comedy\b", "comedic"),
                (r"\b(?:more\s+)?lighthearted\b", "comedic"),
                (r"\b(?:more\s+)?playful\b", "comedic"),
                (r"\b(?:more\s+)?witty\b", "comedic"),
                (r"\b(?:more\s+)?sarcastic\b", "comedic"),
                (r"\b(?:more\s+)?ironic\b", "comedic"),
            ],
            "poetic": [
                (r"\b(?:more\s+)?poetic\b", "poetic"),
                (r"\b(?:more\s+)?lyrical\b", "poetic"),
                (r"\b(?:more\s+)?beautiful\b", "poetic"),
                (r"\b(?:more\s+)?flowing\b", "poetic"),
                (r"\b(?:more\s+)?rhythmic\b", "poetic"),
                (r"\b(?:more\s+)?graceful\b", "poetic"),
                (r"\b(?:more\s+)?ethereal\b", "poetic"),
                (r"\b(?:more\s+)?enchanting\b", "poetic"),
            ],
            "eerie": [
                (r"\b(?:more\s+)?eerie\b", "eerie"),
                (r"\b(?:more\s+)?mysterious\b", "eerie"),
                (r"\b(?:more\s+)?unsettling\b", "eerie"),
                (r"\b(?:more\s+)?spooky\b", "eerie"),
                (r"\b(?:more\s+)?haunting\b", "eerie"),
                (r"\b(?:more\s+)?ominous\b", "eerie"),
                (r"\b(?:more\s+)?foreboding\b", "eerie"),
                (r"\b(?:more\s+)?shadowy\b", "eerie"),
            ],
            "mystical": [
                (r"\b(?:more\s+)?mystical\b", "mystical"),
                (r"\b(?:more\s+)?magical\b", "mystical"),
                (r"\b(?:more\s+)?otherworldly\b", "mystical"),
                (r"\b(?:more\s+)?ancient\b", "mystical"),
                (r"\b(?:more\s+)?supernatural\b", "mystical"),
                (r"\b(?:more\s+)?divine\b", "mystical"),
                (r"\b(?:more\s+)?transcendent\b", "mystical"),
                (r"\b(?:more\s+)?enchanting\b", "mystical"),
            ],
            "neutral": [
                (r"\b(?:more\s+)?neutral\b", "neutral"),
                (r"\b(?:more\s+)?balanced\b", "neutral"),
                (r"\b(?:more\s+)?straightforward\b", "neutral"),
                (r"\b(?:more\s+)?clear\b", "neutral"),
                (r"\b(?:more\s+)?simple\b", "neutral"),
                (r"\b(?:more\s+)?normal\b", "neutral"),
                (r"\b(?:more\s+)?default\b", "neutral"),
            ]
        }
    
    def _build_feedback_patterns(self) -> Dict[str, str]:
        """Build patterns for inferring style from feedback"""
        return {
            # Negative feedback patterns
            r"\b(?:too\s+)?boring\b": "epic",
            r"\b(?:too\s+)?dull\b": "epic",
            r"\b(?:too\s+)?flat\b": "epic",
            r"\b(?:too\s+)?serious\b": "comedic",
            r"\b(?:too\s+)?heavy\b": "comedic",
            r"\b(?:too\s+)?dark\b": "comedic",
            r"\b(?:too\s+)?light\b": "gritty",
            r"\b(?:too\s+)?silly\b": "gritty",
            r"\b(?:too\s+)?simple\b": "poetic",
            r"\b(?:too\s+)?plain\b": "poetic",
            r"\b(?:too\s+)?ordinary\b": "mystical",
            r"\b(?:too\s+)?mundane\b": "mystical",
            
            # Positive direction patterns
            r"\b(?:more\s+)?exciting\b": "epic",
            r"\b(?:more\s+)?intense\b": "epic",
            r"\b(?:more\s+)?fun\b": "comedic",
            r"\b(?:more\s+)?entertaining\b": "comedic",
            r"\b(?:more\s+)?atmospheric\b": "eerie",
            r"\b(?:more\s+)?mysterious\b": "eerie",
            r"\b(?:more\s+)?beautiful\b": "poetic",
            r"\b(?:more\s+)?elegant\b": "poetic",
            r"\b(?:more\s+)?magical\b": "mystical",
            r"\b(?:more\s+)?wondrous\b": "mystical",
        }
    
    def _build_discovery_patterns(self) -> List[str]:
        """Build patterns for detecting style discovery requests"""
        return [
            r"\b(?:what\s+)?(?:narration\s+)?styles?\b",
            r"\b(?:how\s+)?(?:can\s+)?(?:you\s+)?(?:narrate|tell|speak)\b",
            r"\b(?:what\s+)?(?:voices?\s+)?(?:can\s+)?(?:you\s+)?(?:use)\b",
            r"\b(?:show\s+)?(?:me\s+)?(?:the\s+)?(?:styles?|options?)\b",
            r"\b(?:list\s+)?(?:narration\s+)?(?:styles?|options?)\b",
            r"\b(?:available\s+)?(?:styles?|options?)\b",
        ]
    
    def parse_input(self, user_input: str) -> Dict[str, Any]:
        """Parse user input to detect style changes, feedback, and discovery requests"""
        input_lower = user_input.lower().strip()
        
        # Check for style discovery requests
        if self._is_style_discovery_request(input_lower):
            return {
                "type": "style_discovery",
                "message": "The player wants to know about available narration styles"
            }
        
        # Check for explicit style change requests
        style_change = self._detect_style_change(input_lower)
        if style_change:
            return {
                "type": "style_change",
                "style": style_change,
                "message": f"Player requested style change to {style_change}"
            }
        
        # Check for feedback-based style inference
        inferred_style = self._infer_style_from_feedback(input_lower)
        if inferred_style:
            return {
                "type": "style_inference",
                "style": inferred_style,
                "message": f"Inferred style change to {inferred_style} from feedback"
            }
        
        # No style-related content detected
        return {
            "type": "normal_input",
            "message": "Regular game input"
        }
    
    def _is_style_discovery_request(self, input_lower: str) -> bool:
        """Check if input is asking about available styles"""
        for pattern in self.discovery_patterns:
            if re.search(pattern, input_lower):
                return True
        return False
    
    def _detect_style_change(self, input_lower: str) -> Optional[str]:
        """Detect explicit style change requests"""
        for style_name, patterns in self.style_patterns.items():
            for pattern, style in patterns:
                if re.search(pattern, input_lower):
                    return style
        return None
    
    def _infer_style_from_feedback(self, input_lower: str) -> Optional[str]:
        """Infer style from feedback patterns"""
        for pattern, style in self.feedback_patterns.items():
            if re.search(pattern, input_lower):
                return style
        return None
    
    def generate_style_discovery_response(self) -> str:
        """Generate a friendly, in-character response about available styles"""
        all_styles = self.dm_style.get_all_styles()
        current_style = self.dm_style.get_current_style()
        
        # Create a conversational list of styles
        style_descriptions = []
        for style_key, style_info in all_styles.items():
            if style_key == current_style:
                style_descriptions.append(f"**{style_info['name']}** (current)")
            else:
                style_descriptions.append(style_info['name'])
        
        styles_text = ", ".join(style_descriptions[:-1]) + f", and {style_descriptions[-1]}"
        
        responses = [
            f"I can weave your tale in many voices: {styles_text}. Just ask, and I'll shift the wind of words.",
            f"My storytelling can take many forms: {styles_text}. Simply tell me how you'd like to hear your story.",
            f"I have many ways to tell your tale: {styles_text}. Just let me know what mood you're seeking.",
            f"Your story can be told in various tones: {styles_text}. What kind of voice would you like me to use?",
            f"I can narrate in different styles: {styles_text}. How would you like to experience your adventure?"
        ]
        
        import random
        return random.choice(responses)
    
    def generate_style_change_confirmation(self, new_style: str, old_style: str) -> str:
        """Generate a confirmation message in the new style"""
        style_info = self.dm_style.get_style_info(new_style)
        
        confirmations = {
            "epic": [
                f"**The very air crackles with power as I shift to {style_info['name']} narration!** Your tale shall now be told with thunderous might and legendary grandeur.",
                f"**With the weight of destiny upon my words, I embrace the {style_info['name']} style!** From this moment forth, your story shall echo through the annals of legend.",
                f"**The forces of epic storytelling align as I adopt the {style_info['name']} voice!** Your adventures will now be narrated with heroic splendor."
            ],
            "gritty": [
                f"**The harsh reality of storytelling takes hold as I switch to {style_info['name']} narration.** Your tale will now be told with visceral truth and brutal honesty.",
                f"**Blood and sweat mingle in my words as I embrace the {style_info['name']} style.** Your story shall now reflect the grim realities of adventure.",
                f"**The cold bite of truth sharpens my tongue as I adopt {style_info['name']} narration.** Your tale will now be told with unflinching realism."
            ],
            "comedic": [
                f"**The laws of serious storytelling take a coffee break as I switch to {style_info['name']} narration!** 😄 Your tale will now be told with wit and whimsy.",
                f"**In what can only be described as a 'bold storytelling move', I embrace the {style_info['name']} style!** 😄 Your adventures will now be narrated with humor and charm.",
                f"**Chaos theory gets a new data point as I adopt {style_info['name']} narration!** 😄 Your story will now be told with playful delight."
            ],
            "poetic": [
                f"**Like a leaf caught in autumn's embrace, I shift to {style_info['name']} narration.** 🌙 Your tale will now flow with lyrical beauty and rhythmic grace.",
                f"**The moonlight dances upon my words as I embrace the {style_info['name']} style.** 🌙 Your story shall now be woven with poetic elegance.",
                f"**Time flows like a river as I adopt {style_info['name']} narration.** 🌙 Your adventures will now be told with flowing beauty."
            ],
            "eerie": [
                f"**Shadows seem to whisper as I switch to {style_info['name']} narration.** Your tale will now be told with unsettling mystery and dark atmosphere.",
                f"**An unnatural silence falls as I embrace the {style_info['name']} style.** Your story shall now be narrated with eerie foreboding.",
                f"**The darkness itself seems to watch as I adopt {style_info['name']} narration.** Your adventures will now be told with haunting mystery."
            ],
            "mystical": [
                f"**The weave of magic responds to my will as I shift to {style_info['name']} narration.** ✨ Your tale will now be told with otherworldly wonder.",
                f"**Reality itself seems to bend around my words as I embrace the {style_info['name']} style.** ✨ Your story shall now be narrated with mystical enchantment.",
                f"**Ancient forces stir in response as I adopt {style_info['name']} narration.** ✨ Your adventures will now be told with divine wonder."
            ],
            "neutral": [
                f"**With practiced skill, I switch to {style_info['name']} narration.** Your tale will now be told with clear, balanced storytelling.",
                f"**The situation requires a {style_info['name']} approach to narration.** Your story shall now be narrated with straightforward clarity.",
                f"**Your training guides me as I adopt {style_info['name']} narration.** Your adventures will now be told with professional precision."
            ]
        }
        
        import random
        return random.choice(confirmations.get(new_style, confirmations["neutral"]))
