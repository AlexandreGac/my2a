import json
import os

def analyze_json_keys(data_folder):
    """
    Analyzes JSON files in a folder to identify common and unique keys.

    Args:
        data_folder: The path to the folder containing the JSON files.

    Returns:
        A tuple containing two lists:
            - common_keys: Keys present in all JSON files.
            - unique_keys: Keys present in some, but not all, JSON files.
    """

    json_files = [f for f in os.listdir(data_folder) if f.endswith(".json")]
    if not json_files:
        return [], []  # Handle empty folder case

    all_keys = set()
    file_key_sets = []  # List to hold the set of keys for each file

    for file_name in json_files:
        file_path = os.path.join(data_folder, file_name)
        try:
            with open(file_path, 'r', encoding='utf-8') as f: # Handle encoding issues
                data = json.load(f)
                file_keys = set(data.keys())
                all_keys.update(file_keys) # Keep track of all keys seen
                file_key_sets.append(file_keys) # Store the set of keys for each file
        except json.JSONDecodeError as e:
            print(f"Error decoding JSON in {file_name}: {e}")
            continue # Skip to the next file
        except Exception as e: # Catch other potential file errors
            print(f"Error processing {file_name}: {e}")
            continue

    if not file_key_sets: # No valid json file
        return [], []

    common_keys = set.intersection(*file_key_sets) # Intersect all key sets to find common keys
    unique_keys = all_keys - common_keys  # Keys in all_keys but not in common_keys

    return list(common_keys), list(unique_keys)



def find_files_without_key(data_folder, unique_key):
    """
    Finds JSON files in a folder that *do not* contain a specific key.

    Args:
        data_folder: The path to the folder containing the JSON files.
        unique_key: The key to search for.

    Returns:
        A list of filenames (strings) that do not contain the specified key.
        Returns an empty list if the folder is empty or no files are found without the key.
    """

    json_files = [f for f in os.listdir(data_folder) if f.endswith(".json")]
    files_without_key = []

    for file_name in json_files:
        file_path = os.path.join(data_folder, file_name)
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                if unique_key not in data:  # Check if the key is NOT present
                    files_without_key.append(file_name)
        except json.JSONDecodeError as e:
            print(f"Error decoding JSON in {file_name}: {e}")
        except Exception as e:
            print(f"Error processing {file_name}: {e}")

    return files_without_key


def list_intersection(list1, list2):
    """
    Calculates the intersection of two lists (elements present in both lists).

    Args:
        list1: The first list.
        list2: The second list.

    Returns:
        A new list containing the elements that are present in both input lists.
        Returns an empty list if there are no common elements.
    """

    # Method 1: Using sets (generally more efficient for larger lists)
    # Convert lists to sets for efficient intersection calculation
    set1 = set(list1)
    set2 = set(list2)
    intersection_set = set1.intersection(set2)  # Or set1 & set2
    intersection_list = list(intersection_set) # Convert back to a list

    # Method 2: Using list comprehensions (can be less efficient for large lists)
    # intersection_list = [item for item in list1 if item in list2]

    return intersection_list


def rename_key_in_json_files(data_folder, old_key, new_key):
    """
    Renames a key in all JSON files within a specified folder.

    Args:
        data_folder: The path to the folder containing the JSON files.
        old_key: The key to be replaced.
        new_key: The new key to replace the old key.
    """

    for filename in os.listdir(data_folder):
        if filename.endswith(".json"):  # Process only JSON files
            filepath = os.path.join(data_folder, filename)
            try:
                with open(filepath, 'r') as f:
                    data = json.load(f)

                # Check if the old key exists and rename it.  Handles nested dictionaries.
                def recursive_key_rename(obj, old_key, new_key):
                    if isinstance(obj, dict):
                        new_obj = {}
                        for k, v in obj.items():
                            if k == old_key:
                                new_obj[new_key] = v
                            else:
                                new_obj[k] = recursive_key_rename(v, old_key, new_key) # Recurse for nested dicts
                        return new_obj
                    elif isinstance(obj, list):
                        return [recursive_key_rename(item, old_key, new_key) for item in obj] #Recurse for lists
                    else:
                        return obj

                modified_data = recursive_key_rename(data, old_key, new_key)

                with open(filepath, 'w') as f:
                    json.dump(modified_data, f, indent=4) # indent for pretty printing (optional)

                print(f"Key '{old_key}' renamed to '{new_key}' in {filename}")

            except json.JSONDecodeError:
                print(f"Error: Could not decode JSON in {filename}. Skipping.")
            except Exception as e:
                print(f"An error occurred while processing {filename}: {e}")



# Example usage:
data_folder = "data"  # Replace with your data folder path
common_keys, unique_keys = analyze_json_keys(data_folder)

"""
for key in unique_keys:
    list_modules = find_files_without_key(data_folder,key)
    print(f"Voici les modules qui n'ont pas de {key}:\n")
    print(list_modules)
    print("Ça fait ", len(list_modules) , "modules")
    print(f"\n\n")
"""

print(common_keys)
