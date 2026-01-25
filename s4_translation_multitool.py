#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Settlers IV translation multitool
by Pawel C. (PaweX 3)

all rights reserved
"""

import re
from pathlib import Path
import shutil
import sys
import difflib  # Dodano brakujący import dla difflib (używany w similarity_percent)

# --- ustawienia i mapa języków (pierwsze kodowanie to domyślne/sugerowane) ---
TEXT_HEADER_RE = re.compile(r'\s*##\s*Text\s+(\d+)\s*##')
LANG_MAP = {
    0:  ("ENGLISH",   ["cp1252", "iso-8859-1", "latin1", "ascii", "cp437", "cp850"]),
    1:  ("GERMAN",    ["cp1252", "iso-8859-1", "iso-8859-15", "cp850"]),
    2:  ("FRENCH",    ["cp1252", "iso-8859-1", "iso-8859-15", "cp850"]),
    3:  ("SPANISH",   ["cp1252", "iso-8859-1", "iso-8859-15", "cp850"]),
    4:  ("ITALIAN",   ["cp1252", "iso-8859-1", "iso-8859-15", "cp850"]),
    5:  ("POLISH",    ["cp1250", "iso-8859-2", "latin2", "cp852"]),
    6:  ("KOREAN",    ["cp949", "euc-kr", "ks_c_5601-1987"]),
    7:  ("CHINESE",   ["gbk", "cp950", "big5", "big5hkscs"]),
    8:  ("SWEDISH",   ["cp1252", "iso-8859-1", "iso-8859-15", "cp850"]),
    9:  ("DANISH",    ["cp1252", "iso-8859-1", "iso-8859-15", "cp850"]),
    10: ("NORWEGIAN", ["cp1252", "iso-8859-1", "iso-8859-15", "cp850"]),
    11: ("HUNGARIAN", ["cp1250", "iso-8859-2", "latin2", "cp852"]),
    12: ("HEBREW",    ["cp1255", "iso-8859-8", "cp862"]),
    13: ("CZECH",     ["cp1250", "iso-8859-2", "latin2", "cp852"]),
    14: ("FINNISH",   ["cp1252", "iso-8859-1", "iso-8859-15", "cp850"]),
    16: ("RUSSIAN",   ["cp1251", "koi8-r", "iso-8859-5", "cp866"]),
    17: ("THAI",      ["cp874", "iso-8859-11", "tis-620"]),
    18: ("JAPANESE",  ["cp932", "shift_jis", "euc-jp", "iso-2022-jp"]),
}

# --- Słownik tłumaczeń dla komunikatów (dodano do obsługi wielojęzyczności) ---
# Klucze: unikalne identyfikatory komunikatów. Wartości: dict z 'pl' i 'en'.
TRANSLATIONS = {
    'choose_lang': {
        'pl': "Wybierz język programu: 1) Polski, 2) English [2]: ",
        'en': "Choose program language: 1) Polish, 2) English [2]: "
    },
    'invalid_choice': {
        'pl': "Nieprawidłowy wybór. Spróbuj ponownie.",
        'en': "Invalid choice. Try again."
    },
    'main_menu_title': {
        'pl': "\n=== Settlers IV translation tool (menu) ===",
        'en': "\n=== Settlers IV translation tool (menu) ==="
    },
    'main_menu_options': {
        'pl': """Wybierz opcję:
  1) Porównaj pliki projektu A vs B i wygeneruj missingtexts.txt (teksty z B brakujące/wymagające uzupełnienia w A)
  2) Połącz pliki projektu (merge): podmień istniejące i dopisz brakujące z B do A
  3) Import z pliku s4_texts.dat<nr> → wygeneruj <LANG>.s4_translation_project
  4) Eksport pliku .s4_translation_project → s4_texts.dat<nr>
  5) Podgląd tekstów z pliku .dat (interaktywne testowanie kodowań)
  6) Przesuń numery tekstów w pliku projektu A (offset)
  7) Napraw brakujące wpisy w pliku projektu
  8) Dopasuj numery tekstów w pliku projektu A do B (align A ← B)
  9) Wyjście""",
        'en': """Choose an option:
  1) Compare A vs B project files and generate missingtexts.txt (texts from B missing/requiring completion in A)
  2) Merge project files: replace existing and append missing from B to A
  3) Import from s4_texts.dat<nr> → generate <LANG>.s4_translation_project
  4) Export .s4_translation_project → s4_texts.dat<nr>
  5) Preview texts from .dat file (interactive encoding testing)
  6) Shift text numbers in project file A (offset)
  7) Fix missing entries in project file
  8) Align text numbers in project file A to B (align A ← B)
  9) Exit"""
    },
    'main_menu_prompt': {
        'pl': "Wybierz 1, 2, 3, 4, 5, 6, 7, 8 lub 9 [9]: ",
        'en': "Choose 1, 2, 3, 4, 5, 6, 7, 8 or 9 [9]: "
    },
    'exit_message': {
        'pl': "Koniec.",
        'en': "Exit."
    },
    'press_enter_to_exit': {
        'pl': "\nNaciśnij Enter, aby zakończyć...",
        'en': "\nPress Enter to exit..."
    },
    'path_a_prompt': {
        'pl': "Podaj ścieżkę do pliku A (bazowy): ",
        'en': "Enter path to file A (base): "
    },
    'path_b_prompt': {
        'pl': "Podaj ścieżkę do pliku B (referencyjny): ",
        'en': "Enter path to file B (reference): "
    },
    'required_paths': {
        'pl': "Plik A i B są wymagane dla tej opcji. Powrót do menu.",
        'en': "Files A and B are required for this option. Back to menu."
    },
    'invalid_path': {
        'pl': "Nieprawidłowa ścieżka: {}",
        'en': "Invalid path: {}"
    },
    'file_not_exists': {
        'pl': "Plik {} nie istnieje: {}",
        'en': "File {} does not exist: {}"
    },
    'encoding_prompt': {
        'pl': "Kodowanie plików (domyślnie utf-8): ",
        'en': "File encoding (default utf-8): "
    },
    'out_name_prompt': {
        'pl': "Nazwa pliku wynikowego [missingtexts.txt]: ",
        'en': "Output file name [missingtexts.txt]: "
    },
    'missingtexts_saved': {
        'pl': "Zapisano plik z brakującymi tekstami: {}",
        'en': "Saved missing texts file: {}"
    },
    'missing_blocks_count': {
        'pl': "Liczba brakujących bloków: {}. Numery: {}",
        'en': "Number of missing blocks: {}. Numbers: {}"
    },
    'no_missing_blocks': {
        'pl': "Brak brakujących bloków (nic do dopisania).",
        'en': "No missing blocks (nothing to add)."
    },
    'no_missingtexts_saved': {
        'pl': "Brak zapisanego pliku missingtexts.",
        'en': "No missingtexts file saved."
    },
    'summary_changes': {
        'pl': "\nPodsumowanie zmian:",
        'en': "\nSummary of changes:"
    },
    'replaced_numbers': {
        'pl': "  Podmienione numery (z pliku B): {}",
        'en': "  Replaced numbers (from file B): {}"
    },
    'no_replacements': {
        'pl': "  Brak podmian (żaden numer z B nie występował w A).",
        'en': "  No replacements (no number from B occurred in A)."
    },
    'added_numbers': {
        'pl': "  Dodane numery (dopisane na końcu): {}",
        'en': "  Added numbers (appended at the end): {}"
    },
    'no_added': {
        'pl': "  Brak nowych numerów do dodania.",
        'en': "  No new numbers to add."
    },
    'save_method': {
        'pl': "\nWybierz sposób zapisu:",
        'en': "\nChoose save method:"
    },
    'overwrite_a': {
        'pl': "  1) Nadpisać plik A (zrobiona zostanie kopia zapasowa)",
        'en': "  1) Overwrite file A (backup will be created)"
    },
    'save_new': {
        'pl': "  2) Zapisz jako nowy plik (ten sam katalog co A, nazwa + _updated)",
        'en': "  2) Save as new file (same directory as A, name + _updated)"
    },
    'choose_1_or_2': {
        'pl': "Wybierz 1 lub 2 [1]: ",
        'en': "Choose 1 or 2 [1]: "
    },
    'backup_created': {
        'pl': "Utworzono kopię zapasową: {}",
        'en': "Backup created: {}"
    },
    'backup_failed': {
        'pl': "Nie udało się utworzyć kopii zapasowej: {}",
        'en': "Failed to create backup: {}"
    },
    'continue_without_backup': {
        'pl': "Kontynuować bez kopii zapasowej?",
        'en': "Continue without backup?"
    },
    'canceled': {
        'pl': "Anulowano.",
        'en': "Canceled."
    },
    'overwritten_a': {
        'pl': "Nadpisano plik A: {}",
        'en': "Overwritten file A: {}"
    },
    'write_error': {
        'pl': "Błąd zapisu: {}",
        'en': "Write error: {}"
    },
    'out_path_prompt': {
        'pl': "Podaj ścieżkę wyjściową [{}]: ",
        'en': "Enter output path [{}]: "
    },
    'dir_create_failed': {
        'pl': "Nie udało się utworzyć katalogu {}: {}",
        'en': "Failed to create directory {}: {}"
    },
    'file_exists_overwrite': {
        'pl': "Plik {} już istnieje. Nadpisać?",
        'en': "File {} already exists. Overwrite?"
    },
    'saved_to': {
        'pl': "Zapisano wynik do: {}",
        'en': "Saved result to: {}"
    },
    'invalid_save_choice': {
        'pl': "Nieprawidłowy wybór. Kończę bez zapisu.",
        'en': "Invalid choice. Ending without saving."
    },
    'path_dat_prompt': {
        'pl': "Podaj ścieżkę do pliku s4_texts.dat<nr>: ",
        'en': "Enter path to s4_texts.dat<nr>: "
    },
    'path_required': {
        'pl': "Ścieżka do pliku .dat wymagana. Powrót do menu.",
        'en': "Path to .dat file required. Back to menu."
    },
    'lang_num_from_name': {
        'pl': "Znaleziono numer języka w nazwie pliku: {} (sugestia).",
        'en': "Found language number in file name: {} (suggestion)."
    },
    'lang_num_prompt': {
        'pl': "Podaj numer języka (np. 5 dla POLISH). Sugestia: {}: ",
        'en': "Enter language number (e.g. 5 for POLISH). Suggestion: {}: "
    },
    'invalid_number': {
        'pl': "Nieprawidłowy numer. Podaj liczbę całkowitą (np. 5).",
        'en': "Invalid number. Enter an integer (e.g. 5)."
    },
    'selected_lang': {
        'pl': "Wybrany język: {} (numer {}), sugerowane kodowania (pierwsze domyślne): {}",
        'en': "Selected language: {} (number {}), suggested encodings (first default): {}"
    },
    'use_suggested_enc': {
        'pl': "Użyć sugerowanego kodowania '{}'? [Y/n]: ",
        'en': "Use suggested encoding '{}'? [Y/n]: "
    },
    'enc_input_prompt': {
        'pl': "Podaj kodowanie wejściowe (np. big5, cp950, utf-8, cp1251): ",
        'en': "Enter input encoding (e.g. big5, cp950, utf-8, cp1251): "
    },
    'dat_read_error': {
        'pl': "Błąd odczytu pliku .dat: {}",
        'en': "Error reading .dat file: {}"
    },
    'project_saved': {
        'pl': "Zapisano plik projektu: {} (kodowanie wyjściowe: {})",
        'en': "Saved project file: {} (output encoding: {})"
    },
    'project_write_error': {
        'pl': "Błąd zapisu pliku projektu: {}",
        'en': "Error writing project file: {}"
    },
    'project_path_prompt': {
        'pl': "Podaj ścieżkę do pliku .s4_translation_project: ",
        'en': "Enter path to .s4_translation_project file: "
    },
    'project_path_required': {
        'pl': "Ścieżka do pliku projektu wymagana. Powrót do menu.",
        'en': "Path to project file required. Back to menu."
    },
    'project_read_error': {
        'pl': "Błąd odczytu pliku projektu: {}",
        'en': "Error reading project file: {}"
    },
    'header_not_found': {
        'pl': "Nie znaleziono nagłówka 4 bajtów w pliku projektu.",
        'en': "Header 4 bytes not found in project file."
    },
    'header_prompt': {
        'pl': "Podaj 4 liczby (0-255) oddzielone spacjami jako nagłówek (np. '1 2 3 4'): ",
        'en': "Enter 4 numbers (0-255) separated by spaces as header (e.g. '1 2 3 4'): "
    },
    'exactly_4_numbers': {
        'pl': "Podaj dokładnie 4 liczby.",
        'en': "Enter exactly 4 numbers."
    },
    'numbers_0_255': {
        'pl': "Liczby muszą być w zakresie 0-255.",
        'en': "Numbers must be in range 0-255."
    },
    'invalid_numbers': {
        'pl': "Nieprawidłowe liczby. Spróbuj ponownie.",
        'en': "Invalid numbers. Try again."
    },
    'available_langs': {
        'pl': "\nDostępne języki (numer : nazwa):",
        'en': "\nAvailable languages (number : name):"
    },
    'lang_suggestion': {
        'pl': "\nSugestia na podstawie nazwy pliku: {} ({})",
        'en': "\nSuggestion based on file name: {} ({})"
    },
    'lang_num_save_prompt': {
        'pl': "Podaj numer języka do zapisu (np. 5 dla POLISH) [{}]: ",
        'en': "Enter language number for save (e.g. 5 for POLISH) [{}]: "
    },
    'unknown_lang_num': {
        'pl': "Nieznany numer języka. Spróbuj ponownie.",
        'en': "Unknown language number. Try again."
    },
    'selected_lang_save': {
        'pl': "Wybrany język: {} (numer {}). Sugerowane kodowania (pierwsze domyślne): {}",
        'en': "Selected language: {} (number {}). Suggested encodings (first default): {}"
    },
    'use_suggested_enc_out': {
        'pl': "Użyć sugerowanego kodowania '{}'? [Y/n]: ",
        'en': "Use suggested encoding '{}'? [Y/n]: "
    },
    'custom_enc_prompt': {
        'pl': "Podaj kodowanie wyjściowe (np. cp1250, cp950, cp932, cp1251) lub naciśnij Enter aby użyć sugerowanego: ",
        'en': "Enter output encoding (e.g. cp1250, cp950, cp932, cp1251) or press Enter to use suggested: "
    },
    'no_blocks': {
        'pl': "Plik projektu nie zawiera żadnych bloków tekstowych. Anulowano.",
        'en': "Project file contains no text blocks. Canceled."
    },
    'save_texts_from_to': {
        'pl': "Zapiszę wszystkie teksty od 1 do {} (ostatni numer: {}).",
        'en': "Will save all texts from 1 to {} (last number: {})."
    },
    'out_file_prompt': {
        'pl': "Plik wyjściowy [{}]: ",
        'en': "Output file [{}]: "
    },
    'save_as_alt': {
        'pl': "Zapisz jako: {}",
        'en': "Save as: {}"
    },
    'confirm_save_as': {
        'pl': "Zapisz jako {}?",
        'en': "Save as {}?"
    },
    'dat_saved': {
        'pl': "\nZapisano plik .dat: {}",
        'en': "\nSaved .dat file: {}"
    },
    'last_text_num': {
        'pl': "Ostatni zapisany numer tekstu: {}",
        'en': "Last saved text number: {}"
    },
    'texts_count': {
        'pl': "Liczba tekstów zapisanych: {}. Pustych (length=0): {}. Kodowanie: {}",
        'en': "Number of texts saved: {}. Empty (length=0): {}. Encoding: {}"
    },
    'dat_write_error': {
        'pl': "Błąd zapisu pliku .dat: {}",
        'en': "Error writing .dat file: {}"
    },
    'path_dat_preview_prompt': {
        'pl': "Podaj ścieżkę do pliku s4_texts.dat<nr> do podglądu: ",
        'en': "Enter path to s4_texts.dat<nr> for preview: "
    },
    'texts_count_dat': {
        'pl': "Plik zawiera {} tekstów.",
        'en': "File contains {} texts."
    },
    'range_prompt': {
        'pl': "Podaj numer tekstu (np. 57), przedział (np. 60-200), 'all' aby wypisać wszystko, lub 'single' aby podać pojedynczy numer do testu wszystkich kodowań: ",
        'en': "Enter text number (e.g. 57), range (e.g. 60-200), 'all' to print everything, or 'single' to enter single number for all encodings test: "
    },
    'single_text_prompt': {
        'pl': "Podaj numer pojedynczego tekstu do testu wszystkich kodowań: ",
        'en': "Enter single text number for all encodings test: "
    },
    'out_of_range': {
        'pl': "Numer poza zakresem. Spróbuj ponownie.",
        'en': "Number out of range. Try again."
    },
    'invalid_range': {
        'pl': "Nieprawidłowy przedział. Spróbuj ponownie.",
        'en': "Invalid range. Try again."
    },
    'invalid_format': {
        'pl': "Nieprawidłowy format. Użyj np. 60-200.",
        'en': "Invalid format. Use e.g. 60-200."
    },
    'suggested_encs': {
        'pl': "\nSugerowane kodowania (pierwsze domyślne):",
        'en': "\nSuggested encodings (first default):"
    },
    'custom_enc': {
        'pl': "  a) wpisz własne kodowanie (np. big5, cp950, utf-8)",
        'en': "  a) enter custom encoding (e.g. big5, cp950, utf-8)"
    },
    'back_to_menu': {
        'pl': "  m) wróć do menu",
        'en': "  m) back to menu"
    },
    'choose_enc_prompt': {
        'pl': "Wybierz kodowanie do testu (domyślne '{}'): ",
        'en': "Choose encoding to test (default '{}'): "
    },
    'invalid_enc_choice': {
        'pl': "Nieprawidłowy wybór numeru kodowania.",
        'en': "Invalid encoding number choice."
    },
    'custom_enc_prompt_preview': {
        'pl': "Podaj nazwę kodowania (np. big5, cp950, utf-8): ",
        'en': "Enter encoding name (e.g. big5, cp950, utf-8): "
    },
    'test_another_enc': {
        'pl': "Sprawdzić inne kodowanie dla tego zakresu? [Y/n]: ",
        'en': "Test another encoding for this range? [Y/n]: "
    },
    'save_test_prompt': {
        'pl': "Czy zapisać wynik testu do pliku {}_encoding_test.txt? [y/N]: ",
        'en': "Save test result to file {}_encoding_test.txt? [y/N]: "
    },
    'test_saved': {
        'pl': "Zapisano test kodowań do: {}",
        'en': "Saved encoding test to: {}"
    },
    'test_save_error': {
        'pl': "Błąd zapisu testu: {}",
        'en': "Error saving test: {}"
    },
    'test_not_saved': {
        'pl': "Test nie został zapisany.",
        'en': "Test not saved."
    },
    'back_to_menu_msg': {
        'pl': "Powrót do menu.",
        'en': "Back to menu."
    },
    'end_all_enc_test': {
        'pl': "\nKoniec testu wszystkich kodowań. Powrót do menu.",
        'en': "\nEnd of all encodings test. Back to menu."
    },
    'path_a_shift_prompt': {
        'pl': "Podaj ścieżkę do pliku A (oryginał): ",
        'en': "Enter path to file A (original): "
    },
    'no_blocks_found': {
        'pl': "Nie znaleziono żadnych bloków '## Text N ##' w pliku A. Nic do przesunięcia.",
        'en': "No '## Text N ##' blocks found in file A. Nothing to shift."
    },
    'blocks_found': {
        'pl': "Znaleziono {} bloków. Pierwszy numer: {}, ostatni numer: {}.",
        'en': "Found {} blocks. First number: {}, last number: {}."
    },
    'offset_prompt': {
        'pl': "Podaj offset (liczba całkowita, 0 = anuluj): ",
        'en': "Enter offset (integer, 0 = cancel): "
    },
    'no_value_canceled': {
        'pl': "Brak wartości. Anulowano.",
        'en': "No value. Canceled."
    },
    'invalid_integer': {
        'pl': "Proszę podać liczbę całkowitą (może być ujemna).",
        'en': "Please enter an integer (can be negative)."
    },
    'offset_zero': {
        'pl': "Offset = 0 — brak działania. Anulowano.",
        'en': "Offset = 0 — no action. Canceled."
    },
    'negative_ids_error': {
        'pl': "Błąd: po przesunięciu niektóre numery byłyby mniejsze lub równe 0. Wybierz inny offset.",
        'en': "Error: after shift, some numbers would be <= 0. Choose another offset."
    },
    'duplicates_error': {
        'pl': "Błąd: po przesunięciu wystąpiły duplikaty numerów. Anulowano.",
        'en': "Error: after shift, duplicate numbers occurred. Canceled."
    },
    'save_shift_method': {
        'pl': "\nWybierz sposób zapisu przesuniętego pliku:",
        'en': "\nChoose save method for shifted file:"
    },
    'overwrite_a_shift': {
        'pl': "  1) Nadpisać plik A (zrobiona zostanie kopia zapasowa)",
        'en': "  1) Overwrite file A (backup will be created)"
    },
    'save_new_shift': {
        'pl': "  2) Zapisz jako nowy plik (ten sam katalog co A, nazwa + _shifted)",
        'en': "  2) Save as new file (same directory as A, name + _shifted)"
    },
    'choose_1_or_2_shift': {
        'pl': "Wybierz 1 lub 2 [2]: ",
        'en': "Choose 1 or 2 [2]: "
    },
    'shifted_saved': {
        'pl': "Zapisano przesunięty plik do: {}",
        'en': "Saved shifted file to: {}"
    },
    'project_path_fix_prompt': {
        'pl': "Podaj ścieżkę do pliku .s4_translation_project: ",
        'en': "Enter path to .s4_translation_project file: "
    },
    'no_path_canceled': {
        'pl': "Brak ścieżki. Powrót do menu.",
        'en': "No path. Back to menu."
    },
    'range_fix_prompt': {
        'pl': "Podaj przedział numerów do uzupełnienia (np. 1-2000) lub pojedynczy numer (np. 57): ",
        'en': "Enter range of numbers to fix (e.g. 1-2000) or single number (e.g. 57): "
    },
    'no_range_canceled': {
        'pl': "Brak przedziału. Anulowano.",
        'en': "No range. Canceled."
    },
    'invalid_range_fix': {
        'pl': "Nieprawidłowy przedział. Spróbuj ponownie.",
        'en': "Invalid range. Try again."
    },
    'num_ge_1': {
        'pl': "Numer musi być >= 1.",
        'en': "Number must be >= 1."
    },
    'no_missing_entries': {
        'pl': "Brak brakujących wpisów w podanym przedziale. Nic do zrobienia.",
        'en': "No missing entries in given range. Nothing to do."
    },
    'missing_found': {
        'pl': "\nZnaleziono {} brakujących wpisów do dodania.",
        'en': "\nFound {} missing entries to add."
    },
    'added_numbers_fix': {
        'pl': "Dodane numery: {}",
        'en': "Added numbers: {}"
    },
    'no_added_unexpected': {
        'pl': "Brak nowych dodanych numerów (coś poszło nieoczekiwanie).",
        'en': "No new added numbers (something unexpected)."
    },
    'overwrite_prompt': {
        'pl': "\nCzy chcesz nadpisać istniejący plik?",
        'en': "\nDo you want to overwrite existing file?"
    },
    'overwritten': {
        'pl': "Nadpisano plik: {}",
        'en': "Overwritten file: {}"
    },
    'save_as_new_prompt': {
        'pl': "Zapisać jako nowy plik: {}?",
        'en': "Save as new file: {}?"
    },
    'new_saved': {
        'pl': "Zapisano nowy plik: {}",
        'en': "Saved new file: {}"
    },
    'save_canceled': {
        'pl': "Anulowano zapis.",
        'en': "Save canceled."
    },
    'files_count': {
        'pl': "Plik A: {}  —  liczba bloków: {}\nPlik B: {}  —  liczba bloków: {}",
        'en': "File A: {}  —  number of blocks: {}\nFile B: {}  —  number of blocks: {}"
    },
    'max_tries_prompt': {
        'pl': "Ile prób przesunięcia w A użyć przy szukaniu znaczącego tekstu? [domyślnie {}]: ",
        'en': "How many shift attempts in A to use when searching for significant text? [default {}]: "
    },
    'new_offset_set': {
        'pl': "\nNowy offset ustawiony: {} (A:{} -> B:{})",
        'en': "\nNew offset set: {} (A:{} -> B:{})"
    },
    'alignment_report': {
        'pl': "\n--- Raport dopasowania (przed zapisem) ---",
        'en': "\n--- Alignment report (before save) ---"
    },
    'matched_pairs_count': {
        'pl': "Liczba dopasowanych par: {}",
        'en': "Number of matched pairs: {}"
    },
    'matched_ranges': {
        'pl': "Dopasowane przedziały (A_start-A_end => B_start-B_end) z offsetem:",
        'en': "Matched ranges (A_start-A_end => B_start-B_end) with offset:"
    },
    'no_matched_ranges': {
        'pl': "  Brak dopasowanych przedziałów.",
        'en': "  No matched ranges."
    },
    'missing_in_b': {
        'pl': "\nTeksty z A nie znalezione w B (pojedyncze numery lub przedziały):",
        'en': "\nTexts from A not found in B (single numbers or ranges):"
    },
    'all_found': {
        'pl': "\nWszystkie teksty A znalezione w B (przynajmniej częściowo).",
        'en': "\nAll A texts found in B (at least partially)."
    },
    'missing_details': {
        'pl': "\nSzczegóły dla tekstów A nieznalezionych bezpośrednio w B (próba porównania z domniemanymi tekstami z B):",
        'en': "\nDetails for A texts not directly found in B (attempt to compare with guessed B texts):"
    },
    'no_offset': {
        'pl': "  A:{} (brak offsetu, nie można wyznaczyć liczby domniemanego tekstu dla B)",
        'en': "  A:{} (no offset, cannot determine guessed text number for B)"
    },
    'no_sim': {
        'pl': "  A:{} (domniemany tekst B: {} — {})",
        'en': "  A:{} (guessed B text: {} — {})"
    },
    'with_sim': {
        'pl': "  A:{} ({}% podobieństwa z tekstem B: {})",
        'en': "  A:{} ({}% similarity with B text: {})"
    },
    'placeholder_cases': {
        'pl': "\nMiejsca gdzie A był pusty/placeholder, a B miał znaczący tekst:",
        'en': "\nPlaces where A was empty/placeholder, but B had significant text:"
    },
    'conflicts': {
        'pl': "\nMiejsca konfliktów (oba znaczące lub zróżnicowane) — pokazuję procent podobieństwa:",
        'en': "\nConflict places (both significant or differentiated) — showing similarity percentage:"
    },
    'offset_history': {
        'pl': "\nHistoria zmian offsetu (offset, A_index, B_index):",
        'en': "\nOffset change history (offset, A_index, B_index):"
    },
    'no_matches': {
        'pl': "\nBrak dopasowań do zapisania. Nic nie zmieniono.",
        'en': "\nNo matches to save. Nothing changed."
    },
    'save_intent': {
        'pl': "\nZamierzam zapisać {} zaktualizowanych wpisów do pliku A.",
        'en': "\nIntending to save {} updated entries to file A."
    },
    'sample_mappings': {
        'pl': "Przykładowe mapowania (A -> B): {}",
        'en': "Sample mappings (A -> B): {}"
    },
    'overwrite_direct': {
        'pl': "Nadpisać plik A bezpośrednio?",
        'en': "Overwrite file A directly?"
    },
    'assigned_by_offset': {
        'pl': "Liczba wpisów przypisanych na podstawie offsetu: {}",
        'en': "Number of entries assigned based on offset: {}"
    },
    'collisions_warning': {
        'pl': "\nUwaga: wykryto kolizje docelowych indeksów (kilka A trafiło na ten sam target).",
        'en': "\nWarning: detected target index collisions (multiple A hit the same target)."
    },
    'last_a_num': {
        'pl': "Ostatni numer A przetworzony: {}",
        'en': "Last A number processed: {}"
    },
    'done': {
        'pl': "Gotowe.",
        'en': "Done."
    },
    # Dodaj brakujące tłumaczenia, jeśli jakieś pominąłem - kod jest elastyczny.
    'yes_no_prompt': {
        'pl': "Proszę odpowiedzieć tak/nie (y/n).",
        'en': "Please answer yes/no (y/n)."
    },
    'canceled_missingtexts': {
        'pl': "Anulowano zapis missingtexts.",
        'en': "Canceled missingtexts save."
    },
    'no_suggestion': {
        'pl': 'brak',
        'en': 'none'
    },
    'canceled_project_save': {
        'pl': "Anulowano zapis pliku projektu.",
        'en': "Canceled project file save."
    },
    'header_found': {
        'pl': "Znaleziono nagłówek w pliku projektu: {}",
        'en': "Found header in project file: {}"
    },
    'testing_single_text': {
        'pl': "Testing single text #{} across encodings\n",
        'en': "Testing single text #{} across encodings\n"
    },
    'canceled_test_save': {
        'pl': "Anulowano zapis testu.",
        'en': "Canceled test save."
    },
    'out_of_range_start': {
        'pl': "Początkowy numer poza zakresem. Spróbuj ponownie.",
        'en': "Starting number out of range. Try again."
    },
    'overwrite_file': {
        'pl': "Nadpisać plik?",
        'en': "Overwrite file?"
    },
    'save_as_new': {
        'pl': "Zapisz jako nowy?",
        'en': "Save as new?"
    },
    'new_offset_note': {
        'pl': "    // nowy offset {}",
        'en': "    // new offset {}"
    },
    'similarity': {
        'pl': "podobieństwo",
        'en': "similarity"
    },
    'offset_set_at': {
        'pl': "  offset {} ustawiony przy A:{} -> B:{}",
        'en': "  offset {} set at A:{} -> B:{}"
    },
    'no_targets': {
        'pl': "Brak docelowych indeksów do zapisu. Anulowano.",
        'en': "No target indices to save. Canceled."
    },
    'updated_entries': {
        'pl': "Liczba zaktualizowanych wpisów (bez przypisań przez offset): {}",
        'en': "Number of updated entries (without offset assignments): {}"
    },
    'assigned_example': {
        'pl': "  A:{} -> target:{} (offset {})",
        'en': "  A:{} -> target:{} (offset {})"
    },
    'collision_example': {
        'pl': "  kolizja: A:{} -> target {}",
        'en': "  collision: A:{} -> target {}"
    },
    'no_offset_reason': {
        'pl': "brak offsetu",
        'en': "no offset"
    },
    'mb_guess_not_exist': {
        'pl': "mb_guess nie istnieje w B",
        'en': "mb_guess does not exist in B"
    },
    'project_export_prompt': {
        'pl': "Podaj ścieżkę do pliku .s4_translation_project do eksportu: ",
        'en': "Enter path to .s4_translation_project for export: "
    },
    'path_a_required': {
        'pl': "Plik A wymagany dla tej opcji. Powrót do menu.",
        'en': "File A required for this option. Back to menu."
    },
}

# --- pomocnicze ---
def sanitize_path(s: str) -> Path:
    s = s.strip()
    if (s.startswith('"') and s.endswith('"')) or (s.startswith("'") and s.endswith("'")):
        s = s[1:-1]
    s = s.strip()
    p = Path(s).expanduser()
    if p.is_dir():
        raise ValueError("Path points to directory, expected file.")
    return p

def confirm(prompt: str, default: bool = True, lang: str = 'en') -> bool:
    yes = {'y','yes','t','tak'}
    no = {'n','no','nie'}
    if default:
        prompt = f"{prompt} [Y/n]: "
    else:
        prompt = f"{prompt} [y/N]: "
    while True:
        ans = input(prompt).strip().lower()
        if ans == '' and default:
            return True
        if ans == '' and not default:
            return False
        if ans in yes:
            return True
        if ans in no:
            return False
        print(TRANSLATIONS['yes_no_prompt'][lang])

def similarity_percent(a: str, b: str) -> float:
    """
    Zwraca procent podobieństwa tekstów a i b w zakresie 0.0..100.0.
    Normalizuje: usuwa białe znaki (wszystkie), zamienia na małe litery.
    """
    if a is None: a = ''
    if b is None: b = ''
    # normalizacja: usuń białe znaki i zamień na małe litery
    na = re.sub(r'\s+', '', a).lower()
    nb = re.sub(r'\s+', '', b).lower()
    if not na and not nb:
        return 100.0
    if not na or not nb:
        return 0.0  # Dodano wczesne wyjście dla pustych ciągów
    matcher = difflib.SequenceMatcher(None, na, nb)
    return round(matcher.ratio() * 100.0, 2)

# --- parser liniowy (rozpoznaje puste bloki) ---
def parse_blocks_linewise(text: str) -> tuple[str, list[int], dict[int, str]]:
    lines = text.splitlines(keepends=True)
    header_lines = []
    blocks_order = []
    blocks_map = {}

    i = 0
    n = len(lines)
    while i < n and not lines[i].lstrip().startswith('## Text'):
        header_lines.append(lines[i])
        i += 1

    while i < n:
        if lines[i].lstrip().startswith('## Text'):
            m = TEXT_HEADER_RE.match(lines[i])
            if not m:
                i += 1
                continue
            idx = int(m.group(1))
            blocks_order.append(idx)
            i += 1
            content_lines = []
            while i < n and not lines[i].lstrip().startswith('####'):
                content_lines.append(lines[i])
                i += 1
            content = ''.join(content_lines).rstrip('\r\n')
            blocks_map[idx] = content
            if i < n and lines[i].lstrip().startswith('####'):
                i += 1
        else:
            i += 1

    header = ''.join(header_lines)
    return header, blocks_order, blocks_map

# --- placeholder detection ---
def is_placeholder(content: str) -> bool:
    if content is None:
        return True
    s = content.strip()
    if s == '':
        return True
    chars = re.sub(r'[\s\r\n]+', '', content)
    if chars == '':
        return True
    if len(chars) >= 1 and all(c in '?xX' for c in chars):
        return True
    return False

# --- build merged project text ---
def build_output_text(header: str, original_order_ids: list[int], a_map: dict[int, str], b_map: dict[int, str]) -> tuple[str, list[int], list[int]]:
    parts = []
    parts.append(header if header.endswith('\n') or header == '' else header + '\n')
    replaced = []
    for idx in original_order_ids:
        if idx in b_map:
            content = b_map[idx]
            replaced.append(idx)
        else:
            content = a_map.get(idx, '')
        parts.append(f'## Text {idx} ##\n')
        if content != '':
            parts.append(f'{content}\n')
        parts.append('####\n')
    extra_ids = sorted([i for i in b_map.keys() if i not in set(original_order_ids)])
    added = extra_ids.copy()
    for idx in extra_ids:
        content = b_map[idx]
        parts.append(f'## Text {idx} ##\n')
        if content != '':
            parts.append(f'{content}\n')
        parts.append('####\n')
    return ''.join(parts), replaced, added

# --- I/O helpers ---
def read_file(path: Path | str, encoding: str = 'utf-8') -> str:
    data = Path(path).read_bytes()
    text = data.decode(encoding, errors='replace')
    return text.replace('\r\n', '\n').replace('\r', '\n')

def write_file(path: Path | str, text: str, encoding: str = 'utf-8') -> None:
    normalized = text.replace('\r\n', '\n').replace('\r', '\n')
    path = Path(path)
    with open(path, 'wb') as f:
        f.write(normalized.encode(encoding))

# --- option 1: generate missingtexts.txt ---
def generate_missing_texts(path_a: Path, path_b: Path, encoding: str = 'utf-8', out_name: str = 'missingtexts.txt', lang: str = 'en') -> tuple[Path | None, list[int]]:
    text_a = read_file(path_a, encoding=encoding)
    text_b = read_file(path_b, encoding=encoding)
    _, order_a, map_a = parse_blocks_linewise(text_a)
    _, order_b, map_b = parse_blocks_linewise(text_b)

    missing_ids = []
    parts = []
    parts.append(f'# {TRANSLATIONS["missing_texts_generated"][lang]}\n# A: {path_a}\n# B: {path_b}\n\n')
    for idx in order_b:
        b_content = map_b.get(idx, '')
        a_has = idx in map_a
        a_content = map_a.get(idx, '')

        # only if B has real text (not placeholder) and A missing or placeholder
        if is_placeholder(b_content):
            continue
        if (not a_has) or is_placeholder(a_content):
            missing_ids.append(idx)
            parts.append(f'## Text {idx} ##\n')
            if b_content != '':
                parts.append(f'{b_content}\n')
            parts.append('####\n')

    out_path = path_a.parent / out_name
    if out_path.exists():
        if not confirm(TRANSLATIONS['file_exists_overwrite'][lang].format(out_path), default=False, lang=lang):
            print(TRANSLATIONS['canceled_missingtexts'][lang])
            return None, missing_ids
    write_file(out_path, ''.join(parts), encoding=encoding)
    return out_path, missing_ids

TRANSLATIONS['missing_texts_generated'] = {
    'pl': "Missing texts generated from B vs A",
    'en': "Missing texts generated from B vs A"
}

# --- option 2: merge ---
def option_merge(path_a: Path, path_b: Path, encoding: str = 'utf-8', lang: str = 'en') -> None:
    text_a = read_file(path_a, encoding=encoding)
    text_b = read_file(path_b, encoding=encoding)
    header_a, order_a, map_a = parse_blocks_linewise(text_a)
    header_b, order_b, map_b = parse_blocks_linewise(text_b)

    result_text, replaced, added = build_output_text(header_a, order_a, map_a, map_b)

    print(TRANSLATIONS['summary_changes'][lang])
    if replaced:
        print(TRANSLATIONS['replaced_numbers'][lang].format(', '.join(map(str, replaced))))
    else:
        print(TRANSLATIONS['no_replacements'][lang])
    if added:
        print(TRANSLATIONS['added_numbers'][lang].format(', '.join(map(str, added))))
    else:
        print(TRANSLATIONS['no_added'][lang])

    print(TRANSLATIONS['save_method'][lang])
    print(TRANSLATIONS['overwrite_a'][lang])
    print(TRANSLATIONS['save_new'][lang])
    choice = input(TRANSLATIONS['choose_1_or_2'][lang]).strip() or '1'

    if choice == '1':
        bak = path_a.with_suffix(path_a.suffix + '.bak')
        try:
            shutil.copy2(path_a, bak)
            print(TRANSLATIONS['backup_created'][lang].format(bak))
        except Exception as e:
            print(TRANSLATIONS['backup_failed'][lang].format(e))
            if not confirm(TRANSLATIONS['continue_without_backup'][lang], default=False, lang=lang):
                print(TRANSLATIONS['canceled'][lang])
                return
        try:
            write_file(path_a, result_text, encoding=encoding)
            print(TRANSLATIONS['overwritten_a'][lang].format(path_a))
        except Exception as e:
            print(TRANSLATIONS['write_error'][lang].format(e))
            return
    elif choice == '2':
        suggested = path_a.with_name(path_a.stem + '_updated' + path_a.suffix)
        out_path_input = input(TRANSLATIONS['out_path_prompt'][lang].format(suggested)).strip()
        if out_path_input == '':
            out_path = suggested
        else:
            candidate = sanitize_path(out_path_input)
            if candidate.exists() and candidate.is_dir():
                out_path = candidate / suggested.name
            else:
                out_path = candidate
        out_dir = out_path.parent
        if not out_dir.exists():
            try:
                out_dir.mkdir(parents=True, exist_ok=True)
            except Exception as e:
                print(TRANSLATIONS['dir_create_failed'][lang].format(out_dir, e))
                return
        if out_path.exists():
            if not confirm(TRANSLATIONS['file_exists_overwrite'][lang].format(out_path), default=False, lang=lang):
                print(TRANSLATIONS['canceled'][lang])
                return
        try:
            write_file(out_path, result_text, encoding=encoding)
            print(TRANSLATIONS['saved_to'][lang].format(out_path))
        except Exception as e:
            print(TRANSLATIONS['write_error'][lang].format(e))
            return
    else:
        print(TRANSLATIONS['invalid_save_choice'][lang])
        return

# --- s4_texts.dat import helpers ---
def infer_lang_from_filename(path: Path) -> int | None:
    name = path.name
    m = re.search(r'(\d+)(?=\D*$)', name)
    if m:
        try:
            return int(m.group(1))
        except:
            return None
    return None

def read_s4_dat(path: Path) -> tuple[bytes, list[bytes]]:
    data = path.read_bytes()
    if len(data) < 4:
        raise ValueError("File too short, no header.")
    header_bytes = data[0:4]
    pos = 4
    texts_bytes = []
    total_len = len(data)
    while pos + 4 <= total_len:
        length = int.from_bytes(data[pos:pos+4], byteorder='little', signed=False)
        pos += 4
        if length < 0:
            raise ValueError("Negative text length (file error).")
        if pos + length > total_len:
            remaining = total_len - pos
            if remaining <= 0:
                texts_bytes.append(b'')
                continue
            chunk = data[pos:total_len]
            texts_bytes.append(chunk)
            pos = total_len
            break
        else:
            chunk = data[pos:pos+length]
            texts_bytes.append(chunk)
            pos += length
    return header_bytes, texts_bytes

def decode_text_bytes(b: bytes, lang_num: int) -> str:
    """
    Dekoduje bajty używając listy kodowań z LANG_MAP w kolejności.
    Jeśli żadne z nich nie zadziała, próbuje jeszcze kilka uniwersalnych fallbacków,
    a na końcu zwraca wynik z errors='replace'.
    """
    candidates = LANG_MAP.get(lang_num, (None, ['latin-1']))[1][:]
    for c in ['utf-8', 'latin-1', 'cp1252']:
        if c not in candidates:
            candidates.append(c)
    for enc in candidates:
        try:
            return b.decode(enc)
        except Exception:
            continue
    try:
        return b.decode(candidates[0], errors='replace') if candidates else b.decode('latin-1', errors='replace')
    except Exception:
        return b.decode('latin-1', errors='replace')

def option_import_s4(path_dat: Path, encoding_out: str = 'utf-8', lang: str = 'en') -> None:
    inferred = infer_lang_from_filename(path_dat)
    if inferred is not None:
        print(TRANSLATIONS['lang_num_from_name'][lang].format(inferred))
    while True:
        raw = input(TRANSLATIONS['lang_num_prompt'][lang].format(inferred if inferred is not None else TRANSLATIONS['no_suggestion'][lang])).strip()
        if raw == '' and inferred is not None:
            lang_num = inferred
            break
        try:
            lang_num = int(raw)
            break
        except ValueError:
            print(TRANSLATIONS['invalid_number'][lang])

    lang_name = LANG_MAP.get(lang_num, (f"LANG_{lang_num}", ['latin-1']))[0]
    suggested_list = LANG_MAP.get(lang_num, (None, ['latin-1']))[1]
    suggested_encoding = suggested_list[0] if suggested_list else 'latin-1'
    print(TRANSLATIONS['selected_lang'][lang].format(lang_name, lang_num, ', '.join(suggested_list)))

    enc_choice = suggested_encoding or ''
    if enc_choice:
        use_sug = input(TRANSLATIONS['use_suggested_enc'][lang].format(enc_choice)).strip().lower()
        if use_sug == '' or use_sug in ('y','yes','t','tak'):
            chosen_enc = enc_choice
        else:
            chosen_enc = input(TRANSLATIONS['enc_input_prompt'][lang]).strip() or enc_choice
    else:
        chosen_enc = input(TRANSLATIONS['enc_input_prompt'][lang]).strip() or 'latin-1'

    try:
        header_bytes, texts_bytes = read_s4_dat(path_dat)
    except Exception as e:
        print(TRANSLATIONS['dat_read_error'][lang].format(e))
        return

    texts_decoded = []
    for b in texts_bytes:
        try:
            txt = b.decode(chosen_enc)
        except Exception:
            txt = decode_text_bytes(b, lang_num)
        texts_decoded.append(txt)

    header_first4_dec = ' '.join(str(x) for x in header_bytes)
    project_header = (
        "**** Settlers IV Game Translation Tool Project File ** Version PY ****\n"
        f"**** Language: {lang_name} ** @{header_first4_dec}@ ****\n\n"
    )

    parts = [project_header]
    for i, txt in enumerate(texts_decoded, start=1):
        parts.append(f'## Text {i} ##\n')
        if txt != '':
            parts.append(f'{txt}\n')
        parts.append('####\n')

    out_name = f"{lang_name}.s4_translation_project"
    out_path = path_dat.parent / out_name
    if out_path.exists():
        if not confirm(TRANSLATIONS['file_exists_overwrite'][lang].format(out_path), default=False, lang=lang):
            print(TRANSLATIONS['canceled_project_save'][lang])
            return
    try:
        write_file(out_path, ''.join(parts), encoding=encoding_out)
        print(TRANSLATIONS['project_saved'][lang].format(out_path, encoding_out))
    except Exception as e:
        print(TRANSLATIONS['project_write_error'][lang].format(e))


def option_export_proj_to_dat(path_proj: Path | None = None, lang: str = 'en') -> None:
    """
    Eksportuje .s4_translation_project -> s4_texts.dat<langnum>
    Format: 4 bajty nagłówka, potem powtarzane: 4 bajty długości (little-endian), dane tekstu (bajty).
    Zapisuje wszystkie teksty od 1 do ostatniego numeru występującego w projekcie.
    Sugestia numeru języka pochodzi z nazwy pliku projektu (np. 'CHINESE' -> 7).
    """
    # 1) ścieżka pliku projektu
    if path_proj is None:
        raw = input(TRANSLATIONS['project_path_prompt'][lang]).strip()
        if not raw:
            print(TRANSLATIONS['project_path_required'][lang])
            return
        try:
            path_proj = sanitize_path(raw)
        except Exception as e:
            print(TRANSLATIONS['invalid_path'][lang].format(e))
            return
    if not path_proj.exists():
        print(TRANSLATIONS['file_not_exists'][lang].format('projektu', path_proj))
        return

    # 2) wczytaj i sparsuj projekt
    try:
        text = read_file(path_proj, encoding='utf-8')
    except Exception as e:
        print(TRANSLATIONS['project_read_error'][lang].format(e))
        return

    header_text, order, blocks_map = parse_blocks_linewise(text)

    # 3) spróbuj wyciągnąć nagłówek 4 bajtów z nagłówka projektu (w formacie @n1 n2 n3 n4@)
    header_bytes = None
    if header_text:
        m = re.search(r'@\s*([\d\s]{1,})\s*@', header_text)
        if m:
            nums = m.group(1).strip().split()
            if len(nums) >= 4:
                try:
                    hb = [int(x) & 0xFF for x in nums[:4]]
                    if all(0 <= x <= 255 for x in hb):
                        header_bytes = bytes(hb)
                        print(TRANSLATIONS['header_found'][lang].format(hb))
                except Exception:
                    header_bytes = None

    # jeśli nie znaleziono, poproś użytkownika o podanie 4 liczb
    if header_bytes is None:
        print(TRANSLATIONS['header_not_found'][lang])
        while True:
            raw_hdr = input(TRANSLATIONS['header_prompt'][lang]).strip()
            parts = raw_hdr.split()
            if len(parts) != 4:
                print(TRANSLATIONS['exactly_4_numbers'][lang])
                continue
            try:
                nums = [int(x) for x in parts]
                if any(n < 0 or n > 255 for n in nums):
                    print(TRANSLATIONS['numbers_0_255'][lang])
                    continue
                header_bytes = bytes(nums)
                break
            except ValueError:
                print(TRANSLATIONS['invalid_numbers'][lang])

    # 4) sugeruj numer języka na podstawie nazwy pliku projektu (szukamy nazwy języka z LANG_MAP)
    name_upper = path_proj.name.upper()
    # zbuduj mapę nazwa->numer i posortuj po długości nazwy malejąco, żeby preferować dłuższe dopasowania
    name_to_num = {v[0].upper(): k for k, v in LANG_MAP.items()}
    candidates = sorted(name_to_num.keys(), key=lambda s: -len(s))
    inferred = None
    for lang_name in candidates:
        if lang_name in name_upper:
            inferred = name_to_num[lang_name]
            break

    # pokaż listę języków i zaproponuj sugerowany numer (jeśli znaleziono)
    print(TRANSLATIONS['available_langs'][lang])
    for k in sorted(LANG_MAP.keys()):
        print(f"  {k} : {LANG_MAP[k][0]}")
    if inferred is not None:
        print(TRANSLATIONS['lang_suggestion'][lang].format(inferred, LANG_MAP[inferred][0]))
    while True:
        raw_lang = input(TRANSLATIONS['lang_num_save_prompt'][lang].format(inferred if inferred is not None else '')).strip()
        if raw_lang == '' and inferred is not None:
            lang_num = inferred
            break
        try:
            lang_num = int(raw_lang)
            if lang_num not in LANG_MAP:
                print(TRANSLATIONS['unknown_lang_num'][lang])
                continue
            break
        except ValueError:
            print(TRANSLATIONS['invalid_number'][lang])

    lang_name = LANG_MAP[lang_num][0]
    enc_candidates = LANG_MAP[lang_num][1][:]
    if 'utf-8' not in enc_candidates:
        enc_candidates.append('utf-8')

    print(TRANSLATIONS['selected_lang_save'][lang].format(lang_name, lang_num, ', '.join(enc_candidates)))
    chosen_enc = enc_candidates[0]
    use_sug = input(TRANSLATIONS['use_suggested_enc_out'][lang].format(chosen_enc)).strip().lower()
    if use_sug != '' and use_sug not in ('y','yes','t','tak'):
        custom = input(TRANSLATIONS['custom_enc_prompt'][lang]).strip()
        if custom:
            chosen_enc = custom

    # 5) ustal maksymalny numer do zapisu: zawsze zapisujemy wszystkie teksty od 1 do ostatniego istniejącego numeru
    existing_nums = sorted(blocks_map.keys())
    if existing_nums:
        max_index = max(existing_nums)
    else:
        print(TRANSLATIONS['no_blocks'][lang])
        return

    print(TRANSLATIONS['save_texts_from_to'][lang].format(max_index, max_index))

    # 6) przygotuj dane do zapisu: dla i=1..max_index zapisz długość i dane (brak -> długość 0)
    texts_bytes = []
    empty_count = 0
    for i in range(1, max_index + 1):
        content = blocks_map.get(i, '')
        if content is None:
            content = ''
        content_norm = content.replace('\r\n', '\n').replace('\r', '\n')
        try:
            b = content_norm.encode(chosen_enc)
        except Exception:
            # fallback: spróbuj kolejne kodowania z listy, potem latin-1, potem utf-8 replace
            b = None
            for enc in enc_candidates:
                try:
                    b = content_norm.encode(enc)
                    break
                except Exception:
                    continue
            if b is None:
                try:
                    b = content_norm.encode('latin-1', errors='replace')
                except Exception:
                    b = content_norm.encode('utf-8', errors='replace')
        texts_bytes.append(b)
        if len(b) == 0:
            empty_count += 1

    # 7) wybierz nazwę pliku wyjściowego (domyślnie s4_texts.dat<langnum>)
    default_out = path_proj.with_name(f"s4_texts.dat{lang_num}")
    out_input = input(TRANSLATIONS['out_file_prompt'][lang].format(default_out)).strip()
    if out_input == '':
        out_path = default_out
    else:
        out_path = sanitize_path(out_input)

    # 8) sprawdź nadpisanie
    if out_path.exists():
        if not confirm(TRANSLATIONS['file_exists_overwrite'][lang].format(out_path), default=False, lang=lang):
            alt = out_path.with_name(out_path.stem + '_exported' + out_path.suffix)
            print(TRANSLATIONS['save_as_alt'][lang].format(alt))
            if not confirm(TRANSLATIONS['confirm_save_as'][lang].format(alt), default=True, lang=lang):
                print(TRANSLATIONS['save_canceled'][lang])
                return
            out_path = alt

    # 9) zapisz binarnie: header_bytes (4), potem dla każdego tekstu: 4 bajty length (little-endian), dane
    try:
        with open(out_path, 'wb') as f:
            f.write(header_bytes)
            for b in texts_bytes:
                length = len(b)
                f.write(length.to_bytes(4, byteorder='little', signed=False))
                if length > 0:
                    f.write(b)
    except Exception as e:
        print(TRANSLATIONS['dat_write_error'][lang].format(e))
        return

    print(TRANSLATIONS['dat_saved'][lang].format(out_path))
    print(TRANSLATIONS['last_text_num'][lang].format(max_index))
    print(TRANSLATIONS['texts_count'][lang].format(len(texts_bytes), empty_count, chosen_enc))
    

# --- podgląd tekstów z pliku .dat z interaktywnym testowaniem kodowań i zapisu testu ---
def option_preview_dat(path_dat: Path, lang: str = 'en') -> None:
    inferred = infer_lang_from_filename(path_dat)
    if inferred is not None:
        print(TRANSLATIONS['lang_num_from_name'][lang].format(inferred))
    while True:
        raw = input(TRANSLATIONS['lang_num_prompt'][lang].format(inferred if inferred is not None else TRANSLATIONS['no_suggestion'][lang])).strip()
        if raw == '' and inferred is not None:
            lang_num = inferred
            break
        try:
            lang_num = int(raw)
            break
        except ValueError:
            print(TRANSLATIONS['invalid_number'][lang])

    lang_name = LANG_MAP.get(lang_num, (f"LANG_{lang_num}", ['latin-1']))[0]
    suggested_list = LANG_MAP.get(lang_num, (None, ['latin-1']))[1]
    print(TRANSLATIONS['selected_lang'][lang].format(lang_name, lang_num, ', '.join(suggested_list)))

    try:
        header_bytes, texts_bytes = read_s4_dat(path_dat)
    except Exception as e:
        print(TRANSLATIONS['dat_read_error'][lang].format(e))
        return

    total = len(texts_bytes)
    print(TRANSLATIONS['texts_count_dat'][lang].format(total))

    # wybór zakresu lub pojedynczego numeru; jeśli użytkownik wybierze "single" -> można testować wszystkie kodowania
    while True:
        sel = input(TRANSLATIONS['range_prompt'][lang]).strip()
        if sel.lower() == 'all':
            start_idx, end_idx = 1, total
            single_for_all_enc = False
            break
        if sel.lower() == 'single':
            while True:
                s2 = input(TRANSLATIONS['single_text_prompt'][lang]).strip()
                try:
                    idx = int(s2)
                    if idx < 1 or idx > total:
                        print(TRANSLATIONS['out_of_range'][lang])
                        continue
                    start_idx = end_idx = idx
                    single_for_all_enc = True
                    break
                except ValueError:
                    print(TRANSLATIONS['invalid_number'][lang])
            break
        if '-' in sel:
            parts = sel.split('-', 1)
            try:
                start_idx = int(parts[0])
                end_idx = int(parts[1])
                if start_idx < 1 or end_idx < start_idx:
                    print(TRANSLATIONS['invalid_range'][lang])
                    continue
                if start_idx > total:
                    print(TRANSLATIONS['out_of_range_start'][lang])
                    continue
                if end_idx > total:
                    end_idx = total
                single_for_all_enc = False
                break
            except ValueError:
                print(TRANSLATIONS['invalid_format'][lang])
                continue
        else:
            try:
                idx = int(sel)
                if idx < 1 or idx > total:
                    print(TRANSLATIONS['out_of_range'][lang])
                    continue
                start_idx = end_idx = idx
                single_for_all_enc = False
                break
            except ValueError:
                print(TRANSLATIONS['invalid_number'][lang])
                continue

    # przygotuj listę kandydatów kodowań
    candidates = LANG_MAP.get(lang_num, (None, ['latin-1']))[1][:]
    for c in ['utf-8', 'latin-1', 'cp1252']:
        if c not in candidates:
            candidates.append(c)

    # log do zapisu (zbieramy teksty, które wypisujemy)
    log_lines = []
    log_lines.append(f"Encoding test for {lang_name} (file: {path_dat})\n")

    # jeśli użytkownik chce testować wszystkie kodowania:
    if single_for_all_enc:
        idx = start_idx
        b = texts_bytes[idx-1]
        log_lines.append(TRANSLATIONS['testing_single_text'][lang].format(idx))
        for enc in candidates:
            try:
                txt = b.decode(enc)
            except Exception:
                txt = decode_text_bytes(b, lang_num)
            header = f"\n--- Encoding: {enc} ---\n## Text {idx} ##\n"
            print(header)
            print(txt if txt != '' else "(empty)")
            print("####\n")
            log_lines.append(header)
            log_lines.append(txt if txt != '' else "(empty)")
            log_lines.append("\n####\n")
        # zapytaj o zapis
        save = input(TRANSLATIONS['save_test_prompt'][lang].format(lang_name)).strip().lower()
        if save in ('y','yes','t','tak'):
            out_path = path_dat.parent / f"{lang_name}_encoding_test.txt"
            if out_path.exists():
                if not confirm(TRANSLATIONS['file_exists_overwrite'][lang].format(out_path), default=False, lang=lang):
                    print(TRANSLATIONS['canceled_test_save'][lang])
                    return
            try:
                write_file(out_path, '\n'.join(log_lines), encoding='utf-8')
                print(TRANSLATIONS['test_saved'][lang].format(out_path))
            except Exception as e:
                print(TRANSLATIONS['test_save_error'][lang].format(e))
        else:
            print(TRANSLATIONS['test_not_saved'][lang])
        print(TRANSLATIONS['end_all_enc_test'][lang])
        return

    # interaktywne testowanie pojedynczych kodowań lub sekwencji
    default_enc = candidates[0] if candidates else 'latin-1'
    chosen_enc = default_enc

    while True:
        print(TRANSLATIONS['suggested_encs'][lang])
        for i, c in enumerate(candidates, start=1):
            print(f"  {i}) {c}")
        print(TRANSLATIONS['custom_enc'][lang])
        print(TRANSLATIONS['back_to_menu'][lang])

        sel_enc = input(TRANSLATIONS['choose_enc_prompt'][lang].format(default_enc)).strip()
        if sel_enc == '':
            chosen_enc = default_enc
        elif sel_enc.lower() in ('m','menu'):
            print(TRANSLATIONS['back_to_menu_msg'][lang])
            return
        elif sel_enc.lower() == 'a':
            chosen_enc = input(TRANSLATIONS['custom_enc_prompt_preview'][lang]).strip()
            if chosen_enc == '':
                chosen_enc = default_enc
        else:
            try:
                idx_choice = int(sel_enc)
                if 1 <= idx_choice <= len(candidates):
                    chosen_enc = candidates[idx_choice-1]
                else:
                    print(TRANSLATIONS['invalid_enc_choice'][lang])
                    continue
            except ValueError:
                chosen_enc = sel_enc

        # dekoduj i wypisz zakres, zapisuj do logu
        header_run = f"\n--- Tested encoding: {chosen_enc} ---\n"
        print(header_run)
        log_lines.append(header_run)
        for i in range(start_idx, end_idx + 1):
            b = texts_bytes[i-1]
            try:
                txt = b.decode(chosen_enc)
            except Exception:
                txt = decode_text_bytes(b, lang_num)
            block_header = f'## Text {i} ##\n'
            print(block_header)
            if txt != '':
                print(txt)
            print('####\n')
            log_lines.append(block_header)
            log_lines.append(txt if txt != '' else "(empty)")
            log_lines.append('####\n')

        # po teście zapytaj czy testować kolejne kodowanie czy wrócić
        again = input(TRANSLATIONS['test_another_enc'][lang]).strip().lower()
        if again == '' or again in ('y','yes','t','tak'):
            continue
        else:
            # zapytaj czy zapisać log testu
            save = input(TRANSLATIONS['save_test_prompt'][lang].format(lang_name)).strip().lower()
            if save in ('y','yes','t','tak'):
                out_path = path_dat.parent / f"{lang_name}_encoding_test.txt"
                if out_path.exists():
                    if not confirm(TRANSLATIONS['file_exists_overwrite'][lang].format(out_path), default=False, lang=lang):
                        print(TRANSLATIONS['canceled_test_save'][lang])
                        return
                try:
                    write_file(out_path, '\n'.join(log_lines), encoding='utf-8')
                    print(TRANSLATIONS['test_saved'][lang].format(out_path))
                except Exception as e:
                    print(TRANSLATIONS['test_save_error'][lang].format(e))
            else:
                print(TRANSLATIONS['test_not_saved'][lang])
            print(TRANSLATIONS['back_to_menu_msg'][lang])
            return
    

# --- shift ids (przesunięcie numerów) ---
def option_shift_ids(path_a: Path, encoding: str = 'utf-8', lang: str = 'en') -> None:
    text_a = read_file(path_a, encoding=encoding)
    header_a, order_a, map_a = parse_blocks_linewise(text_a)

    if not order_a:
        print(TRANSLATIONS['no_blocks_found'][lang])
        return

    first = order_a[0]
    last = order_a[-1]
    count = len(order_a)
    print(TRANSLATIONS['blocks_found'][lang].format(count, first, last))

    while True:
        raw = input(TRANSLATIONS['offset_prompt'][lang]).strip()
        if raw == '':
            print(TRANSLATIONS['no_value_canceled'][lang])
            return
        try:
            offset = int(raw)
        except ValueError:
            print(TRANSLATIONS['invalid_integer'][lang])
            continue
        if offset == 0:
            print(TRANSLATIONS['offset_zero'][lang])
            return
        break

    new_ids = [i + offset for i in order_a]
    if any(i <= 0 for i in new_ids):
        print(TRANSLATIONS['negative_ids_error'][lang])
        return

    if len(set(new_ids)) != len(new_ids):
        print(TRANSLATIONS['duplicates_error'][lang])
        return

    parts = []
    parts.append(header_a if header_a.endswith('\n') or header_a == '' else header_a + '\n')
    for old_idx in order_a:
        new_idx = old_idx + offset
        content = map_a.get(old_idx, '')
        parts.append(f'## Text {new_idx} ##\n')
        if content != '':
            parts.append(f'{content}\n')
        parts.append('####\n')
    result_text = ''.join(parts)

    print(TRANSLATIONS['save_shift_method'][lang])
    print(TRANSLATIONS['overwrite_a_shift'][lang])
    print(TRANSLATIONS['save_new_shift'][lang])
    choice = input(TRANSLATIONS['choose_1_or_2_shift'][lang]).strip() or '2'

    if choice == '1':
        bak = path_a.with_suffix(path_a.suffix + '.bak')
        try:
            shutil.copy2(path_a, bak)
            print(TRANSLATIONS['backup_created'][lang].format(bak))
        except Exception as e:
            print(TRANSLATIONS['backup_failed'][lang].format(e))
            if not confirm(TRANSLATIONS['continue_without_backup'][lang], default=False, lang=lang):
                print(TRANSLATIONS['canceled'][lang])
                return
        try:
            write_file(path_a, result_text, encoding=encoding)
            print(TRANSLATIONS['overwritten_a'][lang].format(path_a))
        except Exception as e:
            print(TRANSLATIONS['write_error'][lang].format(e))
            return
    elif choice == '2':
        suggested = path_a.with_name(path_a.stem + '_shifted' + path_a.suffix)
        out_path_input = input(TRANSLATIONS['out_path_prompt'][lang].format(suggested)).strip()
        if out_path_input == '':
            out_path = suggested
        else:
            candidate = sanitize_path(out_path_input)
            if candidate.exists() and candidate.is_dir():
                out_path = candidate / suggested.name
            else:
                out_path = candidate
        out_dir = out_path.parent
        if not out_dir.exists():
            try:
                out_dir.mkdir(parents=True, exist_ok=True)
            except Exception as e:
                print(TRANSLATIONS['dir_create_failed'][lang].format(out_dir, e))
                return
        if out_path.exists():
            if not confirm(TRANSLATIONS['file_exists_overwrite'][lang].format(out_path), default=False, lang=lang):
                print(TRANSLATIONS['canceled'][lang])
                return
        try:
            write_file(out_path, result_text, encoding=encoding)
            print(TRANSLATIONS['shifted_saved'][lang].format(out_path))
        except Exception as e:
            print(TRANSLATIONS['write_error'][lang].format(e))
            return
    else:
        print(TRANSLATIONS['invalid_save_choice'][lang])
        return
        
def option_fix_missing_entries(path_proj: Path | None = None, encoding: str = 'utf-8', lang: str = 'en') -> None:
    """
    Uzupełnia brakujące wpisy ## Text N ## w pliku projektu.
    Pyta o nadpisanie lub zapis jako nowy plik <nazwa>_fixed.<ext>.
    """
    # pobierz ścieżkę pliku projektu
    if path_proj is None:
        raw = input(TRANSLATIONS['project_path_fix_prompt'][lang]).strip()
        if not raw:
            print(TRANSLATIONS['no_path_canceled'][lang])
            return
        try:
            path_proj = sanitize_path(raw)
        except Exception as e:
            print(TRANSLATIONS['invalid_path'][lang].format(e))
            return
    if not path_proj.exists():
        print(TRANSLATIONS['file_not_exists'][lang].format('', path_proj))
        return

    # wybór przedziału
    while True:
        rng = input(TRANSLATIONS['range_fix_prompt'][lang]).strip()
        if not rng:
            print(TRANSLATIONS['no_range_canceled'][lang])
            return
        if '-' in rng:
            parts = rng.split('-', 1)
            try:
                start = int(parts[0])
                end = int(parts[1])
                if start < 1 or end < start:
                    print(TRANSLATIONS['invalid_range_fix'][lang])
                    continue
                break
            except ValueError:
                print(TRANSLATIONS['invalid_format'][lang])
                continue
        else:
            try:
                n = int(rng)
                if n < 1:
                    print(TRANSLATIONS['num_ge_1'][lang])
                    continue
                start = end = n
                break
            except ValueError:
                print(TRANSLATIONS['invalid_number'][lang])
                continue

    # wczytaj plik i sparsuj bloki
    try:
        text = read_file(path_proj, encoding=encoding)
    except Exception as e:
        print(TRANSLATIONS['project_read_error'][lang].format(e))
        return

    header, order, blocks_map = parse_blocks_linewise(text)

    # zbierz brakujące numery
    missing = []
    for i in range(start, end + 1):
        if i not in blocks_map:
            missing.append(i)

    if not missing:
        print(TRANSLATIONS['no_missing_entries'][lang])
        return

    # budowanie nowej zawartości
    existing_nums = sorted(blocks_map.keys())
    if existing_nums:
        min_num = min(existing_nums)
        max_num = max(existing_nums)
    else:
        min_num = start
        max_num = end
    overall_min = min(min_num, start)
    overall_max = max(max_num, end)

    parts = []
    if header:
        parts.append(header if header.endswith('\n') else header + '\n')
    else:
        parts.append('')

    added = []
    for idx in range(overall_min, overall_max + 1):
        parts.append(f'## Text {idx} ##\n')
        content = blocks_map.get(idx, '')
        if content:
            content_norm = content.replace('\r\n', '\n').replace('\r', '\n').rstrip('\n')
            parts.append(content_norm + '\n')
        else:
            added.append(idx)
        parts.append('####\n')

    result_text = ''.join(parts)

    # --- raport i logika zapisu ---
    print(TRANSLATIONS['missing_found'][lang].format(len(added)))
    if added:
        print(TRANSLATIONS['added_numbers_fix'][lang].format(', '.join(map(str, added))))
    else:
        print(TRANSLATIONS['no_added_unexpected'][lang])

    print(TRANSLATIONS['overwrite_prompt'][lang])
    if confirm(TRANSLATIONS['overwrite_file'][lang], default=False, lang=lang):
        try:
            write_file(path_proj, result_text, encoding=encoding)
            print(TRANSLATIONS['overwritten'][lang].format(path_proj))
        except Exception as e:
            print(TRANSLATIONS['write_error'][lang].format(e))
        return

    # jeśli NIE nadpisujemy → zapisz jako nowy
    ext = path_proj.suffix
    stem = path_proj.stem
    new_path = path_proj.with_name(f"{stem}_fixed{ext}")

    print(TRANSLATIONS['save_as_new_prompt'][lang].format(new_path))
    if confirm(TRANSLATIONS['save_as_new'][lang], default=True, lang=lang):
        try:
            write_file(new_path, result_text, encoding=encoding)
            print(TRANSLATIONS['new_saved'][lang].format(new_path))
        except Exception as e:
            print(TRANSLATIONS['write_error'][lang].format(e))
    else:
        print(TRANSLATIONS['save_canceled'][lang])

def option_align_versions(path_a: Path, path_b: Path, encoding: str = 'utf-8', max_tries_default: int = 5, lang: str = 'en') -> None:
    """
    Dopasowuje numery tekstów z pliku A do pliku B:
    - porównania ignorują białe znaki,
    - utrzymuje historię offsetów (m - n) i raportuje ich zmiany,
    - zapisuje w pliku wynikowym TE SAME TREŚCI co w A, ale pod DOCelowymi numerami
      (numery z B lub na+offset). Plik B jest read-only.
    """
    from itertools import groupby
    from operator import itemgetter

    # walidacja plików
    if not path_a.exists():
        print(TRANSLATIONS['file_not_exists'][lang].format('A', path_a))
        return
    if not path_b.exists():
        print(TRANSLATIONS['file_not_exists'][lang].format('B', path_b))
        return

    # wczytanie i parsowanie
    text_a = read_file(path_a, encoding=encoding)
    text_b = read_file(path_b, encoding=encoding)
    header_a, order_a, map_a = parse_blocks_linewise(text_a)
    header_b, order_b, map_b = parse_blocks_linewise(text_b)

    total_a = len(order_a)
    total_b = len(order_b)
    print(TRANSLATIONS['files_count'][lang].format(path_a, total_a, path_b, total_b))

    # ile prób przesunięcia w A (domyślnie)
    try:
        raw = input(TRANSLATIONS['max_tries_prompt'][lang].format(max_tries_default)).strip()
        max_tries = int(raw) if raw != '' else max_tries_default
        if max_tries < 1:
            max_tries = max_tries_default
    except Exception:
        max_tries = max_tries_default

    ia_list = sorted(order_a)
    ib_list = sorted(order_b)
    ia_len = len(ia_list)
    ib_len = len(ib_list)

    # normalizacja do porównań: usuń wszystkie białe znaki
    def norm_for_compare(s: str) -> str:
        if s is None:
            return ''
        return re.sub(r'\s+', '', s)

    def get_text(m: dict[int, str], idx: int) -> str:
        return (m.get(idx, '') or '').replace('\r\n', '\n').replace('\r', '\n')

    def is_significant_text(s: str) -> bool:
        return not is_placeholder(s)

    # pomoc: znajdź offset dla danego na (najpierw matching_ranges, potem offset_history)
    def find_offset_for_na(na: int, matching_ranges_list: list[tuple[int, int, int, int, int]], offset_history_list: list[tuple[int, int, int]]) -> int | None:
        for (a1, a2, b1, b2, off) in matching_ranges_list:
            if a1 <= na <= a2:
                return off
        candidate = None
        for (off, aidx, bidx) in offset_history_list:
            if aidx <= na:
                candidate = off
            else:
                break
        return candidate

    # pomoc: znajdź w B pozycję (index in ib_list) gdzie b_text_norm == target_norm, zaczynając od ib_pos
    def find_in_b(target_norm: str, start_ib_pos: int) -> int | None:
        pos = start_ib_pos
        while pos < ib_len:
            m = ib_list[pos]
            b_text = get_text(map_b, m)
            if norm_for_compare(b_text) == target_norm:
                return pos
            pos += 1
        return None

    # struktury raportowe
    mappings: dict[int, int] = {}            # na -> mb (finalne mapowania znalezione sekwencyjnie)
    matched_pairs: list[tuple[int, int]] = []       # lista (na, mb) w kolejności
    matching_ranges: list[tuple[int, int, int, int, int]] = []     # (a_start, a_end, b_start, b_end, offset_at_range)
    missing_in_b: list[int] = []        # list of A indices not found in B (standalone)
    placeholder_cases: list[tuple[int, int]] = []   # (na, mb) gdzie A placeholder a B significant
    conflicts: list[tuple[int, int, str, str, float | None]] = []           # (na, mb, a_text, b_text, similarity)
    offset_history: list[tuple[int, int, int]] = []      # list of (offset, a_index, b_index) w kolejności ustawiania

    current_offset: int | None = None
    ia_pos = 0
    ib_pos = 0

    # główna pętla dopasowań
    while ia_pos < ia_len and ib_pos < ib_len:
        n = ia_list[ia_pos]
        a_text = get_text(map_a, n)
        a_norm = norm_for_compare(a_text)

        tries = 0
        ia_try_pos = ia_pos
        found_alignment = False

        while tries < max_tries and ia_try_pos < ia_len and not found_alignment:
            candidate_n = ia_list[ia_try_pos]
            candidate_text = get_text(map_a, candidate_n)
            candidate_norm = norm_for_compare(candidate_text)

            # jeśli to nie pierwsza próba i candidate jest placeholderem, pomiń (szukamy znaczącego)
            if ia_try_pos != ia_pos and not is_significant_text(candidate_text):
                ia_try_pos += 1
                continue

            # szukaj w B od ib_pos
            ib_found_pos = find_in_b(candidate_norm, ib_pos)
            if ib_found_pos is None:
                tries += 1
                ia_try_pos += 1
                continue

            # znaleziono potencjalne dopasowanie candidate_n <-> ib_list[ib_found_pos]
            m_index = ib_list[ib_found_pos]
            offset = m_index - candidate_n

            # jeśli offset się zmienił, zapisz historię i wypisz informację
            if current_offset is None or offset != current_offset:
                current_offset = offset
                offset_history.append((current_offset, candidate_n, m_index))
                print(TRANSLATIONS['new_offset_set'][lang].format(current_offset, candidate_n, m_index))

            # sekwencyjne dopasowanie kolejnych wpisów (ignorując białe znaki)
            seq_pairs: list[tuple[int, int]] = []
            seq_i = 0
            while (ia_pos + seq_i) < ia_len and (ib_found_pos + seq_i) < ib_len:
                na = ia_list[ia_pos + seq_i]
                mb = ib_list[ib_found_pos + seq_i]
                ta = get_text(map_a, na)
                tb = get_text(map_b, mb)
                if norm_for_compare(ta) == norm_for_compare(tb):
                    seq_pairs.append((na, mb))
                    seq_i += 1
                else:
                    break

            if not seq_pairs:
                tries += 1
                ia_try_pos += 1
                continue

            # zapisz sekwencyjne pary
            for (na, mb) in seq_pairs:
                mappings[na] = mb
                matched_pairs.append((na, mb))
                ta = get_text(map_a, na)
                tb = get_text(map_b, mb)
                if (not is_significant_text(ta)) and is_significant_text(tb):
                    placeholder_cases.append((na, mb))

            # dodaj zakres dopasowania z informacją o offset
            startA = seq_pairs[0][0]
            endA = seq_pairs[-1][0]
            startB = seq_pairs[0][1]
            endB = seq_pairs[-1][1]
            matching_ranges.append((startA, endA, startB, endB, current_offset))

            # przesuwamy wskaźniki A i B
            ia_pos = ia_pos + seq_i
            ib_pos = ib_found_pos + seq_i
            found_alignment = True
            break

        if not found_alignment:
            # nie znaleziono dopasowania dla bieżącego n w B w ramach max_tries
            missing_in_b.append(n)
            ia_pos += 1
            # nie przesuwamy ib_pos — dalej szukamy dopasowań dla kolejnych A względem tego samego miejsca w B

    # jeśli zostały nieprzetworzone A (po wyjściu pętli), oznacz je jako nieznalezione
    while ia_pos < ia_len:
        missing_in_b.append(ia_list[ia_pos])
        ia_pos += 1

    # Po zbudowaniu mappings: sprawdź dla każdej zmapowanej pary, czy oryginalne treści różnią się.
    # Jeśli różne, oblicz similarity_percent i dodaj do conflicts.
    for (na, mb) in matched_pairs:
        ta = get_text(map_a, na)
        tb = get_text(map_b, mb)
        if norm_for_compare(ta) != norm_for_compare(tb):
            try:
                sim = similarity_percent(ta, tb)
            except Exception:
                sim = None
            conflicts.append((na, mb, ta, tb, sim))

    # przygotuj dane do raportu podobieństw dla missing_in_b (dla każdego na spróbuj znaleźć mb_guess)
    matching_ranges_sorted = sorted(matching_ranges, key=lambda r: r[0])
    offset_history_sorted = sorted(offset_history, key=lambda t: t[1])

    missing_similarity: list[tuple[int, int | None, float | None, str]] = []  # list of (na, mb_guess_or_None, similarity_or_None, reason)
    for na in sorted(set(missing_in_b)):
        off = find_offset_for_na(na, matching_ranges_sorted, offset_history_sorted)

        if off is None:
            reason = TRANSLATIONS['no_offset_reason'][lang]
            missing_similarity.append((na, None, None, reason))
            continue

        mb_guess = na + off

        if mb_guess not in map_b:
            reason = TRANSLATIONS['mb_guess_not_exist'][lang]
            missing_similarity.append((na, mb_guess, None, reason))
            continue

        # jeśli dotarliśmy tutaj — offset jest, mb_guess istnieje
        ta = get_text(map_a, na)
        tb = get_text(map_b, mb_guess)

        try:
            sim = similarity_percent(ta, tb)
        except Exception:
            sim = None

        reason = "ok"
        missing_similarity.append((na, mb_guess, sim, reason))

    # skompresuj missing_in_b do przedziałów dla czytelnego raportu
    def compress_ranges(sorted_indices: list[int]) -> list[tuple[int, int]]:
        ranges = []
        for k, g in groupby(enumerate(sorted_indices), lambda ix: ix[0] - ix[1]):
            group = list(map(itemgetter(1), g))
            if len(group) == 1:
                ranges.append((group[0], group[0]))
            else:
                ranges.append((group[0], group[-1]))
        return ranges

    missing_ranges = compress_ranges(sorted(missing_in_b)) if missing_in_b else []

    # raport szczegółowy (przed zapisem)
    print(TRANSLATIONS['alignment_report'][lang])
    print(TRANSLATIONS['matched_pairs_count'][lang].format(len(matched_pairs)))
    if matching_ranges:
        print(TRANSLATIONS['matched_ranges'][lang])
        last_offset = None
        for (a1, a2, b1, b2, off) in matching_ranges:
            note = ""
            if off != last_offset:
                note = TRANSLATIONS['new_offset_note'][lang].format(off)
                last_offset = off
            if a1 == a2:
                print(f"  {a1} => {b1}{note}")
            else:
                print(f"  {a1}-{a2} => {b1}-{b2}{note}")
    else:
        print(TRANSLATIONS['no_matched_ranges'][lang])

    if missing_ranges:
        print(TRANSLATIONS['missing_in_b'][lang])
        for (s, e) in missing_ranges:
            if s == e:
                print(f"  {s}")
            else:
                print(f"  {s}-{e}")
    else:
        print(TRANSLATIONS['all_found'][lang])

    # raport podobieństw dla missing_in_b (szczegóły)
    if missing_similarity:
        print(TRANSLATIONS['missing_details'][lang])
        for na, mb_guess, sim, reason in missing_similarity:
            if mb_guess is None:
                print(TRANSLATIONS['no_offset'][lang].format(na))
            elif sim is None:
                print(TRANSLATIONS['no_sim'][lang].format(na, mb_guess, reason))
            else:
                print(TRANSLATIONS['with_sim'][lang].format(na, sim, mb_guess))

    if placeholder_cases:
        print(TRANSLATIONS['placeholder_cases'][lang])
        for na, mb in placeholder_cases:
            print(f"  A:{na}  <-  B:{mb}")

    if conflicts:
        print(TRANSLATIONS['conflicts'][lang])
        conflicts_sorted = sorted(conflicts, key=lambda x: -(x[4] or 0))
        for na, mb, ta, tb, sim in conflicts_sorted:
            sim_str = f"{sim}%" if sim is not None else "n/a"
            print(f"  A:{na}  !=  B:{mb}   {TRANSLATIONS['similarity'][lang]}: {sim_str}")

    # raport historii offsetów
    if offset_history:
        print(TRANSLATIONS['offset_history'][lang])
        for off, aidx, bidx in offset_history:
            print(TRANSLATIONS['offset_set_at'][lang].format(off, aidx, bidx))

    # jeśli brak mapowań i brak offsetów, kończymy
    if not mappings and not offset_history:
        print(TRANSLATIONS['no_matches'][lang])
        return

    # potwierdzenie zapisu
    total_to_save = len(mappings)
    print(TRANSLATIONS['save_intent'][lang].format(total_to_save))
    sample = matched_pairs[:20]
    if sample:
        print(TRANSLATIONS['sample_mappings'][lang].format(', '.join(f"{a}->{b}" for a, b in sample)))

    if confirm(TRANSLATIONS['overwrite_direct'][lang], default=False, lang=lang):
        out_path = path_a
    else:
        out_path = path_a.with_name(path_a.stem + '_aligned' + path_a.suffix)
        if out_path.exists():
            if not confirm(TRANSLATIONS['file_exists_overwrite'][lang].format(out_path), default=False, lang=lang):
                print(TRANSLATIONS['save_canceled'][lang])
                return

    # przygotowanie mapy docelowej: target_index -> content (treść z A, tylko numer zmieniony)
    target_map: dict[int, str] = {}
    collisions: list[tuple[int, int]] = []

    for na in sorted(map_a.keys()):
        content_from_a = map_a.get(na, '')
        if na in mappings:
            target_idx = mappings[na]
        else:
            off = find_offset_for_na(na, matching_ranges_sorted, offset_history_sorted)
            if off is not None:
                target_idx = na + off
            else:
                target_idx = na
        if target_idx in target_map:
            collisions.append((na, target_idx))
        target_map[target_idx] = content_from_a

    # posortuj docelowe indeksy i zbuduj wynikowy tekst
    target_indices = sorted(k for k in target_map.keys() if isinstance(k, int))
    if not target_indices:
        print(TRANSLATIONS['no_targets'][lang])
        return

    out_parts = []
    if header_a:
        out_parts.append(header_a if header_a.endswith('\n') else header_a + '\n')
    else:
        out_parts.append('')

    for idx in target_indices:
        out_parts.append(f'## Text {idx} ##\n')
        content = target_map.get(idx, '')
        if content:
            content_norm = content.replace('\r\n', '\n').replace('\r', '\n').rstrip('\n')
            out_parts.append(content_norm + '\n')
        out_parts.append('####\n')

    result_text = ''.join(out_parts)

    try:
        write_file(out_path, result_text, encoding=encoding)
    except Exception as e:
        print(TRANSLATIONS['write_error'][lang].format(e))
        return

    # końcowy raport zapisu
    print(TRANSLATIONS['saved_to'][lang].format(out_path))
    print(TRANSLATIONS['updated_entries'][lang].format(len(mappings)))

    # policz przypisania przez offset
    assigned_by_offset: list[tuple[int, int, int]] = []
    for na in sorted(map_a.keys()):
        if na not in mappings:
            off = find_offset_for_na(na, matching_ranges_sorted, offset_history_sorted)
            if off is not None:
                assigned_by_offset.append((na, na + off, off))

    if assigned_by_offset:
        print(TRANSLATIONS['assigned_by_offset'][lang].format(len(assigned_by_offset)))
        for na, mb_guess, off in assigned_by_offset[:200]:
            print(TRANSLATIONS['assigned_example'][lang].format(na, mb_guess, off))

    if collisions:
        print(TRANSLATIONS['collisions_warning'][lang])
        for c in collisions[:50]:
            print(TRANSLATIONS['collision_example'][lang].format(c[0], c[1]))

    print(TRANSLATIONS['last_a_num'][lang].format(max(sorted(map_a.keys())) if map_a else 0))
    print(TRANSLATIONS['done'][lang])
    

# --- main menu ---
def main(lang: str = 'en') -> None:
    while True:
        print(TRANSLATIONS['main_menu_title'][lang])
        print(TRANSLATIONS['main_menu_options'][lang])
        choice = input(TRANSLATIONS['main_menu_prompt'][lang]).strip() or '9'

        if choice not in {'1','2','3','4','5','6','7','8', '9'}:
            print(TRANSLATIONS['invalid_choice'][lang])
            continue
        if choice == '9':
            print(TRANSLATIONS['exit_message'][lang])
            input(TRANSLATIONS['press_enter_to_exit'][lang])
            sys.exit(0)

        if choice == '3':
            raw_dat = input(TRANSLATIONS['path_dat_prompt'][lang]).strip()
            if not raw_dat:
                print(TRANSLATIONS['path_required'][lang])
                continue
            try:
                path_dat = sanitize_path(raw_dat)
            except Exception as e:
                print(TRANSLATIONS['invalid_path'][lang].format(e))
                continue
            if not path_dat.exists():
                print(TRANSLATIONS['file_not_exists'][lang].format('.dat', path_dat))
                continue
            option_import_s4(path_dat, encoding_out='utf-8', lang=lang)
            continue

        if choice == '4':
            raw_proj = input(TRANSLATIONS['project_export_prompt'][lang]).strip()
            if not raw_proj:
                print(TRANSLATIONS['project_path_required'][lang])
                continue
            try:
                path_proj = sanitize_path(raw_proj)
            except Exception as e:
                print(TRANSLATIONS['invalid_path'][lang].format(e))
                continue
            if not path_proj.exists():
                print(TRANSLATIONS['file_not_exists'][lang].format('projektu', path_proj))
                continue
            option_export_proj_to_dat(path_proj, lang=lang)
            continue

        if choice == '5':
            raw_dat = input(TRANSLATIONS['path_dat_preview_prompt'][lang]).strip()
            if not raw_dat:
                print(TRANSLATIONS['path_required'][lang])
                continue
            try:
                path_dat = sanitize_path(raw_dat)
            except Exception as e:
                print(TRANSLATIONS['invalid_path'][lang].format(e))
                continue
            if not path_dat.exists():
                print(TRANSLATIONS['file_not_exists'][lang].format('.dat', path_dat))
                continue
            option_preview_dat(path_dat, lang=lang)
            continue

        if choice in {'1','2','8'}:
            raw_a = input(TRANSLATIONS['path_a_prompt'][lang]).strip()
            raw_b = input(TRANSLATIONS['path_b_prompt'][lang]).strip()
            if not raw_a or not raw_b:
                print(TRANSLATIONS['required_paths'][lang])
                continue
            try:
                path_a = sanitize_path(raw_a)
                path_b = sanitize_path(raw_b)
            except Exception as e:
                print(TRANSLATIONS['invalid_path'][lang].format(e))
                continue
            if not path_a.exists():
                print(TRANSLATIONS['file_not_exists'][lang].format('A', path_a))
                continue
            if not path_b.exists():
                print(TRANSLATIONS['file_not_exists'][lang].format('B', path_b))
                continue
            encoding = input(TRANSLATIONS['encoding_prompt'][lang]).strip() or 'utf-8'
            if choice == '1':
                out_name = input(TRANSLATIONS['out_name_prompt'][lang]).strip() or 'missingtexts.txt'
                out_path, missing_ids = generate_missing_texts(path_a, path_b, encoding=encoding, out_name=out_name, lang=lang)
                if out_path is None:
                    print(TRANSLATIONS['no_missingtexts_saved'][lang])
                else:
                    print(TRANSLATIONS['missingtexts_saved'][lang].format(out_path))
                    if missing_ids:
                        print(TRANSLATIONS['missing_blocks_count'][lang].format(len(missing_ids), ', '.join(map(str, missing_ids))))
                    else:
                        print(TRANSLATIONS['no_missing_blocks'][lang])
            elif choice == '2':
                option_merge(path_a, path_b, encoding=encoding, lang=lang)
            else:
                # zamiast merge uruchamiamy dopasowanie wersji A względem B
                option_align_versions(path_a, path_b, encoding=encoding, lang=lang)
            continue



        if choice == '6':
            raw_a2 = input(TRANSLATIONS['path_a_shift_prompt'][lang]).strip()
            if not raw_a2:
                print(TRANSLATIONS['path_a_required'][lang])
                continue
            try:
                path_a = sanitize_path(raw_a2)
            except Exception as e:
                print(TRANSLATIONS['invalid_path'][lang].format(e))
                continue
            if not path_a.exists():
                print(TRANSLATIONS['file_not_exists'][lang].format('A', path_a))
                continue
            encoding = input(TRANSLATIONS['encoding_prompt'][lang]).strip() or 'utf-8'
            option_shift_ids(path_a, encoding=encoding, lang=lang)
            continue

        if choice == '7':
            raw_proj = input(TRANSLATIONS['project_path_fix_prompt'][lang]).strip()
            if not raw_proj:
                print(TRANSLATIONS['no_path_canceled'][lang])
                continue
            try:
                path_proj = sanitize_path(raw_proj)
            except Exception as e:
                print(TRANSLATIONS['invalid_path'][lang].format(e))
                continue
            if not path_proj.exists():
                print(TRANSLATIONS['file_not_exists'][lang].format('', path_proj))
                continue
            option_fix_missing_entries(path_proj, encoding='utf-8', lang=lang)
            continue

if __name__ == '__main__':
    lang_choice = input(TRANSLATIONS['choose_lang']['en']).strip() or '2'  # Menu wyboru po angielsku domyślnie
    if lang_choice == '1':
        lang = 'pl'
    elif lang_choice == '2':
        lang = 'en'
    else:
        print(TRANSLATIONS['invalid_choice']['en'])
        sys.exit(1)
    main(lang=lang)
