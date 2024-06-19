import tkinter as tk
from tkinter import Listbox, Label, END
import pandas as pd
from collections import defaultdict
import re
import Levenshtein as lev


def load_data(file_path1):
    data1 = pd.read_excel(file_path1)
    # Load data from the specified sheet and only the 'Question' and 'Answer' columns
    #data2 = pd.read_excel(file_path2, usecols=['Question', 'Answer'])
    return pd.concat([data1], ignore_index=True)


def preprocess(text):
    # Updated preprocessing to be more efficient and clear
    return re.sub(r'[^\w\s]', '', text).strip().lower()


def extract_words(data):
    combined_text = ' '.join(data['q'].astype(str)) + ' ' + ' '.join(data['a'].astype(str))
    words = set(preprocess(combined_text).split())
    return words


def create_frequency_dict(data):
    # Use a defaultdict to count occurrences of full questions
    freq_dict = defaultdict(int)
    for entry in data['q']:
        processed_entry = preprocess(entry)
        freq_dict[processed_entry] += 1
    return freq_dict


def autocomplete(input_text, freq_dict):
    # Normalize the input text
    input_text = preprocess(input_text)
    print(f"Autocomplete input_text: {input_text}")
    
    # Find all entries that start with the input text
    suggestions = {phrase: count for phrase, count in freq_dict.items() if phrase.startswith(input_text)}
    print(f"Suggestions before sorting: {suggestions}")
    
    sorted_suggestions = dict(sorted(suggestions.items(), key=lambda item: item[1], reverse=True))
    print(f"Suggestions after sorting: {sorted_suggestions}")
    
    return sorted_suggestions


def find_closest_questions(input_text, data):
    input_text = preprocess(input_text)
    # Using similarity or direct match to find the closest questions
    data['similarity'] = data['q'].apply(lambda question: -lev.distance(preprocess(question), input_text))
    closest_matches = data.sort_values(by='similarity', ascending=False).head(10)
    return closest_matches[['q', 'a']]


class ArabicSpellChecker:
    def __init__(self, dictionary):
        self.dictionary = set(dictionary)

    def is_misspelled(self, word):
        return word not in self.dictionary

    def correct_word(self, word):
        if self.is_misspelled(word):
            return min(self.dictionary, key=lambda x: lev.distance(word, x))
        return word

class AutocompleteApp:
    def __init__(self, freq_dict, dictionary, data):
        self.data = data  # Pass the entire DataFrame
        self.freq_dict = freq_dict
        self.spell_checker = ArabicSpellChecker(dictionary)

    def accept_correction(self, user_input):
        if user_input.startswith("Did you mean:"):
            corrected_text = user_input.split(": ", 1)[1]
            corrected_text = corrected_text[:-1]
            return corrected_text
        return user_input

    def submit_query(self, user_input):
        if user_input.strip() == "":
            return {"message": "Please enter a question."}

        suggestions = find_closest_questions(user_input, self.data)
        if suggestions.empty:
            return {"message": "No matching question found."}
        else:
            first_match = suggestions.iloc[0]
            return {
                "best_match": first_match['q'],
                "answer": first_match['a'],
                "matches": suggestions.to_dict(orient='records')
            }

    def on_listbox_select(self, selected_text):
        return selected_text

    def handle_key_release(self, user_input):
        if user_input.endswith(' '):
            return self.suggest_correction(user_input)
        return self.get_suggestions(user_input)

    def get_suggestions(self, user_input):
        text = user_input.strip()
        if text and text[-1] != ' ':
            words = text.split()
            corrected_words = []
            for word in words:
                if self.spell_checker.is_misspelled(word):
                    corrected_words.append(self.spell_checker.correct_word(word))
                else:
                    corrected_words.append(word)

            corrected_text = ' '.join(corrected_words)
            suggestions = autocomplete(corrected_text, self.freq_dict)
            print(f"Suggestions from first autocomplete: {suggestions}")

            corrected_words[-1] = words[-1]
            corrected_text = ' '.join(corrected_words)
            suggestions2 = autocomplete(corrected_text, self.freq_dict)
            print(f"Suggestions from second autocomplete: {suggestions2}")

            combined_suggestions = {**suggestions, **suggestions2}
            final_suggestions = list(combined_suggestions.keys())[:10]
            print(f"Final combined suggestions: {final_suggestions}")
            return final_suggestions
        return []

    def suggest_correction(self, user_input):
        text = user_input.strip()
        if not text:
            return {}

        words = text.split()
        corrected_words = []
        corrections_made = False
        for word in words:
            if self.spell_checker.is_misspelled(word):
                corrected_word = self.spell_checker.correct_word(word)
                corrected_words.append(corrected_word)
                if corrected_word != word:
                    corrections_made = True
            else:
                corrected_words.append(word)

        corrected_text = ' '.join(corrected_words)
        if corrections_made:
            return {"suggestion": f"Did you mean: {corrected_text}?"}
        else:
            return {}














'''class AutocompleteApp:
    def __init__(self, master, freq_dict, dictionary, data):
        self.master = master
        self.data = data  # Pass the entire DataFrame

        self.freq_dict = freq_dict
        self.spell_checker = ArabicSpellChecker(dictionary)
        master.title("Autocomplete and Suggestion Interface")

        self.entry = tk.Entry(master, width=50)
        self.entry.pack()

        self.submit_button = tk.Button(master, text="Submit", command=self.submit_query)
        self.submit_button.pack()

        self.entry.bind('<KeyRelease>', self.handle_key_release)

        self.listbox = Listbox(master, width=100, height=10)
        self.listbox.pack()

        self.suggestion_label = Label(master, text="", fg="blue")
        self.suggestion_label.pack()

        self.listbox.bind('<<ListboxSelect>>', self.on_listbox_select)

        self.entry.bind('<Return>', self.accept_correction)

    def accept_correction(self, event):
        if self.suggestion_label.cget("text").startswith("Did you mean:"):
            corrected_text = self.suggestion_label.cget("text").split(": ", 1)[1]
            corrected_text = corrected_text[:-1]
            self.entry.delete(0, END)
            self.entry.insert(0, corrected_text)
            self.suggestion_label.config(text="")

    def submit_query(self):
        user_input = self.entry.get()
        if user_input.strip() == "":
            self.suggestion_label.config(text="Please enter a question.")
            return

        suggestions = find_closest_questions(user_input, self.data)
        if suggestions.empty:
            self.suggestion_label.config(text="No matching question found.")
        else:
            first_match = suggestions.iloc[0]
            self.suggestion_label.config(text=f"Best match: {first_match['Question']}\nAnswer: {first_match['Answer']}")
            # Optionally update the listbox with other matches
            self.listbox.delete(0, END)
            for _, row in suggestions.iterrows():
                self.listbox.insert(END, f"{row['Question']}")

    def on_listbox_select(self, event):
        # Get the line index of the selection
        if self.listbox.curselection():
            index = self.listbox.curselection()[0]
            selected_text = self.listbox.get(index)
            self.entry.delete(0, END)
            self.entry.insert(0, selected_text)

    def handle_key_release(self, event):
        if event.char == ' ':  # Check if the last character entered is a space
            self.suggest_correction()
        self.get_suggestions()

    def get_suggestions(self):
        text = self.entry.get().strip()
        if text and text[-1] != ' ':  # Fetch suggestions only if the last character is not a space
            words = text.split()
            corrected_words = []
            for word in words:
                if self.spell_checker.is_misspelled(word):
                    corrected_words.append(self.spell_checker.correct_word(word))
                else:
                    corrected_words.append(word)

            corrected_text = ' '.join(corrected_words)
            suggestions = autocomplete(corrected_text, self.freq_dict)

            # ignore last word mis-spelling (maybe the user is still typing)
            corrected_words[-1] = words[-1]
            corrected_text = ' '.join(corrected_words)
            suggestions2 = autocomplete(corrected_text, self.freq_dict)

            suggestions = {**suggestions, **suggestions2}

            self.listbox.delete(0, END)
            for suggestion in list(suggestions.keys())[:10]:  # Limit to top 10 suggestions
                self.listbox.insert(END, suggestion)

    def suggest_correction(self):
        text = self.entry.get().strip()
        if not text:
            return

        words = text.split()
        corrected_words = []
        corrections_made = False
        for word in words:
            if self.spell_checker.is_misspelled(word):
                corrected_word = self.spell_checker.correct_word(word)
                corrected_words.append(corrected_word)
                if corrected_word != word:
                    corrections_made = True
            else:
                corrected_words.append(word)

        corrected_text = ' '.join(corrected_words)
        if corrections_made:
            self.suggestion_label.config(text=f"Did you mean: {corrected_text}?")
        else:
            self.suggestion_label.config(text="")
'''