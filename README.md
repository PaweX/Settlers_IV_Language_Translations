# Settlers IV Language translations
Collection of language translations for The Settlers IV (Die Siedler IV)

- **txt** folder - Settlers IV language files ready for the game.
- **projects** - folder with project files for S4 Game Translation Tool - the project files can be edited in any text editor.

[Link to the S4 Game Translation Tool](https://pawex3.blogspot.com/2019/01/the-settlers-iv-game-translation-tool.html)

If you made some corrections to one of the language trasnaltions for The Settlers IV, please share it here. **Especially if you made a completely new game trasnlation.**

## Discord Server - Settlers IV Modding
https://discord.gg/qsetQRb

## This is the list of the game languages and their translation status:

### Classic Settlers IV and History Edition:

        0 ENGLISH                          (O-All_HE)
        1 GERMAN                           (O-All_HE)
        2 FRENCH                           (O-All_HE)
        3 SPANISH                          (O-Bas)
        4 ITALIAN                          (O-Bas)
        5 POLISH                           (O-GE + U-All_HE)
        6 KOREAN                           (O-Bas)
        7 CHINESE                          (O-Bas)
        8 SWEDISH                          (O-Bas)
        9 DANISH                           (O-Bas)
        10 NORWEGIAN                       (O-Bas)
        11 HUNGARIAN                       (O-GE)
        12 HEBREW                          (O-Bas)
        13 CZECH                           (O-GE)
        14 FINNISH                         (O-No)
        16 RUSSIAN                         (O-GE + U-All_HE)
        17 THAI                            (O-No)
        18 JAPANESE                        (O-Bas)
        
        
### Description of the codes:
- ***O* - official translation**
- ***U* - unofficial translation (e.g. made by fans)**
- *No* - Nothing, no translation
- *All_HE* - Full translation with extra texts from the History Edition
- *All* - Full translation (old version, not History Edition)
- *GE* - Gold Edition translation
- - *Bas* - the basis of the game
- - *MP1* - Mission CD 1
- - *Tro* - The Trojans and the Elixir of Power
- *SE* - Second Expansions translation
- - *NeW* -  Die Neue Welt (The New World))
- - *MP2* - Community Pack

Future translations can be added to the game after number '18', however they can use only standard ANSI.

### Additional info/tips:
- Chinese language uses Big5 encoding
- Thai seems to be broken in History Edition

## How to set any language from the above list in the History Edition

1. Go to the **Binaries/Txt** directory and download the corresponding file.  
   The ending number of each file corresponds to a specific language (see the table above for language numbers):  
   `s4_texts.dat<language_number>`

   Examples:
   - `s4_texts.dat0` → English  
   - `s4_texts.dat5` → Polish

2. Move the downloaded file to the **txt** folder located in the game installation directory.

3. Change the game language in the game settings:  
   Go to:  
   `C:\Users\<your username>\Documents\TheSettlers4\Config`  
   and open the **GameSettings.cfg** file (e.g., with Notepad).  
   Find the line:  
   `Language = <number>`  
   Replace `<number>` with the language number you want to use (from the list above).  
   Save the file and run the game. The in‑game language should now match your selection.

In the **Gold Edition**, the *GameSettings.cfg* file is located in the **Config** directory inside the game installation folder. All other steps remain the same.

Keep in mind that the **History Edition** is officially translated only to German, English and French. If you change the game language to any other of these three, you will have partial translation of the game - without the New World and the Great Crusades - unless somebody will translate them (check the above table).
It may happen that after some Ubisoft update, you will have to repeat all of these above steps. In the History Edition, the menu texts: *"New World"* and *"Great Crusades"* are only visible in English, German or French, because someone hardcoded them that way in the game code. So for them, the game ignores the translation file of your language, and loads hardcoded signatures. This only happens in the History Edition.

## About the Settlers IV Translation Multitool

This Python script (*s4_translation_multitool.py*) is a command-line multitool for managing translations in Settlers IV game files. It handles project files (`.s4_translation_project`) and binary `.dat` files (e.g., `s4_texts.dat<nr>`), supporting operations like comparison, merging, import/export, previewing, shifting numbers, fixing entries, aligning versions, and applying shift maps. It includes language mappings with encodings and multilingual UI support.

### Key Options and Their Purposes

The tool presents a menu with the following options:

1. **Compare A vs B Project Files**: Analyzes two project files (A as base, B as reference) and generates `missingtexts.txt` containing texts from B that are missing or require completion in A (e.g., placeholders or absent entries).

2. **Merge Project Files**: Combines two project files by replacing matching entries in A with those from B and appending missing ones from B to A, creating a unified sorted output.

3. **Import from .dat File**: Reads a binary `s4_texts.dat<nr>` file, decodes texts using language-specific encodings, and generates a `<LANG>.s4_translation_project` text file for editing.

4. **Export to .dat File**: Converts a `.s4_translation_project` file back to a binary `s4_texts.dat<nr>` file, encoding texts and including a 4-byte header.

5. **Preview Texts from .dat**: Displays texts from a `.dat` file with interactive encoding testing; supports single texts, ranges, or all, with options to test multiple encodings and save results.

6. **Shift Text Numbers (Offset)**: Applies an offset to all text numbers in a project file A, validating for duplicates or negative values, and saves with backup or as a new file.

7. **Fix Missing Entries**: Scans a project file for gaps in text numbers within a specified range or single number, inserts empty placeholders for missing entries, and saves with options for overwrite or new file.

8. **Align Text Numbers (A to B)**: Matches text numbers from project A to B by comparing normalized content, tracks offsets, reports conflicts/mismatches, and saves aligned A (content from A, numbers adjusted to B).

9. **Apply Shift Map to A**: Loads a shift map from a `.txt` file or pasted input (format: e.g., "A:1 offset 663" or "1 663"), applies offsets sequentially to A's numbers, checks for collisions/negatives, and saves with backup or as new.

0. **Exit**: Quits the program.

All operations prompt for file paths, encodings (default UTF-8), and confirmations for overwrites/backups. Errors are handled with multilingual messages.

### Program Interface Available in Languages:

The tool's user interface (menu, prompts, messages, reports) is fully translated and available in the following languages:

- English (en) – default
- Deutsch / German (de)
- Polski / Polish (pl)
- Italiano / Italian (it)
- Español / Spanish (es)
- 简体中文 / Simplified Chinese (zh)
- Русский / Russian (ru)
- 日本語 / Japanese (ja)

At startup, you can choose your preferred language by entering the corresponding number (0–7).  
All in-game text handling (import/export .dat files) uses the appropriate language-specific encodings regardless of the selected UI language.

## Credits:
- **All authors of the original translations**
- *@PaweX (Pawel C. - PaweX3)* - Polish translation of the New World, Great Crusades, extra texts for History Edition and improvement of some original texts.

