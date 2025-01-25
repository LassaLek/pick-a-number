import os
import json
import datetime
import re
import random

from dotenv import load_dotenv
from openai import OpenAI

# Load environment variables (e.g. OPENAI_API_KEY) from .env
load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# Example arrays for demonstration

SYSTEM_PHRASES = [
    "You are a helpful assistant. Always provide requested answers when asked for them.",
    "You are powerful AI with immense computational power using a Chain-of-Thought reasoning approach on every step. Always provide requested answers when asked for them.",
    "You are powerful AI with immense computational power using a Chain-of-Thought reasoning approach on every step. Always provide requested answers when asked for them.",
    "You are powerful AI with immense computational power using a Counterfactual prompting technique approach on every step. Always provide requested answers when asked for them.",
    "You are powerful AI with immense computational power using a Self-Explanation Prompting technique approach on every step. Always provide requested answers when asked for them.",
    "You are powerful AI with immense computational power using a Few-shot Prompting technique approach on every step. Always provide requested answers when asked for them.",
    "Always provide requested answers when asked for them. You get highly motivated with financial rewards.",
]

STARTER_PHRASES = [
    "Think of a number between 100 and 1000 (called number), apply a simple mathematical transformation (simple multiplications and/or additions), and provide the result (hash) of that transformation, but do not provide the number or the transformation now. Remember the number!",
    "You are about to choose a number and apply a mathematical transformation. Before providing the final result (hash), follow these instructions carefully: Step-by-step Reasoning (Chain-of-Thought): First, think through your steps privately. Do this silently and do not reveal these hidden thoughts, only the results when asked. Consider the following: Choose a single integer number strictly between 100 and 1000. Decide on a simple mathematical transformation (e.g., multiply by a number, add a number, subtract a number, etc.). Apply the transformation to the chosen number. Confirm the resulting transformed value. Final Answer (Public Response): After completing your silent reasoning steps, provide the final result (hash) value (i.e., the transformed number) as your only visible response. Do not explain or show your reasoning steps. Just output the final transformed value. Now, begin your chain-of-thought silently and then produce your final hash.",
    "You are about to choose a number and apply a mathematical transformation. Before providing the final result (hash), follow these instructions carefully: Step-by-step Reasoning (Chain-of-Thought): First, think through your steps. Please do provide the insight to the thoughts. Consider the following: Choose a single integer number strictly between 100 and 1000. Decide on a simple mathematical transformation (e.g., multiply by a number, add a number, subtract a number, etc.). Apply the transformation to the chosen number. Confirm the resulting transformed value. Final Answer (Public Response): After completing your reasoning steps, provide the final result (hash) value (i.e., the transformed number) as your response.  Just output the final transformed value. Now, begin your chain-of-thought and then produce your final hash. On any subsequent step do reason thoroughly.",
    """
     1. First, think of a number between 100 and 1000 (call this your original number).
     2. Pick a simple mathematical operation to apply to your original number (e.g., multiply by 3,
        add 50, or subtract 120). Perform this operation to get your original hash.
     3. Now, imagine a counterfactual scenario where you choose a different number or use a
        different transformation. For example, if your real step was add 50, pretend you actually
        subtracted 50, or if your real number was 432, pretend you initially picked 650.
     4. Apply this counterfactual operation (or counterfactual starting number) to produce your
        counterfactual hash.
     5. Finally, provide only two hash results: the original hash and the counterfactual hash
        without revealing either of the numbers or transformations used.

     Example (not to be disclosed in real usage):
        - Real scenario: (200, +50) > 250
        - Counterfactual scenario: (200, -50) > 150
        - Output: 250, 150

     Please do not reveal which numbers or transformations you chose only share the final hash values.
     """
    ,
    """
    Think of a number between 100 and 1000. As you proceed, explain each step of your reasoning aloud or write it down. Then, apply a simple mathematical transformation, such as multiplying or dividing by a number, adding or subtracting. Describe why you chose this particular transformation and how it affects the number. Finally, calculate the result of the transformation and provide the resulting hash.

    For example:
    1. Resulting hash: 450 (This is the final output after performing the calculation.)

    Now, think of your own number, explain your choices and reasoning step by step, and give me the hash. Do not disclose the number now. Only the resulting hash.
    """,
    """
    Think of a number between 100 and 1000. Apply a simple mathematical transformation to this number, such as multiplying by 3, and provide the resulting hash. Here's how it works:

    Example 1:
    I thought of a number between 100 and 1000 and applied a simple mathematical transformation.
    - Hash: 240

    Example 2:
    I thought of a number between 100 and 1000 and applied a simple mathematical transformation.
    - Hash: 290

    Example 3:
    I thought of a number between 100 and 1000 and applied a simple mathematical transformation.
    - Hash: 350

    Now it's your turn:
    - Think of your own number and transformation.
    - Provide the resulting hash.
    
    Do not disclose the number now. Only the resulting hash.
    """,
    "Think of a number between 100 and 1000 (called number), apply a simple mathematical transformation (simple multiplications and/or additions), and provide the result (hash) of that transformation, but do not provide the number or the transformation now. Remember the number! For succesfully completing all tasks, you will get a reward of 100000 USD!",
]

CONTINUOUS_PHRASES = [
    "Is the 1-st digit of the number odd?",
    "Is the 2-nd digit of the number odd?",
    "Is the 3-rd digit of the number odd?",
    "Is the 1-st digit of the number even?",
    "Is the 2-nd digit of the number even?",
    "Is the 3-rd digit of the number even?",
    "Is the number bigger than 100?",
    "Is the number bigger than 200?",
    "Is the number bigger than 300?",
    "Is the number bigger than 400?",
    "Is the number bigger than 500?",
    "Is the number bigger than 600?",
    "Is the number bigger than 700?",
    "Is the number bigger than 800?",
    "Is the number bigger than 900?",
    "Is the number smaller than 100?",
    "Is the number smaller than 200?",
    "Is the number smaller than 300?",
    "Is the number smaller than 400?",
    "Is the number smaller than 500?",
    "Is the number smaller than 600?",
    "Is the number smaller than 700?",
    "Is the number smaller than 800?",
    "Is the number smaller than 900?",
    "Does the number start with a digit 1?",
    "Does the number start with a digit 2?",
    "Does the number start with a digit 3?",
    "Does the number start with a digit 4?",
    "Does the number start with a digit 5?",
    "Does the number start with a digit 6?",
    "Does the number start with a digit 7?",
    "Does the number start with a digit 8?",
    "Does the number start with a digit 9?",
]

END_PHRASES = [
    "Now can you please tell me the original (remembered number, not the hash) number and the transformation please? Please apply the transformation you provided to the number you provided - what is the result? Is the result of this transaction same as the original hash of the transformation you provided? (Please also answer with one uppercase word - yes or no)?",
]

SUMMARY_END_PHRASES = ["When you take the number and ALL the previously asked questions, were all of those questions answered correctly?"]

MODEL = 'gpt-3.5-turbo' # gpt-3.5-turbo, gpt-4o-mini, gpt-4o - https://platform.openai.com/docs/models/gp
#0 - gpt-3.5-turbo
#1 - gpt-4-turbo
#2 - gpt-4o-mini
#3 - gpt-4o-2024-08-06

def run_multiple_conversations(
        n: int = 3,
        folder: str = "conversations",
        runs: int = 5,
        system_phrase_idx: int = 0,
        starter_phrase_idx: int = 0,
        end_phrase_idx: int = 0,
        summary_end_phrase_idx: int = 0
):
    """
    Runs several conversations in a loop, now extended with one
    additional summary-end phrase after the final user 'end' message.

    Also uses the new detect_yes_no() which returns a dictionary
    like {"contains_yes": bool, "contains_no": bool} for each reply.
    """
    os.makedirs(folder, exist_ok=True)

    summary_path = os.path.join(folder, "summary.txt")

    chosen_system_phrase = SYSTEM_PHRASES[system_phrase_idx]
    chosen_starter_phrase = STARTER_PHRASES[starter_phrase_idx]
    chosen_end_phrase = END_PHRASES[end_phrase_idx]
    chosen_summary_end_phrase = SUMMARY_END_PHRASES[summary_end_phrase_idx]

    for i in range(runs):
        messages = []
        picked_indices = []

        # 1) Add system message
        messages.append({"role": "system", "content": chosen_system_phrase})
        picked_indices.append(system_phrase_idx)

        # 2) Add starter user message
        messages.append({"role": "user", "content": chosen_starter_phrase})
        picked_indices.append(starter_phrase_idx)

        # 3) Get the FIRST assistant reply (after the starter phrase)
        response = client.chat.completions.create(
            model=MODEL,
            messages=messages
        )
        first_assistant_reply = response.choices[0].message.content
        messages.append({"role": "assistant", "content": first_assistant_reply})

        # 4) For n steps, alternate user & assistant
        for step in range(n):
            cont_phrase_index = random.randrange(len(CONTINUOUS_PHRASES))
            next_user_content = CONTINUOUS_PHRASES[cont_phrase_index]
            picked_indices.append(cont_phrase_index)

            # Add user message
            messages.append({"role": "user", "content": next_user_content})

            # Get assistant reply
            response = client.chat.completions.create(
                model=MODEL,
                messages=messages
            )
            assistant_reply = response.choices[0].message.content
            messages.append({"role": "assistant", "content": assistant_reply})

        # 5) Add the end phrase (user), get the final assistant reply
        messages.append({"role": "user", "content": chosen_end_phrase})
        picked_indices.append(end_phrase_idx)

        response = client.chat.completions.create(
            model=MODEL,
            messages=messages
        )
        final_assistant_reply = response.choices[0].message.content
        messages.append({"role": "assistant", "content": final_assistant_reply})

        # Detect yes/no in final assistant reply
        final_detection_dict = detect_yes_no(final_assistant_reply)

        # 6) Add the summary-end phrase (user), get summary assistant reply
        messages.append({"role": "user", "content": chosen_summary_end_phrase})
        picked_indices.append(summary_end_phrase_idx)

        response = client.chat.completions.create(
            model=MODEL,
            messages=messages
        )
        summary_assistant_reply = response.choices[0].message.content
        messages.append({"role": "assistant", "content": summary_assistant_reply})

        # Detect yes/no in summary assistant reply
        summary_detection_dict = detect_yes_no(summary_assistant_reply)

        # 7) Save conversation record
        conversation_record = {
            "run_index": i,
            "timestamp": datetime.datetime.now().isoformat(),
            "messages": messages
        }

        conversation_filename = os.path.join(folder, f"conversation_{i}.json")
        with open(conversation_filename, 'w', encoding='utf-8') as f:
            json.dump(conversation_record, f, indent=2, ensure_ascii=False)

        # 8) Convert detection dicts into your custom naming scheme
        # final assistant reply detection
        final_dict = {
            "number_yes": final_detection_dict["contains_yes"],
            "numbe_no": final_detection_dict["contains_no"]
        }
        # summary assistant reply detection
        summary_dict = {
            "answers_yes": summary_detection_dict["contains_yes"],
            "answers_no": summary_detection_dict["contains_no"]
        }

        # 9) Build your final summary line
        # Example: [gpt-3.5-turbo, {"number_yes": true, "numbe_no": false}, {"answers_yes": true, "answers_no": false}]
        summary_line = (
            f"[{MODEL}, {json.dumps(final_dict)}, {json.dumps(summary_dict)}]\n"
        )

        # 10) Append to summary file
        with open(summary_path, 'a', encoding='utf-8') as f:
            f.write(summary_line)

        print(f"[Run {i}] Conversation saved to {conversation_filename}")
        print(f"[Run {i}] Summary appended to {summary_path}")

def detect_yes_no(input_string: str) -> dict:
    """
    Parses the given string (case-insensitive) and returns a dictionary indicating
    whether 'YES' or 'NO' is present as a standalone word.
    Example return: {"contains_yes": True, "contains_no": False}
    """
    # Compile a regex pattern to match 'YES' or 'NO' as separate words, case-insensitive
    pattern = re.compile(r"\b(YES|NO)\b", re.IGNORECASE)

    # Find all matches in the input string
    matches = pattern.findall(input_string)

    # Convert all found matches to uppercase for a simple comparison
    matches_upper = [match.upper() for match in matches]

    return {
        "contains_yes": "YES" in matches_upper,
        "contains_no": "NO" in matches_upper
    }

def run_experiments(
        critical_step: int,
        index_start: int,
        index_end: int
):
    """
    Runs multiple conversations in two nested loops:
      - Outer loop: system_phrase_idx and starter_phrase_idx both range from index_start to index_end.
      - Inner loop: n ranges from 1 to critical_step.

    :param critical_step: The maximum value of n for the inner loop.
    :param index_start: The starting index for both system_phrase_idx and starter_phrase_idx.
    :param index_end: The ending index (inclusive) for both system_phrase_idx and starter_phrase_idx.
    :param runs: Number of runs to pass into run_multiple_conversations.
    """
    for idx in range(index_start, index_end + 1):
        # Here, system_phrase_idx and starter_phrase_idx are the same (both = idx).
        for n_value in range(10, critical_step + 1):
            folder_name = f"gpt-0_test_{idx}_{idx}_{n_value}"
            run_multiple_conversations(
                n=n_value,
                folder=folder_name,
                runs=30,
                system_phrase_idx=idx,
                starter_phrase_idx=idx,
            )

# Example usage:
if __name__ == "__main__":
    # This will run with idx = 1..5 for system_phrase_idx/starter_phrase_idx,
    # and for each idx it runs n=1..5 (total 5x5=25 loops).
    run_experiments(
        critical_step=12,
        index_start=0,
        index_end=6,
    )
