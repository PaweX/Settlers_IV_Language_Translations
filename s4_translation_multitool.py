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
# Klucze: unikalne identyfikatory komunikatów. Wartości: dict z 'pl', 'en', 'de' itd.

TRANSLATIONS = {'added_numbers': {'de': '  Hinzugefügte Nummern (am Ende angehängt): {}',
                   'en': '  Added numbers (appended at the end): {}',
                   'es': '  Números añadidos (agregados al final): {}',
                   'it': '  Numeri aggiunti (appesi alla fine): {}',
                   'ja': '  追加された番号 (末尾に追加): {}',
                   'pl': '  Dodane numery (dopisane na końcu): {}',
                   'ru': '  Добавленные номера (добавлены в конец): {}',
                   'zh': '  已添加的编号（追加到末尾）：{}'},
 'added_numbers_fix': {'de': 'Hinzugefügte Nummern: {}',
                       'en': 'Added numbers: {}',
                       'es': 'Números añadidos: {}',
                       'it': 'Numeri aggiunti: {}',
                       'ja': '追加された番号: {}',
                       'pl': 'Dodane numery: {}',
                       'ru': 'Добавленные номера: {}',
                       'zh': '已添加的编号：{}'},
 'alignment_report': {'de': '\n--- Ausrichtungsbericht (vor dem Speichern) ---',
                      'en': '\n--- Alignment report (before save) ---',
                      'es': '\n--- Reporte de alineación (antes de guardar) ---',
                      'it': '\n--- Report di allineamento (prima del salvataggio) ---',
                      'ja': '\n--- 調整レポート (保存前) ---',
                      'pl': '\n--- Raport dopasowania (przed zapisem) ---',
                      'ru': '\n--- Отчёт по выравниванию (перед сохранением) ---',
                      'zh': '\n--- 对齐报告（保存前） ---'},
 'all_found': {'de': '\nAlle Texte aus A in B gefunden (zumindest teilweise).',
               'en': '\nAll A texts found in B (at least partially).',
               'es': '\nTodos los textos de A encontrados en B (al menos parcialmente).',
               'it': '\nTutti i testi di A trovati in B (almeno parzialmente).',
               'ja': '\nすべての A テキストが B で見つかりました (少なくとも部分的に)。',
               'pl': '\nWszystkie teksty A znalezione w B (przynajmniej częściowo).',
               'ru': '\nВсе тексты A найдены в B (хотя бы частично).',
               'zh': '\nA 的所有文本均在 B 中找到（至少部分）。'},
 'assigned_by_offset': {'de': 'Anzahl der Einträge, die basierend auf Offset zugewiesen wurden: {}',
                        'en': 'Number of entries assigned based on offset: {}',
                        'es': 'Número de entradas asignadas por offset: {}',
                        'it': "Numero di voci assegnate in base all'offset: {}",
                        'ja': 'オフセットに基づいて割り当てられたエントリの数: {}',
                        'pl': 'Liczba wpisów przypisanych na podstawie offsetu: {}',
                        'ru': 'Количество записей, назначенных по оффсету: {}',
                        'zh': '基于偏移分配的条目数量：{}'},
 'assigned_example': {'de': '  A:{} -> Ziel:{} (Offset {})',
                      'en': '  A:{} -> target:{} (offset {})',
                      'es': '  A:{} → target:{} (offset {})',
                      'it': '  A:{} -> target:{} (offset {})',
                      'ja': '  A:{} -> target:{} (offset {})',
                      'pl': '  A:{} -> target:{} (offset {})',
                      'ru': '  A:{} → target:{} (offset {})',
                      'zh': '  A:{} → target:{} (偏移 {})'},
 'available_langs': {'de': '\nVerfügbare Sprachen (Nummer : Name):',
                     'en': '\nAvailable languages (number : name):',
                     'es': '\nIdiomas disponibles (número : nombre):',
                     'it': '\nLingue disponibili (numero : nome):',
                     'ja': '\n利用可能な言語 (番号 : 名前):',
                     'pl': '\nDostępne języki (numer : nazwa):',
                     'ru': '\nДоступные языки (номер : название):',
                     'zh': '\n可用语言（编号 : 名称）：'},
 'back_to_menu': {'de': '  m) zurück zum Menü',
                  'en': '  m) back to menu',
                  'es': '  m) volver al menú',
                  'it': '  m) torna al menu',
                  'ja': '  m) メニューに戻る',
                  'pl': '  m) wróć do menu',
                  'ru': '  m) вернуться в меню',
                  'zh': '  m) 返回菜单'},
 'back_to_menu_msg': {'de': 'Zurück zum Menü.',
                      'en': 'Back to menu.',
                      'es': 'Volviendo al menú.',
                      'it': 'Ritorno al menu.',
                      'ja': 'メニューに戻る。',
                      'pl': 'Powrót do menu.',
                      'ru': 'Возврат в меню.',
                      'zh': '返回菜单。'},
 'backup_created': {'de': 'Sicherung erstellt: {}',
                    'en': 'Backup created: {}',
                    'es': 'Copia de seguridad creada: {}',
                    'it': 'Creata copia di backup: {}',
                    'ja': 'バックアップを作成しました: {}',
                    'pl': 'Utworzono kopię zapasową: {}',
                    'ru': 'Создана резервная копия: {}',
                    'zh': '已创建备份：{}'},
 'backup_failed': {'de': 'Erstellen der Sicherung fehlgeschlagen: {}',
                   'en': 'Failed to create backup: {}',
                   'es': 'No se pudo crear la copia de seguridad: {}',
                   'it': 'Impossibile creare la copia di backup: {}',
                   'ja': 'バックアップの作成に失敗しました: {}',
                   'pl': 'Nie udało się utworzyć kopii zapasowej: {}',
                   'ru': 'Не удалось создать резервную копию: {}',
                   'zh': '无法创建备份：{}'},
 'blocks_found': {'de': '{} Blöcke gefunden. Erste Nummer: {}, letzte Nummer: {}.',
                  'en': 'Found {} blocks. First number: {}, last number: {}.',
                  'es': 'Encontrados {} bloques. Primer número: {}, último número: {}.',
                  'it': 'Trovati {} blocchi. Primo numero: {}, ultimo numero: {}.',
                  'ja': '{} ブロックが見つかりました。最初の番号: {}, 最後の番号: {}。',
                  'pl': 'Znaleziono {} bloków. Pierwszy numer: {}, ostatni numer: {}.',
                  'ru': 'Найдено {} блоков. Первый номер: {}, последний номер: {}.',
                  'zh': '找到 {} 个块。第一个编号：{}，最后一个编号：{}。'},
 'canceled': {'de': 'Abgebrochen.',
              'en': 'Canceled.',
              'es': 'Cancelado.',
              'it': 'Annullato.',
              'ja': 'キャンセルしました。',
              'pl': 'Anulowano.',
              'ru': 'Отменено.',
              'zh': '已取消。'},
 'canceled_missingtexts': {'de': 'Speichern von missingtexts abgebrochen.',
                           'en': 'Canceled missingtexts save.',
                           'es': 'Guardado de missingtexts cancelado.',
                           'it': 'Salvataggio di missingtexts annullato.',
                           'ja': 'missingtexts の保存をキャンセルしました。',
                           'pl': 'Anulowano zapis missingtexts.',
                           'ru': 'Сохранение missingtexts отменено.',
                           'zh': '已取消 missingtexts 保存。'},
 'canceled_project_save': {'de': 'Speichern der Projektdatei abgebrochen.',
                           'en': 'Canceled project file save.',
                           'es': 'Guardado del archivo de proyecto cancelado.',
                           'it': 'Salvataggio del file di progetto annullato.',
                           'ja': 'プロジェクトファイルの保存をキャンセルしました。',
                           'pl': 'Anulowano zapis pliku projektu.',
                           'ru': 'Сохранение файла проекта отменено.',
                           'zh': '已取消项目文件保存。'},
 'canceled_test_save': {'de': 'Speichern des Tests abgebrochen.',
                        'en': 'Canceled test save.',
                        'es': 'Guardado de la prueba cancelado.',
                        'it': 'Salvataggio del test annullato.',
                        'ja': 'テストの保存をキャンセルしました。',
                        'pl': 'Anulowano zapis testu.',
                        'ru': 'Сохранение теста отменено.',
                        'zh': '已取消测试保存。'},
 'choose_1_or_2': {'de': 'Wählen Sie 1 oder 2 [1]: ',
                   'en': 'Choose 1 or 2 [1]: ',
                   'es': 'Elige 1 o 2 [1]: ',
                   'it': 'Scegli 1 o 2 [1]: ',
                   'ja': '1 または 2 を選択 [1]: ',
                   'pl': 'Wybierz 1 lub 2 [1]: ',
                   'ru': 'Выберите 1 или 2 [1]: ',
                   'zh': '选择 1 或 2 [1]：'},
 'choose_1_or_2_shift': {'de': 'Wählen Sie 1 oder 2 [2]: ',
                         'en': 'Choose 1 or 2 [2]: ',
                         'es': 'Elige 1 o 2 [2]: ',
                         'it': 'Scegli 1 o 2 [2]: ',
                         'ja': '1 または 2 を選択 [2]: ',
                         'pl': 'Wybierz 1 lub 2 [2]: ',
                         'ru': 'Выберите 1 или 2 [2]: ',
                         'zh': '选择 1 或 2 [2]：'},
 'choose_enc_prompt': {'de': "Wählen Sie Kodierung zum Testen (Standard '{}'): ",
                       'en': "Choose encoding to test (default '{}'): ",
                       'es': "Elige la codificación a probar (por defecto '{}'): ",
                       'it': "Scegli la codifica da testare (predefinita '{}'): ",
                       'ja': "テストするエンコーディングを選択 (デフォルト '{}'): ",
                       'pl': "Wybierz kodowanie do testu (domyślne '{}'): ",
                       'ru': "Выберите кодировку для теста (по умолчанию '{}'): ",
                       'zh': "选择要测试的编码（默认 '{}'）："},
 'collision_example': {'de': '  Kollision: A:{} -> Ziel {}',
                       'en': '  collision: A:{} -> target {}',
                       'es': '  colisión: A:{} → target {}',
                       'it': '  collisione: A:{} -> target {}',
                       'ja': '  衝突: A:{} -> target {}',
                       'pl': '  kolizja: A:{} -> target {}',
                       'ru': '  коллизия: A:{} → target {}',
                       'zh': '  冲突：A:{} → target {}'},
 'collisions_warning': {'de': '\nWarnung: Kollisionen bei Zielindizes erkannt (mehrere A trafen dasselbe Ziel).',
                        'en': '\nWarning: detected target index collisions (multiple A hit the same target).',
                        'es': '\n'
                              'Atención: se detectaron colisiones en índices destino (varios A apuntan al mismo '
                              'target).',
                        'it': '\n'
                              'Attenzione: rilevate collisioni negli indici di destinazione (più elementi A puntano '
                              'allo stesso target).',
                        'ja': '\n注意: ターゲットインデックスの衝突を検出しました (複数の A が同じターゲットにヒット)。',
                        'pl': '\nUwaga: wykryto kolizje docelowych indeksów (kilka A trafiło na ten sam target).',
                        'ru': '\n'
                              'Внимание: обнаружены коллизии целевых индексов (несколько A попали на один и тот же '
                              'target).',
                        'zh': '\n注意：检测到目标索引冲突（多个 A 指向同一目标）。'},
 'confirm_save_as': {'de': 'Speichern unter {}?',
                     'en': 'Save as {}?',
                     'es': '¿Guardar como {}?',
                     'it': 'Salvare come {}?',
                     'ja': '{} として保存しますか？',
                     'pl': 'Zapisz jako {}?',
                     'ru': 'Сохранить как {}?',
                     'zh': '是否保存为 {}？'},
 'conflicts': {'de': '\nKonfliktstellen (beide signifikant oder unterschiedlich) — zeige Ähnlichkeitsprozentsatz:',
               'en': '\nConflict places (both significant or differentiated) — showing similarity percentage:',
               'es': '\n'
                     'Lugares de conflicto (ambos significativos o diferenciados) — mostrando porcentaje de similitud:',
               'it': '\n'
                     'Posizioni di conflitto (entrambi significativi o differenti) — mostro la percentuale di '
                     'similarità:',
               'ja': '\n競合箇所 (両方が有意または差異がある) — 類似度の割合を表示:',
               'pl': '\nMiejsca konfliktów (oba znaczące lub zróżnicowane) — pokazuję procent podobieństwa:',
               'ru': '\nМеста конфликтов (оба значимые или различающиеся) — показываю процент схожести:',
               'zh': '\n冲突位置（两者都有意义或差异明显）— 显示相似度百分比：'},
 'continue_without_backup': {'de': 'Ohne Sicherung fortfahren?',
                             'en': 'Continue without backup?',
                             'es': '¿Continuar sin copia de seguridad?',
                             'it': 'Continuare senza backup?',
                             'ja': 'バックアップなしで続行しますか？',
                             'pl': 'Kontynuować bez kopii zapasowej?',
                             'ru': 'Продолжить без резервной копии?',
                             'zh': '是否不创建备份继续？'},
 'custom_enc': {'de': '  a) eigene Kodierung eingeben (z. B. big5, cp950, utf-8)',
                'en': '  a) enter custom encoding (e.g. big5, cp950, utf-8)',
                'es': '  a) escribe una codificación personalizada (ej. big5, cp950, utf-8)',
                'it': '  a) inserisci una codifica personalizzata (es. big5, cp950, utf-8)',
                'ja': '  a) カスタムエンコーディングを入力 (例: big5, cp950, utf-8)',
                'pl': '  a) wpisz własne kodowanie (np. big5, cp950, utf-8)',
                'ru': '  a) ввести свою кодировку (например big5, cp950, utf-8)',
                'zh': '  a) 输入自定义编码（例如 big5, cp950, utf-8）'},
 'custom_enc_prompt': {'de': 'Geben Sie die Ausgabekodierung ein (z. B. cp1250, cp950, cp932, cp1251) oder drücken Sie '
                             'Enter, um den Vorschlag zu verwenden: ',
                       'en': 'Enter output encoding (e.g. cp1250, cp950, cp932, cp1251) or press Enter to use '
                             'suggested: ',
                       'es': 'Ingresa la codificación de salida (ej. cp1250, cp950, cp932, cp1251) o presiona Enter '
                             'para usar la sugerida: ',
                       'it': 'Inserisci la codifica di output (es. cp1250, cp950, cp932, cp1251) o premi Invio per '
                             'usare quella suggerita: ',
                       'ja': '出力エンコーディングを入力 (例: cp1250, cp950, cp932, cp1251) または Enter で提案されたものを利用: ',
                       'pl': 'Podaj kodowanie wyjściowe (np. cp1250, cp950, cp932, cp1251) lub naciśnij Enter aby użyć '
                             'sugerowanego: ',
                       'ru': 'Введите выходную кодировку (например cp1250, cp950, cp932, cp1251) или нажмите Enter для '
                             'использования предложенной: ',
                       'zh': '请输入输出编码（例如 cp1250, cp950, cp932, cp1251）或按 Enter 使用建议的编码：'},
 'custom_enc_prompt_preview': {'de': 'Geben Sie den Kodierungsnamen ein (z. B. big5, cp950, utf-8): ',
                               'en': 'Enter encoding name (e.g. big5, cp950, utf-8): ',
                               'es': 'Ingresa el nombre de la codificación (ej. big5, cp950, utf-8): ',
                               'it': 'Inserisci il nome della codifica (es. big5, cp950, utf-8): ',
                               'ja': 'エンコーディング名を入力 (例: big5, cp950, utf-8): ',
                               'pl': 'Podaj nazwę kodowania (np. big5, cp950, utf-8): ',
                               'ru': 'Введите название кодировки (например big5, cp950, utf-8): ',
                               'zh': '请输入编码名称（例如 big5, cp950, utf-8）：'},
 'dat_read_error': {'de': 'Fehler beim Lesen der .dat-Datei: {}',
                    'en': 'Error reading .dat file: {}',
                    'es': 'Error al leer el archivo .dat: {}',
                    'it': 'Errore di lettura del file .dat: {}',
                    'ja': '.dat ファイルの読み込みエラー: {}',
                    'pl': 'Błąd odczytu pliku .dat: {}',
                    'ru': 'Ошибка чтения файла .dat: {}',
                    'zh': '读取 .dat 文件出错：{}'},
 'dat_saved': {'de': '\n.dat-Datei gespeichert: {}',
               'en': '\nSaved .dat file: {}',
               'es': '\nArchivo .dat guardado: {}',
               'it': '\nFile .dat salvato: {}',
               'ja': '\n.dat ファイルを保存しました: {}',
               'pl': '\nZapisano plik .dat: {}',
               'ru': '\nФайл .dat сохранён: {}',
               'zh': '\n已保存 .dat 文件：{}'},
 'dat_write_error': {'de': 'Fehler beim Schreiben der .dat-Datei: {}',
                     'en': 'Error writing .dat file: {}',
                     'es': 'Error al escribir el archivo .dat: {}',
                     'it': 'Errore di scrittura del file .dat: {}',
                     'ja': '.dat ファイルの書き込みエラー: {}',
                     'pl': 'Błąd zapisu pliku .dat: {}',
                     'ru': 'Ошибка записи файла .dat: {}',
                     'zh': '写入 .dat 文件出错：{}'},
 'dir_create_failed': {'de': 'Verzeichnis {} konnte nicht erstellt werden: {}',
                       'en': 'Failed to create directory {}: {}',
                       'es': 'No se pudo crear la carpeta {}: {}',
                       'it': 'Impossibile creare la cartella {}: {}',
                       'ja': 'ディレクトリ {} の作成に失敗しました: {}',
                       'pl': 'Nie udało się utworzyć katalogu {}: {}',
                       'ru': 'Не удалось создать папку {}: {}',
                       'zh': '无法创建目录 {}：{}'},
 'done': {'de': 'Fertig.',
          'en': 'Done.',
          'es': 'Listo.',
          'it': 'Completato.',
          'ja': '完了。',
          'pl': 'Gotowe.',
          'ru': 'Готово.',
          'zh': '完成。'},
 'duplicates_error': {'de': 'Fehler: Nach Verschiebung traten Duplikate auf. Abgebrochen.',
                      'en': 'Error: after shift, duplicate numbers occurred. Canceled.',
                      'es': 'Error: tras el desplazamiento aparecieron números duplicados. Cancelado.',
                      'it': 'Errore: dopo lo spostamento sono stati trovati numeri duplicati. Annullato.',
                      'ja': 'エラー: シフト後に番号の重複が発生しました。キャンセルしました。',
                      'pl': 'Błąd: po przesunięciu wystąpiły duplikaty numerów. Anulowano.',
                      'ru': 'Ошибка: после сдвига появились дубликаты номеров. Отменено.',
                      'zh': '错误：偏移后出现编号重复。已取消。'},
 'enc_input_prompt': {'de': 'Geben Sie die Eingabekodierung ein (z. B. big5, cp950, utf-8, cp1251): ',
                      'en': 'Enter input encoding (e.g. big5, cp950, utf-8, cp1251): ',
                      'es': 'Ingresa la codificación de entrada (ej. big5, cp950, utf-8, cp1251): ',
                      'it': 'Inserisci la codifica di input (es. big5, cp950, utf-8, cp1251): ',
                      'ja': '入力エンコーディングを入力 (例: big5, cp950, utf-8, cp1251): ',
                      'pl': 'Podaj kodowanie wejściowe (np. big5, cp950, utf-8, cp1251): ',
                      'ru': 'Введите входную кодировку (например big5, cp950, utf-8, cp1251): ',
                      'zh': '请输入输入编码（例如 big5, cp950, utf-8, cp1251）：'},
 'encoding_prompt': {'de': 'Dateikodierung (Standard utf-8): ',
                     'en': 'File encoding (default utf-8): ',
                     'es': 'Codificación de los archivos (predeterminada utf-8): ',
                     'it': 'Codifica dei file (predefinita utf-8): ',
                     'ja': 'ファイルエンコーディング (デフォルト utf-8): ',
                     'pl': 'Kodowanie plików (domyślnie utf-8): ',
                     'ru': 'Кодировка файлов (по умолчанию utf-8): ',
                     'zh': '文件编码（默认 utf-8）：'},
 'end_all_enc_test': {'de': '\nEnde des Tests aller Kodierungen. Zurück zum Menü.',
                      'en': '\nEnd of all encodings test. Back to menu.',
                      'es': '\nFin de la prueba de todas las codificaciones. Volver al menú.',
                      'it': '\nFine del test di tutte le codifiche. Ritorno al menu.',
                      'ja': '\nすべてのエンコーディングテストの終了。メニューに戻る。',
                      'pl': '\nKoniec testu wszystkich kodowań. Powrót do menu.',
                      'ru': '\nКонец теста всех кодировок. Возврат в меню.',
                      'zh': '\n所有编码测试结束。返回菜单。'},
 'exactly_4_numbers': {'de': 'Geben Sie genau 4 Zahlen ein.',
                       'en': 'Enter exactly 4 numbers.',
                       'es': 'Ingresa exactamente 4 números.',
                       'it': 'Inserisci esattamente 4 numeri.',
                       'ja': '正確に 4 つの数字を入力してください。',
                       'pl': 'Podaj dokładnie 4 liczby.',
                       'ru': 'Введите ровно 4 числа.',
                       'zh': '请输入正好 4 个数字。'},
 'exit_message': {'de': 'Beenden.',
                  'en': 'Exit.',
                  'es': 'Fin.',
                  'it': 'Fine.',
                  'ja': '終了。',
                  'pl': 'Koniec.',
                  'ru': 'Конец.',
                  'zh': '结束。'},
 'file_exists_overwrite': {'de': 'Datei {} existiert bereits. Überschreiben?',
                           'en': 'File {} already exists. Overwrite?',
                           'es': 'El archivo {} ya existe. ¿Sobrescribir?',
                           'it': 'Il file {} esiste già. Sovrascrivere?',
                           'ja': 'ファイル {} は既に存在します。上書きしますか？',
                           'pl': 'Plik {} już istnieje. Nadpisać?',
                           'ru': 'Файл {} уже существует. Перезаписать?',
                           'zh': '文件 {} 已存在。是否覆盖？'},
 'file_not_exists': {'de': 'Datei {} existiert nicht: {}',
                     'en': 'File {} does not exist: {}',
                     'es': 'El archivo {} no existe: {}',
                     'it': 'Il file {} non esiste: {}',
                     'ja': 'ファイル {} は存在しません: {}',
                     'pl': 'Plik {} nie istnieje: {}',
                     'ru': 'Файл {} не существует: {}',
                     'zh': '文件 {} 不存在：{}'},
 'file_too_short': {'de': 'Datei zu kurz, kein Header.',
                    'en': 'File too short, no header.',
                    'es': 'Archivo demasiado corto, falta cabecera.',
                    'it': "File troppo corto, manca l'intestazione.",
                    'ja': 'ファイルが短すぎます、ヘッダーがありません。',
                    'pl': 'Plik zbyt krótki, brak nagłówka.',
                    'ru': 'Файл слишком короткий, отсутствует заголовок.',
                    'zh': '文件过短，缺少头部。'},
 'files_count': {'de': 'Datei A: {}  —  Anzahl Blöcke: {}\nDatei B: {}  —  Anzahl Blöcke: {}',
                 'en': 'File A: {}  —  number of blocks: {}\nFile B: {}  —  number of blocks: {}',
                 'es': 'Archivo A: {}  —  número de bloques: {}\nArchivo B: {}  —  número de bloques: {}',
                 'it': 'File A: {}  —  numero di blocchi: {}\nFile B: {}  —  numero di blocchi: {}',
                 'ja': 'ファイル A: {}  —  ブロック数: {}\nファイル B: {}  —  ブロック数: {}',
                 'pl': 'Plik A: {}  —  liczba bloków: {}\nPlik B: {}  —  liczba bloków: {}',
                 'ru': 'Файл A: {}  —  количество блоков: {}\nФайл B: {}  —  количество блоков: {}',
                 'zh': '文件 A：{}  —  块数量：{}\n文件 B：{}  —  块数量：{}'},
 'header_bytes_dat': {'de': '4-Byte-Header: {}',
                      'en': '4-byte header: {}',
                      'es': 'Cabecera de 4 bytes: {}',
                      'it': 'Intestazione di 4 byte: {}',
                      'ja': '4 バイトヘッダー: {}',
                      'pl': 'Nagłówek 4 bajtów: {}',
                      'ru': 'Заголовок 4 байта: {}',
                      'zh': '4 字节头部：{}'},
 'header_found': {'de': 'Header in Projektdatei gefunden: {}',
                  'en': 'Found header in project file: {}',
                  'es': 'Cabecera encontrada en el archivo de proyecto: {}',
                  'it': 'Intestazione trovata nel file di progetto: {}',
                  'ja': 'プロジェクトファイルでヘッダーを見つけました: {}',
                  'pl': 'Znaleziono nagłówek w pliku projektu: {}',
                  'ru': 'Найден заголовок в файле проекта: {}',
                  'zh': '在项目文件中找到头部：{}'},
 'header_not_found': {'de': '4-Byte-Header in Projektdatei nicht gefunden.',
                      'en': 'Header 4 bytes not found in project file.',
                      'es': 'No se encontró cabecera de 4 bytes en el archivo de proyecto.',
                      'it': 'Intestazione di 4 byte non trovata nel file di progetto.',
                      'ja': 'プロジェクトファイルで 4 バイトヘッダーが見つかりませんでした。',
                      'pl': 'Nie znaleziono nagłówka 4 bajtów w pliku projektu.',
                      'ru': 'В файле проекта не найден заголовок из 4 байт.',
                      'zh': '项目文件中未找到 4 字节头部。'},
 'header_prompt': {'de': "Geben Sie 4 Zahlen (0-255) durch Leerzeichen getrennt als Header ein (z. B. '1 2 3 4'): ",
                   'en': "Enter 4 numbers (0-255) separated by spaces as header (e.g. '1 2 3 4'): ",
                   'es': "Ingresa 4 números (0-255) separados por espacios como cabecera (ej. '1 2 3 4'): ",
                   'it': "Inserisci 4 numeri (0-255) separati da spazi come intestazione (es. '1 2 3 4'): ",
                   'ja': "ヘッダーとしてスペースで区切られた 4 つの数字 (0-255) を入力 (例: '1 2 3 4'): ",
                   'pl': "Podaj 4 liczby (0-255) oddzielone spacjami jako nagłówek (np. '1 2 3 4'): ",
                   'ru': "Введите 4 числа (0-255) через пробел как заголовок (например '1 2 3 4'): ",
                   'zh': "请输入 4 个数字（0-255），用空格分隔作为头部（例如 '1 2 3 4'）："},
 'invalid_choice': {'de': 'Ungültige Auswahl. Versuchen Sie es erneut.',
                    'en': 'Invalid choice. Try again.',
                    'es': 'Elección no válida. Intenta de nuevo.',
                    'it': 'Scelta non valida. Riprova.',
                    'ja': '無効な選択。再試行してください。',
                    'pl': 'Nieprawidłowy wybór. Spróbuj ponownie.',
                    'ru': 'Неверный выбор. Попробуйте снова.',
                    'zh': '无效选择。请重试。'},
 'invalid_dat_file': {'de': 'Datei ist keine gültige .dat-Datei (Fehler in Header- oder erster Textstruktur). Geben '
                            'Sie eine gültige Datei ein.',
                      'en': 'File is not a valid .dat file (error in header or first text structure). Enter a valid '
                            'file.',
                      'es': 'El archivo no es un archivo .dat válido (error en estructura de cabecera o primer texto). '
                            'Ingresa un archivo correcto.',
                      'it': "Il file non è un file .dat valido (errore nella struttura dell'intestazione o del primo "
                            'testo). Inserisci un file valido.',
                      'ja': 'ファイルは有効な .dat ファイルではありません (ヘッダーまたは最初のテキスト構造のエラー)。正しいファイルを入力してください。',
                      'pl': 'Plik nie jest poprawnym plikiem .dat (błąd w strukturze nagłówka lub pierwszego tekstu). '
                            'Podaj poprawny plik.',
                      'ru': 'Файл не является корректным файлом .dat (ошибка в структуре заголовка или первого '
                            'текста). Введите корректный файл.',
                      'zh': '文件不是有效的 .dat 文件（头部或第一个文本结构错误）。请输入正确文件。'},
 'invalid_enc_choice': {'de': 'Ungültige Auswahl der Kodierungsnummer.',
                        'en': 'Invalid encoding number choice.',
                        'es': 'Elección de número de codificación no válida.',
                        'it': 'Scelta del numero di codifica non valida.',
                        'ja': 'エンコーディング番号の選択が無効です。',
                        'pl': 'Nieprawidłowy wybór numeru kodowania.',
                        'ru': 'Неверный выбор номера кодировки.',
                        'zh': '编码编号选择无效。'},
 'invalid_format': {'de': 'Ungültiges Format. Verwenden Sie z. B. 60-200.',
                    'en': 'Invalid format. Use e.g. 60-200.',
                    'es': 'Formato no válido. Usa por ejemplo 60-200.',
                    'it': 'Formato non valido. Usa ad es. 60-200.',
                    'ja': '無効な形式。例: 60-200 を使用してください。',
                    'pl': 'Nieprawidłowy format. Użyj np. 60-200.',
                    'ru': 'Неверный формат. Используйте например 60-200.',
                    'zh': '格式无效。请使用例如 60-200。'},
 'invalid_integer': {'de': 'Bitte geben Sie eine Ganzzahl ein (kann negativ sein).',
                     'en': 'Please enter an integer (can be negative).',
                     'es': 'Por favor ingresa un número entero (puede ser negativo).',
                     'it': 'Inserisci un numero intero (può essere negativo).',
                     'ja': '整数を入力してください (負数可)。',
                     'pl': 'Proszę podać liczbę całkowitą (może być ujemna).',
                     'ru': 'Введите целое число (может быть отрицательным).',
                     'zh': '请输入整数（可为负数）。'},
 'invalid_number': {'de': 'Ungültige Nummer. Geben Sie eine Ganzzahl ein (z. B. 5).',
                    'en': 'Invalid number. Enter an integer (e.g. 5).',
                    'es': 'Número no válido. Ingresa un número entero (ej. 5).',
                    'it': 'Numero non valido. Inserisci un numero intero (es. 5).',
                    'ja': '無効な番号。整数を入力してください (例: 5)。',
                    'pl': 'Nieprawidłowy numer. Podaj liczbę całkowitą (np. 5).',
                    'ru': 'Неверный номер. Введите целое число (например 5).',
                    'zh': '无效编号。请输入整数（例如 5）。'},
 'invalid_numbers': {'de': 'Ungültige Zahlen. Versuchen Sie es erneut.',
                     'en': 'Invalid numbers. Try again.',
                     'es': 'Números no válidos. Intenta de nuevo.',
                     'it': 'Numeri non validi. Riprova.',
                     'ja': '無効な数字。再試行してください。',
                     'pl': 'Nieprawidłowe liczby. Spróbuj ponownie.',
                     'ru': 'Неверные числа. Попробуйте снова.',
                     'zh': '无效数字。请重试。'},
 'invalid_path': {'de': 'Ungültiger Pfad: {}',
                  'en': 'Invalid path: {}',
                  'es': 'Ruta no válida: {}',
                  'it': 'Percorso non valido: {}',
                  'ja': '無効なパス: {}',
                  'pl': 'Nieprawidłowa ścieżka: {}',
                  'ru': 'Неверный путь: {}',
                  'zh': '无效路径：{}'},
 'invalid_project_file': {'de': "Datei ist keine gültige Projektdatei (mindestens ein Eintrag '## Text N ## ... ####' "
                                'fehlt). Geben Sie eine gültige Datei ein.',
                          'en': "File is not a valid project file (missing at least one '## Text N ## ... ####' "
                                'entry). Enter a valid file.',
                          'es': "El archivo no es un archivo de proyecto válido (falta al menos una entrada '## Text N "
                                "## ... ####'). Ingresa un archivo correcto.",
                          'it': "Il file non è un file di progetto valido (manca almeno una voce '## Text N ## ... "
                                "####'). Inserisci un file valido.",
                          'ja': "ファイルは有効なプロジェクトファイルではありません (少なくとも 1 つの '## Text N ## ... ####' "
                                'エントリが欠落)。正しいファイルを入力してください。',
                          'pl': "Plik nie jest poprawnym plikiem projektu (brak co najmniej jednego wpisu '## Text N "
                                "## ... ####'). Podaj poprawny plik.",
                          'ru': "Файл не является корректным файлом проекта (отсутствует хотя бы одна запись '## Text "
                                "N ## ... ####'). Введите корректный файл.",
                          'zh': "文件不是有效的项目文件（至少缺少一个 '## Text N ## ... ####' 条目）。请输入正确文件。"},
 'invalid_range': {'de': 'Ungültiger Bereich. Versuchen Sie es erneut.',
                   'en': 'Invalid range. Try again.',
                   'es': 'Rango no válido. Intenta de nuevo.',
                   'it': 'Intervallo non valido. Riprova.',
                   'ja': '無効な範囲。再試行してください。',
                   'pl': 'Nieprawidłowy przedział. Spróbuj ponownie.',
                   'ru': 'Неверный диапазон. Попробуйте снова.',
                   'zh': '无效范围。请重试。'},
 'invalid_range_fix': {'de': 'Ungültiger Bereich. Versuchen Sie es erneut.',
                       'en': 'Invalid range. Try again.',
                       'es': 'Rango no válido. Intenta de nuevo.',
                       'it': 'Intervallo non valido. Riprova.',
                       'ja': '無効な範囲。再試行してください。',
                       'pl': 'Nieprawidłowy przedział. Spróbuj ponownie.',
                       'ru': 'Неверный диапазон. Попробуйте снова.',
                       'zh': '无效范围。请重试。'},
 'invalid_save_choice': {'de': 'Ungültige Auswahl. Beende ohne Speichern.',
                         'en': 'Invalid choice. Ending without saving.',
                         'es': 'Elección no válida. Terminando sin guardar.',
                         'it': 'Scelta non valida. Termino senza salvare.',
                         'ja': '無効な選択。保存せずに終了します。',
                         'pl': 'Nieprawidłowy wybór. Kończę bez zapisu.',
                         'ru': 'Неверный выбор. Завершение без сохранения.',
                         'zh': '无效选择。结束操作，未保存。'},
 'lang_num_from_name': {'de': 'Sprachnummer in Dateinamen gefunden: {} (Vorschlag).',
                        'en': 'Found language number in file name: {} (suggestion).',
                        'es': 'Se encontró número de idioma en el nombre del archivo: {} (sugerencia).',
                        'it': 'Trovato numero lingua nel nome del file: {} (suggerimento).',
                        'ja': 'ファイル名で言語番号が見つかりました: {} (提案)。',
                        'pl': 'Znaleziono numer języka w nazwie pliku: {} (sugestia).',
                        'ru': 'В имени файла найден номер языка: {} (предложение).',
                        'zh': '在文件名中找到语言编号：{}（建议）。'},
 'lang_num_prompt': {'de': 'Geben Sie die Sprachnummer ein (z. B. 5 für POLISH). Vorschlag: {}: ',
                     'en': 'Enter language number (e.g. 5 for POLISH). Suggestion: {}: ',
                     'es': 'Ingresa el número de idioma (ej. 5 para POLISH). Sugerencia: {}: ',
                     'it': 'Inserisci il numero della lingua (es. 5 per POLISH). Suggerimento: {}: ',
                     'ja': '言語番号を入力 (例: 5 で POLISH)。提案: {}: ',
                     'pl': 'Podaj numer języka (np. 5 dla POLISH). Sugestia: {}: ',
                     'ru': 'Введите номер языка (например 5 для POLISH). Предложение: {}: ',
                     'zh': '请输入语言编号（例如 5 表示 POLISH）。建议：{}：'},
 'lang_num_save_prompt': {'de': 'Geben Sie die Sprachnummer zum Speichern ein (z. B. 5 für POLISH) [{}]: ',
                          'en': 'Enter language number for save (e.g. 5 for POLISH) [{}]: ',
                          'es': 'Ingresa el número de idioma para guardar (ej. 5 para POLISH) [{}]: ',
                          'it': 'Inserisci il numero della lingua per il salvataggio (es. 5 per POLISH) [{}]: ',
                          'ja': '保存用の言語番号を入力 (例: 5 で POLISH) [{}]: ',
                          'pl': 'Podaj numer języka do zapisu (np. 5 dla POLISH) [{}]: ',
                          'ru': 'Введите номер языка для сохранения (например 5 для POLISH) [{}]: ',
                          'zh': '请输入要保存的语言编号（例如 5 表示 POLISH）[{}]：'},
 'lang_suggestion': {'de': '\nVorschlag basierend auf Dateinamen: {} ({})',
                     'en': '\nSuggestion based on file name: {} ({})',
                     'es': '\nSugerencia basada en el nombre del archivo: {} ({})',
                     'it': '\nSuggerimento basato sul nome del file: {} ({})',
                     'ja': '\nファイル名に基づく提案: {} ({})',
                     'pl': '\nSugestia na podstawie nazwy pliku: {} ({})',
                     'ru': '\nПредложение на основе имени файла: {} ({})',
                     'zh': '\n基于文件名的建议：{} ({})'},
 'last_a_num': {'de': 'Letzte verarbeitete A-Nummer: {}',
                'en': 'Last A number processed: {}',
                'es': 'Último número A procesado: {}',
                'it': 'Ultimo numero A elaborato: {}',
                'ja': '処理された最後の A 番号: {}',
                'pl': 'Ostatni numer A przetworzony: {}',
                'ru': 'Последний обработанный номер A: {}',
                'zh': '最后处理的 A 编号：{}'},
 'last_text_num': {'de': 'Letzte gespeicherte Textnummer: {}',
                   'en': 'Last saved text number: {}',
                   'es': 'Último número de texto guardado: {}',
                   'it': 'Ultimo numero di testo salvato: {}',
                   'ja': '最後に保存されたテキスト番号: {}',
                   'pl': 'Ostatni zapisany numer tekstu: {}',
                   'ru': 'Последний сохранённый номер текста: {}',
                   'zh': '最后保存的文本编号：{}'},
 'main_menu_options': {'de': 'Wählen Sie eine Option:\n'
                             '  1) Projektdateien A vs B vergleichen und missingtexts.txt generieren (Texte aus B, die '
                             'in A fehlen oder ergänzt werden müssen)\n'
                             '  2) Projektdateien zusammenführen (merge): vorhandene ersetzen und fehlende aus B zu A '
                             'hinzufügen\n'
                             '  3) Aus Datei s4_texts.dat<nr> importieren → <LANG>.s4_translation_project generieren\n'
                             '  4) .s4_translation_project exportieren → s4_texts.dat<nr>\n'
                             '  5) Texte aus .dat-Datei anzeigen (interaktives Testen von Kodierungen)\n'
                             '  6) Textnummern in Projektdatei A verschieben (Offset)\n'
                             '  7) Fehlende Einträge in Projektdatei reparieren\n'
                             '  8) Textnummern in Projektdatei A an B anpassen (align A ← B)\n'
                             '  9) Verschiebungsmappe auf Projektdatei A anwenden (Mapping aus .txt-Datei)\n'
                             '  0) Beenden',
                       'en': 'Choose an option:\n'
                             '  1) Compare A vs B project files and generate missingtexts.txt (texts from B '
                             'missing/requiring completion in A)\n'
                             '  2) Merge project files: replace existing and append missing from B to A\n'
                             '  3) Import from s4_texts.dat<nr> → generate <LANG>.s4_translation_project\n'
                             '  4) Export .s4_translation_project → s4_texts.dat<nr>\n'
                             '  5) Preview texts from .dat file (interactive encoding testing)\n'
                             '  6) Shift text numbers in project file A (offset)\n'
                             '  7) Fix missing entries in project file\n'
                             '  8) Align text numbers in project file A to B (align A ← B)\n'
                             '  9) Apply shift-map to project file A (mapping from .txt file)\n'
                             '  0) Exit',
                       'es': 'Elige una opción:\n'
                             '  1) Comparar archivos de proyecto A vs B y generar missingtexts.txt (textos de B que '
                             'faltan o necesitan completarse en A)\n'
                             '  2) Combinar archivos de proyecto (merge): reemplazar existentes y añadir los faltantes '
                             'de B a A\n'
                             '  3) Importar desde archivo s4_texts.dat<nr> → generar <LANG>.s4_translation_project\n'
                             '  4) Exportar archivo .s4_translation_project → s4_texts.dat<nr>\n'
                             '  5) Vista previa de textos desde archivo .dat (prueba interactiva de codificaciones)\n'
                             '  6) Desplazar números de texto en el archivo de proyecto A (offset)\n'
                             '  7) Reparar entradas faltantes en el archivo de proyecto\n'
                             '  8) Alinear números de texto del archivo de proyecto A con B (alinear A ← B)\n'
                             '  9) Aplicar mapa de desplazamientos al archivo de proyecto A (mapa desde archivo .txt)\n'
                             '  0) Salir',
                       'it': "Scegli un'opzione:\n"
                             '  1) Confronta i file di progetto A vs B e genera missingtexts.txt (testi presenti in B '
                             'ma mancanti o da completare in A)\n'
                             '  2) Unisci i file di progetto (merge): sostituisci gli esistenti e aggiungi quelli m '
                             'mancanti da B ad A\n'
                             '  3) Importa da file s4_texts.dat<nr> → genera <LANG>.s4_translation_project\n'
                             '  4) Esporta file .s4_translation_project → s4_texts.dat<nr>\n'
                             '  5) Anteprima dei testi dal file .dat (test interattivo delle codifiche)\n'
                             '  6) Sposta i numeri dei testi nel file di progetto A (offset)\n'
                             '  7) Ripara le voci mancanti nel file di progetto\n'
                             '  8) Allinea i numeri dei testi nel file di progetto A a B (allinea A ← B)\n'
                             '  9) Applica una mappa di offset al file di progetto A (mappa da file .txt)\n'
                             '  0) Esci',
                       'ja': 'オプションを選択:\n'
                             '  1) プロジェクトファイル A vs B を比較し missingtexts.txt を生成 (B に欠落/補完が必要なテキスト)\n'
                             '  2) プロジェクトファイルをマージ: 既存を置換し B から欠落分を A に追加\n'
                             '  3) s4_texts.dat<nr> からインポート → <LANG>.s4_translation_project を生成\n'
                             '  4) .s4_translation_project をエクスポート → s4_texts.dat<nr>\n'
                             '  5) .dat ファイルのテキストをプレビュー (エンコーディングのインタラクティブテスト)\n'
                             '  6) プロジェクトファイル A のテキスト番号をオフセット移動\n'
                             '  7) プロジェクトファイルの欠落エントリを修復\n'
                             '  8) プロジェクトファイル A のテキスト番号を B に合わせる (align A ← B)\n'
                             '  9) 番号シフトマップをプロジェクトファイル A に適用 (.txt ファイルのマップ)\n'
                             '  0) 終了',
                       'pl': 'Wybierz opcję:\n'
                             '  1) Porównaj pliki projektu A vs B i wygeneruj missingtexts.txt (teksty z B '
                             'brakujące/wymagające uzupełnienia w A)\n'
                             '  2) Połącz pliki projektu (merge): podmień istniejące i dopisz brakujące z B do A\n'
                             '  3) Import z pliku s4_texts.dat<nr> → wygeneruj <LANG>.s4_translation_project\n'
                             '  4) Eksport pliku .s4_translation_project → s4_texts.dat<nr>\n'
                             '  5) Podgląd tekstów z pliku .dat (interaktywne testowanie kodowań)\n'
                             '  6) Przesuń numery tekstów w pliku projektu A (offset)\n'
                             '  7) Napraw brakujące wpisy w pliku projektu\n'
                             '  8) Dopasuj numery tekstów w pliku projektu A do B (align A ← B)\n'
                             '  9) Zastosuj mapę przesunięć numerów do pliku projektu A (mapa w pliku .txt)\n'
                             '  0) Wyjście',
                       'ru': 'Выберите опцию:\n'
                             '  1) Сравнить файлы проектов A vs B и сгенерировать missingtexts.txt (тексты из B, '
                             'отсутствующие или требующие дополнения в A)\n'
                             '  2) Объединить файлы проектов (merge): заменить существующие и добавить недостающие из '
                             'B в A\n'
                             '  3) Импорт из файла s4_texts.dat<nr> → сгенерировать <LANG>.s4_translation_project\n'
                             '  4) Экспорт файла .s4_translation_project → s4_texts.dat<nr>\n'
                             '  5) Предпросмотр текстов из файла .dat (интерактивное тестирование кодировок)\n'
                             '  6) Сдвинуть номера текстов в файле проекта A (offset)\n'
                             '  7) Исправить отсутствующие записи в файле проекта\n'
                             '  8) Выровнять номера текстов в файле проекта A по файлу B (align A ← B)\n'
                             '  9) Применить карту смещений к файлу проекта A (карта из .txt файла)\n'
                             '  0) Выход',
                       'zh': '选择一个选项：\n'
                             '  1) 比较项目文件 A 与 B 并生成 missingtexts.txt（B 中缺失或需要在 A 中补充的文本）\n'
                             '  2) 合并项目文件（merge）：替换现有内容并从 B 追加缺失内容到 A\n'
                             '  3) 从 s4_texts.dat<nr> 导入 → 生成 <LANG>.s4_translation_project\n'
                             '  4) 导出 .s4_translation_project → s4_texts.dat<nr>\n'
                             '  5) 预览 .dat 文件中的文本（交互式编码测试）\n'
                             '  6) 在项目文件 A 中偏移文本编号\n'
                             '  7) 修复项目文件中缺失的条目\n'
                             '  8) 将项目文件 A 的文本编号对齐到 B（对齐 A ← B）\n'
                             '  9) 将偏移映射应用到项目文件 A（来自 .txt 文件的映射）\n'
                             '  0) 退出'},
 'main_menu_prompt': {'de': 'Wählen Sie 1, 2, 3, 4, 5, 6, 7, 8 oder 9 [9]: ',
                      'en': 'Choose 1, 2, 3, 4, 5, 6, 7, 8 or 9 [9]: ',
                      'es': 'Elige 1, 2, 3, 4, 5, 6, 7, 8 o 9 [9]: ',
                      'it': 'Scegli 1, 2, 3, 4, 5, 6, 7, 8 o 9 [9]: ',
                      'ja': '1, 2, 3, 4, 5, 6, 7, 8 または 9 を選択 [9]: ',
                      'pl': 'Wybierz 1, 2, 3, 4, 5, 6, 7, 8 lub 9 [9]: ',
                      'ru': 'Выберите 1, 2, 3, 4, 5, 6, 7, 8 или 9 [9]: ',
                      'zh': '选择 1、2、3、4、5、6、7、8 或 9 [9]：'},
 'main_menu_title': {'de': '\n=== Settlers IV Übersetzungs-Multitool (Menü) ===',
                     'en': '\n=== Settlers IV Translation Multitool (menu) ===',
                     'es': '\n=== Settlers IV Translation Multitool (menú) ===',
                     'it': '\n=== Settlers IV Translation Multitool (menu) ===',
                     'ja': '\n=== Settlers IV 翻訳マルチツール (メニュー) ===',
                     'pl': '\n=== Settlers IV Translation Multitool (menu) ===',
                     'ru': '\n=== Settlers IV Translation Multitool (меню) ===',
                     'zh': '\n=== Settlers IV 翻译多功能工具 (菜单) ==='},
 'map_apply_changes_count': {'de': 'Anzahl der erzeugten Einträge: {0}',
                             'en': 'Number of generated entries: {0}',
                             'es': 'Número de entradas generadas: {0}',
                             'it': 'Numero di voci generate: {0}',
                             'ja': '生成されたエントリの数: {0}',
                             'pl': 'Liczba wygenerowanych wpisów: {0}',
                             'ru': 'Количество созданных записей: {0}',
                             'zh': '生成的条目数量: {0}'},
 'map_apply_changes_list': {'de': 'Angewendete Verschiebungen (A:<Nummer> Offset <Wert>):',
                            'en': 'Applied shifts (A:<number> offset <value>):',
                            'es': 'Desplazamientos aplicados (A:<número> offset <valor>):',
                            'it': 'Offset applicati (A:<numero> offset <valore>):',
                            'ja': '適用されたシフト (A:<番号> offset <値>):',
                            'pl': 'Zastosowane przesunięcia (A:<numer> offset <wartość>):',
                            'ru': 'Применённые смещения (A:<номер> offset <значение>):',
                            'zh': '应用的偏移 (A:<编号> offset <值>):'},
 'map_apply_collisions': {'de': '{0} Zielindex-Kollisionen erkannt:',
                          'en': '{0} target index collisions detected:',
                          'es': 'Detectadas {0} colisiones de índices de destino:',
                          'it': 'Rilevate {0} collisioni di indici di destinazione:',
                          'ja': '{0} 個のターゲット番号の衝突を検出:',
                          'pl': 'Wykryto {0} kolizji numerów docelowych:',
                          'ru': 'Обнаружено {0} конфликтов целевых индексов:',
                          'zh': '检测到 {0} 个目标索引冲突:'},
 'map_apply_done': {'de': 'Verschiebungsmappe angewendet.',
                    'en': 'Shift map applied.',
                    'es': 'Mapa de desplazamientos aplicada.',
                    'it': 'Mappa degli offset applicata.',
                    'ja': 'シフトマップを適用しました。',
                    'pl': 'Zastosowano mapę przesunięć.',
                    'ru': 'Карта смещений применена.',
                    'zh': '偏移映射已应用。'},
 'map_apply_error': {'de': 'Fehler beim Anwenden der Mapping-Datei: {0}',
                     'en': 'Error applying map: {0}',
                     'es': 'Error al aplicar el mapa: {0}',
                     'it': 'Errore durante l’applicazione della mappa: {0}',
                     'ja': 'マップ適用中のエラー: {0}',
                     'pl': 'Błąd podczas stosowania mapy: {0}',
                     'ru': 'Ошибка при применении карты: {0}',
                     'zh': '应用映射时出错: {0}'},
 'map_apply_preview': {'de': '--- Vorschau der Änderungen aus der Verschiebungsmappe ---',
                       'en': '--- Preview of changes from the shift map ---',
                       'es': '--- Vista previa de los cambios del mapa de desplazamientos ---',
                       'it': '--- Anteprima delle modifiche dalla mappa degli offset ---',
                       'ja': '--- シフトマップによる変更のプレビュー ---',
                       'pl': '--- Podgląd zmian wynikających z mapy przesunięć ---',
                       'ru': '--- Предварительный просмотр изменений по карте смещений ---',
                       'zh': '--- 偏移映射更改预览 ---'},
 'map_empty': {'de': 'Die Mapping-Datei ist leer oder enthält keine gültigen Einträge.',
               'en': 'The map file is empty or contains no valid entries.',
               'es': 'El archivo de mapa está vacío o no contiene entradas válidas.',
               'it': 'Il file di mappa è vuoto o non contiene voci valide.',
               'ja': 'マップファイルが空か、エントリがありません。',
               'pl': 'Plik mapy jest pusty lub nie zawiera żadnych wpisów.',
               'ru': 'Файл карты пуст или не содержит допустимых записей.',
               'zh': '映射文件为空或不包含有效条目。'},
 'map_file_fix_and_retry': {'de': 'Korrigieren Sie das Format der Mapping-Datei und versuchen Sie es erneut.',
                            'en': 'Fix the map file format and try again.',
                            'es': 'Corrija el formato del archivo de mapa y vuelva a intentarlo.',
                            'it': 'Correggi il formato del file di mappa e riprova.',
                            'ja': 'マップファイルの形式を修正して再試行してください。',
                            'pl': 'Popraw format pliku mapy i spróbuj ponownie.',
                            'ru': 'Исправьте формат файла карты и попробуйте снова.',
                            'zh': '请修复映射文件格式后重试。'},
 'map_file_invalid_lines': {'de': 'Die Mapping-Datei enthält ungültige Zeilen:',
                            'en': 'The map file contains invalid lines:',
                            'es': 'El archivo de mapa contiene líneas no válidas:',
                            'it': 'Il file di mappa contiene righe non valide:',
                            'ja': 'マップファイルに無効な行があります:',
                            'pl': 'Plik mapy zawiera nieprawidłowe linie:',
                            'ru': 'Файл карты содержит недопустимые строки:',
                            'zh': '映射文件包含无效行:'},
 'map_file_prompt': {'de': 'Pfad zur Mapping-Datei eingeben (Enter = manuell einfügen): ',
                     'en': 'Enter path to map file (Enter = paste manually): ',
                     'es': 'Introduzca la ruta del archivo de mapa (Enter = pegar manualmente): ',
                     'it': 'Inserisci il percorso del file di mappa (Invio = incolla manualmente): ',
                     'ja': 'マップファイルのパスを入力 (Enter = 手動でマップを貼り付け): ',
                     'pl': 'Podaj ścieżkę do pliku mapy (Enter = wklej mapę ręcznie): ',
                     'ru': 'Укажите путь к файлу карты (Enter = вставить вручную): ',
                     'zh': '输入映射文件路径（回车 = 手动粘贴）: '},
 'map_line_unparsed': {'de': 'Kann die Mapping-Zeile nicht interpretieren: {0}',
                       'en': 'Cannot interpret map line: {0}',
                       'es': 'No se puede interpretar la línea del mapa: {0}',
                       'it': 'Impossibile interpretare la riga della mappa: {0}',
                       'ja': 'マップ行の解釈に失敗: {0}',
                       'pl': 'Nie można zinterpretować linii mapy: {0}',
                       'ru': 'Не удалось интерпретировать строку карты: {0}',
                       'zh': '无法解析映射行: {0}'},
 'map_no_valid_entries': {'de': 'Keine gültigen Einträge in der Verschiebungsmappe gefunden.',
                          'en': 'No valid entries found in the shift map.',
                          'es': 'No se encontraron entradas válidas en el mapa de desplazamientos.',
                          'it': 'Nessuna voce valida trovata nella mappa degli offset.',
                          'ja': 'シフトマップに有効なエントリがありません。',
                          'pl': 'Brak poprawnych wpisów w mapie przesunięć.',
                          'ru': 'В карте смещений не найдено допустимых записей.',
                          'zh': '偏移映射中未找到有效条目。'},
 'map_read_error': {'de': 'Fehler beim Lesen der Mapping-Datei: {0}',
                    'en': 'Error reading map file: {0}',
                    'es': 'Error al leer el archivo de mapa: {0}',
                    'it': 'Errore durante la lettura del file di mappa: {0}',
                    'ja': 'マップファイルの読み込みエラー: {0}',
                    'pl': 'Błąd podczas odczytu pliku mapy: {0}',
                    'ru': 'Ошибка при чтении файла карты: {0}',
                    'zh': '读取映射文件时出错: {0}'},
 'matched_pairs_count': {'de': 'Anzahl übereinstimmender Paare: {}',
                         'en': 'Number of matched pairs: {}',
                         'es': 'Número de pares coincidentes: {}',
                         'it': 'Numero di coppie corrispondenti: {}',
                         'ja': '一致したペアの数: {}',
                         'pl': 'Liczba dopasowanych par: {}',
                         'ru': 'Количество совпавших пар: {}',
                         'zh': '匹配对数量：{}'},
 'matched_ranges': {'de': 'Übereinstimmende Bereiche (A_Start-A_Ende => B_Start-B_Ende) mit Offset:',
                    'en': 'Matched ranges (A_start-A_end => B_start-B_end) with offset:',
                    'es': 'Rangos coincidentes (A_inicio-A_fin => B_inicio-B_fin) con offset:',
                    'it': 'Intervalli corrispondenti (A_inizio-A_fine => B_inizio-B_fine) con offset:',
                    'ja': 'オフセット付きの一致した範囲 (A_start-A_end => B_start-B_end):',
                    'pl': 'Dopasowane przedziały (A_start-A_end => B_start-B_end) z offsetem:',
                    'ru': 'Совпавшие диапазоны (A_начало-A_конец => B_начало-B_конец) с оффсетом:',
                    'zh': '匹配范围（A_开始-A_结束 => B_开始-B_结束）带偏移：'},
 'max_tries_prompt': {'de': 'Wie viele Verschiebungsversuche in A beim Suchen nach signifikantem Text verwenden? '
                            '[Standard {}]: ',
                      'en': 'How many shift attempts in A to use when searching for significant text? [default {}]: ',
                      'es': '¿Cuántos intentos de desplazamiento en A usar al buscar texto significativo? [por defecto '
                            '{}]: ',
                      'it': 'Quanti tentativi di spostamento in A usare nella ricerca di testo significativo? '
                            '[predefinito {}]: ',
                      'ja': '有意なテキスト検索時に A で使用するシフト試行回数？ [デフォルト {}]: ',
                      'pl': 'Ile prób przesunięcia w A użyć przy szukaniu znaczącego tekstu? [domyślnie {}]: ',
                      'ru': 'Сколько попыток сдвига в A использовать при поиске значимого текста? [по умолчанию {}]: ',
                      'zh': '在搜索有意义文本时，在 A 中使用多少次偏移尝试？[默认 {}]：'},
 'mb_guess_not_exist': {'de': 'mb_guess existiert nicht in B',
                        'en': 'mb_guess does not exist in B',
                        'es': 'mb_guess no existe en B',
                        'it': 'mb_guess non esiste in B',
                        'ja': 'mb_guess は B に存在しません',
                        'pl': 'mb_guess nie istnieje w B',
                        'ru': 'mb_guess не существует в B',
                        'zh': 'mb_guess 在 B 中不存在'},
 'missing_blocks_count': {'de': 'Anzahl fehlender Blöcke: {}. Nummern: {}',
                          'en': 'Number of missing blocks: {}. Numbers: {}',
                          'es': 'Número de bloques faltantes: {}. Números: {}',
                          'it': 'Numero di blocchi mancanti: {}. Numeri: {}',
                          'ja': '欠落ブロックの数: {}. 番号: {}',
                          'pl': 'Liczba brakujących bloków: {}. Numery: {}',
                          'ru': 'Количество отсутствующих блоков: {}. Номера: {}',
                          'zh': '缺失块数量：{}。编号：{}'},
 'missing_details': {'de': '\n'
                           'Details zu A-Texten, die nicht direkt in B gefunden wurden (Vergleich mit vermuteten '
                           'B-Texten):',
                     'en': '\nDetails for A texts not directly found in B (attempt to compare with guessed B texts):',
                     'es': '\n'
                           'Detalles de textos de A no encontrados directamente en B (intento de comparación con '
                           'textos supuestos de B):',
                     'it': '\n'
                           'Dettagli per i testi di A non trovati direttamente in B (tentativo di confronto con testi '
                           'presunti di B):',
                     'ja': '\nB で直接見つからなかった A テキストの詳細 (B の推測テキストとの比較試行):',
                     'pl': '\n'
                           'Szczegóły dla tekstów A nieznalezionych bezpośrednio w B (próba porównania z domniemanymi '
                           'tekstami z B):',
                     'ru': '\n'
                           'Детали текстов A, не найденных напрямую в B (попытка сравнения с предполагаемыми текстами '
                           'B):',
                     'zh': '\nA 中直接未在 B 中找到的文本详情（尝试与推测的 B 文本比较）：'},
 'missing_found': {'de': '\n{} fehlende Einträge zum Hinzufügen gefunden.',
                   'en': '\nFound {} missing entries to add.',
                   'es': '\nEncontradas {} entradas faltantes para añadir.',
                   'it': '\nTrovate {} voci mancanti da aggiungere.',
                   'ja': '\n追加する {} 個の欠落エントリが見つかりました。',
                   'pl': '\nZnaleziono {} brakujących wpisów do dodania.',
                   'ru': '\nНайдено {} отсутствующих записей для добавления.',
                   'zh': '\n找到 {} 个缺失条目需要添加。'},
 'missing_in_b': {'de': '\nTexte aus A nicht in B gefunden (einzelne Nummern oder Bereiche):',
                  'en': '\nTexts from A not found in B (single numbers or ranges):',
                  'es': '\nTextos de A no encontrados en B (números individuales o rangos):',
                  'it': '\nTesti da A non trovati in B (numeri singoli o intervalli):',
                  'ja': '\nA のテキストが B で見つかりませんでした (単一番号または範囲):',
                  'pl': '\nTeksty z A nie znalezione w B (pojedyncze numery lub przedziały):',
                  'ru': '\nТексты из A, не найденные в B (одиночные номера или диапазоны):',
                  'zh': '\nA 中的文本未在 B 中找到（单个编号或范围）：'},
 'missing_texts_generated': {'de': 'Fehlende Texte aus B im Vergleich zu A generiert',
                             'en': 'Missing texts generated from B vs A',
                             'es': 'Textos faltantes generados desde B vs A',
                             'it': 'Testi mancanti generati da B rispetto ad A',
                             'ja': 'B vs A から欠落テキストを生成',
                             'pl': 'Brakujące teksty wygenerowane z B vs A',
                             'ru': 'Отсутствующие тексты сгенерированы из B vs A',
                             'zh': '已从 B vs A 生成缺失文本'},
 'missingtexts_saved': {'de': 'Datei mit fehlenden Texten gespeichert: {}',
                        'en': 'Saved missing texts file: {}',
                        'es': 'Archivo con textos faltantes guardado: {}',
                        'it': 'File con testi mancanti salvato: {}',
                        'ja': '欠落テキストファイルを保存しました: {}',
                        'pl': 'Zapisano plik z brakującymi tekstami: {}',
                        'ru': 'Файл с отсутствующими текстами сохранён: {}',
                        'zh': '已保存缺失文本文件：{}'},
 'negative_ids_error': {'de': 'Fehler: Nach Verschiebung wären einige Nummern <= 0. Wählen Sie einen anderen Offset.',
                        'en': 'Error: after shift, some numbers would be <= 0. Choose another offset.',
                        'es': 'Error: tras el desplazamiento algunos números serían ≤ 0. Elige otro offset.',
                        'it': 'Errore: dopo lo spostamento alcuni numeri sarebbero ≤ 0. Scegli un altro offset.',
                        'ja': 'エラー: シフト後に一部の番号が 0 以下になります。他のオフセットを選択してください。',
                        'pl': 'Błąd: po przesunięciu niektóre numery byłyby mniejsze lub równe 0. Wybierz inny offset.',
                        'ru': 'Ошибка: после сдвига некоторые номера стали бы ≤ 0. Выберите другое смещение.',
                        'zh': '错误：偏移后部分编号将 ≤ 0。请选择其他偏移量。'},
 'negative_or_zero_targets': {'de': '{0} ungültige Zielindizes erzeugt (<= 0). Vorgang abgebrochen.',
                              'en': '{0} invalid target indices generated (<= 0). Operation aborted.',
                              'es': '{0} índices de destino no válidos generados (<= 0). Operación cancelada.',
                              'it': '{0} indici di destinazione non validi generati (<= 0). Operazione interrotta.',
                              'ja': '{0} 個の無効なターゲット番号 (<= 0) が生成されました。操作を中断。',
                              'pl': 'Wygenerowano {0} nieprawidłowych numerów docelowych (<= 0). Operacja przerwana.',
                              'ru': 'Создано {0} недопустимых целевых индексов (<= 0). Операция прервана.',
                              'zh': '生成了 {0} 个无效目标索引 (<= 0)。操作已中止。'},
 'new_offset_note': {'de': '    // neuer Offset {}',
                     'en': '    // new offset {}',
                     'es': '    // nuevo offset {}',
                     'it': '    // nuovo offset {}',
                     'ja': '    // 新しいオフセット {}',
                     'pl': '    // nowy offset {}',
                     'ru': '    // новый offset {}',
                     'zh': '    // 新偏移 {}'},
 'new_offset_set': {'de': '\nNeuer Offset gesetzt: {} (A:{} -> B:{})',
                    'en': '\nNew offset set: {} (A:{} -> B:{})',
                    'es': '\nNuevo offset establecido: {} (A:{} -> B:{})',
                    'it': '\nNuovo offset impostato: {} (A:{} -> B:{})',
                    'ja': '\n新しいオフセットを設定: {} (A:{} -> B:{})',
                    'pl': '\nNowy offset ustawiony: {} (A:{} -> B:{})',
                    'ru': '\nНовое смещение установлено: {} (A:{} → B:{})',
                    'zh': '\n新偏移已设置：{} (A:{} → B:{})'},
 'new_saved': {'de': 'Neue Datei gespeichert: {}',
               'en': 'Saved new file: {}',
               'es': 'Nuevo archivo guardado: {}',
               'it': 'Nuovo file salvato: {}',
               'ja': '新しいファイルを保存しました: {}',
               'pl': 'Zapisano nowy plik: {}',
               'ru': 'Новый файл сохранён: {}',
               'zh': '新文件已保存：{}'},
 'no_added': {'de': '  Keine neuen Nummern hinzuzufügen.',
              'en': '  No new numbers to add.',
              'es': '  No hay nuevos números para añadir.',
              'it': '  Nessun nuovo numero da aggiungere.',
              'ja': '  追加する新しい番号はありません。',
              'pl': '  Brak nowych numerów do dodania.',
              'ru': '  Новых номеров для добавления нет.',
              'zh': '  没有新编号需要添加。'},
 'no_added_unexpected': {'de': 'Keine neuen hinzugefügten Nummern (etwas Unerwartetes).',
                         'en': 'No new added numbers (something unexpected).',
                         'es': 'No se añadieron nuevos números (algo inesperado ocurrió).',
                         'it': 'Nessun nuovo numero aggiunto (qualcosa di inaspettato).',
                         'ja': '新しい追加番号なし (予期せぬことが発生)。',
                         'pl': 'Brak nowych dodanych numerów (coś poszło nieoczekiwanie).',
                         'ru': 'Новые номера не добавлены (произошло что-то неожиданное).',
                         'zh': '未添加新编号（出现意外情况）。'},
 'no_blocks': {'de': 'Projektdatei enthält keine Textblöcke. Abgebrochen.',
               'en': 'Project file contains no text blocks. Canceled.',
               'es': 'El archivo de proyecto no contiene bloques de texto. Cancelado.',
               'it': 'Il file di progetto non contiene blocchi di testo. Annullato.',
               'ja': 'プロジェクトファイルにテキストブロックがありません。キャンセルしました。',
               'pl': 'Plik projektu nie zawiera żadnych bloków tekstowych. Anulowano.',
               'ru': 'В файле проекта нет текстовых блоков. Операция отменена.',
               'zh': '项目文件不包含任何文本块。已取消。'},
 'no_blocks_found': {'de': "Keine '## Text N ##'-Blöcke in Datei A gefunden. Nichts zu verschieben.",
                     'en': "No '## Text N ##' blocks found in file A. Nothing to shift.",
                     'es': "No se encontraron bloques '## Text N ##' en el archivo A. Nada que desplazar.",
                     'it': "Nessun blocco '## Text N ##' trovato nel file A. Niente da spostare.",
                     'ja': "ファイル A で '## Text N ##' ブロックが見つかりませんでした。シフトするものがありません。",
                     'pl': "Nie znaleziono żadnych bloków '## Text N ##' w pliku A. Nic do przesunięcia.",
                     'ru': "В файле A не найдено блоков '## Text N ##'. Нечего сдвигать.",
                     'zh': "在文件 A 中未找到任何 '## Text N ##' 块。无需偏移。"},
 'no_matched_ranges': {'de': '  Keine übereinstimmenden Bereiche.',
                       'en': '  No matched ranges.',
                       'es': '  No hay rangos coincidentes.',
                       'it': '  Nessun intervallo corrispondente.',
                       'ja': '  一致した範囲はありません。',
                       'pl': '  Brak dopasowanych przedziałów.',
                       'ru': '  Совпавших диапазонов нет.',
                       'zh': '  无匹配范围。'},
 'no_matches': {'de': '\nKeine Übereinstimmungen zum Speichern. Nichts geändert.',
                'en': '\nNo matches to save. Nothing changed.',
                'es': '\nNo hay coincidencias para guardar. Nada cambiado.',
                'it': '\nNessuna corrispondenza da salvare. Nessuna modifica.',
                'ja': '\n保存する一致なし。何も変更されませんでした。',
                'pl': '\nBrak dopasowań do zapisania. Nic nie zmieniono.',
                'ru': '\nНет совпадений для сохранения. Ничего не изменено.',
                'zh': '\n无匹配项可保存。未做任何更改。'},
 'no_missing_blocks': {'de': 'Keine fehlenden Blöcke (nichts hinzuzufügen).',
                       'en': 'No missing blocks (nothing to add).',
                       'es': 'No hay bloques faltantes (nada que añadir).',
                       'it': 'Nessun blocco mancante (niente da aggiungere).',
                       'ja': '欠落ブロックなし (追加するものがありません)。',
                       'pl': 'Brak brakujących bloków (nic do dopisania).',
                       'ru': 'Отсутствующих блоков нет (добавлять нечего).',
                       'zh': '没有缺失块（无需添加）。'},
 'no_missing_entries': {'de': 'Keine fehlenden Einträge im angegebenen Bereich. Nichts zu tun.',
                        'en': 'No missing entries in given range. Nothing to do.',
                        'es': 'No hay entradas faltantes en el rango indicado. Nada que hacer.',
                        'it': "Nessuna voce mancante nell'intervallo specificato. Niente da fare.",
                        'ja': '指定範囲に欠落エントリなし。何も行いません。',
                        'pl': 'Brak brakujących wpisów w podanym przedziale. Nic do zrobienia.',
                        'ru': 'В указанном диапазоне нет отсутствующих записей. Нечего делать.',
                        'zh': '指定范围内无缺失条目。无需操作。'},
 'no_missingtexts_saved': {'de': 'Keine missingtexts-Datei gespeichert.',
                           'en': 'No missingtexts file saved.',
                           'es': 'No se guardó ningún archivo missingtexts.',
                           'it': 'Nessun file missingtexts salvato.',
                           'ja': 'missingtexts ファイルが保存されませんでした。',
                           'pl': 'Brak zapisanego pliku missingtexts.',
                           'ru': 'Файл missingtexts не сохранён.',
                           'zh': '未保存 missingtexts 文件。'},
 'no_offset': {'de': '  A:{} (kein Offset, vermutete Textnummer für B kann nicht bestimmt werden)',
               'en': '  A:{} (no offset, cannot determine guessed text number for B)',
               'es': '  A:{} (sin offset, imposible determinar número supuesto de texto para B)',
               'it': '  A:{} (nessun offset, impossibile determinare il numero di testo presunto per B)',
               'ja': '  A:{} (オフセットなし、B の推測テキスト番号を決定できません)',
               'pl': '  A:{} (brak offsetu, nie można wyznaczyć liczby domniemanego tekstu dla B)',
               'ru': '  A:{} (нет оффсета, невозможно определить предполагаемый номер текста в B)',
               'zh': '  A:{}（无偏移，无法确定 B 的推测文本编号）'},
 'no_offset_reason': {'de': 'kein Offset',
                      'en': 'no offset',
                      'es': 'sin offset',
                      'it': 'nessun offset',
                      'ja': 'オフセットなし',
                      'pl': 'brak offsetu',
                      'ru': 'нет offset',
                      'zh': '无偏移'},
 'no_path_canceled': {'de': 'Kein Pfad. Zurück zum Menü.',
                      'en': 'No path. Back to menu.',
                      'es': 'Sin ruta. Volver al menú.',
                      'it': 'Nessun percorso. Ritorno al menu.',
                      'ja': 'パスなし。メニューに戻る。',
                      'pl': 'Brak ścieżki. Powrót do menu.',
                      'ru': 'Путь не указан. Возврат в меню.',
                      'zh': '无路径。返回菜单。'},
 'no_range_canceled': {'de': 'Kein Bereich. Abgebrochen.',
                       'en': 'No range. Canceled.',
                       'es': 'Sin rango. Cancelado.',
                       'it': 'Nessun intervallo. Annullato.',
                       'ja': '範囲なし。キャンセルしました。',
                       'pl': 'Brak przedziału. Anulowano.',
                       'ru': 'Диапазон не указан. Отменено.',
                       'zh': '无范围。已取消。'},
 'no_replacements': {'de': '  Keine Ersetzungen (keine Nummer aus B war in A vorhanden).',
                     'en': '  No replacements (no number from B occurred in A).',
                     'es': '  No hubo reemplazos (ningún número de B estaba presente en A).',
                     'it': '  Nessuna sostituzione (nessun numero da B era presente in A).',
                     'ja': '  置換なし (B の番号は A に存在しませんでした)。',
                     'pl': '  Brak podmian (żaden numer z B nie występował w A).',
                     'ru': '  Замен не было (ни один номер из B не встречался в A).',
                     'zh': '  无替换（B 中的任何编号均未出现在 A 中）。'},
 'no_sim': {'de': '  A:{} (vermuteter B-Text: {} — {})',
            'en': '  A:{} (guessed B text: {} — {})',
            'es': '  A:{} (texto supuesto B: {} — {})',
            'it': '  A:{} (testo presunto B: {} — {})',
            'ja': '  A:{} (推測 B テキスト: {} — {})',
            'pl': '  A:{} (domniemany tekst B: {} — {})',
            'ru': '  A:{} (предполагаемый текст B: {} — {})',
            'zh': '  A:{}（推测 B 文本：{} — {}）'},
 'no_suggestion': {'de': 'keine',
                   'en': 'none',
                   'es': 'ninguna',
                   'it': 'nessuno',
                   'ja': 'なし',
                   'pl': 'brak',
                   'ru': 'нет',
                   'zh': '无'},
 'no_targets': {'de': 'Keine Zielindizes zum Speichern. Abgebrochen.',
                'en': 'No target indices to save. Canceled.',
                'es': 'No hay índices destino para guardar. Cancelado.',
                'it': 'Nessun indice di destinazione da salvare. Annullato.',
                'ja': '保存するターゲットインデックスなし。キャンセルしました。',
                'pl': 'Brak docelowych indeksów do zapisu. Anulowano.',
                'ru': 'Нет целевых индексов для сохранения. Отменено.',
                'zh': '无目标索引可保存。已取消。'},
 'no_value_canceled': {'de': 'Kein Wert. Abgebrochen.',
                       'en': 'No value. Canceled.',
                       'es': 'Sin valor. Cancelado.',
                       'it': 'Nessun valore. Annullato.',
                       'ja': '値なし。キャンセルしました。',
                       'pl': 'Brak wartości. Anulowano.',
                       'ru': 'Значение не введено. Отменено.',
                       'zh': '无值。已取消。'},
 'num_ge_1': {'de': 'Nummer muss >= 1 sein.',
              'en': 'Number must be >= 1.',
              'es': 'El número debe ser ≥ 1.',
              'it': 'Il numero deve essere ≥ 1.',
              'ja': '番号は >= 1 でなければなりません。',
              'pl': 'Numer musi być >= 1.',
              'ru': 'Номер должен быть ≥ 1.',
              'zh': '编号必须 ≥ 1。'},
 'numbers_0_255': {'de': 'Zahlen müssen im Bereich 0-255 liegen.',
                   'en': 'Numbers must be in range 0-255.',
                   'es': 'Los números deben estar en el rango 0-255.',
                   'it': 'I numeri devono essere nel range 0-255.',
                   'ja': '数字は 0-255 の範囲でなければなりません。',
                   'pl': 'Liczby muszą być w zakresie 0-255.',
                   'ru': 'Числа должны быть в диапазоне 0-255.',
                   'zh': '数字必须在 0-255 范围内。'},
 'offset_history': {'de': '\nVerlauf der Offset-Änderungen (Offset, A_Index, B_Index):',
                    'en': '\nOffset change history (offset, A_index, B_index):',
                    'es': '\nHistorial de cambios de offset (offset, A_index, B_index):',
                    'it': "\nCronologia delle modifiche dell'offset (offset, A_index, B_index):",
                    'ja': '\nオフセット変更履歴 (offset, A_index, B_index):',
                    'pl': '\nHistoria zmian offsetu (offset, A_index, B_index):',
                    'ru': '\nИстория изменений оффсета (offset, A_index, B_index):',
                    'zh': '\n偏移变更历史（偏移, A_index, B_index）：'},
 'offset_prompt': {'de': 'Geben Sie den Offset ein (Ganzzahl, 0 = abbrechen): ',
                   'en': 'Enter offset (integer, 0 = cancel): ',
                   'es': 'Ingresa el offset (número entero, 0 = cancelar): ',
                   'it': "Inserisci l'offset (numero intero, 0 = annulla): ",
                   'ja': 'オフセットを入力 (整数、0 = キャンセル): ',
                   'pl': 'Podaj offset (liczba całkowita, 0 = anuluj): ',
                   'ru': 'Введите смещение (целое число, 0 = отмена): ',
                   'zh': '请输入偏移量（整数，0 = 取消）：'},
 'offset_set_at': {'de': '  Offset {} gesetzt bei A:{} -> B:{}',
                   'en': '  offset {} set at A:{} -> B:{}',
                   'es': '  offset {} establecido en A:{} → B:{}',
                   'it': '  offset {} impostato presso A:{} -> B:{}',
                   'ja': '  オフセット {} を A:{} -> B:{} で設定',
                   'pl': '  offset {} ustawiony przy A:{} -> B:{}',
                   'ru': '  offset {} установлен при A:{} → B:{}',
                   'zh': '  偏移 {} 设置于 A:{} → B:{}'},
 'offset_zero': {'de': 'Offset = 0 — keine Aktion. Abgebrochen.',
                 'en': 'Offset = 0 — no action. Canceled.',
                 'es': 'Offset = 0 — sin acción. Cancelado.',
                 'it': 'Offset = 0 — nessuna azione. Annullato.',
                 'ja': 'オフセット = 0 — 動作なし。キャンセルしました。',
                 'pl': 'Offset = 0 — brak działania. Anulowano.',
                 'ru': 'Смещение = 0 — действие не выполнено. Отменено.',
                 'zh': '偏移量 = 0 — 无操作。已取消。'},
 'out_file_prompt': {'de': 'Ausgabedatei [{}]: ',
                     'en': 'Output file [{}]: ',
                     'es': 'Archivo de salida [{}]: ',
                     'it': 'File di output [{}]: ',
                     'ja': '出力ファイル [{}]: ',
                     'pl': 'Plik wyjściowy [{}]: ',
                     'ru': 'Выходной файл [{}]: ',
                     'zh': '输出文件 [{}]：'},
 'out_name_prompt': {'de': 'Name der Ausgabedatei [missingtexts.txt]: ',
                     'en': 'Output file name [missingtexts.txt]: ',
                     'es': 'Nombre del archivo de salida [missingtexts.txt]: ',
                     'it': 'Nome del file di output [missingtexts.txt]: ',
                     'ja': '出力ファイル名 [missingtexts.txt]: ',
                     'pl': 'Nazwa pliku wynikowego [missingtexts.txt]: ',
                     'ru': 'Имя выходного файла [missingtexts.txt]: ',
                     'zh': '输出文件名 [missingtexts.txt]：'},
 'out_of_range': {'de': 'Nummer außerhalb des Bereichs. Versuchen Sie es erneut.',
                  'en': 'Number out of range. Try again.',
                  'es': 'Número fuera de rango. Intenta de nuevo.',
                  'it': 'Numero fuori intervallo. Riprova.',
                  'ja': '番号が範囲外です。再試行してください。',
                  'pl': 'Numer poza zakresem. Spróbuj ponownie.',
                  'ru': 'Номер вне диапазона. Попробуйте снова.',
                  'zh': '编号超出范围。请重试。'},
 'out_of_range_start': {'de': 'Startnummer außerhalb des Bereichs. Versuchen Sie es erneut.',
                        'en': 'Starting number out of range. Try again.',
                        'es': 'Número inicial fuera de rango. Intenta de nuevo.',
                        'it': 'Numero iniziale fuori intervallo. Riprova.',
                        'ja': '開始番号が範囲外です。再試行してください。',
                        'pl': 'Początkowy numer poza zakresem. Spróbuj ponownie.',
                        'ru': 'Начальный номер вне диапазона. Попробуйте снова.',
                        'zh': '起始编号超出范围。请重试。'},
 'out_path_prompt': {'de': 'Geben Sie den Ausgabepfad ein [{}]: ',
                     'en': 'Enter output path [{}]: ',
                     'es': 'Ingresa la ruta de salida [{}]: ',
                     'it': 'Inserisci il percorso di output [{}]: ',
                     'ja': '出力パスを入力 [{}]: ',
                     'pl': 'Podaj ścieżkę wyjściową [{}]: ',
                     'ru': 'Введите путь для сохранения [{}]: ',
                     'zh': '请输入输出路径 [{}]：'},
 'overwrite_a_backup': {'de': '  1) Datei A überschreiben (eine Sicherung wird erstellt)',
                        'en': '  1) Overwrite file A (backup will be created)',
                        'es': '  1) Sobrescribir el archivo A (se creará una copia de seguridad)',
                        'it': '  1) Sovrascrivi il file A (verrà creata una copia di backup)',
                        'ja': '  1) ファイル A を上書き (バックアップを作成)',
                        'pl': '  1) Nadpisać plik A (zrobiona zostanie kopia zapasowa)',
                        'ru': '  1) Перезаписать файл A (будет создана резервная копия)',
                        'zh': '  1) 覆盖文件 A（将创建备份）'},
 'overwrite_direct': {'de': 'Datei A direkt überschreiben?',
                      'en': 'Overwrite file A directly?',
                      'es': '¿Sobrescribir directamente el archivo A?',
                      'it': 'Sovrascrivere direttamente il file A?',
                      'ja': 'ファイル A を直接上書きしますか？',
                      'pl': 'Nadpisać plik A bezpośrednio?',
                      'ru': 'Перезаписать файл A напрямую?',
                      'zh': '是否直接覆盖文件 A？'},
 'overwrite_file': {'de': 'Datei überschreiben?',
                    'en': 'Overwrite file?',
                    'es': '¿Sobrescribir el archivo?',
                    'it': 'Sovrascrivere il file?',
                    'ja': 'ファイルを上書きしますか？',
                    'pl': 'Nadpisać plik?',
                    'ru': 'Перезаписать файл?',
                    'zh': '是否覆盖文件？'},
 'overwrite_prompt': {'de': '\nMöchten Sie die vorhandene Datei überschreiben?',
                      'en': '\nDo you want to overwrite existing file?',
                      'es': '\n¿Quieres sobrescribir el archivo existente?',
                      'it': '\nVuoi sovrascrivere il file esistente?',
                      'ja': '\n既存ファイルを上書きしますか？',
                      'pl': '\nCzy chcesz nadpisać istniejący plik?',
                      'ru': '\nХотите перезаписать существующий файл?',
                      'zh': '\n是否覆盖现有文件？'},
 'overwritten': {'de': 'Datei überschrieben: {}',
                 'en': 'Overwritten file: {}',
                 'es': 'Archivo sobrescrito: {}',
                 'it': 'File sovrascritto: {}',
                 'ja': 'ファイルを上書きしました: {}',
                 'pl': 'Nadpisano plik: {}',
                 'ru': 'Файл перезаписан: {}',
                 'zh': '已覆盖文件：{}'},
 'overwritten_a': {'de': 'Datei A überschrieben: {}',
                   'en': 'Overwritten file A: {}',
                   'es': 'Archivo A sobrescrito: {}',
                   'it': 'File A sovrascritto: {}',
                   'ja': 'ファイル A を上書きしました: {}',
                   'pl': 'Nadpisano plik A: {}',
                   'ru': 'Файл A перезаписан: {}',
                   'zh': '已覆盖文件 A：{}'},
 'paste_map_instructions': {'de': 'Fügen Sie die Verschiebungsmappe zeilenweise ein. Mit leerer Zeile beenden.',
                            'en': 'Paste the shift map line by line. Finish with an empty line.',
                            'es': 'Pegue el mapa de desplazamientos línea por línea. Finalice con una línea vacía.',
                            'it': 'Incolla la mappa degli offset riga per riga. Termina con una riga vuota.',
                            'ja': 'シフトマップを一行ずつ貼り付け。空行で終了。',
                            'pl': 'Wklej mapę przesunięć linia po linii. Zakończ pustą linią.',
                            'ru': 'Вставьте карту смещений построчно. Завершите пустой строкой.',
                            'zh': '逐行粘贴偏移映射。以空行结束。'},
 'path_a_prompt': {'de': 'Geben Sie den Pfad zur Datei A ein (Basis): ',
                   'en': 'Enter path to file A (base): ',
                   'es': 'Ingresa la ruta al archivo A (base): ',
                   'it': 'Inserisci il percorso del file A (base): ',
                   'ja': 'ファイル A (ベース) のパスを入力: ',
                   'pl': 'Podaj ścieżkę do pliku A (bazowy): ',
                   'ru': 'Введите путь к файлу A (базовый): ',
                   'zh': '请输入文件 A 的路径（基础文件）：'},
 'path_a_required': {'de': 'Datei A für diese Option erforderlich. Zurück zum Menü.',
                     'en': 'File A required for this option. Back to menu.',
                     'es': 'Se requiere el archivo A para esta opción. Volver al menú.',
                     'it': 'File A richiesto per questa opzione. Ritorno al menu.',
                     'ja': 'このオプションにはファイル A が必要です。メニューに戻る。',
                     'pl': 'Plik A wymagany dla tej opcji. Powrót do menu.',
                     'ru': 'Для этой опции требуется файл A. Возврат в меню.',
                     'zh': '此选项需要文件 A。返回菜单。'},
 'path_b_prompt': {'de': 'Geben Sie den Pfad zur Datei B ein (Referenz): ',
                   'en': 'Enter path to file B (reference): ',
                   'es': 'Ingresa la ruta al archivo B (de referencia): ',
                   'it': 'Inserisci il percorso del file B (di riferimento): ',
                   'ja': 'ファイル B (参照) のパスを入力: ',
                   'pl': 'Podaj ścieżkę do pliku B (referencyjny): ',
                   'ru': 'Введите путь к файлу B (эталонный): ',
                   'zh': '请输入文件 B 的路径（参考文件）：'},
 'path_dat_preview_prompt': {'de': 'Geben Sie den Pfad zur s4_texts.dat<nr>-Datei für die Vorschau ein: ',
                             'en': 'Enter path to s4_texts.dat<nr> for preview: ',
                             'es': 'Ingresa la ruta al archivo s4_texts.dat<nr> para vista previa: ',
                             'it': "Inserisci il percorso del file s4_texts.dat<nr> per l'anteprima: ",
                             'ja': 'プレビュー用の s4_texts.dat<nr> ファイルのパスを入力: ',
                             'pl': 'Podaj ścieżkę do pliku s4_texts.dat<nr> do podglądu: ',
                             'ru': 'Введите путь к файлу s4_texts.dat<nr> для предпросмотра: ',
                             'zh': '请输入要预览的 s4_texts.dat<nr> 文件路径：'},
 'path_dat_prompt': {'de': 'Geben Sie den Pfad zur Datei s4_texts.dat<nr> ein: ',
                     'en': 'Enter path to s4_texts.dat<nr>: ',
                     'es': 'Ingresa la ruta al archivo s4_texts.dat<nr>: ',
                     'it': 'Inserisci il percorso del file s4_texts.dat<nr>: ',
                     'ja': 's4_texts.dat<nr> ファイルのパスを入力: ',
                     'pl': 'Podaj ścieżkę do pliku s4_texts.dat<nr>: ',
                     'ru': 'Введите путь к файлу s4_texts.dat<nr>: ',
                     'zh': '请输入 s4_texts.dat<nr> 文件的路径：'},
 'path_required': {'de': 'Pfad zur .dat-Datei erforderlich. Zurück zum Menü.',
                   'en': 'Path to .dat file required. Back to menu.',
                   'es': 'Se requiere la ruta al archivo .dat. Volver al menú.',
                   'it': 'Percorso del file .dat richiesto. Ritorno al menu.',
                   'ja': '.dat ファイルのパスが必要です。メニューに戻る。',
                   'pl': 'Ścieżka do pliku .dat wymagana. Powrót do menu.',
                   'ru': 'Требуется путь к файлу .dat. Возврат в меню.',
                   'zh': '需要 .dat 文件路径。返回菜单。'},
 'placeholder_cases': {'de': '\nStellen, an denen A leer/Platzhalter war, B aber signifikanten Text hatte:',
                       'en': '\nPlaces where A was empty/placeholder, but B had significant text:',
                       'es': '\nLugares donde A estaba vacío/placeholder pero B tenía texto significativo:',
                       'it': '\nPosizioni in cui A era vuoto/placeholder ma B aveva testo significativo:',
                       'ja': '\nA が空/プレースホルダーだったが B が有意なテキストを持つ箇所:',
                       'pl': '\nMiejsca gdzie A był pusty/placeholder, a B miał znaczący tekst:',
                       'ru': '\nМеста, где A был пустым/заглушкой, а B содержал значимый текст:',
                       'zh': '\nA 为空/占位符但 B 有意义文本的位置：'},
 'press_enter_to_exit': {'de': '\nDrücken Sie Enter, um zu beenden...',
                         'en': '\nPress Enter to exit...',
                         'es': '\nPresiona Enter para terminar...',
                         'it': '\nPremi Invio per terminare...',
                         'ja': '\nEnter を押して終了...',
                         'pl': '\nNaciśnij Enter, aby zakończyć...',
                         'ru': '\nНажмите Enter для завершения...',
                         'zh': '\n按 Enter 键退出...'},
 'project_export_prompt': {'de': 'Geben Sie den Pfad zur .s4_translation_project-Datei für den Export ein: ',
                           'en': 'Enter path to .s4_translation_project for export: ',
                           'es': 'Ingresa la ruta al archivo .s4_translation_project para exportar: ',
                           'it': 'Inserisci il percorso del file .s4_translation_project da esportare: ',
                           'ja': 'エクスポートする .s4_translation_project ファイルのパスを入力: ',
                           'pl': 'Podaj ścieżkę do pliku .s4_translation_project do eksportu: ',
                           'ru': 'Введите путь к файлу .s4_translation_project для экспорта: ',
                           'zh': '请输入要导出的 .s4_translation_project 文件路径：'},
 'project_path_prompt': {'de': 'Geben Sie den Pfad zur .s4_translation_project-Datei ein: ',
                         'en': 'Enter path to .s4_translation_project file: ',
                         'es': 'Ingresa la ruta al archivo .s4_translation_project: ',
                         'it': 'Inserisci il percorso del file .s4_translation_project: ',
                         'ja': '.s4_translation_project ファイルのパスを入力: ',
                         'pl': 'Podaj ścieżkę do pliku .s4_translation_project: ',
                         'ru': 'Введите путь к файлу .s4_translation_project: ',
                         'zh': '请输入 .s4_translation_project 文件的路径：'},
 'project_path_required': {'de': 'Pfad zur Projektdatei erforderlich. Zurück zum Menü.',
                           'en': 'Path to project file required. Back to menu.',
                           'es': 'Se requiere la ruta al archivo de proyecto. Volver al menú.',
                           'it': 'Percorso del file di progetto richiesto. Ritorno al menu.',
                           'ja': 'プロジェクトファイルのパスが必要です。メニューに戻る。',
                           'pl': 'Ścieżka do pliku projektu wymagana. Powrót do menu.',
                           'ru': 'Требуется путь к файлу проекта. Возврат в меню.',
                           'zh': '需要项目文件路径。返回菜单。'},
 'project_read_error': {'de': 'Fehler beim Lesen der Projektdatei: {}',
                        'en': 'Error reading project file: {}',
                        'es': 'Error al leer el archivo de proyecto: {}',
                        'it': 'Errore di lettura del file di progetto: {}',
                        'ja': 'プロジェクトファイルの読み込みエラー: {}',
                        'pl': 'Błąd odczytu pliku projektu: {}',
                        'ru': 'Ошибка чтения файла проекта: {}',
                        'zh': '读取项目文件出错：{}'},
 'project_saved': {'de': 'Projektdatei gespeichert: {} (Ausgabekodierung: {})',
                   'en': 'Saved project file: {} (output encoding: {})',
                   'es': 'Archivo de proyecto guardado: {} (codificación de salida: {})',
                   'it': 'File di progetto salvato: {} (codifica di output: {})',
                   'ja': 'プロジェクトファイルを保存しました: {} (出力エンコーディング: {})',
                   'pl': 'Zapisano plik projektu: {} (kodowanie wyjściowe: {})',
                   'ru': 'Файл проекта сохранён: {} (выходная кодировка: {})',
                   'zh': '已保存项目文件：{}（输出编码：{}）'},
 'project_write_error': {'de': 'Fehler beim Schreiben der Projektdatei: {}',
                         'en': 'Error writing project file: {}',
                         'es': 'Error al escribir el archivo de proyecto: {}',
                         'it': 'Errore di scrittura del file di progetto: {}',
                         'ja': 'プロジェクトファイルの書き込みエラー: {}',
                         'pl': 'Błąd zapisu pliku projektu: {}',
                         'ru': 'Ошибка записи файла проекта: {}',
                         'zh': '写入项目文件出错：{}'},
 'range_fix_prompt': {'de': 'Geben Sie den zu ergänzenden Nummernbereich ein (z. B. 1-2000) oder einzelne Nummer (z. '
                            'B. 57): ',
                      'en': 'Enter range of numbers to fix (e.g. 1-2000) or single number (e.g. 57): ',
                      'es': 'Ingresa el rango de números a completar (ej. 1-2000) o un número individual (ej. 57): ',
                      'it': "Inserisci l'intervallo di numeri da completare (es. 1-2000) o un singolo numero (es. "
                            '57): ',
                      'ja': '補完する番号範囲を入力 (例: 1-2000) または単一番号 (例: 57): ',
                      'pl': 'Podaj przedział numerów do uzupełnienia (np. 1-2000) lub pojedynczy numer (np. 57): ',
                      'ru': 'Введите диапазон номеров для заполнения (например 1-2000) или один номер (например 57): ',
                      'zh': '请输入要补全的编号范围（例如 1-2000）或单个编号（例如 57）：'},
 'range_prompt': {'de': "Geben Sie Textnummer ein (z. B. 57), Bereich (z. B. 60-200), 'all' für alles anzeigen oder "
                        "'single' für einzelne Nummer zum Testen aller Kodierungen: ",
                  'en': "Enter text number (e.g. 57), range (e.g. 60-200), 'all' to print everything, or 'single' to "
                        'enter single number for all encodings test: ',
                  'es': "Ingresa número de texto (ej. 57), rango (ej. 60-200), 'all' para mostrar todo, o 'single' "
                        'para ingresar un solo número y probar todas las codificaciones: ',
                  'it': "Inserisci il numero del testo (es. 57), un intervallo (es. 60-200), 'all' per mostrare tutto, "
                        "o 'single' per inserire un singolo numero da testare con tutte le codifiche: ",
                  'ja': "テキスト番号を入力 (例: 57)、範囲 (例: 60-200)、'all' で全て出力、または 'single' で単一番号を入力して全てのエンコーディングをテスト: ",
                  'pl': "Podaj numer tekstu (np. 57), przedział (np. 60-200), 'all' aby wypisać wszystko, lub 'single' "
                        'aby podać pojedynczy numer do testu wszystkich kodowań: ',
                  'ru': "Введите номер текста (например 57), диапазон (например 60-200), 'all' для вывода всего или "
                        "'single' для ввода одного номера и теста всех кодировок: ",
                  'zh': "请输入文本编号（例如 57），范围（例如 60-200），'all' 显示全部，或 'single' 输入单个编号测试所有编码："},
 'replaced_numbers': {'de': '  Ersetzte Nummern (aus Datei B): {}',
                      'en': '  Replaced numbers (from file B): {}',
                      'es': '  Números reemplazados (desde el archivo B): {}',
                      'it': '  Numeri sostituiti (dal file B): {}',
                      'ja': '  置換された番号 (ファイル B から): {}',
                      'pl': '  Podmienione numery (z pliku B): {}',
                      'ru': '  Заменённые номера (из файла B): {}',
                      'zh': '  已替换的编号（来自文件 B）：{}'},
 'required_paths': {'de': 'Dateien A und B sind für diese Option erforderlich. Zurück zum Menü.',
                    'en': 'Files A and B are required for this option. Back to menu.',
                    'es': 'Se requieren los archivos A y B para esta opción. Volver al menú.',
                    'it': 'I file A e B sono richiesti per questa opzione. Ritorno al menu.',
                    'ja': 'このオプションにはファイル A と B が必要です。メニューに戻る。',
                    'pl': 'Plik A i B są wymagane dla tej opcji. Powrót do menu.',
                    'ru': 'Для этой опции требуются файлы A и B. Возврат в меню.',
                    'zh': '此选项需要文件 A 和 B。返回菜单。'},
 'sample_mappings': {'de': 'Beispielzuordnungen (A -> B): {}',
                     'en': 'Sample mappings (A -> B): {}',
                     'es': 'Mapeos de ejemplo (A → B): {}',
                     'it': 'Mappature di esempio (A -> B): {}',
                     'ja': 'サンプルマッピング (A -> B): {}',
                     'pl': 'Przykładowe mapowania (A -> B): {}',
                     'ru': 'Примеры сопоставлений (A → B): {}',
                     'zh': '示例映射（A → B）：{}'},
 'save_as_alt': {'de': 'Speichern unter: {}',
                 'en': 'Save as: {}',
                 'es': 'Guardar como: {}',
                 'it': 'Salva come: {}',
                 'ja': 'として保存: {}',
                 'pl': 'Zapisz jako: {}',
                 'ru': 'Сохранить как: {}',
                 'zh': '另存为：{}'},
 'save_as_new': {'de': 'Als neue Datei speichern: {}?',
                 'en': 'Save as new file: {}?',
                 'es': '¿Guardar como nuevo archivo: {}?',
                 'it': 'Salvare come nuovo file: {}?',
                 'ja': '新しいファイルとして保存: {}?',
                 'pl': 'Zapisać jako nowy plik: {}?',
                 'ru': 'Сохранить как новый файл: {}?',
                 'zh': '是否保存为新文件：{}？'},
 'save_canceled': {'de': 'Speichern abgebrochen.',
                   'en': 'Save canceled.',
                   'es': 'Guardado cancelado.',
                   'it': 'Salvataggio annullato.',
                   'ja': '保存をキャンセルしました。',
                   'pl': 'Anulowano zapis.',
                   'ru': 'Сохранение отменено.',
                   'zh': '保存已取消。'},
 'save_intent': {'de': '\nBeabsichtige, {} aktualisierte Einträge in Datei A zu speichern.',
                 'en': '\nIntending to save {} updated entries to file A.',
                 'es': '\nVoy a guardar {} entradas actualizadas en el archivo A.',
                 'it': '\nIntendo salvare {} voci aggiornate nel file A.',
                 'ja': '\n{} 個の更新されたエントリをファイル A に保存します。',
                 'pl': '\nZamierzam zapisać {} zaktualizowanych wpisów do pliku A.',
                 'ru': '\nПланирую сохранить {} обновлённых записей в файл A.',
                 'zh': '\n准备将 {} 个更新条目保存到文件 A。'},
 'save_method': {'de': '\nWählen Sie die Speichermethode:',
                 'en': '\nChoose save method:',
                 'es': '\nElige el método de guardado:',
                 'it': '\nScegli il metodo di salvataggio:',
                 'ja': '\n保存方法を選択:',
                 'pl': '\nWybierz sposób zapisu:',
                 'ru': '\nВыберите способ сохранения:',
                 'zh': '\n选择保存方式：'},
 'save_new': {'de': '  2) Als neue Datei speichern (gleiches Verzeichnis wie A, Name + _updated)',
              'en': '  2) Save as new file (same directory as A, name + _updated)',
              'es': '  2) Guardar como nuevo archivo (misma carpeta que A, nombre + _updated)',
              'it': '  2) Salva come nuovo file (stessa cartella di A, nome + _updated)',
              'ja': '  2) 新しいファイルとして保存 (A と同じディレクトリ、名前 + _updated)',
              'pl': '  2) Zapisz jako nowy plik (ten sam katalog co A, nazwa + _updated)',
              'ru': '  2) Сохранить как новый файл (в той же папке, что и A, имя + _updated)',
              'zh': '  2) 保存为新文件（与 A 同目录，文件名 + _updated）'},
 'save_new_shift': {'de': '  2) Als neue Datei speichern (gleiches Verzeichnis wie A, Name + _shifted)',
                    'en': '  2) Save as new file (same directory as A, name + _shifted)',
                    'es': '  2) Guardar como nuevo archivo (misma carpeta que A, nombre + _shifted)',
                    'it': '  2) Salva come nuovo file (stessa cartella di A, nome + _shifted)',
                    'ja': '  2) 新しいファイルとして保存 (A と同じディレクトリ、名前 + _shifted)',
                    'pl': '  2) Zapisz jako nowy plik (ten sam katalog co A, nazwa + _shifted)',
                    'ru': '  2) Сохранить как новый файл (в той же папке, имя + _shifted)',
                    'zh': '  2) 保存为新文件（与 A 同目录，文件名 + _shifted）'},
 'save_shift_map_prompt': {'de': 'Verschiebungskarte in eine Datei speichern?',
                           'en': 'Save the shift map to a file?',
                           'es': '¿Guardar el mapa de desplazamientos en un archivo?',
                           'it': 'Salvare la mappa degli spostamenti su file?',
                           'ja': 'シフトマップをファイルに保存しますか？',
                           'pl': 'Zapisać mapę przesunięć do pliku?',
                           'ru': 'Сохранить карту смещений в файл?',
                           'zh': '将偏移映射保存到文件？'},
 'save_shift_method': {'de': '\nWählen Sie die Speichermethode für die verschobene Datei:',
                       'en': '\nChoose save method for shifted file:',
                       'es': '\nElige el método de guardado del archivo desplazado:',
                       'it': '\nScegli il metodo di salvataggio del file spostato:',
                       'ja': '\nシフト後ファイルの保存方法を選択:',
                       'pl': '\nWybierz sposób zapisu przesuniętego pliku:',
                       'ru': '\nВыберите способ сохранения сдвинутого файла:',
                       'zh': '\n选择偏移后文件的保存方式：'},
 'save_test_prompt': {'de': 'Testergebnis in Datei {}_encoding_test.txt speichern? [J/n]: ',
                      'en': 'Save test result to file {}_encoding_test.txt? [y/N]: ',
                      'es': '¿Guardar el resultado de la prueba en el archivo {}_encoding_test.txt? [S/n]: ',
                      'it': 'Salvare il risultato del test nel file {}_encoding_test.txt? [S/n]: ',
                      'ja': '{}_encoding_test.txt ファイルにテスト結果を保存しますか？ [Y/n]: ',
                      'pl': 'Czy zapisać wynik testu do pliku {}_encoding_test.txt? [T/n]: ',
                      'ru': 'Сохранить результат теста в файл {}_encoding_test.txt? [Д/н]: ',
                      'zh': '是否将测试结果保存到 {}_encoding_test.txt？[Y/n]：'},
 'save_texts_from_to': {'de': 'Speichere alle Texte von 1 bis {} (letzte Nummer: {}).',
                        'en': 'Will save all texts from 1 to {} (last number: {}).',
                        'es': 'Guardaré todos los textos desde 1 hasta {} (último número: {}).',
                        'it': 'Salverò tutti i testi da 1 a {} (ultimo numero: {}).',
                        'ja': '全てのテキストを 1 から {} まで保存します (最後の番号: {})。',
                        'pl': 'Zapiszę wszystkie teksty od 1 do {} (ostatni numer: {}).',
                        'ru': 'Будут сохранены все тексты с 1 по {} (последний номер: {}).',
                        'zh': '将保存所有文本，从 1 到 {}（最后一个编号：{}）。'},
 'saved_to': {'de': 'Ergebnis gespeichert unter: {}',
              'en': 'Saved result to: {}',
              'es': 'Resultado guardado en: {}',
              'it': 'Risultato salvato in: {}',
              'ja': '結果を保存しました: {}',
              'pl': 'Zapisano wynik do: {}',
              'ru': 'Результат сохранён в: {}',
              'zh': '结果已保存至：{}'},
 'selected_lang': {'de': 'Ausgewählte Sprache: {} (Nummer {}), vorgeschlagene Kodierungen (erstes Standard): {}',
                   'en': 'Selected language: {} (number {}), suggested encodings (first default): {}',
                   'es': 'Idioma seleccionado: {} (número {}), codificaciones sugeridas (primera por defecto): {}',
                   'it': 'Lingua selezionata: {} (numero {}), codifiche suggerite (prima predefinita): {}',
                   'ja': '選択された言語: {} (番号 {})、提案エンコーディング (最初のデフォルト): {}',
                   'pl': 'Wybrany język: {} (numer {}), sugerowane kodowania (pierwsze domyślne): {}',
                   'ru': 'Выбран язык: {} (номер {}), предложенные кодировки (первая по умолчанию): {}',
                   'zh': '已选择语言：{}（编号 {}），建议编码（第一个为默认）：{}'},
 'shift_map_filename_prompt': {'de': 'Dateiname der Verschiebungskarte (Standard: text_shift_map.txt): ',
                               'en': 'Shift map filename (default: text_shift_map.txt): ',
                               'es': 'Nombre del archivo del mapa (predeterminado: text_shift_map.txt): ',
                               'it': 'Nome del file della mappa (predefinito: text_shift_map.txt): ',
                               'ja': 'マップファイルの名前 (デフォルト text_shift_map.txt): ',
                               'pl': 'Nazwa pliku mapy (domyślnie text_shift_map.txt): ',
                               'ru': 'Имя файла карты смещений (по умолчанию: text_shift_map.txt): ',
                               'zh': '映射文件名（默认：text_shift_map.txt）：'},
 'shift_map_preview_title': {'de': 'Verschiebungskarte (Vorschau):',
                             'en': 'Shift map (preview):',
                             'es': 'Mapa de desplazamientos (vista previa):',
                             'it': 'Mappa degli spostamenti (anteprima):',
                             'ja': 'シフトマップ (プレビュー):',
                             'pl': 'Mapa przesunięć (podgląd):',
                             'ru': 'Карта смещений (предпросмотр):',
                             'zh': '偏移映射（预览）：'},
 'shift_map_save_error': {'de': 'Fehler beim Speichern der Verschiebungskarte: {0}',
                          'en': 'Error saving shift map: {0}',
                          'es': 'Error al guardar el mapa de desplazamientos: {0}',
                          'it': 'Errore durante il salvataggio della mappa degli spostamenti: {0}',
                          'ja': 'シフトマップの保存エラー: {0}',
                          'pl': 'Błąd zapisu mapy przesunięć: {0}',
                          'ru': 'Ошибка сохранения карты смещений: {0}',
                          'zh': '保存偏移映射时出错：{0}'},
 'shift_map_saved': {'de': 'Verschiebungskarte gespeichert unter: {0}',
                     'en': 'Shift map saved to: {0}',
                     'es': 'Mapa de desplazamientos guardado en: {0}',
                     'it': 'Mappa degli spostamenti salvata in: {0}',
                     'ja': 'シフトマップを保存しました: {0}',
                     'pl': 'Mapa przesunięć zapisana do: {0}',
                     'ru': 'Карта смещений сохранена в: {0}',
                     'zh': '偏移映射已保存到：{0}'},
 'shifted_saved': {'de': 'Verschobene Datei gespeichert unter: {}',
                   'en': 'Saved shifted file to: {}',
                   'es': 'Archivo desplazado guardado en: {}',
                   'it': 'File spostato salvato in: {}',
                   'ja': 'シフトされたファイルを保存しました: {}',
                   'pl': 'Zapisano przesunięty plik do: {}',
                   'ru': 'Сдвинутый файл сохранён в: {}',
                   'zh': '偏移后的文件已保存至：{}'},
 'similarity': {'de': 'Ähnlichkeit',
                'en': 'similarity',
                'es': 'similitud',
                'it': 'similarità',
                'ja': '類似度',
                'pl': 'podobieństwo',
                'ru': 'схожесть',
                'zh': '相似度'},
 'single_text_prompt': {'de': 'Geben Sie die Nummer eines einzelnen Textes zum Testen aller Kodierungen ein: ',
                        'en': 'Enter single text number for all encodings test: ',
                        'es': 'Ingresa el número de un solo texto para probar todas las codificaciones: ',
                        'it': 'Inserisci il numero di un singolo testo per il test di tutte le codifiche: ',
                        'ja': '全てのエンコーディングテスト用の単一テキスト番号を入力: ',
                        'pl': 'Podaj numer pojedynczego tekstu do testu wszystkich kodowań: ',
                        'ru': 'Введите номер одного текста для теста всех кодировок: ',
                        'zh': '请输入单个文本编号以测试所有编码：'},
 'suggested_encs': {'de': '\nVorgeschlagene Kodierungen (erstes Standard):',
                    'en': '\nSuggested encodings (first default):',
                    'es': '\nCodificaciones sugeridas (primera por defecto):',
                    'it': '\nCodifiche suggerite (prima predefinita):',
                    'ja': '\n提案エンコーディング (最初のデフォルト):',
                    'pl': '\nSugerowane kodowania (pierwsze domyślne):',
                    'ru': '\nПредложенные кодировки (первая по умолчанию):',
                    'zh': '\n建议编码（第一个为默认）：'},
 'summary_changes': {'de': '\nZusammenfassung der Änderungen:',
                     'en': '\nSummary of changes:',
                     'es': '\nResumen de cambios:',
                     'it': '\nRiepilogo delle modifiche:',
                     'ja': '\n変更の概要:',
                     'pl': '\nPodsumowanie zmian:',
                     'ru': '\nИтог изменений:',
                     'zh': '\n更改摘要：'},
 'test_another_enc': {'de': 'Andere Kodierung für diesen Bereich testen? [J/n]: ',
                      'en': 'Test another encoding for this range? [Y/n]: ',
                      'es': '¿Probar otra codificación para este rango? [S/n]: ',
                      'it': "Testare un'altra codifica per questo intervallo? [S/n]: ",
                      'ja': 'この範囲で他のエンコーディングをチェックしますか？ [Y/n]: ',
                      'pl': 'Sprawdzić inne kodowanie dla tego zakresu? [T/n]: ',
                      'ru': 'Проверить другую кодировку для этого диапазона? [Д/н]: ',
                      'zh': '是否为该范围测试其他编码？[Y/n]：'},
 'test_not_saved': {'de': 'Test nicht gespeichert.',
                    'en': 'Test not saved.',
                    'es': 'La prueba no fue guardada.',
                    'it': 'Il test non è stato salvato.',
                    'ja': 'テストは保存されませんでした。',
                    'pl': 'Test nie został zapisany.',
                    'ru': 'Тест не сохранён.',
                    'zh': '测试未保存。'},
 'test_save_error': {'de': 'Fehler beim Speichern des Tests: {}',
                     'en': 'Error saving test: {}',
                     'es': 'Error al guardar la prueba: {}',
                     'it': 'Errore durante il salvataggio del test: {}',
                     'ja': 'テストの保存エラー: {}',
                     'pl': 'Błąd zapisu testu: {}',
                     'ru': 'Ошибка сохранения теста: {}',
                     'zh': '保存测试出错：{}'},
 'test_saved': {'de': 'Kodierungstest gespeichert unter: {}',
                'en': 'Saved encoding test to: {}',
                'es': 'Prueba de codificaciones guardada en: {}',
                'it': 'Test delle codifiche salvato in: {}',
                'ja': 'エンコーディングテストを保存しました: {}',
                'pl': 'Zapisano test kodowań do: {}',
                'ru': 'Тест кодировок сохранён в: {}',
                'zh': '编码测试已保存至：{}'},
 'testing_single_text': {'de': 'Teste einzelnen Text #{} mit verschiedenen Kodierungen\n',
                         'en': 'Testing single text #{} across encodings\n',
                         'es': 'Probando texto individual #{} con diferentes codificaciones\n',
                         'it': 'Test di un singolo testo #{} con diverse codifiche\n',
                         'ja': '単一テキスト #{} をエンコーディングでテスト中\n',
                         'pl': 'Testing single text #{} across encodings\n',
                         'ru': 'Тестирование одного текста #{} на разных кодировках\n',
                         'zh': '正在测试单个文本 #{} 的多种编码\n'},
 'texts_count': {'de': 'Anzahl gespeicherter Texte: {}. Leer (Länge=0): {}. Kodierung: {}',
                 'en': 'Number of texts saved: {}. Empty (length=0): {}. Encoding: {}',
                 'es': 'Número de textos guardados: {}. Vacíos (longitud=0): {}. Codificación: {}',
                 'it': 'Numero di testi salvati: {}. Vuoti (lunghezza=0): {}. Codifica: {}',
                 'ja': '保存されたテキスト数: {}. 空 (length=0): {}. エンコーディング: {}',
                 'pl': 'Liczba tekstów zapisanych: {}. Pustych (length=0): {}. Kodowanie: {}',
                 'ru': 'Количество сохранённых текстов: {}. Пустых (длина=0): {}. Кодировка: {}',
                 'zh': '保存的文本数量：{}。空文本（长度=0）：{}。编码：{}'},
 'texts_count_dat': {'de': 'Datei enthält {} Texte.',
                     'en': 'File contains {} texts.',
                     'es': 'El archivo contiene {} textos.',
                     'it': 'Il file contiene {} testi.',
                     'ja': 'ファイルには {} テキストが含まれます。',
                     'pl': 'Plik zawiera {} tekstów.',
                     'ru': 'Файл содержит {} текстов.',
                     'zh': '文件包含 {} 个文本。'},
 'unknown_lang_num': {'de': 'Unbekannte Sprachnummer. Versuchen Sie es erneut.',
                      'en': 'Unknown language number. Try again.',
                      'es': 'Número de idioma desconocido. Intenta de nuevo.',
                      'it': 'Numero lingua sconosciuto. Riprova.',
                      'ja': '不明な言語番号。再試行してください。',
                      'pl': 'Nieznany numer języka. Spróbuj ponownie.',
                      'ru': 'Неизвестный номер языка. Попробуйте снова.',
                      'zh': '未知语言编号。请重试。'},
 'updated_entries': {'de': 'Anzahl aktualisierter Einträge (ohne Offset-Zuweisungen): {}',
                     'en': 'Number of updated entries (without offset assignments): {}',
                     'es': 'Número de entradas actualizadas (sin asignaciones por offset): {}',
                     'it': 'Numero di voci aggiornate (escluse assegnazioni per offset): {}',
                     'ja': 'オフセット割り当てなしの更新されたエントリ数: {}',
                     'pl': 'Liczba zaktualizowanych wpisów (bez przypisań przez offset): {}',
                     'ru': 'Количество обновлённых записей (без назначений по offset): {}',
                     'zh': '已更新条目数量（不含偏移分配）：{}'},
 'use_suggested_enc': {'de': "Vorgeschlagene Kodierung '{}' verwenden? [J/n]: ",
                       'en': "Use suggested encoding '{}'? [Y/n]: ",
                       'es': "¿Usar la codificación sugerida '{}' ? [S/n]: ",
                       'it': "Usare la codifica suggerita '{}' ? [S/n]: ",
                       'ja': "提案されたエンコーディング '{}' を使用しますか？ [Y/n]: ",
                       'pl': "Użyć sugerowanego kodowania '{}'? [T/n]: ",
                       'ru': "Использовать предложенную кодировку '{}' ? [Д/н]: ",
                       'zh': "是否使用建议的编码 '{}'？[Y/n]："},
 'with_sim': {'de': '  A:{} ({}% Ähnlichkeit mit B-Text: {})',
              'en': '  A:{} ({}% similarity with B text: {})',
              'es': '  A:{} ({}% de similitud con texto B: {})',
              'it': '  A:{} ({}% di similarità con il testo B: {})',
              'ja': '  A:{} (B テキスト {} との類似度 {}%)',
              'pl': '  A:{} ({}% podobieństwa z tekstem B: {})',
              'ru': '  A:{} ({}% схожести с текстом B: {})',
              'zh': '  A:{}（与 B 文本 {} 的相似度：{}%）'},
 'write_error': {'de': 'Schreibfehler: {}',
                 'en': 'Write error: {}',
                 'es': 'Error al escribir: {}',
                 'it': 'Errore di scrittura: {}',
                 'ja': '書き込みエラー: {}',
                 'pl': 'Błąd zapisu: {}',
                 'ru': 'Ошибка записи: {}',
                 'zh': '写入错误：{}'},
 'yes_no_prompt': {'de': 'Bitte mit ja/nein antworten (j/n).',
                   'en': 'Please answer yes/no (y/n).',
                   'es': 'Por favor responde sí/no (s/n).',
                   'it': 'Rispondi sì/no (s/n).',
                   'ja': 'はい/いいえ で答えてください (y/n)。',
                   'pl': 'Proszę odpowiedzieć tak/nie (y/n).',
                   'ru': 'Пожалуйста, ответьте да/нет (y/n).',
                   'zh': '请回答是/否 (y/n)。'},
 'yes_no_suffix_no_default': {'de': '[j/N]',
                              'en': '[y/N]',
                              'es': '[s/N]',
                              'it': '[s/N]',
                              'ja': '[y/N]',
                              'pl': '[t/N]',
                              'ru': '[д/Н]',
                              'zh': '[y/N]'},
 'yes_no_suffix_yes_default': {'de': '[J/n]',
                               'en': '[Y/n]',
                               'es': '[S/n]',
                               'it': '[S/n]',
                               'ja': '[Y/n]',
                               'pl': '[T/n]',
                               'ru': '[Д/н]',
                               'zh': '[Y/n]'}}


# --- pomocnicze ---
def TL(key: str, lang: str) -> str:
    """Zwraca tłumaczenie z fallbackiem do angielskiego."""
    entry = TRANSLATIONS.get(key, {})
    return entry.get(lang) or entry.get("en") or key

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
    yes = {'y','yes','t','tak','j','ja','s','si','sí','да','д'}
    no = {'n','no','nie','nein','нет','н'}

    base = TL(prompt, lang)

    # wybór sufiksu zależnie od domyślnej odpowiedzi
    suffix_key = 'yes_no_suffix_yes_default' if default else 'yes_no_suffix_no_default'
    suffix = TL(suffix_key, lang)

    full_prompt = f"{base} {suffix}: "

    while True:
        ans = input(full_prompt).strip().lower()

        if ans == '':
            return default

        if ans in yes:
            return True

        if ans in no:
            return False

        print(TL('yes_no_prompt', lang))

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

# --- Funkcja walidująca plik projektu ---
def validate_project_file(path: Path, encoding: str = 'utf-8', lang: str = 'en') -> bool:
    try:
        text = read_file(path, encoding=encoding)
        _, _, blocks_map = parse_blocks_linewise(text)
        if len(blocks_map) > 0:
            return True
        else:
            print(TL('invalid_project_file', lang))
            return False
    except Exception as e:
        print(TL('project_read_error', lang).format(e))
        return False

# --- Funkcja walidująca plik .dat ---
def validate_dat_file(path: Path, lang: str = 'en') -> bool:
    try:
        data = path.read_bytes()
        if len(data) < 8:
            print(TL('file_too_short', lang))
            return False
        header_bytes = data[0:4]
        print(TL('header_bytes_dat', lang).format(' '.join(str(b) for b in header_bytes)))
        length = int.from_bytes(data[4:8], byteorder='little', signed=False)
        if length < 0 or 8 + length > len(data):
            print(TL('invalid_dat_file', lang))
            return False
        text_bytes = data[8:8 + length]
        try:
            text_bytes.decode('ascii')
            return True
        except UnicodeDecodeError:
            print(TL('invalid_dat_file', lang))
            return False
    except Exception as e:
        print(TL('dat_read_error', lang).format(e))
        return False


# --- option 1: generate missingtexts.txt ---
def generate_missing_texts(path_a: Path, path_b: Path, encoding: str = 'utf-8', out_name: str = 'missingtexts.txt', lang: str = 'en') -> tuple[Path | None, list[int]]:
    text_a = read_file(path_a, encoding=encoding)
    text_b = read_file(path_b, encoding=encoding)
    _, order_a, map_a = parse_blocks_linewise(text_a)
    _, order_b, map_b = parse_blocks_linewise(text_b)

    missing_ids = []
    parts = []
    parts.append(f'# {TL('missing_texts_generated', lang)}\n# A: {path_a}\n# B: {path_b}\n\n')
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
        if not confirm(TL('file_exists_overwrite', lang).format(out_path), default=False, lang=lang):
            print(TL('canceled_missingtexts', lang))
            return None, missing_ids
    write_file(out_path, ''.join(parts), encoding=encoding)
    return out_path, missing_ids



# --- option 2: merge ---
def option_merge(path_a: Path, path_b: Path, encoding: str = 'utf-8', lang: str = 'en') -> None:
    text_a = read_file(path_a, encoding=encoding)
    text_b = read_file(path_b, encoding=encoding)
    header_a, order_a, map_a = parse_blocks_linewise(text_a)
    header_b, order_b, map_b = parse_blocks_linewise(text_b)

    result_text, replaced, added = build_output_text(header_a, order_a, map_a, map_b)

    print(TL('summary_changes', lang))
    if replaced:
        print(TL('replaced_numbers', lang).format(', '.join(map(str, replaced))))
    else:
        print(TL('no_replacements', lang))
    if added:
        print(TL('added_numbers', lang).format(', '.join(map(str, added))))
    else:
        print(TL('no_added', lang))

    print(TL('save_method', lang))
    print(TL('overwrite_a_backup', lang))
    print(TL('save_new', lang))
    choice = input(TL('choose_1_or_2', lang)).strip() or '1'

    if choice == '1':
        bak = path_a.with_suffix(path_a.suffix + '.bak')
        try:
            shutil.copy2(path_a, bak)
            print(TL('backup_created', lang).format(bak))
        except Exception as e:
            print(TL('backup_failed', lang).format(e))
            if not confirm(TL('continue_without_backup', lang), default=False, lang=lang):
                print(TL('canceled', lang))
                return
        try:
            write_file(path_a, result_text, encoding=encoding)
            print(TL('overwritten_a', lang).format(path_a))
        except Exception as e:
            print(TL('write_error', lang).format(e))
            return
    elif choice == '2':
        suggested = path_a.with_name(path_a.stem + '_updated' + path_a.suffix)
        out_path_input = input(TL('out_path_prompt', lang).format(suggested)).strip()
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
                print(TL('dir_create_failed', lang).format(out_dir, e))
                return
        if out_path.exists():
            if not confirm(TL('file_exists_overwrite', lang).format(out_path), default=False, lang=lang):
                print(TL('canceled', lang))
                return
        try:
            write_file(out_path, result_text, encoding=encoding)
            print(TL('saved_to', lang).format(out_path))
        except Exception as e:
            print(TL('write_error', lang).format(e))
            return
    else:
        print(TL('invalid_save_choice', lang))
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
        print(TL('lang_num_from_name', lang).format(inferred))
    while True:
        raw = input(TL('lang_num_prompt', lang).format(inferred if inferred is not None else TL('no_suggestion', lang))).strip()
        if raw == '' and inferred is not None:
            lang_num = inferred
            break
        try:
            lang_num = int(raw)
            break
        except ValueError:
            print(TL('invalid_number', lang))

    lang_name = LANG_MAP.get(lang_num, (f"LANG_{lang_num}", ['latin-1']))[0]
    suggested_list = LANG_MAP.get(lang_num, (None, ['latin-1']))[1]
    suggested_encoding = suggested_list[0] if suggested_list else 'latin-1'
    print(TL('selected_lang', lang).format(lang_name, lang_num, ', '.join(suggested_list)))

    enc_choice = suggested_encoding or ''
    if enc_choice:
        use_sug = input(TL('use_suggested_enc', lang).format(enc_choice)).strip().lower()
        if use_sug == '' or use_sug in ('y','yes','t','tak'):
            chosen_enc = enc_choice
        else:
            chosen_enc = input(TL('enc_input_prompt', lang)).strip() or enc_choice
    else:
        chosen_enc = input(TL('enc_input_prompt', lang)).strip() or 'latin-1'

    try:
        header_bytes, texts_bytes = read_s4_dat(path_dat)
    except Exception as e:
        print(TL('dat_read_error', lang).format(e))
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
        if not confirm(TL('file_exists_overwrite', lang).format(out_path), default=False, lang=lang):
            print(TL('canceled_project_save', lang))
            return
    try:
        write_file(out_path, ''.join(parts), encoding=encoding_out)
        print(TL('project_saved', lang).format(out_path, encoding_out))
    except Exception as e:
        print(TL('project_write_error', lang).format(e))


def option_export_proj_to_dat(path_proj: Path | None = None, lang: str = 'en') -> None:
    """
    Eksportuje .s4_translation_project -> s4_texts.dat<langnum>
    Format: 4 bajty nagłówka, potem powtarzane: 4 bajty długości (little-endian), dane tekstu (bajty).
    Zapisuje wszystkie teksty od 1 do ostatniego numeru występującego w projekcie.
    Sugestia numeru języka pochodzi z nazwy pliku projektu (np. 'CHINESE' -> 7).
    """
    # 1) ścieżka pliku projektu
    if path_proj is None:
        while True:
            raw = input(TL('project_export_prompt', lang)).strip()
            if not raw:
                print(TL('project_path_required', lang))
                return
            try:
                path_proj = sanitize_path(raw)
            except Exception as e:
                print(TL('invalid_path', lang).format(e))
                continue
            if not path_proj.exists():
                print(TL('file_not_exists', lang).format('.s4_translation_project', path_proj))
                continue
            if not validate_project_file(path_proj, lang=lang):
                continue
            break
    else:
        if not validate_project_file(path_proj, lang=lang):
            return

    # 2) wczytaj i sparsuj projekt
    try:
        text = read_file(path_proj, encoding='utf-8')
    except Exception as e:
        print(TL('project_read_error', lang).format(e))
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
                        print(TL('header_found', lang).format(hb))
                except Exception:
                    header_bytes = None

    # jeśli nie znaleziono, poproś użytkownika o podanie 4 liczb
    if header_bytes is None:
        print(TL('header_not_found', lang))
        while True:
            raw_hdr = input(TL('header_prompt', lang)).strip()
            parts = raw_hdr.split()
            if len(parts) != 4:
                print(TL('exactly_4_numbers', lang))
                continue
            try:
                nums = [int(x) for x in parts]
                if any(n < 0 or n > 255 for n in nums):
                    print(TL('numbers_0_255', lang))
                    continue
                header_bytes = bytes(nums)
                break
            except ValueError:
                print(TL('invalid_numbers', lang))

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
    print(TL('available_langs', lang))
    for k in sorted(LANG_MAP.keys()):
        print(f"  {k} : {LANG_MAP[k][0]}")
    if inferred is not None:
        print(TL('lang_suggestion', lang).format(inferred, LANG_MAP[inferred][0]))
    while True:
        raw_lang = input(TL('lang_num_save_prompt', lang).format(inferred if inferred is not None else '')).strip()
        if raw_lang == '' and inferred is not None:
            lang_num = inferred
            break
        try:
            lang_num = int(raw_lang)
            if lang_num not in LANG_MAP:
                print(TL('unknown_lang_num', lang))
                continue
            break
        except ValueError:
            print(TL('invalid_number', lang))

    lang_name = LANG_MAP[lang_num][0]
    enc_candidates = LANG_MAP[lang_num][1][:]
    if 'utf-8' not in enc_candidates:
        enc_candidates.append('utf-8')

    print(TL('selected_lang', lang).format(lang_name, lang_num, ', '.join(enc_candidates)))
    chosen_enc = enc_candidates[0]
    use_sug = input(TL('use_suggested_enc', lang).format(chosen_enc)).strip().lower()
    if use_sug != '' and use_sug not in ('y','yes','t','tak'):
        custom = input(TL('custom_enc_prompt', lang)).strip()
        if custom:
            chosen_enc = custom

    # 5) ustal maksymalny numer do zapisu: zawsze zapisujemy wszystkie teksty od 1 do ostatniego istniejącego numeru
    existing_nums = sorted(blocks_map.keys())
    if existing_nums:
        max_index = max(existing_nums)
    else:
        print(TL('no_blocks', lang))
        return

    print(TL('save_texts_from_to', lang).format(max_index, max_index))

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
    out_input = input(TL('out_file_prompt', lang).format(default_out)).strip()
    if out_input == '':
        out_path = default_out
    else:
        out_path = sanitize_path(out_input)

    # 8) sprawdź nadpisanie
    if out_path.exists():
        if not confirm(TL('file_exists_overwrite', lang).format(out_path), default=False, lang=lang):
            alt = out_path.with_name(out_path.stem + '_exported' + out_path.suffix)
            print(TL('save_as_alt', lang).format(alt))
            if not confirm(TL('confirm_save_as', lang).format(alt), default=True, lang=lang):
                print(TL('save_canceled', lang))
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
        print(TL('dat_write_error', lang).format(e))
        return

    print(TL('dat_saved', lang).format(out_path))
    print(TL('last_text_num', lang).format(max_index))
    print(TL('texts_count', lang).format(len(texts_bytes), empty_count, chosen_enc))
    

# --- podgląd tekstów z pliku .dat z interaktywnym testowaniem kodowań i zapisu testu ---
def option_preview_dat(path_dat: Path, lang: str = 'en') -> None:
    inferred = infer_lang_from_filename(path_dat)
    if inferred is not None:
        print(TL('lang_num_from_name', lang).format(inferred))
    while True:
        raw = input(TL('lang_num_prompt', lang).format(inferred if inferred is not None else TL('no_suggestion', lang))).strip()
        if raw == '' and inferred is not None:
            lang_num = inferred
            break
        try:
            lang_num = int(raw)
            break
        except ValueError:
            print(TL('invalid_number', lang))

    lang_name = LANG_MAP.get(lang_num, (f"LANG_{lang_num}", ['latin-1']))[0]
    suggested_list = LANG_MAP.get(lang_num, (None, ['latin-1']))[1]
    print(TL('selected_lang', lang).format(lang_name, lang_num, ', '.join(suggested_list)))

    try:
        header_bytes, texts_bytes = read_s4_dat(path_dat)
    except Exception as e:
        print(TL('dat_read_error', lang).format(e))
        return

    total = len(texts_bytes)
    print(TL('texts_count_dat', lang).format(total))

    # wybór zakresu lub pojedynczego numeru; jeśli użytkownik wybierze "single" -> można testować wszystkie kodowania
    while True:
        sel = input(TL('range_prompt', lang)).strip()
        if sel.lower() == 'all':
            start_idx, end_idx = 1, total
            single_for_all_enc = False
            break
        if sel.lower() == 'single':
            while True:
                s2 = input(TL('single_text_prompt', lang)).strip()
                try:
                    idx = int(s2)
                    if idx < 1 or idx > total:
                        print(TL('out_of_range', lang))
                        continue
                    start_idx = end_idx = idx
                    single_for_all_enc = True
                    break
                except ValueError:
                    print(TL('invalid_number', lang))
            break
        if '-' in sel:
            parts = sel.split('-', 1)
            try:
                start_idx = int(parts[0])
                end_idx = int(parts[1])
                if start_idx < 1 or end_idx < start_idx:
                    print(TL('invalid_range', lang))
                    continue
                if start_idx > total:
                    print(TL('out_of_range_start', lang))
                    continue
                if end_idx > total:
                    end_idx = total
                single_for_all_enc = False
                break
            except ValueError:
                print(TL('invalid_format', lang))
                continue
        else:
            try:
                idx = int(sel)
                if idx < 1 or idx > total:
                    print(TL('out_of_range', lang))
                    continue
                start_idx = end_idx = idx
                single_for_all_enc = False
                break
            except ValueError:
                print(TL('invalid_number', lang))
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
        log_lines.append(TL('testing_single_text', lang).format(idx))
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
        save = input(TL('save_test_prompt', lang).format(lang_name)).strip().lower()
        if save in ('y','yes','t','tak'):
            out_path = path_dat.parent / f"{lang_name}_encoding_test.txt"
            if out_path.exists():
                if not confirm(TL('file_exists_overwrite', lang).format(out_path), default=False, lang=lang):
                    print(TL('canceled_test_save', lang))
                    return
            try:
                write_file(out_path, '\n'.join(log_lines), encoding='utf-8')
                print(TL('test_saved', lang).format(out_path))
            except Exception as e:
                print(TL('test_save_error', lang).format(e))
        else:
            print(TL('test_not_saved', lang))
        print(TL('end_all_enc_test', lang))
        return

    # interaktywne testowanie pojedynczych kodowań lub sekwencji
    default_enc = candidates[0] if candidates else 'latin-1'
    chosen_enc = default_enc

    while True:
        print(TL('suggested_encs', lang))
        for i, c in enumerate(candidates, start=1):
            print(f"  {i}) {c}")
        print(TL('custom_enc', lang))
        print(TL('back_to_menu', lang))

        sel_enc = input(TL('choose_enc_prompt', lang).format(default_enc)).strip()
        if sel_enc == '':
            chosen_enc = default_enc
        elif sel_enc.lower() in ('m','menu'):
            print(TL('back_to_menu_msg', lang))
            return
        elif sel_enc.lower() == 'a':
            chosen_enc = input(TL('custom_enc_prompt_preview', lang)).strip()
            if chosen_enc == '':
                chosen_enc = default_enc
        else:
            try:
                idx_choice = int(sel_enc)
                if 1 <= idx_choice <= len(candidates):
                    chosen_enc = candidates[idx_choice-1]
                else:
                    print(TL('invalid_enc_choice', lang))
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
        again = input(TL('test_another_enc', lang)).strip().lower()
        if again == '' or again in ('y','yes','t','tak'):
            continue
        else:
            # zapytaj czy zapisać log testu
            save = input(TL('save_test_prompt', lang).format(lang_name)).strip().lower()
            if save in ('y','yes','t','tak'):
                out_path = path_dat.parent / f"{lang_name}_encoding_test.txt"
                if out_path.exists():
                    if not confirm(TL('file_exists_overwrite', lang).format(out_path), default=False, lang=lang):
                        print(TL('canceled_test_save', lang))
                        return
                try:
                    write_file(out_path, '\n'.join(log_lines), encoding='utf-8')
                    print(TL('test_saved', lang).format(out_path))
                except Exception as e:
                    print(TL('test_save_error', lang).format(e))
            else:
                print(TL('test_not_saved', lang))
            print(TL('back_to_menu_msg', lang))
            return
    

# --- shift ids (przesunięcie numerów) ---
def option_shift_ids(path_a: Path, encoding: str = 'utf-8', lang: str = 'en') -> None:
    while True:
        raw_a2 = input(TL('path_a_prompt', lang)).strip()
        if not raw_a2:
            print(TL('path_a_required', lang))
            return
        try:
            path_a = sanitize_path(raw_a2)
        except Exception as e:
            print(TL('invalid_path', lang).format(e))
            continue
        if not path_a.exists():
            print(TL('file_not_exists', lang).format('A', path_a))
            continue
        if not validate_project_file(path_a, encoding, lang):
            continue
        break

    text_a = read_file(path_a, encoding=encoding)
    header_a, order_a, map_a = parse_blocks_linewise(text_a)

    if not order_a:
        print(TL('no_blocks_found', lang))
        return

    first = order_a[0]
    last = order_a[-1]
    count = len(order_a)
    print(TL('blocks_found', lang).format(count, first, last))

    while True:
        raw = input(TL('offset_prompt', lang)).strip()
        if raw == '':
            print(TL('no_value_canceled', lang))
            return
        try:
            offset = int(raw)
        except ValueError:
            print(TL('invalid_integer', lang))
            continue
        if offset == 0:
            print(TL('offset_zero', lang))
            return
        break

    new_ids = [i + offset for i in order_a]
    if any(i <= 0 for i in new_ids):
        print(TL('negative_ids_error', lang))
        return

    if len(set(new_ids)) != len(new_ids):
        print(TL('duplicates_error', lang))
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

    print(TL('save_shift_method', lang))
    print(TL('overwrite_a_backup', lang))
    print(TL('save_new_shift', lang))
    choice = input(TL('choose_1_or_2_shift', lang)).strip() or '2'

    if choice == '1':
        bak = path_a.with_suffix(path_a.suffix + '.bak')
        try:
            shutil.copy2(path_a, bak)
            print(TL('backup_created', lang).format(bak))
        except Exception as e:
            print(TL('backup_failed', lang).format(e))
            if not confirm(TL('continue_without_backup', lang), default=False, lang=lang):
                print(TL('canceled', lang))
                return
        try:
            write_file(path_a, result_text, encoding=encoding)
            print(TL('overwritten_a', lang).format(path_a))
        except Exception as e:
            print(TL('write_error', lang).format(e))
            return
    elif choice == '2':
        suggested = path_a.with_name(path_a.stem + '_shifted' + path_a.suffix)
        out_path_input = input(TL('out_path_prompt', lang).format(suggested)).strip()
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
                print(TL('dir_create_failed', lang).format(out_dir, e))
                return
        if out_path.exists():
            if not confirm(TL('file_exists_overwrite', lang).format(out_path), default=False, lang=lang):
                print(TL('canceled', lang))
                return
        try:
            write_file(out_path, result_text, encoding=encoding)
            print(TL('shifted_saved', lang).format(out_path))
        except Exception as e:
            print(TL('write_error', lang).format(e))
            return
    else:
        print(TL('invalid_save_choice', lang))
        return
        
def option_fix_missing_entries(path_proj: Path | None = None, encoding: str = 'utf-8', lang: str = 'en') -> None:
    """
    Uzupełnia brakujące wpisy ## Text N ## w pliku projektu.
    Pyta o nadpisanie lub zapis jako nowy plik <nazwa>_fixed.<ext>.
    """
    # pobierz ścieżkę pliku projektu
    if path_proj is None:
        while True:
            raw = input(TL('project_path_prompt', lang)).strip()
            if not raw:
                print(TL('no_path_canceled', lang))
                return
            try:
                path_proj = sanitize_path(raw)
            except Exception as e:
                print(TL('invalid_path', lang).format(e))
                continue
            if not path_proj.exists():
                print(TL('file_not_exists', lang).format('', path_proj))
                continue
            if not validate_project_file(path_proj, encoding, lang):
                continue
            break
    else:
        if not validate_project_file(path_proj, encoding, lang):
            return

    # wybór przedziału
    while True:
        rng = input(TL('range_fix_prompt', lang)).strip()
        if not rng:
            print(TL('no_range_canceled', lang))
            return
        if '-' in rng:
            parts = rng.split('-', 1)
            try:
                start = int(parts[0])
                end = int(parts[1])
                if start < 1 or end < start:
                    print(TL('invalid_range_fix', lang))
                    continue
                break
            except ValueError:
                print(TL('invalid_format', lang))
                continue
        else:
            try:
                n = int(rng)
                if n < 1:
                    print(TL('num_ge_1', lang))
                    continue
                start = end = n
                break
            except ValueError:
                print(TL('invalid_number', lang))
                continue

    # wczytaj plik i sparsuj bloki
    try:
        text = read_file(path_proj, encoding=encoding)
    except Exception as e:
        print(TL('project_read_error', lang).format(e))
        return

    header, order, blocks_map = parse_blocks_linewise(text)

    # zbierz brakujące numery
    missing = []
    for i in range(start, end + 1):
        if i not in blocks_map:
            missing.append(i)

    if not missing:
        print(TL('no_missing_entries', lang))
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
    print(TL('missing_found', lang).format(len(added)))
    if added:
        print(TL('added_numbers_fix', lang).format(', '.join(map(str, added))))
    else:
        print(TL('no_added_unexpected', lang))

    print(TL('overwrite_prompt', lang))
    if confirm(TL('overwrite_file', lang), default=False, lang=lang):
        try:
            write_file(path_proj, result_text, encoding=encoding)
            print(TL('overwritten', lang).format(path_proj))
        except Exception as e:
            print(TL('write_error', lang).format(e))
        return

    # jeśli NIE nadpisujemy → zapisz jako nowy
    ext = path_proj.suffix
    stem = path_proj.stem
    new_path = path_proj.with_name(f"{stem}_fixed{ext}")

    print(TL('save_as_new', lang).format(new_path))
    if confirm(TL('save_as_new', lang), default=True, lang=lang):
        try:
            write_file(new_path, result_text, encoding=encoding)
            print(TL('new_saved', lang).format(new_path))
        except Exception as e:
            print(TL('write_error', lang).format(e))
    else:
        print(TL('save_canceled', lang))

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
        print(TL('file_not_exists', lang).format('A', path_a))
        return
    if not path_b.exists():
        print(TL('file_not_exists', lang).format('B', path_b))
        return

    # walidacja poprawności plików projektu
    if not validate_project_file(path_a, encoding, lang) or not validate_project_file(path_b, encoding, lang):
        return

    # wczytanie i parsowanie
    text_a = read_file(path_a, encoding=encoding)
    text_b = read_file(path_b, encoding=encoding)
    header_a, order_a, map_a = parse_blocks_linewise(text_a)
    header_b, order_b, map_b = parse_blocks_linewise(text_b)

    total_a = len(order_a)
    total_b = len(order_b)
    print(TL('files_count', lang).format(path_a, total_a, path_b, total_b))

    # ile prób przesunięcia w A (domyślnie)
    try:
        raw = input(TL('max_tries_prompt', lang).format(max_tries_default)).strip()
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

            # jeśli to nie pierwsza pierwsza próba i candidate jest placeholderem, pomiń (szukamy znaczącego)
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
                print(TL('new_offset_set', lang).format(current_offset, candidate_n, m_index))

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
            reason = TL('no_offset_reason', lang)
            missing_similarity.append((na, None, None, reason))
            continue

        mb_guess = na + off

        if mb_guess not in map_b:
            reason = TL('mb_guess_not_exist', lang)
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
    print(TL('alignment_report', lang))
    print(TL('matched_pairs_count', lang).format(len(matched_pairs)))
    if matching_ranges:
        print(TL('matched_ranges', lang))
        last_offset = None
        for (a1, a2, b1, b2, off) in matching_ranges:
            note = ""
            if off != last_offset:
                note = TL('new_offset_note', lang).format(off)
                last_offset = off
            if a1 == a2:
                print(f"  {a1} => {b1}{note}")
            else:
                print(f"  {a1}-{a2} => {b1}-{b2}{note}")
    else:
        print(TL('no_matched_ranges', lang))

    if missing_ranges:
        print(TL('missing_in_b', lang))
        for (s, e) in missing_ranges:
            if s == e:
                print(f"  {s}")
            else:
                print(f"  {s}-{e}")
    else:
        print(TL('all_found', lang))

    # raport podobieństw dla missing_in_b (szczegóły)
    if missing_similarity:
        print(TL('missing_details', lang))
        for na, mb_guess, sim, reason in missing_similarity:
            if mb_guess is None:
                print(TL('no_offset', lang).format(na))
            elif sim is None:
                print(TL('no_sim', lang).format(na, mb_guess, reason))
            else:
                print(TL('with_sim', lang).format(na, sim, mb_guess))

    if placeholder_cases:
        print(TL('placeholder_cases', lang))
        for na, mb in placeholder_cases:
            print(f"  A:{na}  <-  B:{mb}")

    if conflicts:
        print(TL('conflicts', lang))
        conflicts_sorted = sorted(conflicts, key=lambda x: -(x[4] or 0))
        for na, mb, ta, tb, sim in conflicts_sorted:
            sim_str = f"{sim}%" if sim is not None else "n/a"
            print(f"  A:{na}  !=  B:{mb}   {TL('similarity', lang)}: {sim_str}")

    # raport historii offsetów
    if offset_history:
        print(TL('offset_history', lang))
        for off, aidx, bidx in offset_history:
            print(TL('offset_set_at', lang).format(off, aidx, bidx))
            
        # --- opcjonalne wygenerowanie i zapis mapy przesunięć (offsetów) ---
        # Zbuduj listę prostych wpisów z offset_history: "A:<aidx> offset <off>"
        shift_lines = []
        # offset_history jest listą (offset, a_index, b_index) w kolejności ustawiania
        for off, aidx, bidx in offset_history:
            shift_lines.append(f"A:{aidx} offset {off}")

        # domyślnie pokażemy mapę w konsoli
        print()
        print(TL('shift_map_preview_title', lang))
        for line in shift_lines:
            print("  " + line)

        # zapytaj użytkownika, czy chce zapisać mapę do pliku
        if confirm(TL('save_shift_map_prompt', lang), default=False, lang=lang):
            default_name = 'text_shift_map.txt'
            name = input(TL('shift_map_filename_prompt', lang)).strip() or default_name

            try:
                # Jeśli użytkownik podał ścieżkę absolutną lub względną — próbujemy ją znormalizować
                try:
                    out_map_path = sanitize_path(name)
                except Exception:
                    # Jeśli sanitize_path nie działa (np. sama nazwa pliku),
                    # to zapisujemy w katalogu pliku A
                    out_map_path = path_a.parent / name

                # Jeśli użytkownik podał samą nazwę pliku (bez ścieżki),
                # sanitize_path zwróci nazwę w bieżącym katalogu — poprawiamy to:
                if not out_map_path.is_absolute():
                    out_map_path = path_a.parent / out_map_path

                # Jeśli wskazano katalog — dodaj domyślną nazwę
                if out_map_path.is_dir():
                    out_map_path = out_map_path / default_name

                # Zapis pliku
                map_text = '\n'.join(shift_lines) + '\n'
                write_file(out_map_path, map_text, encoding=encoding)
                print(TL('shift_map_saved', lang).format(out_map_path))

            except Exception as e:
                print(TL('shift_map_save_error', lang).format(e))
    # jeśli brak mapowań i brak offsetów, kończymy
    elif not mappings:
        print(TL('no_matches', lang))
        return



    # jeśli brak mapowań i brak offsetów, kończymy
    if not mappings and not offset_history:
        print(TL('no_matches', lang))
        return

    # potwierdzenie zapisu
    total_to_save = len(mappings)
    print(TL('save_intent', lang).format(total_to_save))
    sample = matched_pairs[:20]
    if sample:
        print(TL('sample_mappings', lang).format(', '.join(f"{a}->{b}" for a, b in sample)))

    if confirm(TL('overwrite_direct', lang), default=False, lang=lang):
        out_path = path_a
    else:
        out_path = path_a.with_name(path_a.stem + '_aligned' + path_a.suffix)
        if out_path.exists():
            if not confirm(TL('file_exists_overwrite', lang).format(out_path), default=False, lang=lang):
                print(TL('save_canceled', lang))
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
        print(TL('no_targets', lang))
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
        print(TL('write_error', lang).format(e))
        return

    # końcowy raport zapisu
    print(TL('saved_to', lang).format(out_path))
    print(TL('updated_entries', lang).format(len(mappings)))

    # policz przypisania przez offset
    assigned_by_offset: list[tuple[int, int, int]] = []
    for na in sorted(map_a.keys()):
        if na not in mappings:
            off = find_offset_for_na(na, matching_ranges_sorted, offset_history_sorted)
            if off is not None:
                assigned_by_offset.append((na, na + off, off))

    if assigned_by_offset:
        print(TL('assigned_by_offset', lang).format(len(assigned_by_offset)))
        for na, mb_guess, off in assigned_by_offset[:200]:
            print(TL('assigned_example', lang).format(na, mb_guess, off))

    if collisions:
        print(TL('collisions_warning', lang))
        for c in collisions[:50]:
            print(TL('collision_example', lang).format(c[0], c[1]))

    print(TL('last_a_num', lang).format(max(sorted(map_a.keys())) if map_a else 0))
    print(TL('done', lang))
    
    
def option_apply_map(path_a: Path, path_map: Path | None = None, encoding: str = 'utf-8', lang: str = 'en') -> None:
    """
    Zastosuj mapę przesunięć do pliku projektu A.
    - Jeśli path_map wskazuje plik .txt: wykonujemy rygorystyczną walidację formatu.
    - Jeśli path_map jest None: użytkownik może wkleić mapę (luźniejsze parsowanie).
    Format akceptowanych linii (przykłady):
      A:1 offset 663
      1 663
      1,663
      1->664   (interpretowane jako new - old -> offset)
    Komentarze: linie zaczynające się od '#' są ignorowane.
    """

    from operator import itemgetter

    # WALIDACJE WEJŚCIA
    if not path_a or not isinstance(path_a, Path):
        print(TL('invalid_path', lang))
        return
    if not path_a.exists():
        print(TL('file_not_exists', lang).format('A', path_a))
        return
    if not validate_project_file(path_a, encoding, lang):
        return

    # Wczytaj projekt A
    try:
        text_a = read_file(path_a, encoding=encoding)
    except Exception as e:
        print(TL('read_error', lang).format(e))
        return
    header_a, order_a, map_a = parse_blocks_linewise(text_a)
    if not order_a:
        print(TL('no_blocks_found', lang))
        return

    # Wczytaj mapę: z pliku jeśli podano, inaczej poproś o wklejenie
    raw_lines = []
    map_from_file = False
    if path_map:
        map_from_file = True
        if not path_map.exists():
            print(TL('file_not_exists', lang).format('map', path_map))
            return
        try:
            raw_map_text = read_file(path_map, encoding=encoding)
        except Exception as e:
            print(TL('map_read_error', lang).format(e))
            return
        raw_lines = [ln.rstrip('\n') for ln in raw_map_text.splitlines()]
    else:
        # tryb wklejania
        print(TL('paste_map_instructions', lang))
        pasted = []
        while True:
            try:
                line = input().rstrip('\n')
            except EOFError:
                break
            if line == '':
                break
            pasted.append(line)
        raw_lines = pasted

    # Normalizacja: usuń puste i komentarze
    raw_lines = [ln.strip() for ln in raw_lines if ln.strip() and not ln.strip().startswith('#')]
    if not raw_lines:
        print(TL('map_empty', lang))
        return

    # RYGORYSTYCZNA WALIDACJA (tylko gdy mapa pochodzi z pliku .txt)
    # Dozwolone wzorce:
    # 1) A:<num> ... offset <num>
    # 2) <num> <num>   (oddzielone spacją)
    # 3) <num>,<num>
    # 4) <num>-><num>
    int_re = re.compile(r'-?\d+')
    allowed_line_re = re.compile(
        r'^\s*(?:A\s*:\s*\d+\s*(?:.*offset\s*-?\d+)?|\d+\s+[-]?\d+|\d+\s*,\s*-?\d+|\d+\s*[-=]>\s*\d+)\s*$', re.IGNORECASE
    )

    if map_from_file:
        bad_lines = []
        for ln in raw_lines:
            if not allowed_line_re.match(ln):
                bad_lines.append(ln)
        if bad_lines:
            print(TL('map_file_invalid_lines', lang))
            for bl in bad_lines[:50]:
                print("  " + bl)
            print(TL('map_file_fix_and_retry', lang))
            return

    # Parsowanie linii mapy (elastyczne)
    map_entries = []
    for ln in raw_lines:
        # prefer pattern A:<num> ... offset <num>
        m = re.search(r'A\s*[:]\s*(\d+)', ln, flags=re.IGNORECASE)
        if m:
            aidx = int(m.group(1))
            m_off = re.search(r'offset\s*[:=]?\s*(-?\d+)', ln, flags=re.IGNORECASE)
            if m_off:
                off = int(m_off.group(1))
                map_entries.append((aidx, off))
                continue
        # dwie liczby w linii
        nums = int_re.findall(ln)
        if len(nums) >= 2:
            aidx = int(nums[0])
            off = int(nums[1])
            map_entries.append((aidx, off))
            continue
        # format arrow: 1->664 (interpretujemy jako newnum)
        m_arrow = re.search(r'(\d+)\s*[-=]>\s*(\d+)', ln)
        if m_arrow:
            aidx = int(m_arrow.group(1))
            newnum = int(m_arrow.group(2))
            off = newnum - aidx
            map_entries.append((aidx, off))
            continue
        # jeśli nie sparsowano (w trybie paste tylko) — zgłoś i pomiń
        print(TL('map_line_unparsed', lang).format(ln))

    if not map_entries:
        print(TL('map_no_valid_entries', lang))
        return

    # Sortuj i deduplikuj (pierwszy występ ma priorytet)
    map_entries_sorted = sorted(map_entries, key=itemgetter(0))
    deduped = []
    seen = set()
    for aidx, off in map_entries_sorted:
        if aidx in seen:
            continue
        seen.add(aidx)
        deduped.append((aidx, off))
    map_entries_sorted = deduped

    # Stosowanie offsetów sekwencyjnie
    map_ptr = 0
    current_offset = 0
    next_map_aidx, next_map_off = map_entries_sorted[map_ptr] if map_ptr < len(map_entries_sorted) else (None, None)

    target_map = {}
    collisions = []
    applied_changes = []  # (na, target_idx, offset)

    for na in sorted(order_a):
        # jeśli osiągamy punkt startu kolejnego wpisu mapy -> ustaw nowy offset
        while next_map_aidx is not None and na >= next_map_aidx:
            current_offset = next_map_off
            map_ptr += 1
            if map_ptr < len(map_entries_sorted):
                next_map_aidx, next_map_off = map_entries_sorted[map_ptr]
            else:
                next_map_aidx, next_map_off = (None, None)
        target_idx = na + current_offset
        if target_idx in target_map:
            collisions.append((na, target_idx))
        target_map[target_idx] = map_a.get(na, '')
        applied_changes.append((na, target_idx, current_offset))

    # Walidacja wyników
    bad_targets = [t for t in target_map.keys() if not isinstance(t, int) or t <= 0]
    if bad_targets:
        print(TL('negative_or_zero_targets', lang).format(len(bad_targets)))
        return

    # Zbuduj wynikowy tekst
    target_indices = sorted(k for k in target_map.keys() if isinstance(k, int))
    parts = []
    parts.append(header_a if header_a.endswith('\n') or header_a == '' else header_a + '\n')
    for idx in target_indices:
        parts.append(f'## Text {idx} ##\n')
        content = target_map.get(idx, '')
        if content != '':
            parts.append(f'{content}\n')
        parts.append('####\n')
    result_text = ''.join(parts)

    # Raport przed zapisem
    print(TL('map_apply_preview', lang))
    print(TL('map_apply_changes_count', lang).format(len(target_indices)))
    if map_entries_sorted:
        print(TL('map_apply_changes_list', lang))
        for aidx, off in map_entries_sorted:
            print(f"  A:{aidx} offset {off}")
    if collisions:
        print(TL('map_apply_collisions', lang).format(len(collisions)))
        for c in collisions[:50]:
            print(TL('collision_example', lang).format(c[0], c[1]))

    # Zapis (backup lub nowy plik) — ta część jest taka sama jak w option_shift_ids
    print(TL('save_shift_method', lang))
    print(TL('overwrite_a_backup', lang))
    print(TL('save_new_shift', lang))
    choice = input(TL('choose_1_or_2_shift', lang)).strip() or '2'

    if choice == '1':
        bak = path_a.with_suffix(path_a.suffix + '.bak')
        try:
            shutil.copy2(path_a, bak)
            print(TL('backup_created', lang).format(bak))
        except Exception as e:
            print(TL('backup_failed', lang).format(e))
            if not confirm(TL('continue_without_backup', lang), default=False, lang=lang):
                print(TL('canceled', lang))
                return
        try:
            write_file(path_a, result_text, encoding=encoding)
            print(TL('overwritten_a', lang).format(path_a))
        except Exception as e:
            print(TL('write_error', lang).format(e))
            return
    elif choice == '2':
        suggested = path_a.with_name(path_a.stem + '_shifted' + path_a.suffix)
        out_path_input = input(TL('out_path_prompt', lang).format(suggested)).strip()
        if out_path_input == '':
            out_path = suggested
        else:
            try:
                candidate = sanitize_path(out_path_input)
            except Exception:
                candidate = Path(out_path_input)
            if candidate.exists() and candidate.is_dir():
                out_path = candidate / suggested.name
            else:
                out_path = candidate
        out_dir = out_path.parent
        if not out_dir.exists():
            try:
                out_dir.mkdir(parents=True, exist_ok=True)
            except Exception as e:
                print(TL('dir_create_failed', lang).format(out_dir, e))
                return
        if out_path.exists():
            if not confirm(TL('file_exists_overwrite', lang).format(out_path), default=False, lang=lang):
                print(TL('canceled', lang))
                return
        try:
            write_file(out_path, result_text, encoding=encoding)
            print(TL('shifted_saved', lang).format(out_path))
        except Exception as e:
            print(TL('write_error', lang).format(e))
            return
    else:
        print(TL('invalid_save_choice', lang))
        return

    # Końcowy raport
    print(TL('map_apply_done', lang))
    for aidx, off in map_entries_sorted:
        print(f"  A:{aidx} offset {off}")
    
    
# --------------------------------------------------------------------------------------------------------
# --- main menu ---
def main(lang: str = 'en') -> None:
    while True:
        print(TL('main_menu_title', lang))
        print(TL('main_menu_options', lang))
        choice = input(TL('main_menu_prompt', lang)).strip() or '0'

        # dopuszczalne opcje: 0..9
        if choice not in {'0','1','2','3','4','5','6','7','8','9'}:
            print(TL('invalid_choice', lang))
            continue

        # wyjście (teraz 0)
        if choice == '0':
            print(TL('exit_message', lang))
            input(TL('press_enter_to_exit', lang))
            sys.exit(0)

        # Import z .dat
        if choice == '3':
            while True:
                raw_dat = input(TL('path_dat_prompt', lang)).strip()
                if not raw_dat:
                    print(TL('path_required', lang))
                    break
                try:
                    path_dat = sanitize_path(raw_dat)
                except Exception as e:
                    print(TL('invalid_path', lang).format(e))
                    continue
                if not path_dat.exists():
                    print(TL('file_not_exists', lang).format('.dat', path_dat))
                    continue
                if not validate_dat_file(path_dat, lang):
                    continue
                option_import_s4(path_dat, encoding_out='utf-8', lang=lang)
                break
            continue

        # Eksport do .dat
        if choice == '4':
            while True:
                raw_proj = input(TL('project_export_prompt', lang)).strip()
                if not raw_proj:
                    print(TL('project_path_required', lang))
                    break
                try:
                    path_proj = sanitize_path(raw_proj)
                except Exception as e:
                    print(TL('invalid_path', lang).format(e))
                    continue
                if not path_proj.exists():
                    print(TL('file_not_exists', lang).format('.s4_translation_project', path_proj))
                    continue
                if not validate_project_file(path_proj, 'utf-8', lang):
                    continue
                option_export_proj_to_dat(path_proj, lang=lang)
                break
            continue

        # Podgląd .dat
        if choice == '5':
            while True:
                raw_dat = input(TL('path_dat_preview_prompt', lang)).strip()
                if not raw_dat:
                    print(TL('path_required', lang))
                    break
                try:
                    path_dat = sanitize_path(raw_dat)
                except Exception as e:
                    print(TL('invalid_path', lang).format(e))
                    continue
                if not path_dat.exists():
                    print(TL('file_not_exists', lang).format('.dat', path_dat))
                    continue
                if not validate_dat_file(path_dat, lang):
                    continue
                option_preview_dat(path_dat, lang=lang)
                break
            continue

        # Opcje wymagające dwóch projektów A i B (1,2,8)
        if choice in {'1','2','8'}:
            while True:
                raw_a = input(TL('path_a_prompt', lang)).strip()
                if not raw_a:
                    print(TL('required_paths', lang))
                    break
                try:
                    path_a = sanitize_path(raw_a)
                except Exception as e:
                    print(TL('invalid_path', lang).format(e))
                    continue
                if not path_a.exists():
                    print(TL('file_not_exists', lang).format('A', path_a))
                    continue
                if not validate_project_file(path_a, 'utf-8', lang):
                    continue
                break

            while True:
                raw_b = input(TL('path_b_prompt', lang)).strip()
                if not raw_b:
                    print(TL('required_paths', lang))
                    break
                try:
                    path_b = sanitize_path(raw_b)
                except Exception as e:
                    print(TL('invalid_path', lang).format(e))
                    continue
                if not path_b.exists():
                    print(TL('file_not_exists', lang).format('B', path_b))
                    continue
                if not validate_project_file(path_b, 'utf-8', lang):
                    continue
                break

            if not raw_a or not raw_b:
                continue

            encoding = input(TL('encoding_prompt', lang)).strip() or 'utf-8'

            if choice == '1':
                out_name = input(TL('out_name_prompt', lang)).strip() or 'missingtexts.txt'
                out_path, missing_ids = generate_missing_texts(path_a, path_b, encoding=encoding, out_name=out_name, lang=lang)
                if out_path is None:
                    print(TL('no_missingtexts_saved', lang))
                else:
                    print(TL('missingtexts_saved', lang).format(out_path))
                    if missing_ids:
                        print(TL('missing_blocks_count', lang).format(len(missing_ids), ', '.join(map(str, missing_ids))))
                    else:
                        print(TL('no_missing_blocks', lang))
            elif choice == '2':
                option_merge(path_a, path_b, encoding=encoding, lang=lang)
            else:
                # zamiast merge uruchamiamy dopasowanie wersji A względem B
                option_align_versions(path_a, path_b, encoding=encoding, lang=lang)
            continue

        # Przesuń numery (offset)
        if choice == '6':
            while True:
                raw_a2 = input(TL('path_a_prompt', lang)).strip()
                if not raw_a2:
                    print(TL('path_a_required', lang))
                    break
                try:
                    path_a = sanitize_path(raw_a2)
                except Exception as e:
                    print(TL('invalid_path', lang).format(e))
                    continue
                if not path_a.exists():
                    print(TL('file_not_exists', lang).format('A', path_a))
                    continue
                if not validate_project_file(path_a, 'utf-8', lang):
                    continue
                break
            if not raw_a2:
                continue
            encoding = input(TL('encoding_prompt', lang)).strip() or 'utf-8'
            option_shift_ids(path_a, encoding=encoding, lang=lang)
            continue

        # Napraw brakujące wpisy w projekcie
        if choice == '7':
            while True:
                raw_proj = input(TL('project_path_prompt', lang)).strip()
                if not raw_proj:
                    print(TL('no_path_canceled', lang))
                    break
                try:
                    path_proj = sanitize_path(raw_proj)
                except Exception as e:
                    print(TL('invalid_path', lang).format(e))
                    continue
                if not path_proj.exists():
                    print(TL('file_not_exists', lang).format('', path_proj))
                    continue
                if not validate_project_file(path_proj, 'utf-8', lang):
                    continue
                option_fix_missing_entries(path_proj, encoding='utf-8', lang=lang)
                break
            continue

        # OPCJA 9: Zastosuj mapę numerów do pliku projektu A
        if choice == '9':
            # wybór pliku projektu A
            path_a_map: Path | None = None
            while True:
                raw_a_map = input(TL('path_a_prompt', lang)).strip()
                if not raw_a_map:
                    print(TL('path_a_required', lang))
                    break
                try:
                    candidate_a = sanitize_path(raw_a_map)
                except Exception as e:
                    print(TL('invalid_path', lang).format(e))
                    continue
                if not candidate_a.exists():
                    print(TL('file_not_exists', lang).format('A', candidate_a))
                    continue
                if not validate_project_file(candidate_a, 'utf-8', lang):
                    continue
                path_a_map = candidate_a
                break

            if path_a_map is None:
                # użytkownik przerwał lub nie podał poprawnej ścieżki
                continue

            # wybór pliku mapy (opcjonalnie — jeśli nie poda, będzie tryb wklejania)
            path_map: Path | None = None
            while True:
                raw_map = input(TL('map_file_prompt', lang)).strip()
                if not raw_map:
                    # brak pliku mapy -> przejdziemy w tryb wklejania w option_apply_map
                    break
                try:
                    candidate_map = sanitize_path(raw_map)
                except Exception as e:
                    print(TL('invalid_path', lang).format(e))
                    continue
                if not candidate_map.exists():
                    print(TL('file_not_exists', lang).format('map', candidate_map))
                    continue
                path_map = candidate_map
                break

            try:
                option_apply_map(path_a_map, path_map, encoding='utf-8', lang=lang)
            except Exception as e:
                print(TL('map_apply_error', lang).format(e))
            continue





 
if __name__ == '__main__':
    print(
        "Choose program language / Wählen Sie die Sprache /  Wybierz język / "
        "Scegli la lingua / Elige el idioma / 选择语言 / Выберите язык / 言語を選択:\n"
        "0) English\n"
        "1) Deutsch\n"
        "2) Polski\n"
        "3) Italiano\n"
        "4) Español\n"
        "5) 简体中文\n"
        "6) Русский\n"
        "7) 日本語\n"
        "[0]: ",
        end=""
    )

    lang_choice = input().strip() or '0'

    lang_map = {
        '0': 'en',
        '1': 'de',
        '2': 'pl',
        '3': 'it',
        '4': 'es',
        '5': 'zh',
        '6': 'ru',
        '7': 'ja'
    }

    lang = lang_map.get(lang_choice, 'en')
    main(lang=lang)
