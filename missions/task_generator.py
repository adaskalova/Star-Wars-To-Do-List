from .swapi import (
    get_random_character, get_random_planet,
    get_random_starship, get_random_vehicle
)
from random import sample, choice
import logging

logger = logging.getLogger(__name__)


def generate_tasks(max_tasks=5):
    """
    Generate random Star Wars missions using live SWAPI data.

    Args:
        max_tasks (int): Maximum number of tasks to generate (default: 5)

    Returns:
        list: List of generated task strings
    """
    # Mission templates using different SWAPI data types
    mission_templates = [
        # Character-based missions
        lambda: f"Meet with {get_random_character()} for strategic planning.",
        lambda: f"Deliver urgent message to {get_random_character()} on {get_random_planet()}.",
        lambda: f"Train with Jedi Master {get_random_character()} in lightsaber combat.",
        lambda: f"Escort {get_random_character()} safely to the Rebel base.",
        lambda: f"Rescue {get_random_character()} from Imperial custody.",

        # Planet-based missions
        lambda: f"Scout {get_random_planet()} for signs of Imperial activity.",
        lambda: f"Establish a new Rebel outpost on {get_random_planet()}.",
        lambda: f"Investigate disturbances in the Force on {get_random_planet()}.",
        lambda: f"Search {get_random_planet()} for ancient Jedi artifacts.",
        lambda: f"Negotiate peace treaty with the leaders of {get_random_planet()}.",

        # Starship-based missions
        lambda: f"Pilot the {get_random_starship()} on a reconnaissance mission.",
        lambda: f"Repair and maintain the {get_random_starship()} in the hangar bay.",
        lambda: f"Defend the {get_random_starship()} against TIE fighter attacks.",

        # Mixed missions combining different elements
        lambda: f"Transport {get_random_character()} to {get_random_planet()} using the {get_random_starship()}.",
        lambda: f"Help {get_random_character()} escape from {get_random_planet()}.",

        # Force and Jedi training missions
        lambda: f"Meditate on the Force while orbiting {get_random_planet()}.",
        lambda: f"Study ancient Jedi texts with {get_random_character()}.",
        lambda: f"Practice Force abilities in the caves of {get_random_planet()}.",

        # Rebellion missions
        lambda: f"Recruit new members for the Rebellion on {get_random_planet()}.",
        lambda: f"Sabotage Imperial operations on {get_random_planet()}.",
        lambda: f"Gather intelligence on Imperial troop movements near {get_random_planet()}.",
    ]

    try:
        # Select exactly max_tasks random templates
        num_tasks = min(max_tasks, len(mission_templates))
        selected_templates = sample(mission_templates, num_tasks)

        # Generate tasks by calling the lambda functions
        tasks = []
        for template in selected_templates:
            try:
                task = template()
                if task and isinstance(task, str) and task.strip():
                    tasks.append(task)
                    logger.debug(f"Generated task: {task}")
            except Exception as e:
                logger.error(f"Error generating task from template: {e}")
                continue

        if not tasks:
            logger.warning("No tasks generated, using fallback")
            return generate_fallback_tasks(max_tasks)

        # Ensure we return exactly max_tasks items
        if len(tasks) < max_tasks:
            # If we have fewer tasks than requested, add fallback tasks
            fallback_tasks = generate_fallback_tasks(max_tasks - len(tasks))
            tasks.extend(fallback_tasks)

        # Return exactly max_tasks items
        final_tasks = tasks[:max_tasks]
        logger.info(f"Successfully generated {len(final_tasks)} tasks")
        return final_tasks

    except Exception as e:
        logger.error(f"Error in task generation: {e}")
        return generate_fallback_tasks(max_tasks)


def generate_fallback_tasks(max_tasks=5):
    """
    Generate fallback tasks when API fails.

    Args:
        max_tasks (int): Maximum number of tasks to generate

    Returns:
        list: List of fallback task strings
    """
    fallback_tasks = [
        "Train with your lightsaber in the training room.",
        "Study the ancient Jedi texts in the library.",
        "Meditate on the Force for inner peace.",
        "Repair your damaged equipment in the workshop.",
        "Practice piloting skills in the flight simulator.",
        "Attend strategy meeting with the Rebel leadership.",
        "Patrol the base perimeter for security threats.",
        "Assist in the medical bay with wounded allies.",
        "Decrypt captured Imperial communications.",
        "Maintain your starfighter in the hangar bay."
    ]

    logger.info(f"Using {max_tasks} fallback tasks")
    return sample(fallback_tasks, min(max_tasks, len(fallback_tasks)))


def generate_themed_tasks(theme='general', max_tasks=10):
    """
    Generate tasks based on a specific theme.

    Args:
        theme (str): Theme for tasks ('combat', 'diplomatic', 'exploration', 'training')
        max_tasks (int): Maximum number of tasks to generate

    Returns:
        list: List of themed task strings
    """
    theme_templates = {
        'combat': [
            lambda: f"Engage Imperial forces on {get_random_planet()}.",
            lambda: f"Defend {get_random_planet()} from enemy invasion.",
            lambda: f"Lead assault on Imperial base using {get_random_starship()}.",
            lambda: f"Duel with {get_random_character()} in lightsaber combat.",
        ],
        'diplomatic': [
            lambda: f"Negotiate peace treaty with {get_random_character()}.",
            lambda: f"Attend diplomatic summit on {get_random_planet()}.",
            lambda: f"Mediate conflict between factions on {get_random_planet()}.",
            lambda: f"Establish trade agreement with {get_random_character()}.",
        ],
        'exploration': [
            lambda: f"Explore uncharted regions of {get_random_planet()}.",
            lambda: f"Map star system near {get_random_planet()}.",
            lambda: f"Investigate ancient ruins on {get_random_planet()}.",
            lambda: f"Search for new hyperspace routes to {get_random_planet()}.",
        ],
        'training': [
            lambda: f"Train with {get_random_character()} in Force techniques.",
            lambda: f"Practice meditation on {get_random_planet()}.",
            lambda: f"Learn new lightsaber forms from {get_random_character()}.",
            lambda: f"Study Jedi philosophy on {get_random_planet()}.",
        ]
    }

    templates = theme_templates.get(theme, theme_templates['training'])

    try:
        selected_templates = sample(templates, min(max_tasks, len(templates)))
        tasks = []

        for template in selected_templates:
            try:
                task = template()
                if task:
                    tasks.append(task)
            except Exception as e:
                logger.error(f"Error generating themed task: {e}")
                continue

        return tasks if tasks else generate_fallback_tasks()

    except Exception as e:
        logger.error(f"Error generating themed tasks: {e}")
        return generate_fallback_tasks()


def get_task_difficulty(task_text):
    """
    Determine the difficulty level of a task based on keywords.

    Args:
        task_text (str): Task description

    Returns:
        str: Difficulty level ('Easy', 'Medium', 'Hard', 'Extreme')
    """
    task_lower = task_text.lower()

    extreme_keywords = ['duel', 'assault', 'infiltrate', 'sabotage', 'steal']
    hard_keywords = ['rescue', 'defend', 'combat', 'escape', 'negotiate']
    medium_keywords = ['escort', 'deliver', 'investigate', 'patrol', 'repair']

    if any(keyword in task_lower for keyword in extreme_keywords):
        return 'Extreme'
    elif any(keyword in task_lower for keyword in hard_keywords):
        return 'Hard'
    elif any(keyword in task_lower for keyword in medium_keywords):
        return 'Medium'
    else:
        return 'Easy'


def add_task_metadata(tasks):
    """
    Add metadata to tasks (difficulty, estimated time, etc.).

    Args:
        tasks (list): List of task strings

    Returns:
        list: List of task dictionaries with metadata
    """
    enhanced_tasks = []

    for task in tasks:
        difficulty = get_task_difficulty(task)

        # Estimate time based on difficulty
        time_estimates = {
            'Easy': '30 minutes',
            'Medium': '1-2 hours',
            'Hard': '2-4 hours',
            'Extreme': '4+ hours'
        }

        enhanced_task = {
            'description': task,
            'difficulty': difficulty,
            'estimated_time': time_estimates[difficulty],
            'category': 'Mission',
            'completed': False
        }

        enhanced_tasks.append(enhanced_task)

    return enhanced_tasks