#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Settlers IV translation tool
Options:
  1) Compare A vs B → missingtexts.txt
  2) Merge A and B
  3) Import from s4_texts.dat<nr> → <LANG>.s4_translation_project
  4) Preview texts from .dat file (interactive encoding testing, option to save test)
  5) Shift text numbers in file A (offset)
  6) Exit
"""
import re
from pathlib import Path
import shutil
import sys

# --- settings and language map (first encoding is default/suggested) ---
TEXT_HEADER_RE = re.compile(r'\s*##\s*Text\s+(\d+)\s*##')

LANG_MAP = {
    0: ("ENGLISH", ["cp1252", "iso-8859-1", "latin1", "ascii", "cp437", "cp850"]),
    1: ("GERMAN", ["cp1252", "iso-8859-1", "iso-8859-15", "cp850"]),
    2: ("FRENCH", ["cp1252", "iso-8859-1", "iso-8859-15", "cp850"]),
    3: ("SPANISH", ["cp1252", "iso-8859-1", "iso-8859-15", "cp850"]),
    4: ("ITALIAN", ["cp1252", "iso-8859-1", "iso-8859-15", "cp850"]),
    5: ("POLISH", ["cp1250", "iso-8859-2", "latin2", "cp852"]),
    6: ("KOREAN", ["cp949", "euc-kr", "ks_c_5601-1987"]),
    7: ("CHINESE",   ["gbk", "cp950", "big5", "big5hkscs"]),
    8: ("SWEDISH", ["cp1252", "iso-8859-1", "iso-8859-15", "cp850"]),
    9: ("DANISH", ["cp1252", "iso-8859-1", "iso-8859-15", "cp850"]),
    10: ("NORWEGIAN", ["cp1252", "iso-8859-1", "iso-8859-15", "cp850"]),
    11: ("HUNGARIAN", ["cp1250", "iso-8859-2", "latin2", "cp852"]),
    12: ("HEBREW", ["cp1255", "iso-8859-8", "cp862"]),
    13: ("CZECH", ["cp1250", "iso-8859-2", "latin2", "cp852"]),
    14: ("FINNISH", ["cp1252", "iso-8859-1", "iso-8859-15", "cp850"]),
    16: ("RUSSIAN", ["cp1251", "koi8-r", "iso-8859-5", "cp866"]),
    17: ("THAI", ["cp874", "iso-8859-11", "tis-620"]),
    18: ("JAPANESE", ["cp932", "shift_jis", "euc-jp", "iso-2022-jp"]),
}

# --- helpers ---
def sanitize_path(s: str) -> Path:
    s = s.strip()
    if (s.startswith('"') and s.endswith('"')) or (s.startswith("'") and s.endswith("'")):
        s = s[1:-1]
    s = s.strip()
    return Path(s).expanduser()


def confirm(prompt, default=True):
    yes = {'y', 'yes', 't', 'true'}
    no = {'n', 'no', 'false'}
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
        print("Please answer yes/no (y/n).")


# --- line-by-line block parser (recognizes empty blocks) ---
def parse_blocks_linewise(text):
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
def build_output_text(header, original_order_ids, a_map, b_map):
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
def read_file(path, encoding='utf-8'):
    data = Path(path).read_bytes()
    text = data.decode(encoding, errors='replace')
    return text.replace('\r\n', '\n').replace('\r', '\n')


def write_file(path, text, encoding='utf-8'):
    normalized = text.replace('\r\n', '\n').replace('\r', '\n')
    with open(path, 'wb') as f:
        f.write(normalized.encode(encoding))


# --- option 1: generate missingtexts.txt ---
def generate_missing_texts(path_a, path_b, encoding='utf-8', out_name='missingtexts.txt'):
    text_a = read_file(path_a, encoding=encoding)
    text_b = read_file(path_b, encoding=encoding)
    _, order_a, map_a = parse_blocks_linewise(text_a)
    _, order_b, map_b = parse_blocks_linewise(text_b)

    missing_ids = []
    parts = []
    parts.append(f'# Missing texts generated from B vs A\n# A: {path_a}\n# B: {path_b}\n\n')

    for idx in order_b:
        b_content = map_b.get(idx, '')
        a_has = idx in map_a
        a_content = map_a.get(idx, '')

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
        if not confirm(f"File {out_path} already exists. Overwrite?", default=False):
            print("Saving missingtexts cancelled.")
            return None, missing_ids

    write_file(out_path, ''.join(parts), encoding=encoding)
    return out_path, missing_ids


# --- option 2: merge ---
def option_merge(path_a, path_b, encoding='utf-8'):
    text_a = read_file(path_a, encoding=encoding)
    text_b = read_file(path_b, encoding=encoding)
    header_a, order_a, map_a = parse_blocks_linewise(text_a)
    header_b, order_b, map_b = parse_blocks_linewise(text_b)

    result_text, replaced, added = build_output_text(header_a, order_a, map_a, map_b)

    print("\nSummary of changes:")
    if replaced:
        print(f" Replaced IDs (from file B): {', '.join(map(str, replaced))}")
    else:
        print(" No replacements (no ID from B existed in A).")
    if added:
        print(f" Added IDs (appended at the end): {', '.join(map(str, added))}")
    else:
        print(" No new IDs to add.")

    print("\nChoose save method:")
    print(" 1) Overwrite file A (a backup will be created)")
    print(" 2) Save as new file (same folder as A, name + _updated)")
    choice = input("Choose 1 or 2 [1]: ").strip() or '1'

    if choice == '1':
        bak = path_a.with_suffix(path_a.suffix + '.bak')
        try:
            shutil.copy2(path_a, bak)
            print(f"Backup created: {bak}")
        except Exception as e:
            print(f"Failed to create backup: {e}")
            if not confirm("Continue without backup?", default=False):
                print("Cancelled.")
                return

        try:
            write_file(path_a, result_text, encoding=encoding)
            print(f"Overwritten file A: {path_a}")
        except Exception as e:
            print(f"Write error: {e}")
            return

    elif choice == '2':
        suggested = path_a.with_name(path_a.stem + '_updated' + path_a.suffix)
        out_path_input = input(f"Output path [{suggested}]: ").strip()
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
                print(f"Failed to create directory {out_dir}: {e}")
                return

        if out_path.exists():
            if not confirm(f"File {out_path} already exists. Overwrite?", default=False):
                print("Cancelled.")
                return

        try:
            write_file(out_path, result_text, encoding=encoding)
            print(f"Saved result to: {out_path}")
        except Exception as e:
            print(f"Write error: {e}")
            return
    else:
        print("Invalid choice. Exiting without saving.")
        return


# --- s4_texts.dat helpers ---
def infer_lang_from_filename(path: Path):
    name = path.name
    m = re.search(r'(\d+)(?=\D*$)', name)
    if m:
        try:
            return int(m.group(1))
        except:
            return None
    return None


def read_s4_dat(path: Path):
    data = path.read_bytes()
    if len(data) < 4:
        raise ValueError("File too short, missing header.")
    header_bytes = data[0:4]
    pos = 4
    texts_bytes = []
    total_len = len(data)
    while pos + 4 <= total_len:
        length = int.from_bytes(data[pos:pos+4], byteorder='little', signed=False)
        pos += 4
        if length < 0:
            raise ValueError("Negative text length (file corrupted).")
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


def decode_text_bytes(b: bytes, lang_num: int):
    """
    Decodes bytes using encodings from LANG_MAP in order.
    Falls back to some universal encodings if needed,
    and finally uses errors='replace'.
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


def option_import_s4(path_dat: Path, encoding_out='utf-8'):
    inferred = infer_lang_from_filename(path_dat)
    if inferred is not None:
        print(f"Language number found in filename: {inferred} (suggestion).")

    while True:
        raw = input(f"Enter language number (e.g. 5 for POLISH). Suggestion: {inferred if inferred is not None else 'none'}: ").strip()
        if raw == '' and inferred is not None:
            lang_num = inferred
            break
        try:
            lang_num = int(raw)
            break
        except ValueError:
            print("Invalid number. Enter an integer (e.g. 5).")

    lang_name = LANG_MAP.get(lang_num, (f"LANG_{lang_num}", ['latin-1']))[0]
    suggested_list = LANG_MAP.get(lang_num, (None, ['latin-1']))[1]
    suggested_encoding = suggested_list[0] if suggested_list else 'latin-1'

    print(f"Selected language: {lang_name} (number {lang_num}), suggested encodings (first is default): {', '.join(suggested_list)}")

    enc_choice = suggested_encoding or ''
    if enc_choice:
        use_sug = input(f"Use suggested encoding '{enc_choice}'? [Y/n]: ").strip().lower()
        if use_sug == '' or use_sug in ('y', 'yes', 't', 'true'):
            chosen_enc = enc_choice
        else:
            chosen_enc = input("Enter input encoding (e.g. big5, cp950, utf-8, cp1251): ").strip() or enc_choice
    else:
        chosen_enc = input("Enter input encoding (e.g. big5, cp950, utf-8, cp1251): ").strip() or 'latin-1'

    try:
        header_bytes, texts_bytes = read_s4_dat(path_dat)
    except Exception as e:
        print(f"Error reading .dat file: {e}")
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
        if not confirm(f"File {out_path} already exists. Overwrite?", default=False):
            print("Saving project file cancelled.")
            return

    try:
        write_file(out_path, ''.join(parts), encoding=encoding_out)
        print(f"Project file saved: {out_path} (output encoding: {encoding_out})")
    except Exception as e:
        print(f"Error saving project file: {e}")

def option_export_proj_to_dat(path_proj: Path = None):
    """
    Exports .s4_translation_project → s4_texts.dat<langnum>
    Format: 4-byte header, then repeated: 4-byte length (little-endian), text data (bytes).
    Exports all texts from 1 to the highest number present in the project.
    Language number suggestion is derived from the project filename (e.g. 'CHINESE' → 7).
    """
    # 1) Get project file path
    if path_proj is None:
        raw = input("Enter path to the .s4_translation_project file: ").strip()
        if not raw:
            print("No path provided. Cancelled.")
            return
        try:
            path_proj = sanitize_path(raw)
        except Exception as e:
            print(f"Invalid path: {e}")
            return

    if not path_proj.exists():
        print(f"File does not exist: {path_proj}")
        return

    # 2) Load and parse project
    try:
        text = read_file(path_proj, encoding='utf-8')
    except Exception as e:
        print(f"Error reading project file: {e}")
        return

    header_text, order, blocks_map = parse_blocks_linewise(text)

    # 3) Try to extract 4-byte header from project header (format @n1 n2 n3 n4@)
    import re
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
                        print(f"Found header in project file: {hb}")
                except Exception:
                    header_bytes = None

    # If not found, ask user for 4 bytes
    if header_bytes is None:
        print("No 4-byte header found in project file.")
        while True:
            raw_hdr = input("Enter 4 numbers (0-255) separated by spaces as header (e.g. '1 2 3 4'): ").strip()
            parts = raw_hdr.split()
            if len(parts) != 4:
                print("Enter exactly 4 numbers.")
                continue
            try:
                nums = [int(x) for x in parts]
                if any(n < 0 or n > 255 for n in nums):
                    print("Numbers must be in range 0-255.")
                    continue
                header_bytes = bytes(nums)
                break
            except ValueError:
                print("Invalid numbers. Try again.")

    # 4) Suggest language number based on project filename
    name_upper = path_proj.name.upper()
    # Build name → number map, sorted by name length descending for better matching
    name_to_num = {v[0].upper(): k for k, v in LANG_MAP.items()}
    candidates = sorted(name_to_num.keys(), key=lambda s: -len(s))
    inferred = None
    for lang_name in candidates:
        if lang_name in name_upper:
            inferred = name_to_num[lang_name]
            break

    # Show list of languages and suggested number (if found)
    print("\nAvailable languages (number : name):")
    for k in sorted(LANG_MAP.keys()):
        print(f" {k} : {LANG_MAP[k][0]}")

    if inferred is not None:
        print(f"\nSuggestion based on filename: {inferred} ({LANG_MAP[inferred][0]})")

    while True:
        raw_lang = input(
            f"Enter language number for export (e.g. 5 for POLISH) "
            f"[{inferred if inferred is not None else ''}]: "
        ).strip()
        if raw_lang == '' and inferred is not None:
            lang_num = inferred
            break
        try:
            lang_num = int(raw_lang)
            if lang_num not in LANG_MAP:
                print("Unknown language number. Try again.")
                continue
            break
        except ValueError:
            print("Enter an integer corresponding to a language number.")

    lang_name = LANG_MAP[lang_num][0]
    enc_candidates = LANG_MAP[lang_num][1][:]
    if 'utf-8' not in enc_candidates:
        enc_candidates.append('utf-8')

    print(f"Selected language: {lang_name} (number {lang_num}). "
          f"Suggested encodings (first is default): {', '.join(enc_candidates)}")

    chosen_enc = enc_candidates[0]
    use_sug = input(f"Use suggested encoding '{chosen_enc}'? [Y/n]: ").strip().lower()
    if use_sug != '' and use_sug not in ('y', 'yes', 't', 'true'):
        custom = input(
            "Enter output encoding (e.g. cp1250, cp950, cp932, cp1251) "
            "or press Enter to use suggested: "
        ).strip()
        if custom:
            chosen_enc = custom

    # 5) Determine max index to export: always 1 to highest existing number
    existing_nums = sorted(blocks_map.keys())
    if existing_nums:
        max_index = max(existing_nums)
    else:
        print("Project file contains no text blocks. Cancelled.")
        return

    print(f"Will export all texts from 1 to {max_index} (last number: {max_index}).")

    # 6) Prepare data: for i=1..max_index → length + data (missing → length 0)
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
            # fallback: try candidates, then latin-1, then utf-8 replace
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

    # 7) Choose output filename (default: s4_texts.dat<langnum>)
    default_out = path_proj.with_name(f"s4_texts.dat{lang_num}")
    out_input = input(f"Output file [{default_out}]: ").strip()
    if out_input == '':
        out_path = default_out
    else:
        out_path = sanitize_path(out_input)

    # 8) Check overwrite
    if out_path.exists():
        if not confirm(f"File {out_path} already exists. Overwrite?", default=False):
            alt = out_path.with_name(out_path.stem + '_exported' + out_path.suffix)
            print(f"Save as: {alt}")
            if not confirm(f"Save as {alt}?", default=True):
                print("Save cancelled.")
                return
            out_path = alt

    # 9) Write binary: header (4 bytes), then for each text: 4-byte length + data
    try:
        with open(out_path, 'wb') as f:
            f.write(header_bytes)
            for b in texts_bytes:
                length = len(b)
                f.write(length.to_bytes(4, byteorder='little', signed=False))
                if length > 0:
                    f.write(b)
    except Exception as e:
        print(f"Error writing .dat file: {e}")
        return

    print(f"\n.dat file saved: {out_path}")
    print(f"Last exported text number: {max_index}")
    print(f"Total texts exported: {len(texts_bytes)}. Empty (length=0): {empty_count}. Encoding: {chosen_enc}")

# --- preview .dat texts with interactive encoding test ---
def option_preview_dat(path_dat: Path):
    inferred = infer_lang_from_filename(path_dat)
    if inferred is not None:
        print(f"Language number found in filename: {inferred} (suggestion).")

    while True:
        raw = input(f"Enter language number (e.g. 5 for POLISH). Suggestion: {inferred if inferred is not None else 'none'}: ").strip()
        if raw == '' and inferred is not None:
            lang_num = inferred
            break
        try:
            lang_num = int(raw)
            break
        except ValueError:
            print("Invalid number. Enter an integer (e.g. 5).")

    lang_name = LANG_MAP.get(lang_num, (f"LANG_{lang_num}", ['latin-1']))[0]
    suggested_list = LANG_MAP.get(lang_num, (None, ['latin-1']))[1]
    print(f"Selected language: {lang_name} (number {lang_num}). Suggested encodings (first is default): {', '.join(suggested_list)}")

    try:
        header_bytes, texts_bytes = read_s4_dat(path_dat)
    except Exception as e:
        print(f"Error reading .dat file: {e}")
        return

    total = len(texts_bytes)
    print(f"File contains {total} texts.")

    while True:
        sel = input(
            "Enter text number (e.g. 57), range (e.g. 60-200), 'all' to show everything, "
            "or 'single' to test one text with all encodings: "
        ).strip().lower()

        if sel == 'all':
            start_idx, end_idx = 1, total
            single_for_all_enc = False
            break

        if sel == 'single':
            while True:
                s2 = input("Enter single text number to test all encodings: ").strip()
                try:
                    idx = int(s2)
                    if idx < 1 or idx > total:
                        print("Number out of range. Try again.")
                        continue
                    start_idx = end_idx = idx
                    single_for_all_enc = True
                    break
                except ValueError:
                    print("Invalid number. Try again.")
            break

        if '-' in sel:
            parts = sel.split('-', 1)
            try:
                start_idx = int(parts[0])
                end_idx = int(parts[1])
                if start_idx < 1 or end_idx < start_idx:
                    print("Invalid range. Try again.")
                    continue
                if start_idx > total:
                    print("Start number out of range. Try again.")
                    continue
                if end_idx > total:
                    end_idx = total
                single_for_all_enc = False
                break
            except ValueError:
                print("Invalid format. Use e.g. 60-200.")
                continue

        else:
            try:
                idx = int(sel)
                if idx < 1 or idx > total:
                    print("Number out of range. Try again.")
                    continue
                start_idx = end_idx = idx
                single_for_all_enc = False
                break
            except ValueError:
                print("Invalid number. Try again.")
                continue

    candidates = LANG_MAP.get(lang_num, (None, ['latin-1']))[1][:]
    for c in ['utf-8', 'latin-1', 'cp1252']:
        if c not in candidates:
            candidates.append(c)

    log_lines = []
    log_lines.append(f"Encoding test for {lang_name} (file: {path_dat})\n")

    if single_for_all_enc:
        idx = start_idx
        b = texts_bytes[idx-1]
        log_lines.append(f"Testing single text #{idx} across encodings\n")

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

        save = input(f"Save encoding test to {lang_name}_encoding_test.txt? [y/N]: ").strip().lower()
        if save in ('y', 'yes', 't', 'true'):
            out_path = path_dat.parent / f"{lang_name}_encoding_test.txt"
            if out_path.exists():
                if not confirm(f"File {out_path} already exists. Overwrite?", default=False):
                    print("Test save cancelled.")
                    return
            try:
                write_file(out_path, '\n'.join(log_lines), encoding='utf-8')
                print(f"Encoding test saved to: {out_path}")
            except Exception as e:
                print(f"Error saving test: {e}")
        else:
            print("Test not saved.")
        print("\nFinished testing all encodings. Returning to menu.")
        return

    # interactive single-encoding testing
    default_enc = candidates[0] if candidates else 'latin-1'
    chosen_enc = default_enc

    while True:
        print("\nSuggested encodings (first is default):")
        for i, c in enumerate(candidates, start=1):
            print(f" {i}) {c}")
        print(" a) enter custom encoding (e.g. big5, cp950, utf-8)")
        print(" m) return to menu")

        sel_enc = input(f"Select encoding to test (default '{default_enc}'): ").strip()

        if sel_enc == '':
            chosen_enc = default_enc
        elif sel_enc.lower() in ('m', 'menu'):
            print("Returning to menu.")
            return
        elif sel_enc.lower() == 'a':
            chosen_enc = input("Enter encoding name (e.g. big5, cp950, utf-8): ").strip()
            if chosen_enc == '':
                chosen_enc = default_enc
        else:
            try:
                idx_choice = int(sel_enc)
                if 1 <= idx_choice <= len(candidates):
                    chosen_enc = candidates[idx_choice-1]
                else:
                    print("Invalid encoding number.")
                    continue
            except ValueError:
                chosen_enc = sel_enc

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

        again = input("Test another encoding for this range? [Y/n]: ").strip().lower()
        if again == '' or again in ('y', 'yes', 't', 'true'):
            continue
        else:
            save = input(f"Save test result to {lang_name}_encoding_test.txt? [y/N]: ").strip().lower()
            if save in ('y', 'yes', 't', 'true'):
                out_path = path_dat.parent / f"{lang_name}_encoding_test.txt"
                if out_path.exists():
                    if not confirm(f"File {out_path} already exists. Overwrite?", default=False):
                        print("Test save cancelled.")
                        return
                try:
                    write_file(out_path, '\n'.join(log_lines), encoding='utf-8')
                    print(f"Encoding test saved to: {out_path}")
                except Exception as e:
                    print(f"Error saving test: {e}")
            else:
                print("Test not saved.")
            print("Returning to menu.")
            return


# --- option 5: shift text IDs ---
def option_shift_ids(path_a, encoding='utf-8'):
    text_a = read_file(path_a, encoding=encoding)
    header_a, order_a, map_a = parse_blocks_linewise(text_a)

    if not order_a:
        print("No '## Text N ##' blocks found in file A. Nothing to shift.")
        return

    first = order_a[0]
    last = order_a[-1]
    count = len(order_a)
    print(f"Found {count} blocks. First number: {first}, last number: {last}.")

    while True:
        raw = input("Enter offset (integer, 0 = cancel): ").strip()
        if raw == '':
            print("No value provided. Cancelled.")
            return
        try:
            offset = int(raw)
        except ValueError:
            print("Please enter an integer (can be negative).")
            continue
        if offset == 0:
            print("Offset = 0 — no action. Cancelled.")
            return
        break

    new_ids = [i + offset for i in order_a]
    if any(i <= 0 for i in new_ids):
        print("Error: after shifting some numbers would be <= 0. Choose different offset.")
        return
    if len(set(new_ids)) != len(new_ids):
        print("Error: after shifting duplicate numbers appeared. Cancelled.")
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

    print("\nChoose save method for shifted file:")
    print(" 1) Overwrite file A (backup will be created)")
    print(" 2) Save as new file (same folder as A, name + _shifted)")
    choice = input("Choose 1 or 2 [2]: ").strip() or '2'

    if choice == '1':
        bak = path_a.with_suffix(path_a.suffix + '.bak')
        try:
            shutil.copy2(path_a, bak)
            print(f"Backup created: {bak}")
        except Exception as e:
            print(f"Failed to create backup: {e}")
            if not confirm("Continue without backup?", default=False):
                print("Cancelled.")
                return

        try:
            write_file(path_a, result_text, encoding=encoding)
            print(f"Overwritten file A: {path_a}")
        except Exception as e:
            print(f"Write error: {e}")
            return

    elif choice == '2':
        suggested = path_a.with_name(path_a.stem + '_shifted' + path_a.suffix)
        out_path_input = input(f"Output path [{suggested}]: ").strip()
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
                print(f"Failed to create directory {out_dir}: {e}")
                return

        if out_path.exists():
            if not confirm(f"File {out_path} already exists. Overwrite?", default=False):
                print("Cancelled.")
                return

        try:
            write_file(out_path, result_text, encoding=encoding)
            print(f"Shifted file saved to: {out_path}")
        except Exception as e:
            print(f"Write error: {e}")
            return
    else:
        print("Invalid choice. Exiting without saving.")
        return

def option_fix_missing_entries(path_proj: Path = None, encoding='utf-8'):
    """
    Adds missing ## Text N ## entries in the project file.
    Asks whether to overwrite the original file or save as a new file <name>_fixed.<ext>.
    """
    # Get path to project file
    if path_proj is None:
        raw = input("Enter path to the .s4_translation_project file: ").strip()
        if not raw:
            print("No path provided. Cancelled.")
            return
        try:
            path_proj = sanitize_path(raw)
        except Exception as e:
            print(f"Invalid path: {e}")
            return

    if not path_proj.exists():
        print(f"File does not exist: {path_proj}")
        return

    # Select range
    while True:
        rng = input("Enter range of numbers to fill (e.g. 1-2000) or single number (e.g. 57): ").strip()
        if not rng:
            print("No range provided. Cancelled.")
            return

        if '-' in rng:
            parts = rng.split('-', 1)
            try:
                start = int(parts[0])
                end = int(parts[1])
                if start < 1 or end < start:
                    print("Invalid range. Try again.")
                    continue
                break
            except ValueError:
                print("Invalid format. Use e.g. 1-2000 or 57.")
                continue
        else:
            try:
                n = int(rng)
                if n < 1:
                    print("Number must be >= 1.")
                    continue
                start = end = n
                break
            except ValueError:
                print("Invalid number. Try again.")
                continue

    # Load and parse the file
    try:
        text = read_file(path_proj, encoding=encoding)
    except Exception as e:
        print(f"Error reading file: {e}")
        return

    header, order, blocks_map = parse_blocks_linewise(text)

    # Collect missing numbers
    missing = []
    for i in range(start, end + 1):
        if i not in blocks_map:
            missing.append(i)

    if not missing:
        print("No missing entries in the specified range. Nothing to do.")
        return

    # Build new content
    existing_nums = sorted(blocks_map.keys())
    min_num = min(existing_nums) if existing_nums else start
    max_num = max(existing_nums) if existing_nums else end

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

    # --- report and save logic ---
    print(f"\nFound {len(added)} missing entries to add.")
    if added:
        print("Added numbers:", ', '.join(map(str, added)))
    else:
        print("No new numbers added (unexpected situation).")

    print("\nDo you want to overwrite the existing file?")
    if confirm("Overwrite file?", default=False):
        try:
            write_file(path_proj, result_text, encoding=encoding)
            print(f"File overwritten: {path_proj}")
        except Exception as e:
            print(f"Write error: {e}")
        return

    # If not overwriting → save as new file
    ext = path_proj.suffix
    stem = path_proj.stem
    new_path = path_proj.with_name(f"{stem}_fixed{ext}")

    print(f"Save as new file: {new_path}?")
    if confirm("Save as new?", default=True):
        try:
            write_file(new_path, result_text, encoding=encoding)
            print(f"New file saved: {new_path}")
        except Exception as e:
            print(f"Write error: {e}")
    else:
        print("Save cancelled.")
      

# --- main menu ---
def main():
    while True:
        print("\n=== Settlers IV translation tool (menu) ===")
        print("Choose an option:")
        print(" 1) Compare A vs B and generate missingtexts.txt (texts from B missing/needing update in A)")
        print(" 2) Merge files: replace existing entries and append missing ones from B to A")
        print(" 3) Import from s4_texts.dat<nr> → generate <LANG>.s4_translation_project")
        print(" 4) Export .s4_translation_project → s4_texts.dat<nr>")
        print(" 5) Preview texts from .dat file (interactive encoding testing)")
        print(" 6) Shift text numbers in file A (offset)")
        print(" 7) Fix missing entries in project file")
        print(" 8) Exit")
        choice = input("Choose 1, 2, 3, 4, 5, 6, 7 or 8 [8]: ").strip() or '8'

        if choice not in {'1', '2', '3', '4', '5', '6', '7', '8'}:
            print("Invalid choice. Try again.")
            continue

        if choice == '8':
            print("Exiting.")
            input("\nPress Enter to close...")
            sys.exit(0)

        if choice == '3':
            raw_dat = input("Enter path to s4_texts.dat<nr> file: ").strip()
            if not raw_dat:
                print("Path to .dat file required. Returning to menu.")
                continue
            try:
                path_dat = sanitize_path(raw_dat)
            except Exception as e:
                print(f"Invalid path: {e}")
                continue
            if not path_dat.exists():
                print(f".dat file does not exist: {path_dat}")
                continue
            option_import_s4(path_dat, encoding_out='utf-8')
            continue

        if choice == '4':
            raw_proj = input("Enter path to .s4_translation_project file to export: ").strip()
            if not raw_proj:
                print("Path to project file required. Returning to menu.")
                continue
            try:
                path_proj = sanitize_path(raw_proj)
            except Exception as e:
                print(f"Invalid path: {e}")
                continue
            if not path_proj.exists():
                print(f"Project file does not exist: {path_proj}")
                continue
            option_export_proj_to_dat(path_proj)
            continue

        if choice == '5':
            raw_dat = input("Enter path to s4_texts.dat<nr> file to preview: ").strip()
            if not raw_dat:
                print("Path to .dat file required. Returning to menu.")
                continue
            try:
                path_dat = sanitize_path(raw_dat)
            except Exception as e:
                print(f"Invalid path: {e}")
                continue
            if not path_dat.exists():
                print(f".dat file does not exist: {path_dat}")
                continue
            option_preview_dat(path_dat)
            continue

        if choice in {'1', '2'}:
            raw_a = input("Enter path to file A (original): ").strip()
            raw_b = input("Enter path to file B (corrections): ").strip()
            if not raw_a or not raw_b:
                print("Files A and B are required for this option. Returning to menu.")
                continue
            try:
                path_a = sanitize_path(raw_a)
                path_b = sanitize_path(raw_b)
            except Exception as e:
                print(f"Invalid path: {e}")
                continue
            if not path_a.exists():
                print(f"File A does not exist: {path_a}")
                continue
            if not path_b.exists():
                print(f"File B does not exist: {path_b}")
                continue
            encoding = input("File encoding (default utf-8): ").strip() or 'utf-8'

            if choice == '1':
                out_name = input("Output filename [missingtexts.txt]: ").strip() or 'missingtexts.txt'
                out_path, missing_ids = generate_missing_texts(path_a, path_b, encoding=encoding, out_name=out_name)
                if out_path is None:
                    print("No missingtexts file saved.")
                else:
                    print(f"Missing texts file saved: {out_path}")
                    if missing_ids:
                        print(f"Number of missing blocks: {len(missing_ids)}. IDs: {', '.join(map(str, missing_ids))}")
                    else:
                        print("No missing blocks (nothing to add).")
            else:
                option_merge(path_a, path_b, encoding=encoding)
            continue

        if choice == '6':
            raw_a2 = input("Enter path to file A (original): ").strip()
            if not raw_a2:
                print("File A required for this option. Returning to menu.")
                continue
            try:
                path_a = sanitize_path(raw_a2)
            except Exception as e:
                print(f"Invalid path: {e}")
                continue
            if not path_a.exists():
                print(f"File A does not exist: {path_a}")
                continue
            encoding = input("File encoding (default utf-8): ").strip() or 'utf-8'
            option_shift_ids(path_a, encoding=encoding)
            continue

        if choice == '7':
            raw_proj = input("Enter path to .s4_translation_project file: ").strip()
            if not raw_proj:
                print("No path provided. Returning to menu.")
                continue
            try:
                path_proj = sanitize_path(raw_proj)
            except Exception as e:
                print(f"Invalid path: {e}")
                continue
            if not path_proj.exists():
                print(f"File does not exist: {path_proj}")
                continue
            option_fix_missing_entries(path_proj, encoding='utf-8')
            continue


if __name__ == '__main__':
    main()
