# Errata in the source text files

Notes for other localisers, found while producing the Hebrew translation.

The game's development language is **German**. Every other file, **including the
English**, is a translation of it — so the English contains translation errors, and any
language translated *from the English* has probably inherited them. Several have.

If you maintain another language file, the items in §1 are worth checking on your side.

**Evidence for German being the source**, since some of the notes below depend on it:
entry **715** credits `Übersetzung ins Englische` — "translation *into* English" — and
there is no reciprocal "translation into German" anywhere in the sixteen files. Every
garbled English sentence has a clean German counterpart and never the reverse (see §3).
**108** German entries use formal *Sie*, a register English does not have. Blue Byte
(credited at entry 139) was a Düsseldorf studio.

**But German is not automatically right** — see §2. Where English and German conflict, the
most reliable tiebreaker we found is **Hungarian**, which is German-derived: the reading
Hungarian shares is usually the intended one. Czech, Polish and Russian follow the English
closely and so corroborate nothing.

---

## 1. English mistranslations that changed the meaning

### 1.1 Entry 3019 — "sinned" should be "atoned"

| | |
|---|---|
| German | `Doch die Frevler haben noch nicht **gesühnt**.` |
| English | "But the blasphemers have not yet **sinned**..." |

`sühnen` means **to atone / to expiate**, not *to sin* (`sündigen`). The English reading
contradicts the sentence immediately before it — *"The blasphemers destroyed the
temples!"* — and destroys the purpose of the line, which is to set up the mission: the
blasphemers have not yet been **punished**, so go and punish them. The next paragraph is
"our scouts have located the enemy settlements … Thor's Hammer will crush them."

`gesündigt` appears **nowhere** in the German file; `gesühnt` appears exactly once, here.

**Inherited by:** Czech (`nezhřešili`), Polish (`nie zgrzeszyli`), Russian
(`еще не согрешили`). **French** dropped the sentence entirely. **Hungarian** got it right
(`nem bűnhödött meg`, "has not been punished") — it is the only language besides German
that does.

### 1.2 Entry 3000 — wrong direction, and the English contradicts itself

| | |
|---|---|
| German | `Erobern Sie den Heiligen Baum im **Südosten**!` |
| English | "Take over the Holy Tree in the **Southwest**!" |

This is a **mission objective**, so it sends the player to the wrong corner of the map.

The decisive evidence needs no cross-language argument at all: **entry 3018, the briefing
for this same mission, says "Southeast" in the English itself** — "another Mayan settlement
to the Southeast … We must conquer the Holy Tree in the Southeast." The German says
`Südosten` in both 3000 and 3018 and is self-consistent; the English contradicts itself two
entries apart about where one object is.

**Inherited by:** Czech (`jihozápadě`), French (`sud-ouest`), Polish
(`południowym zachodzie`), Russian (`юго-западе`), Hungarian (`délnyugatra`) — note
Hungarian's own 3018 says `délkeletre`, southeast, so it too is now self-contradictory.

### 1.3 Entries 2016, 2055, 2304, 2315 — "Settlefest" is not a festival

| | |
|---|---|
| German | `Wettsiedeln` |
| English | `Settlefest` / `Settlefest Mode` |

`Wett-` is the German competitive prefix (*Wettlauf* = race, *Wettkampf* = contest,
*Wettbewerb* = competition). **`Wettsiedeln` is a settling *race*** — a build-fastest game
mode. It has nothing to do with a feast.

The German makes it a deliberate pair with **`Freies Siedeln`** ("Free Settle") in the same
mode list. "Settlefest" reads as *settle + festival*, and the languages that worked from
the English followed it into "fest":

| Read the German correctly | Followed the English "fest" |
|---|---|
| Chinese 建设竞赛 "construction competition" | Danish `Bosætterfest` |
| Japanese 入植競争 "settlement competition" | Swedish `Nybyggarfest` |
| French `Mode développement` | Spanish `Fiesta colonial` |
| Hungarian `Szimultán` (simultaneous) | Czech `Slavnosti osadníků` "settlers' festivities" |
| Korean 개별 정착 "individual settling" | Norwegian `Nybyggerbonanza` |
| | Russian `Праздник жизни` "feast of life" |

Italian and Polish left it untranslated as "Settlefest".

### 1.4 Entry 2767 — the agent is inverted

| | |
|---|---|
| German | `…werden uns auch die letzten kampfbereiten Trojaner **nicht aufhalten können**.` |
| English | "…**we won't be able to stop** the last belligerent Trojans." |

German: *the last battle-ready Trojans will not be able to stop **us***. The English
reverses who is stopping whom, which also contradicts the next sentence, "Only we shall
emerge victorious from this battle!"

### 1.5 Entry 3776 — a relative clause attached to the wrong person

| | |
|---|---|
| German | `Cortés der sich über die ausbleibenden Berichte der Pinedo-Expedition wundert, schickt Späher aus.` |
| English | "The Huastecs are crushing the Spaniards led by Alonso Alvárez Pinedo, **who is surprised by the lack of reports from the Pinedo expedition**, and has sent out Scouts…" |

German has two sentences and **Cortés** is the one puzzled by the missing reports. The
English merged them, leaving "who is surprised" dangling off **Pinedo** — who cannot be
surprised by the absence of reports from his own expedition.

### 1.6 Entry 3251 — unresolved, please check on your side

| | |
|---|---|
| German | `An der **südöstlichen** Küste sind fremdartige Wesen gelandet.` |
| English | "Strange creatures have landed on the **southwest** coast." |

The same `Südost` → "southwest" slip as §1.2, but here there is **no second entry to
arbitrate against**, so we could not settle it from the files alone. Czech, French, Polish
and Russian all say southwest. If anyone can confirm in play which coast the creatures
actually land on, that resolves it.

## 2. Where the German is the one that is wrong

### 2.1 Entry 3738 — German says east, everyone else says west

| | |
|---|---|
| German | `Besiegen Sie die Römer im Gebiet **östlich** von Ihnen.` |
| English | "Defeat the Romans in the area to your **west**." |

**Thirteen** languages say west — Chinese 西方, Czech `západní`, Danish `vest`, French
`ouest`, Hungarian `nyugatra`, Italian `occidentale`, Japanese 西, Korean 서쪽, Norwegian
`vest`, Polish `zachodzie`, Spanish `oeste`, Swedish `väster`, plus English. German is the
lone outlier, and **Hungarian sides against it here**.

(Russian says `на севере`, north — a third, separate error.)

### 2.2 Entry 3838 — German says "no fishermen" where it means "no fish"

| | |
|---|---|
| German | `Diese Fischerhütte findet in seinem jetzigen Arbeitsbereich keine **Fischer** mehr` |
| English | "This Fisherman's Hut can no longer find any **fish** in the working area" |

`Fischer` is *fisherman*; `Fische` is *fish*. The hut is short of fish, not staff. The
English corrected it. (The German also has `in **seinem**` where `Fischerhütte` is
feminine — `in ihrem`.)

## 3. English typos and slips

Cosmetic, but they are visible in-game and they are what identifies the English as the
downstream translation — each has a clean German counterpart.

| Entry | English | Should be |
|---|---|---|
| 2773 | "You **have to must** sneak over the island" | one modal (`Sie müssen sich … schleichen`) |
| 453 | "Our **must** vulnerable point has been hit." | "most" (`Unser wundester Punkt`) |
| 2895 | "We haven't **become get** fat and lazy" | "become" (`Wir sind nicht fett und faul geworden`) |
| 3211 | "**Immeasureable** in size" | "Immeasurable" (`unermesslich`) |
| 2897 | "have **no affect**" | "no effect" |
| 583 | "that **chared** ground" | "charred" |
| 3596 | "the **mininmum** or maximum contingent" | "minimum" |
| 3344 | "**Lano** Estacado" in the title, "**Lana** Estacado" in the body | one spelling (the real place is *Llano Estacado*) |
| 3115 | "Dirk **Wihelmy**" | "Wilhelmy", as spelled correctly at entry 183 |

## 4. An inconsistency present in the German original

**Entry 1579 — `Saboteur`, singular, in a list of plurals.** The unit-filter list uses
plural labels throughout: `Axe Warriors` / `Axtkämpfer`, `Bowmen` / `Bogenschützen`,
`Priests` / `Priester`, `Gardeners` / `Gärtner`. Entry 1579 is singular in **both** German
and English (`Saboteur`), while its own paired tooltip at 1580 is plural ("Show
Saboteur**s** in the selected area").

This is a source-level slip rather than a translation error, but it makes localisers guess.
Italian (`Sabotatori`), Polish (`Sabotażyści`) and Russian (`Саботажники`) pluralised it;
most other languages kept the singular.

## 5. Structural note on the `.dat` files

The shipped `Binaries/Txt/s4_texts.dat<n>` files fall into two families:

| header | records | languages |
|---|---|---|
| 21 | 3838 | English (0), German (1), French (2), Polish (5), Russian (16) |
| 15 | 3754 | Spanish, Italian, Korean, Chinese, Swedish, Danish, Norwegian, Hungarian, Hebrew, Czech, Finnish, Japanese |

The second family is 84 records short and therefore cannot address the last entries at
all, including **3838**, the Fisherman's Hut message above. If you are completing a
language in that family, note that the record count — not just the text — has to grow, and
the 4-byte header changes from 15 to 21.

Format, for reference: a 4-byte header, then per entry a 4-byte little-endian length
followed by that many bytes of text in the language's legacy code page. Absent or empty
entries are written as length 0.

---

*All quotations above were verified directly against the files in
`projects/History Edition/` at the time of writing.*
