from typing import Sequence

import requests

from loguru import logger


def upsert_anki_deck(
    deck_name: str,
    words: list[dict] = {},  # front, back, tags, pronunciation
    remove_others: bool = False,
    reset_updated: bool = True,
    allow_duplicates: bool = True,
):
    base_url = "http://localhost:8765"

    def send_request(action, params):
        request = {"action": action, "version": 6, "params": params}
        response = requests.post(base_url, json=request).json()
        if len(response) != 2:
            raise Exception("Unexpected number of fields in response")
        if "error" not in response:
            raise Exception("Response is missing required error field")
        if "result" not in response:
            raise Exception("Response is missing required result field")
        if response["error"] is not None:
            raise Exception(response["error"])
        return response["result"]

    def create_deck(deck_name):
        send_request("createDeck", {"deck": deck_name})

    def delete_deck(deck_name):
        send_request("deleteDecks", {"decks": [deck_name], "cardsToo": True})

    def find_notes(query):
        return send_request("findNotes", {"query": query})

    def get_notes_info(note_ids):
        return send_request("notesInfo", {"notes": note_ids})

    def add_notes(notes):
        return send_request("addNotes", {"notes": notes})

    def update_note(note_id, fields):
        send_request("updateNoteFields", {"note": {"id": note_id, "fields": fields}})

    def delete_notes(note_ids):
        send_request("deleteNotes", {"notes": note_ids})

    def reset_cards(card_ids):
        send_request("relearnCards", {"cards": card_ids})

    if not words:
        delete_deck(deck_name)
        logger.debug(f"Deck '{deck_name}' deleted as no words were specified.")
        return

    create_deck(deck_name)

    existing_deck_notes = find_notes(f"deck:{deck_name}")
    existing_deck_notes_info = get_notes_info(existing_deck_notes) if existing_deck_notes else []

    existing_deck_notes_dict = {note["fields"]["Back"]["value"]: note for note in existing_deck_notes_info}

    # Update existing notes and add new ones
    notes_to_add = []
    cards_to_reset = []
    for word in words:
        if word["back"] in existing_deck_notes_dict:
            # - Get current

            current_note = {
                key.lower(): existing_deck_notes_dict[word["back"]]["fields"][key]["value"]
                for key in ["Front", "Back", "Pronunciation", "Comment"]
            }
            note_id = existing_deck_notes_dict[word["back"]]["noteId"]

            # - Update if needed

            if current_note != word:
                update_note(
                    note_id,
                    {
                        "Front": word["front"],
                        "Back": word["back"],
                        "Pronunciation": word["pronunciation"],
                        "Comment": word["comment"],
                    },
                )

            # - Reset cards (deprecated)

            # cards_to_reset.append(note_id)
        else:
            note = {
                "deckName": deck_name,
                "modelName": "Basic",
                "fields": {
                    "Front": word["front"],
                    "Back": word["back"],
                    "Pronunciation": word["pronunciation"],
                    "Comment": word["comment"],
                },
                "options": {"allowDuplicate": allow_duplicates},
                "tags": word.get("tags", []),
            }
            notes_to_add.append(note)

    if notes_to_add:
        add_notes(notes_to_add)

    if reset_updated and cards_to_reset:
        reset_cards([note["noteId"] for note in existing_deck_notes_info if note["noteId"] in cards_to_reset])

    # - Remove missing words
    if remove_others:
        notes_to_delete = [
            note["noteId"]
            for back, note in existing_deck_notes_dict.items()
            if back not in [word["back"] for word in words]
        ]
        if notes_to_delete:
            delete_notes(notes_to_delete)

    logger.debug("Upsert operation completed successfully!")


def test():
    upsert_anki_deck(
        deck_name="Default::Sure?::Vocabulary",
        words=[{"front": "test", "back": "test updated 4", "pronunciation": "test", "tags": ["test"]}],
        remove_others=True,
    )


if __name__ == "__main__":
    test()
