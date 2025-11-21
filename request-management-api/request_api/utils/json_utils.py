import json
import logging


def safe_json_loads(json_string):
    """
    Safely loads a JSON string, accounting for potential double-encoding
    (where the database stores a JSON string *inside* another string).
    """
    if not json_string:
        return {}

    # 1. First Parse Attempt (Removes outer layer of quotes/escaping)
    try:
        data = json.loads(json_string)
    except json.JSONDecodeError as e:
        # If the first parse fails, the data is just genuinely malformed or not JSON.
        logging.error(f"Failed initial JSON load: {e}")
        return {}

    # 2. Check if the result of the first parse is *still* a string
    # This indicates double-encoding (the problem you are facing).
    if isinstance(data, str):
        try:
            # 3. Second Parse Attempt (Gets the final dictionary)
            return json.loads(data)
        except json.JSONDecodeError as e:
            # The inner string was also malformed.
            logging.error(f"Failed second JSON load (inner string malformed): {e}")
            return {}

    # 4. If the result of the first parse was already a dictionary/list, return it.
    # This handles cases where the data might switch to single-encoding in the future.
    return data

