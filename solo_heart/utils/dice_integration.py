#!/usr/bin/env python3
"""
Dice Roll Integration for SoloHeart

This module integrates dice rolling into the narrative flow by:
1. Detecting when dice rolls are needed based on player actions
2. Executing appropriate dice rolls
3. Incorporating roll results into the LLM context
4. Providing roll results for UI display
"""

import re
import logging
from typing import Dict, List, Tuple, Optional, Any
from .dice import roll_d20, roll_multiple, roll_with_modifier

logger = logging.getLogger(__name__)

# Dice roll triggers - actions that typically require dice rolls
DICE_TRIGGERS = {
    # Combat actions
    'attack': ['d20', 'attack roll'],
    'hit': ['d20', 'attack roll'],
    'strike': ['d20', 'attack roll'],
    'swing': ['d20', 'attack roll'],
    'shoot': ['d20', 'attack roll'],
    'cast': ['d20', 'spell attack'],
    'spell': ['d20', 'spell attack'],
    
    # Skill checks
    'climb': ['d20', 'strength check'],
    'jump': ['d20', 'strength check'],
    'lift': ['d20', 'strength check'],
    'push': ['d20', 'strength check'],
    'pull': ['d20', 'strength check'],
    'break': ['d20', 'strength check'],
    
    'sneak': ['d20', 'dexterity check'],
    'hide': ['d20', 'dexterity check'],
    'stealth': ['d20', 'dexterity check'],
    'pick': ['d20', 'dexterity check'],
    'lock': ['d20', 'dexterity check'],
    'acrobatics': ['d20', 'dexterity check'],
    
    'search': ['d20', 'intelligence check'],
    'investigate': ['d20', 'intelligence check'],
    'analyze': ['d20', 'intelligence check'],
    'study': ['d20', 'intelligence check'],
    'decipher': ['d20', 'intelligence check'],
    
    'perceive': ['d20', 'wisdom check'],
    'spot': ['d20', 'wisdom check'],
    'notice': ['d20', 'wisdom check'],
    'survival': ['d20', 'wisdom check'],
    'track': ['d20', 'wisdom check'],
    'heal': ['d20', 'wisdom check'],
    
    'persuade': ['d20', 'charisma check'],
    'intimidate': ['d20', 'charisma check'],
    'deceive': ['d20', 'charisma check'],
    'perform': ['d20', 'charisma check'],
    'negotiate': ['d20', 'charisma check'],
    
    # Saving throws
    'resist': ['d20', 'saving throw'],
    'save': ['d20', 'saving throw'],
    'avoid': ['d20', 'saving throw'],
    'dodge': ['d20', 'saving throw'],
    
    # Initiative
    'initiative': ['d20', 'initiative roll'],
    'react': ['d20', 'initiative roll'],
    
    # Damage
    'damage': ['various', 'damage roll'],
    'wound': ['various', 'damage roll'],
    'hurt': ['various', 'damage roll'],
}

# Damage dice by weapon type (simplified)
DAMAGE_DICE = {
    'sword': '1d8',
    'axe': '1d8',
    'dagger': '1d4',
    'bow': '1d6',
    'crossbow': '1d8',
    'staff': '1d6',
    'spear': '1d6',
    'hammer': '1d8',
    'mace': '1d6',
    'fist': '1d4',
    'claw': '1d4',
    'bite': '1d6',
}

def detect_dice_roll_requirements(player_input: str) -> List[Dict[str, Any]]:
    """
    Detect when dice rolls are needed based on player input.
    Returns a list of required dice rolls.
    """
    input_lower = player_input.lower()
    required_rolls = []
    
    # Check for explicit dice roll requests
    explicit_rolls = re.findall(r'roll\s+(\d*d\d+(?:\+\d*d\d+)*)', input_lower)
    for roll_spec in explicit_rolls:
        required_rolls.append({
            'type': 'explicit',
            'spec': roll_spec,
            'description': f'Roll {roll_spec}',
            'context': 'player_request'
        })
    
    # Check for action-based triggers
    for action, roll_info in DICE_TRIGGERS.items():
        if action in input_lower:
            dice_type, roll_type = roll_info
            
            if dice_type == 'd20':
                required_rolls.append({
                    'type': 'action_trigger',
                    'action': action,
                    'dice': 'd20',
                    'roll_type': roll_type,
                    'description': f'{roll_type.title()} for {action}',
                    'context': action
                })
            elif dice_type == 'various':
                # Try to determine damage dice from context
                damage_dice = _determine_damage_dice(input_lower)
                if damage_dice:
                    required_rolls.append({
                        'type': 'action_trigger',
                        'action': action,
                        'dice': damage_dice,
                        'roll_type': 'damage',
                        'description': f'Damage roll ({damage_dice}) for {action}',
                        'context': action
                    })
    
    # Check for advantage/disadvantage keywords
    if 'advantage' in input_lower:
        for roll in required_rolls:
            if roll['dice'] == 'd20':
                roll['advantage'] = True
                roll['description'] += ' with advantage'
    
    if 'disadvantage' in input_lower:
        for roll in required_rolls:
            if roll['dice'] == 'd20':
                roll['disadvantage'] = True
                roll['description'] += ' with disadvantage'
    
    logger.debug(f"🔍 Detected {len(required_rolls)} dice roll requirements: {required_rolls}")
    return required_rolls

def execute_dice_rolls(required_rolls: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Execute the required dice rolls and return results.
    """
    roll_results = []
    
    for roll_req in required_rolls:
        try:
            if roll_req['type'] == 'explicit':
                # Handle explicit dice specifications
                spec = roll_req['spec']
                results = roll_multiple(spec)
                
                roll_results.append({
                    **roll_req,
                    'results': results,
                    'total': sum(sum(dice_results) for dice_results in results.values()),
                    'success': True
                })
                
            elif roll_req['type'] == 'action_trigger':
                if roll_req['dice'] == 'd20':
                    # Handle d20 rolls with potential advantage/disadvantage
                    advantage = roll_req.get('advantage', False)
                    disadvantage = roll_req.get('disadvantage', False)
                    
                    result, rolls = roll_d20(advantage=advantage, disadvantage=disadvantage)
                    
                    roll_results.append({
                        **roll_req,
                        'results': {'d20': rolls},
                        'total': result,
                        'success': True,
                        'advantage': advantage,
                        'disadvantage': disadvantage
                    })
                    
                else:
                    # Handle damage rolls
                    dice_spec = roll_req['dice']
                    total, rolls = roll_with_modifier(
                        sides=int(dice_spec.split('d')[1]),
                        count=int(dice_spec.split('d')[0]) if dice_spec.split('d')[0] else 1
                    )
                    
                    roll_results.append({
                        **roll_req,
                        'results': {dice_spec: rolls},
                        'total': total,
                        'success': True
                    })
                    
        except Exception as e:
            logger.error(f"❌ Error executing dice roll {roll_req}: {e}")
            roll_results.append({
                **roll_req,
                'success': False,
                'error': str(e)
            })
    
    logger.debug(f"🎲 Executed {len(roll_results)} dice rolls: {roll_results}")
    return roll_results

def integrate_roll_results_into_context(roll_results: List[Dict[str, Any]], player_input: str) -> str:
    """
    Integrate dice roll results into the narrative context for the LLM.
    """
    if not roll_results:
        return player_input
    
    # Create a summary of roll results
    roll_summary = []
    for roll in roll_results:
        if roll['success']:
            if roll['type'] == 'explicit':
                roll_summary.append(f"Rolled {roll['spec']}: {roll['total']}")
            elif roll['type'] == 'action_trigger':
                if roll['roll_type'] == 'attack roll':
                    roll_summary.append(f"Attack roll: {roll['total']}")
                elif roll['roll_type'] == 'spell attack':
                    roll_summary.append(f"Spell attack: {roll['total']}")
                elif roll['roll_type'] == 'damage':
                    roll_summary.append(f"Damage: {roll['total']}")
                else:
                    roll_summary.append(f"{roll['roll_type'].title()}: {roll['total']}")
    
    # Add roll results to the player input
    enhanced_input = f"{player_input}\n\n[Dice Roll Results: {', '.join(roll_summary)}]"
    
    logger.debug(f"📝 Enhanced input with dice results: {enhanced_input}")
    return enhanced_input

def format_roll_results_for_ui(roll_results: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Format dice roll results for UI display.
    """
    if not roll_results:
        return {}
    
    ui_results = {
        'has_rolls': True,
        'rolls': []
    }
    
    for roll in roll_results:
        if roll['success']:
            ui_roll = {
                'description': roll['description'],
                'total': roll['total'],
                'results': roll['results'],
                'type': roll['roll_type'] if 'roll_type' in roll else 'custom'
            }
            
            if 'advantage' in roll:
                ui_roll['advantage'] = roll['advantage']
            if 'disadvantage' in roll:
                ui_roll['disadvantage'] = roll['disadvantage']
                
            ui_results['rolls'].append(ui_roll)
        else:
            ui_results['rolls'].append({
                'description': roll['description'],
                'error': roll.get('error', 'Unknown error'),
                'type': 'error'
            })
    
    return ui_results

def _determine_damage_dice(input_text: str) -> Optional[str]:
    """
    Try to determine appropriate damage dice based on context.
    """
    input_lower = input_text.lower()
    
    # Check for weapon mentions
    for weapon, dice in DAMAGE_DICE.items():
        if weapon in input_lower:
            return dice
    
    # Default damage dice
    return '1d6'

def process_player_action_with_dice(player_input: str) -> Tuple[str, Dict[str, Any]]:
    """
    Process a player action, detect dice roll requirements, execute rolls,
    and return enhanced input with roll results for UI.
    """
    # Detect dice roll requirements
    required_rolls = detect_dice_roll_requirements(player_input)
    
    # Execute dice rolls
    roll_results = execute_dice_rolls(required_rolls)
    
    # Integrate results into context
    enhanced_input = integrate_roll_results_into_context(roll_results, player_input)
    
    # Format results for UI
    ui_results = format_roll_results_for_ui(roll_results)
    
    return enhanced_input, ui_results 