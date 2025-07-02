#!/usr/bin/env python3
"""
Character Sheet Renderer for SoloHeart
Converts character JSON data into HTML for web display.
"""

import json
import logging
from typing import Dict, List, Optional
from datetime import datetime

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class CharacterSheetRenderer:
    """Renders character data as HTML for web display."""
    
    def __init__(self):
        self.css_styles = self._get_css_styles()
    
    def _get_css_styles(self) -> str:
        """Get CSS styles for character sheet."""
        return """
        <style>
        .character-sheet {
            font-family: 'Georgia', serif;
            background: linear-gradient(135deg, #1a1a2e 0%, #16213e 50%, #0f3460 100%);
            color: #e8e8e8;
            padding: 2rem;
            max-width: 1200px;
            margin: 0 auto;
        }
        
        .sheet-header {
            text-align: center;
            margin-bottom: 2rem;
            padding: 1rem;
            background: rgba(0, 0, 0, 0.3);
            border: 2px solid #ffd700;
            border-radius: 10px;
        }
        
        .character-name {
            font-size: 2.5rem;
            color: #ffd700;
            text-shadow: 0 0 20px rgba(255, 215, 0, 0.5);
            margin-bottom: 0.5rem;
        }
        
        .character-subtitle {
            font-size: 1.2rem;
            color: #ccc;
        }
        
        .sheet-grid {
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 2rem;
            margin-bottom: 2rem;
        }
        
        .sheet-section {
            background: rgba(0, 0, 0, 0.2);
            border: 1px solid #333;
            border-radius: 8px;
            padding: 1.5rem;
        }
        
        .section-title {
            color: #ffd700;
            font-size: 1.3rem;
            margin-bottom: 1rem;
            border-bottom: 1px solid #ffd700;
            padding-bottom: 0.5rem;
        }
        
        .ability-scores {
            display: grid;
            grid-template-columns: repeat(3, 1fr);
            gap: 1rem;
        }
        
        .ability-score {
            text-align: center;
            padding: 1rem;
            background: rgba(255, 215, 0, 0.1);
            border: 1px solid #ffd700;
            border-radius: 5px;
        }
        
        .ability-name {
            font-weight: bold;
            color: #ffd700;
            text-transform: uppercase;
            font-size: 0.9rem;
        }
        
        .ability-value {
            font-size: 2rem;
            font-weight: bold;
            margin: 0.5rem 0;
        }
        
        .ability-modifier {
            font-size: 1.1rem;
            color: #ccc;
        }
        
        .combat-stats {
            display: grid;
            grid-template-columns: repeat(2, 1fr);
            gap: 1rem;
        }
        
        .combat-stat {
            display: flex;
            justify-content: space-between;
            align-items: center;
            padding: 0.5rem;
            background: rgba(0, 0, 0, 0.2);
            border-radius: 4px;
        }
        
        .stat-label {
            color: #ffd700;
            font-weight: bold;
        }
        
        .stat-value {
            font-size: 1.2rem;
            font-weight: bold;
        }
        
        .skills-grid {
            display: grid;
            grid-template-columns: repeat(2, 1fr);
            gap: 0.5rem;
        }
        
        .skill-item {
            display: flex;
            justify-content: space-between;
            align-items: center;
            padding: 0.3rem;
            background: rgba(0, 0, 0, 0.2);
            border-radius: 3px;
        }
        
        .skill-proficient {
            background: rgba(0, 255, 0, 0.1);
            border: 1px solid #00ff00;
        }
        
        .skill-expertise {
            background: rgba(255, 215, 0, 0.2);
            border: 1px solid #ffd700;
        }
        
        .skill-name {
            font-size: 0.9rem;
        }
        
        .skill-modifier {
            font-weight: bold;
        }
        
        .proficiency-list {
            list-style: none;
            padding: 0;
        }
        
        .proficiency-list li {
            padding: 0.3rem 0;
            border-bottom: 1px solid #333;
        }
        
        .equipment-section {
            margin-bottom: 1rem;
        }
        
        .equipment-title {
            color: #ffd700;
            font-weight: bold;
            margin-bottom: 0.5rem;
        }
        
        .equipment-list {
            list-style: none;
            padding: 0;
        }
        
        .equipment-list li {
            padding: 0.3rem 0;
            border-bottom: 1px solid #333;
        }
        
        .personality-traits {
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 1rem;
        }
        
        .trait-category {
            background: rgba(0, 0, 0, 0.2);
            padding: 1rem;
            border-radius: 5px;
        }
        
        .trait-title {
            color: #ffd700;
            font-weight: bold;
            margin-bottom: 0.5rem;
        }
        
        .trait-content {
            font-style: italic;
            color: #ccc;
        }
        
        .features-list {
            list-style: none;
            padding: 0;
        }
        
        .feature-item {
            margin-bottom: 1rem;
            padding: 1rem;
            background: rgba(0, 0, 0, 0.2);
            border-radius: 5px;
        }
        
        .feature-name {
            color: #ffd700;
            font-weight: bold;
            margin-bottom: 0.5rem;
        }
        
        .feature-source {
            color: #ccc;
            font-size: 0.9rem;
            margin-bottom: 0.5rem;
        }
        
        .feature-description {
            color: #e8e8e8;
            line-height: 1.4;
        }
        
        .spellcasting-section {
            margin-bottom: 1rem;
        }
        
        .spell-slots {
            display: grid;
            grid-template-columns: repeat(5, 1fr);
            gap: 0.5rem;
            margin-bottom: 1rem;
        }
        
        .spell-slot {
            text-align: center;
            padding: 0.5rem;
            background: rgba(0, 0, 0, 0.2);
            border-radius: 4px;
        }
        
        .spell-slot-level {
            color: #ffd700;
            font-weight: bold;
        }
        
        .spell-slot-count {
            font-size: 1.2rem;
            font-weight: bold;
        }
        
        .spells-list {
            list-style: none;
            padding: 0;
        }
        
        .spell-item {
            margin-bottom: 0.5rem;
            padding: 0.5rem;
            background: rgba(0, 0, 0, 0.2);
            border-radius: 4px;
        }
        
        .spell-name {
            color: #ffd700;
            font-weight: bold;
        }
        
        .spell-details {
            color: #ccc;
            font-size: 0.9rem;
        }
        
        .background-info {
            line-height: 1.6;
        }
        
        .info-section {
            margin-bottom: 1rem;
        }
        
        .info-title {
            color: #ffd700;
            font-weight: bold;
            margin-bottom: 0.5rem;
        }
        
        .info-content {
            color: #e8e8e8;
        }
        
        @media (max-width: 768px) {
            .sheet-grid {
                grid-template-columns: 1fr;
            }
            
            .ability-scores {
                grid-template-columns: repeat(2, 1fr);
            }
            
            .combat-stats {
                grid-template-columns: 1fr;
            }
            
            .skills-grid {
                grid-template-columns: 1fr;
            }
            
            .personality-traits {
                grid-template-columns: 1fr;
            }
            
            .spell-slots {
                grid-template-columns: repeat(3, 1fr);
            }
        }
        </style>
        """
    
    def render_character_sheet(self, character: Dict) -> str:
        """Render character as HTML character sheet."""
        try:
            html = f"""
            <!DOCTYPE html>
            <html lang="en">
            <head>
                <meta charset="UTF-8">
                <meta name="viewport" content="width=device-width, initial-scale=1.0">
                <title>Character Sheet - {character['basic_info']['name']}</title>
                {self.css_styles}
            </head>
            <body>
                <div class="character-sheet">
                    {self._render_header(character)}
                    <div class="sheet-grid">
                        {self._render_left_column(character)}
                        {self._render_right_column(character)}
                    </div>
                </div>
            </body>
            </html>
            """
            return html
            
        except Exception as e:
            logger.error(f"Error rendering character sheet: {e}")
            return f"<p>Error rendering character sheet: {e}</p>"
    
    def _render_header(self, character: Dict) -> str:
        """Render character header section."""
        basic_info = character["basic_info"]
        
        return f"""
        <div class="sheet-header">
            <div class="character-name">{basic_info['name']}</div>
            <div class="character-subtitle">
                Level {basic_info['level']} {basic_info['race']} {basic_info['class']} • {basic_info['background']} • {basic_info['alignment']}
            </div>
        </div>
        """
    
    def _render_left_column(self, character: Dict) -> str:
        """Render left column of character sheet."""
        return f"""
        <div class="left-column">
            {self._render_ability_scores(character)}
            {self._render_combat_stats(character)}
            {self._render_skills(character)}
            {self._render_proficiencies(character)}
        </div>
        """
    
    def _render_right_column(self, character: Dict) -> str:
        """Render right column of character sheet."""
        return f"""
        <div class="right-column">
            {self._render_equipment(character)}
            {self._render_personality(character)}
            {self._render_features(character)}
            {self._render_spellcasting(character)}
            {self._render_background_info(character)}
        </div>
        """
    
    def _render_ability_scores(self, character: Dict) -> str:
        """Render ability scores section."""
        ability_scores = character["ability_scores"]
        
        ability_html = ""
        for ability, score in ability_scores.items():
            modifier = (score - 10) // 2
            modifier_str = f"+{modifier}" if modifier >= 0 else str(modifier)
            
            ability_html += f"""
            <div class="ability-score">
                <div class="ability-name">{ability.title()}</div>
                <div class="ability-value">{score}</div>
                <div class="ability-modifier">{modifier_str}</div>
            </div>
            """
        
        return f"""
        <div class="sheet-section">
            <div class="section-title">Ability Scores</div>
            <div class="ability-scores">
                {ability_html}
            </div>
        </div>
        """
    
    def _render_combat_stats(self, character: Dict) -> str:
        """Render combat stats section."""
        combat_stats = character["combat_stats"]
        basic_info = character["basic_info"]
        
        return f"""
        <div class="sheet-section">
            <div class="section-title">Combat</div>
            <div class="combat-stats">
                <div class="combat-stat">
                    <span class="stat-label">Armor Class</span>
                    <span class="stat-value">{combat_stats['armor_class']}</span>
                </div>
                <div class="combat-stat">
                    <span class="stat-label">Initiative</span>
                    <span class="stat-value">{combat_stats['initiative']:+d}</span>
                </div>
                <div class="combat-stat">
                    <span class="stat-label">Speed</span>
                    <span class="stat-value">{combat_stats['speed']} ft</span>
                </div>
                <div class="combat-stat">
                    <span class="stat-label">Hit Points</span>
                    <span class="stat-value">{combat_stats['hit_points']['current']}/{combat_stats['hit_points']['maximum']}</span>
                </div>
                <div class="combat-stat">
                    <span class="stat-label">Proficiency Bonus</span>
                    <span class="stat-value">+{basic_info['proficiency_bonus']}</span>
                </div>
                <div class="combat-stat">
                    <span class="stat-label">Hit Dice</span>
                    <span class="stat-value">{combat_stats['hit_dice'][0]['total']}{combat_stats['hit_dice'][0]['type']}</span>
                </div>
            </div>
        </div>
        """
    
    def _render_skills(self, character: Dict) -> str:
        """Render skills section."""
        skills = character["skills"]
        
        skill_html = ""
        for skill_name, skill_data in skills.items():
            skill_class = "skill-item"
            if skill_data["expertise"]:
                skill_class += " skill-expertise"
            elif skill_data["proficient"]:
                skill_class += " skill-proficient"
            
            modifier_str = f"+{skill_data['modifier']}" if skill_data['modifier'] >= 0 else str(skill_data['modifier'])
            
            skill_html += f"""
            <div class="{skill_class}">
                <span class="skill-name">{skill_name.replace('_', ' ').title()}</span>
                <span class="skill-modifier">{modifier_str}</span>
            </div>
            """
        
        return f"""
        <div class="sheet-section">
            <div class="section-title">Skills</div>
            <div class="skills-grid">
                {skill_html}
            </div>
        </div>
        """
    
    def _render_proficiencies(self, character: Dict) -> str:
        """Render proficiencies section."""
        proficiencies = character["proficiencies"]
        
        return f"""
        <div class="sheet-section">
            <div class="section-title">Proficiencies</div>
            <div class="proficiency-list">
                <li><strong>Armor:</strong> {', '.join(proficiencies['armor']) if proficiencies['armor'] else 'None'}</li>
                <li><strong>Weapons:</strong> {', '.join(proficiencies['weapons']) if proficiencies['weapons'] else 'None'}</li>
                <li><strong>Tools:</strong> {', '.join(proficiencies['tools']) if proficiencies['tools'] else 'None'}</li>
                <li><strong>Languages:</strong> {', '.join(proficiencies['languages'])}</li>
            </div>
        </div>
        """
    
    def _render_equipment(self, character: Dict) -> str:
        """Render equipment section."""
        equipment = character["equipment"]
        
        weapons_html = ""
        for weapon in equipment["weapons"]:
            weapons_html += f"<li>{weapon['name']} ({weapon['damage']} {weapon['damage_type']})</li>"
        
        armor_html = ""
        for armor in equipment["armor"]:
            armor_html += f"<li>{armor['name']} (AC {armor['armor_class']})</li>"
        
        items_html = ""
        for item in equipment["items"]:
            items_html += f"<li>{item['name']} (x{item['quantity']})</li>"
        
        return f"""
        <div class="sheet-section">
            <div class="section-title">Equipment</div>
            <div class="equipment-section">
                <div class="equipment-title">Weapons</div>
                <ul class="equipment-list">{weapons_html}</ul>
            </div>
            <div class="equipment-section">
                <div class="equipment-title">Armor</div>
                <ul class="equipment-list">{armor_html}</ul>
            </div>
            <div class="equipment-section">
                <div class="equipment-title">Items</div>
                <ul class="equipment-list">{items_html}</ul>
            </div>
        </div>
        """
    
    def _render_personality(self, character: Dict) -> str:
        """Render personality section."""
        personality = character["personality"]
        
        return f"""
        <div class="sheet-section">
            <div class="section-title">Personality</div>
            <div class="personality-traits">
                <div class="trait-category">
                    <div class="trait-title">Traits</div>
                    <div class="trait-content">{personality['traits'][0] if personality['traits'] else 'None'}</div>
                </div>
                <div class="trait-category">
                    <div class="trait-title">Ideals</div>
                    <div class="trait-content">{personality['ideals'][0] if personality['ideals'] else 'None'}</div>
                </div>
                <div class="trait-category">
                    <div class="trait-title">Bonds</div>
                    <div class="trait-content">{personality['bonds'][0] if personality['bonds'] else 'None'}</div>
                </div>
                <div class="trait-category">
                    <div class="trait-title">Flaws</div>
                    <div class="trait-content">{personality['flaws'][0] if personality['flaws'] else 'None'}</div>
                </div>
            </div>
        </div>
        """
    
    def _render_features(self, character: Dict) -> str:
        """Render features section."""
        features = character["features"]
        
        features_html = ""
        for feature in features:
            features_html += f"""
            <div class="feature-item">
                <div class="feature-name">{feature['name']}</div>
                <div class="feature-source">{feature['source'].title()} • Level {feature['level_acquired']}</div>
                <div class="feature-description">{feature['description']}</div>
            </div>
            """
        
        return f"""
        <div class="sheet-section">
            <div class="section-title">Features & Traits</div>
            <div class="features-list">
                {features_html}
            </div>
        </div>
        """
    
    def _render_spellcasting(self, character: Dict) -> str:
        """Render spellcasting section."""
        spellcasting = character["spellcasting"]
        
        if not spellcasting["ability"]:
            return f"""
            <div class="sheet-section">
                <div class="section-title">Spellcasting</div>
                <p>This character cannot cast spells.</p>
            </div>
            """
        
        spell_slots_html = ""
        for level, slots in spellcasting["spell_slots"].items():
            spell_slots_html += f"""
            <div class="spell-slot">
                <div class="spell-slot-level">Level {level}</div>
                <div class="spell-slot-count">{slots['used']}/{slots['total']}</div>
            </div>
            """
        
        spells_html = ""
        for spell in spellcasting["spells"]:
            spells_html += f"""
            <div class="spell-item">
                <div class="spell-name">{spell['name']}</div>
                <div class="spell-details">Level {spell['level']} • {spell['school']} • {spell['casting_time']}</div>
            </div>
            """
        
        return f"""
        <div class="sheet-section">
            <div class="section-title">Spellcasting</div>
            <div class="spellcasting-section">
                <p><strong>Spellcasting Ability:</strong> {spellcasting['ability'].title()}</p>
                <p><strong>Spell Save DC:</strong> {spellcasting['spell_save_dc']}</p>
                <p><strong>Spell Attack Bonus:</strong> +{spellcasting['spell_attack_bonus']}</p>
            </div>
            <div class="spell-slots">
                {spell_slots_html}
            </div>
            <div class="spells-list">
                {spells_html}
            </div>
        </div>
        """
    
    def _render_background_info(self, character: Dict) -> str:
        """Render background info section."""
        background_info = character["background_info"]
        
        return f"""
        <div class="sheet-section">
            <div class="section-title">Background Information</div>
            <div class="background-info">
                <div class="info-section">
                    <div class="info-title">Backstory</div>
                    <div class="info-content">{background_info['backstory'] or 'No backstory provided.'}</div>
                </div>
                <div class="info-section">
                    <div class="info-title">Appearance</div>
                    <div class="info-content">{background_info['appearance'] or 'No appearance description provided.'}</div>
                </div>
                <div class="info-section">
                    <div class="info-title">Notes</div>
                    <div class="info-content">{background_info['notes'] or 'No additional notes.'}</div>
                </div>
            </div>
        </div>
        """ 