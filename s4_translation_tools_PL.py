#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Settlers IV translation tool
Opcje:
  1) Porównaj A vs B -> missingtexts.txt
  2) Merge A i B
  3) Import z s4_texts.dat<nr> -> <LANG>.s4_translation_project
  4) Podgląd tekstów z pliku .dat (interaktywne testowanie kodowań, opcja zapisu testu)
  5) Przesuń numery tekstów w pliku A (offset)
  6) Wyjście
"""

import re
from pathlib import Path
import shutil
import sys

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

# --- pomocnicze ---
def sanitize_path(s: str) -> Path:
    s = s.strip()
    if (s.startswith('"') and s.endswith('"')) or (s.startswith("'") and s.endswith("'")):
        s = s[1:-1]
    s = s.strip()
    return Path(s).expanduser()

def confirm(prompt, default=True):
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
        print("Proszę odpowiedzieć tak/nie (y/n).")

# --- parser liniowy (rozpoznaje puste bloki) ---
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
        if not confirm(f"Plik {out_path} już istnieje. Nadpisać?", default=False):
            print("Anulowano zapis missingtexts.")
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

    print("\nPodsumowanie zmian:")
    if replaced:
        print(f"  Podmienione numery (z pliku B): {', '.join(map(str, replaced))}")
    else:
        print("  Brak podmian (żaden numer z B nie występował w A).")
    if added:
        print(f"  Dodane numery (dopisane na końcu): {', '.join(map(str, added))}")
    else:
        print("  Brak nowych numerów do dodania.")

    print("\nWybierz sposób zapisu:")
    print("  1) Nadpisać plik A (zrobiona zostanie kopia zapasowa)")
    print("  2) Zapisz jako nowy plik (ten sam katalog co A, nazwa + _updated)")
    choice = input("Wybierz 1 lub 2 [1]: ").strip() or '1'

    if choice == '1':
        bak = path_a.with_suffix(path_a.suffix + '.bak')
        try:
            shutil.copy2(path_a, bak)
            print(f"Utworzono kopię zapasową: {bak}")
        except Exception as e:
            print(f"Nie udało się utworzyć kopii zapasowej: {e}")
            if not confirm("Kontynuować bez kopii zapasowej?", default=False):
                print("Anulowano.")
                return
        try:
            write_file(path_a, result_text, encoding=encoding)
            print(f"Nadpisano plik A: {path_a}")
        except Exception as e:
            print(f"Błąd zapisu: {e}")
            return
    elif choice == '2':
        suggested = path_a.with_name(path_a.stem + '_updated' + path_a.suffix)
        out_path_input = input(f"Podaj ścieżkę wyjściową [{suggested}]: ").strip()
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
                print(f"Nie udało się utworzyć katalogu {out_dir}: {e}")
                return
        if out_path.exists():
            if not confirm(f"Plik {out_path} już istnieje. Nadpisać?", default=False):
                print("Anulowano.")
                return
        try:
            write_file(out_path, result_text, encoding=encoding)
            print(f"Zapisano wynik do: {out_path}")
        except Exception as e:
            print(f"Błąd zapisu: {e}")
            return
    else:
        print("Nieprawidłowy wybór. Kończę bez zapisu.")
        return

# --- s4_texts.dat import helpers ---
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
        raise ValueError("Plik zbyt krótki, brak nagłówka.")
    header_bytes = data[0:4]
    pos = 4
    texts_bytes = []
    total_len = len(data)
    while pos + 4 <= total_len:
        length = int.from_bytes(data[pos:pos+4], byteorder='little', signed=False)
        pos += 4
        if length < 0:
            raise ValueError("Ujemna długość tekstu (błąd pliku).")
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

def option_import_s4(path_dat: Path, encoding_out='utf-8'):
    inferred = infer_lang_from_filename(path_dat)
    if inferred is not None:
        print(f"Znaleziono numer języka w nazwie pliku: {inferred} (sugestia).")
    while True:
        raw = input(f"Podaj numer języka (np. 5 dla POLISH). Sugestia: {inferred if inferred is not None else 'brak'}: ").strip()
        if raw == '' and inferred is not None:
            lang_num = inferred
            break
        try:
            lang_num = int(raw)
            break
        except ValueError:
            print("Nieprawidłowy numer. Podaj liczbę całkowitą (np. 5).")

    lang_name = LANG_MAP.get(lang_num, (f"LANG_{lang_num}", ['latin-1']))[0]
    suggested_list = LANG_MAP.get(lang_num, (None, ['latin-1']))[1]
    suggested_encoding = suggested_list[0] if suggested_list else 'latin-1'
    print(f"Wybrany język: {lang_name} (numer {lang_num}), sugerowane kodowania (pierwsze domyślne): {', '.join(suggested_list)}")

    enc_choice = suggested_encoding or ''
    if enc_choice:
        use_sug = input(f"Użyć sugerowanego kodowania '{enc_choice}'? [Y/n]: ").strip().lower()
        if use_sug == '' or use_sug in ('y','yes','t','tak'):
            chosen_enc = enc_choice
        else:
            chosen_enc = input("Podaj kodowanie wejściowe (np. big5, cp950, utf-8, cp1251): ").strip() or enc_choice
    else:
        chosen_enc = input("Podaj kodowanie wejściowe (np. big5, cp950, utf-8, cp1251): ").strip() or 'latin-1'

    try:
        header_bytes, texts_bytes = read_s4_dat(path_dat)
    except Exception as e:
        print(f"Błąd odczytu pliku .dat: {e}")
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
        if not confirm(f"Plik {out_path} już istnieje. Nadpisać?", default=False):
            print("Anulowano zapis pliku projektu.")
            return
    try:
        write_file(out_path, ''.join(parts), encoding=encoding_out)
        print(f"Zapisano plik projektu: {out_path} (kodowanie wyjściowe: {encoding_out})")
    except Exception as e:
        print(f"Błąd zapisu pliku projektu: {e}")

# --- podgląd tekstów z pliku .dat z interaktywnym testowaniem kodowań i zapisem testu ---
def option_preview_dat(path_dat: Path):
    inferred = infer_lang_from_filename(path_dat)
    if inferred is not None:
        print(f"Znaleziono numer języka w nazwie pliku: {inferred} (sugestia).")
    while True:
        raw = input(f"Podaj numer języka (np. 5 dla POLISH). Sugestia: {inferred if inferred is not None else 'brak'}: ").strip()
        if raw == '' and inferred is not None:
            lang_num = inferred
            break
        try:
            lang_num = int(raw)
            break
        except ValueError:
            print("Nieprawidłowy numer. Podaj liczbę całkowitą (np. 5).")

    lang_name = LANG_MAP.get(lang_num, (f"LANG_{lang_num}", ['latin-1']))[0]
    suggested_list = LANG_MAP.get(lang_num, (None, ['latin-1']))[1]
    print(f"Wybrany język: {lang_name} (numer {lang_num}). Sugerowane kodowania (pierwsze domyślne): {', '.join(suggested_list)}")

    try:
        header_bytes, texts_bytes = read_s4_dat(path_dat)
    except Exception as e:
        print(f"Błąd odczytu pliku .dat: {e}")
        return

    total = len(texts_bytes)
    print(f"Plik zawiera {total} tekstów.")

    # wybór zakresu lub pojedynczego numeru; jeśli użytkownik wybierze "single" -> można testować wszystkie kodowania
    while True:
        sel = input("Podaj numer tekstu (np. 57), przedział (np. 60-200), 'all' aby wypisać wszystko, lub 'single' aby podać pojedynczy numer do testu wszystkich kodowań: ").strip()
        if sel.lower() == 'all':
            start_idx, end_idx = 1, total
            single_for_all_enc = False
            break
        if sel.lower() == 'single':
            while True:
                s2 = input("Podaj numer pojedynczego tekstu do testu wszystkich kodowań: ").strip()
                try:
                    idx = int(s2)
                    if idx < 1 or idx > total:
                        print("Numer poza zakresem. Spróbuj ponownie.")
                        continue
                    start_idx = end_idx = idx
                    single_for_all_enc = True
                    break
                except ValueError:
                    print("Nieprawidłowy numer. Spróbuj ponownie.")
            break
        if '-' in sel:
            parts = sel.split('-', 1)
            try:
                start_idx = int(parts[0])
                end_idx = int(parts[1])
                if start_idx < 1 or end_idx < start_idx:
                    print("Nieprawidłowy przedział. Spróbuj ponownie.")
                    continue
                if start_idx > total:
                    print("Początkowy numer poza zakresem. Spróbuj ponownie.")
                    continue
                if end_idx > total:
                    end_idx = total
                single_for_all_enc = False
                break
            except ValueError:
                print("Nieprawidłowy format. Użyj np. 60-200.")
                continue
        else:
            try:
                idx = int(sel)
                if idx < 1 or idx > total:
                    print("Numer poza zakresem. Spróbuj ponownie.")
                    continue
                start_idx = end_idx = idx
                single_for_all_enc = False
                break
            except ValueError:
                print("Nieprawidłowy numer. Spróbuj ponownie.")
                continue

    # przygotuj listę kandydatów kodowań
    candidates = LANG_MAP.get(lang_num, (None, ['latin-1']))[1][:]
    for c in ['utf-8', 'latin-1', 'cp1252']:
        if c not in candidates:
            candidates.append(c)

    # log do zapisu (zbieramy teksty, które wypisujemy)
    log_lines = []
    log_lines.append(f"Encoding test for {lang_name} (file: {path_dat})\n")

    # jeśli użytk chce testować wszystkie kodowania:
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
        # zapytaj o zapis
        save = input(f"Czy zapisać wynik testu do pliku {lang_name}_encoding_test.txt? [y/N]: ").strip().lower()
        if save in ('y','yes','t','tak'):
            out_path = path_dat.parent / f"{lang_name}_encoding_test.txt"
            if out_path.exists():
                if not confirm(f"Plik {out_path} już istnieje. Nadpisać?", default=False):
                    print("Anulowano zapis testu.")
                    return
            try:
                write_file(out_path, '\n'.join(log_lines), encoding='utf-8')
                print(f"Zapisano test kodowań do: {out_path}")
            except Exception as e:
                print(f"Błąd zapisu testu: {e}")
        else:
            print("Test nie został zapisany.")
        print("\nKoniec testu wszystkich kodowań. Powrót do menu.")
        return

    # interaktywne testowanie pojedynczych kodowań lub sekwencji
    default_enc = candidates[0] if candidates else 'latin-1'
    chosen_enc = default_enc

    while True:
        print("\nSugerowane kodowania (pierwsze domyślne):")
        for i, c in enumerate(candidates, start=1):
            print(f"  {i}) {c}")
        print("  a) wpisz własne kodowanie (np. big5, cp950, utf-8)")
        print("  m) wróć do menu")

        sel_enc = input(f"Wybierz kodowanie do testu (domyślne '{default_enc}'): ").strip()
        if sel_enc == '':
            chosen_enc = default_enc
        elif sel_enc.lower() in ('m','menu'):
            print("Powrót do menu.")
            return
        elif sel_enc.lower() == 'a':
            chosen_enc = input("Podaj nazwę kodowania (np. big5, cp950, utf-8): ").strip()
            if chosen_enc == '':
                chosen_enc = default_enc
        else:
            try:
                idx_choice = int(sel_enc)
                if 1 <= idx_choice <= len(candidates):
                    chosen_enc = candidates[idx_choice-1]
                else:
                    print("Nieprawidłowy wybór numeru kodowania.")
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
        again = input("Sprawdzić inne kodowanie dla tego zakresu? [Y/n]: ").strip().lower()
        if again == '' or again in ('y','yes','t','tak'):
            continue
        else:
            # zapytaj czy zapisać log testu
            save = input(f"Czy zapisać wynik testu do pliku {lang_name}_encoding_test.txt? [y/N]: ").strip().lower()
            if save in ('y','yes','t','tak'):
                out_path = path_dat.parent / f"{lang_name}_encoding_test.txt"
                if out_path.exists():
                    if not confirm(f"Plik {out_path} już istnieje. Nadpisać?", default=False):
                        print("Anulowano zapis testu.")
                        return
                try:
                    write_file(out_path, '\n'.join(log_lines), encoding='utf-8')
                    print(f"Zapisano test kodowań do: {out_path}")
                except Exception as e:
                    print(f"Błąd zapisu testu: {e}")
            else:
                print("Test nie został zapisany.")
            print("Powrót do menu.")
            return

# --- option 5: shift ids (przesunięcie numerów) ---
def option_shift_ids(path_a, encoding='utf-8'):
    text_a = read_file(path_a, encoding=encoding)
    header_a, order_a, map_a = parse_blocks_linewise(text_a)

    if not order_a:
        print("Nie znaleziono żadnych bloków '## Text N ##' w pliku A. Nic do przesunięcia.")
        return

    first = order_a[0]
    last = order_a[-1]
    count = len(order_a)
    print(f"Znaleziono {count} bloków. Pierwszy numer: {first}, ostatni numer: {last}.")

    while True:
        raw = input("Podaj offset (liczba całkowita, 0 = anuluj): ").strip()
        if raw == '':
            print("Brak wartości. Anulowano.")
            return
        try:
            offset = int(raw)
        except ValueError:
            print("Proszę podać liczbę całkowitą (może być ujemna).")
            continue
        if offset == 0:
            print("Offset = 0 — brak działania. Anulowano.")
            return
        break

    new_ids = [i + offset for i in order_a]
    if any(i <= 0 for i in new_ids):
        print("Błąd: po przesunięciu niektóre numery byłyby mniejsze lub równe 0. Wybierz inny offset.")
        return

    if len(set(new_ids)) != len(new_ids):
        print("Błąd: po przesunięciu wystąpiły duplikaty numerów. Anulowano.")
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

    print("\nWybierz sposób zapisu przesuniętego pliku:")
    print("  1) Nadpisać plik A (zrobiona zostanie kopia zapasowa)")
    print("  2) Zapisz jako nowy plik (ten sam katalog co A, nazwa + _shifted)")
    choice = input("Wybierz 1 lub 2 [2]: ").strip() or '2'

    if choice == '1':
        bak = path_a.with_suffix(path_a.suffix + '.bak')
        try:
            shutil.copy2(path_a, bak)
            print(f"Utworzono kopię zapasową: {bak}")
        except Exception as e:
            print(f"Nie udało się utworzyć kopii zapasowej: {e}")
            if not confirm("Kontynuować bez kopii zapasowej?", default=False):
                print("Anulowano.")
                return
        try:
            write_file(path_a, result_text, encoding=encoding)
            print(f"Nadpisano plik A: {path_a}")
        except Exception as e:
            print(f"Błąd zapisu: {e}")
            return
    elif choice == '2':
        suggested = path_a.with_name(path_a.stem + '_shifted' + path_a.suffix)
        out_path_input = input(f"Podaj ścieżkę wyjściową [{suggested}]: ").strip()
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
                print(f"Nie udało się utworzyć katalogu {out_dir}: {e}")
                return
        if out_path.exists():
            if not confirm(f"Plik {out_path} już istnieje. Nadpisać?", default=False):
                print("Anulowano.")
                return
        try:
            write_file(out_path, result_text, encoding=encoding)
            print(f"Zapisano przesunięty plik do: {out_path}")
        except Exception as e:
            print(f"Błąd zapisu: {e}")
            return
    else:
        print("Nieprawidłowy wybór. Kończę bez zapisu.")
        return
        
def option_fix_missing_entries(path_proj: Path = None, encoding='utf-8'):
    """
    Uzupełnia brakujące wpisy ## Text N ## w pliku projektu.
    Pyta o nadpisanie lub zapis jako nowy plik <nazwa>_fixed.<ext>.
    """
    # pobierz ścieżkę pliku projektu
    if path_proj is None:
        raw = input("Podaj ścieżkę do pliku .s4_translation_project: ").strip()
        if not raw:
            print("Brak ścieżki. Anulowano.")
            return
        try:
            path_proj = sanitize_path(raw)
        except Exception as e:
            print(f"Nieprawidłowa ścieżka: {e}")
            return
    if not path_proj.exists():
        print(f"Plik nie istnieje: {path_proj}")
        return

    # wybór przedziału
    while True:
        rng = input("Podaj przedział numerów do uzupełnienia (np. 1-2000) lub pojedynczy numer (np. 57): ").strip()
        if not rng:
            print("Brak przedziału. Anulowano.")
            return
        if '-' in rng:
            parts = rng.split('-', 1)
            try:
                start = int(parts[0])
                end = int(parts[1])
                if start < 1 or end < start:
                    print("Nieprawidłowy przedział. Spróbuj ponownie.")
                    continue
                break
            except ValueError:
                print("Nieprawidłowy format. Użyj np. 1-2000 lub 57.")
                continue
        else:
            try:
                n = int(rng)
                if n < 1:
                    print("Numer musi być >= 1.")
                    continue
                start = end = n
                break
            except ValueError:
                print("Nieprawidłowy numer. Spróbuj ponownie.")
                continue

    # wczytaj plik i sparsuj bloki
    try:
        text = read_file(path_proj, encoding=encoding)
    except Exception as e:
        print(f"Błąd odczytu pliku: {e}")
        return

    header, order, blocks_map = parse_blocks_linewise(text)

    # zbierz brakujące numery
    missing = []
    for i in range(start, end + 1):
        if i not in blocks_map:
            missing.append(i)

    if not missing:
        print("Brak brakujących wpisów w podanym przedziale. Nic do zrobienia.")
        return

    # budowanie nowej zawartości
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

    # --- raport i logika zapisu ---
    print(f"\nZnaleziono {len(added)} brakujących wpisów do dodania.")
    if added:
        print("Dodane numery:", ', '.join(map(str, added)))
    else:
        print("Brak nowych dodanych numerów (coś poszło nieoczekiwanie).")

    print("\nCzy chcesz nadpisać istniejący plik?")
    if confirm("Nadpisać plik?", default=False):
        try:
            write_file(path_proj, result_text, encoding=encoding)
            print(f"Nadpisano plik: {path_proj}")
        except Exception as e:
            print(f"Błąd zapisu: {e}")
        return

    # jeśli NIE nadpisujemy → zapisz jako nowy
    ext = path_proj.suffix
    stem = path_proj.stem
    new_path = path_proj.with_name(f"{stem}_fixed{ext}")

    print(f"Zapisać jako nowy plik: {new_path}?")
    if confirm("Zapisz jako nowy?", default=True):
        try:
            write_file(new_path, result_text, encoding=encoding)
            print(f"Zapisano nowy plik: {new_path}")
        except Exception as e:
            print(f"Błąd zapisu: {e}")
    else:
        print("Anulowano zapis.")


# --- main menu ---
def main():
    while True:
        print("\n=== Settlers IV translation tool (menu) ===")
        print("Wybierz opcję:")
        print("  1) Porównaj A vs B i wygeneruj missingtexts.txt (teksty z B brakujące/wymagające uzupełnienia w A)")
        print("  2) Połącz pliki (merge): podmień istniejące i dopisz brakujące z B do A")
        print("  3) Import z pliku s4_texts.dat<nr> → wygeneruj <LANG>.s4_translation_project")
        print("  4) Podgląd tekstów z pliku .dat (interaktywne testowanie kodowań)")
        print("  5) Przesuń numery tekstów w pliku A (offset)")
        print("  6) Napraw brakujące wpisy w pliku projektu")
        print("  7) Wyjście")
        choice = input("Wybierz 1, 2, 3, 4, 5, 6 lub 7 [7]: ").strip() or '7'

        if choice not in {'1','2','3','4','5','6','7'}:
            print("Nieprawidłowy wybór. Spróbuj ponownie.")
            continue
        if choice == '7':
            print("Koniec.")
            input("\nNaciśnij Enter, aby zakończyć...")
            sys.exit(0)

        if choice == '3':
            raw_dat = input("Podaj ścieżkę do pliku s4_texts.dat<nr>: ").strip()
            if not raw_dat:
                print("Ścieżka do pliku .dat wymagana. Powrót do menu.")
                continue
            try:
                path_dat = sanitize_path(raw_dat)
            except Exception as e:
                print(f"Nieprawidłowa ścieżka: {e}")
                continue
            if not path_dat.exists():
                print(f"Plik .dat nie istnieje: {path_dat}")
                continue
            option_import_s4(path_dat, encoding_out='utf-8')
            continue

        if choice == '4':
            raw_dat = input("Podaj ścieżkę do pliku s4_texts.dat<nr> do podglądu: ").strip()
            if not raw_dat:
                print("Ścieżka do pliku .dat wymagana. Powrót do menu.")
                continue
            try:
                path_dat = sanitize_path(raw_dat)
            except Exception as e:
                print(f"Nieprawidłowa ścieżka: {e}")
                continue
            if not path_dat.exists():
                print(f"Plik .dat nie istnieje: {path_dat}")
                continue
            option_preview_dat(path_dat)
            continue

        if choice in {'1','2'}:
            raw_a = input("Podaj ścieżkę do pliku A (oryginał): ").strip()
            raw_b = input("Podaj ścieżkę do pliku B (poprawki): ").strip()
            if not raw_a or not raw_b:
                print("Plik A i B są wymagane dla tej opcji. Powrót do menu.")
                continue
            try:
                path_a = sanitize_path(raw_a)
                path_b = sanitize_path(raw_b)
            except Exception as e:
                print(f"Nieprawidłowa ścieżka: {e}")
                continue
            if not path_a.exists():
                print(f"Plik A nie istnieje: {path_a}")
                continue
            if not path_b.exists():
                print(f"Plik B nie istnieje: {path_b}")
                continue
            encoding = input("Kodowanie plików (domyślnie utf-8): ").strip() or 'utf-8'
            if choice == '1':
                out_name = input("Nazwa pliku wynikowego [missingtexts.txt]: ").strip() or 'missingtexts.txt'
                out_path, missing_ids = generate_missing_texts(path_a, path_b, encoding=encoding, out_name=out_name)
                if out_path is None:
                    print("Brak zapisanego pliku missingtexts.")
                else:
                    print(f"Zapisano plik z brakującymi tekstami: {out_path}")
                    if missing_ids:
                        print(f"Liczba brakujących bloków: {len(missing_ids)}. Numery: {', '.join(map(str, missing_ids))}")
                    else:
                        print("Brak brakujących bloków (nic do dopisania).")
            else:
                option_merge(path_a, path_b, encoding=encoding)
            continue

        if choice == '5':
            raw_a2 = input("Podaj ścieżkę do pliku A (oryginał): ").strip()
            if not raw_a2:
                print("Plik A wymagany dla tej opcji. Powrót do menu.")
                continue
            try:
                path_a = sanitize_path(raw_a2)
            except Exception as e:
                print(f"Nieprawidłowa ścieżka: {e}")
                continue
            if not path_a.exists():
                print(f"Plik A nie istnieje: {path_a}")
                continue
            encoding = input("Kodowanie plików (domyślnie utf-8): ").strip() or 'utf-8'
            option_shift_ids(path_a, encoding=encoding)
            continue
            
        if choice == '6':
            raw_proj = input("Podaj ścieżkę do pliku .s4_translation_project: ").strip()
            if not raw_proj:
                print("Brak ścieżki. Powrót do menu.")
                continue
            try:
                path_proj = sanitize_path(raw_proj)
            except Exception as e:
                print(f"Nieprawidłowa ścieżka: {e}")
                continue
            if not path_proj.exists():
                print(f"Plik nie istnieje: {path_proj}")
                continue
            option_fix_missing_entries(path_proj, encoding='utf-8')
            continue

if __name__ == '__main__':
    main()
