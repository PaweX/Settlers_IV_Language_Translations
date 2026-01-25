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
    7: ("CHINESE", ["cp950", "big5", "big5hkscs", "gbk"]),
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


# --- option 4: preview .dat texts with interactive encoding test ---
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


# --- main menu ---
def main():
    while True:
        print("\n=== Settlers IV translation tool (menu) ===")
        print("Choose option:")
        print(" 1) Compare A vs B and generate missingtexts.txt (texts from B missing/needing update in A)")
        print(" 2) Merge files: replace existing and append missing from B to A")
        print(" 3) Import from s4_texts.dat<nr> → generate <LANG>.s4_translation_project")
        print(" 4) Preview texts from .dat file (interactive encoding testing)")
        print(" 5) Shift text numbers in file A (offset)")
        print(" 6) Exit")
        choice = input("Choose 1, 2, 3, 4, 5 or 6 [6]: ").strip() or '6'

        if choice not in {'1','2','3','4','5','6'}:
            print("Invalid choice. Try again.")
            continue

        if choice == '6':
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
                    print(f"Missing texts saved to: {out_path}")
                    if missing_ids:
                        print(f"Number of missing blocks: {len(missing_ids)}. IDs: {', '.join(map(str, missing_ids))}")
                    else:
                        print("No missing blocks (nothing to add).")
            else:
                option_merge(path_a, path_b, encoding=encoding)
            continue

        if choice == '5':
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


if __name__ == '__main__':
    main()
