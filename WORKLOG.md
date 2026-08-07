# Tööregister — Trenn ja toitumine

Kerge päevapõhine logi: mida tehti, hinnanguline aeg.
Seosed: [PROJECT.md](PROJECT.md) (versioonid + roadmap) · [ARENDUSJUHEND.md](ARENDUSJUHEND.md) (tehniline viide) · [memory/](../../../Library/Application%20Support/Claude/local-agent-mode-sessions/)

---

## 2026-06-21 · ~2–3 h
**Projekt alustatud**
- Loodud projektistruktuur ja kaustad
- `OSTUKORV.md` — esimene dokument, ostukorvi loogika
- `exercises.json` — harjutuste andmebaas (algversioon)
- `categories.json` — lihasgruppide kategooriad

---

## 2026-06-22 · ~6–8 h
**Suurim arenduspäev — andmed + UI alus**

*Andmefailid:*
- `exercises.json` → 52+ harjutust
- `nutrition.json`, `recipes.json`, `custom_recipes.json` — toitumisandmed
- `supplements.json` — toidulisandid
- `shopping.json` — ostukorvi struktuur
- `user.json` — kasutajaprofiil
- `btb-phases.json` — BtB faaside parameetrid (seeriad, kordused, puhkus, tempo)
- `training-plan.json` v2.0 — phase_1/phase_2 massiivid, circuit + order väljad

*Dokumendid:*
- `HARJUTUSED.md`, `TREENINGKAVA.md`, `TOITUMISKAVA.md`, `RETSEPTID.md`
- `karlova_valijousaal.md` — jõusaali spetsiifika

*app.html arendus:*
- Tab 1–4 alus
- BtB faaside süsteem (Faas 1+2, coming_soon 3–4)
- Circuit/superset formaat (A/B/C-ringid, D-finišer)
- Faaside navigatsioonipaneel (N1–N5 nupud, deload märge)
- Ilmaprognoos widget (Open-Meteo API, Karlova koordinaadid)
- Tab 4 Progress: `muscleColor()` BtB-teadlik valem
- Tab 4 Progress: `renderMuscleVolumeCard()` — maht-kaart lihasgrupile

*Versioon:* v0.5.0

---

## 2026-06-23 · ~3–4 h
**Nädalagraafik + ostukorv**

- `shopping.json` — lõplik struktuur
- `analysis.json` — toitumisanalüüs
- Tab 3: `renderWeekSchedule()` — E–P graafik, plaanitud vs tehtud vs puhkus
  - Ikoonid: ✓ tehtud / 💪 plaanitud / 😊 puhkus
  - `localStr(d)` UTC-bugfix
  - `ttm_train_sched` localStorage
- Backup-süsteem (File System Access API, `ttm-backup-2026-06-23.json`)

---

## 2026-06-25 · ~4–5 h
**BMX mode + hinnauuendus**

- `scripts/update_prices.py` — automaatne hinnauuendus ostukorvid.ee kaudu
- `data/prices.json` — hinnad uuendatud
- Tab 3: BMX mode v0.6.0
  - `renderBmxWidget()` — nupp / aktiivne banner / taastumiskorv
  - `isTodayTrainingDay()` — treeningpäeva tuvastus
  - `startBmxSession()` / `stopBmxSession()` — sessiooni loogika
  - `renderBmxRecoveryBasket()` — taastumiskorv ostukorvi toodete põhjal
  - ~500 kcal/h kalkulatsioon, `ttm_bmx_*` localStorage võtmed
- Dokumentatsioon uuendatud: PROJECT.md, ARENDUSJUHEND.md, memory failid

*Versioon:* v0.6.0 ✅

---

---

## 28.06.2026

**v0.7.1 — Tab refactor + Kaloriloogika alus**

- Tab struktuur 7 → 6: Progress tab eemaldatud, Mina neelab sisu
  - Nav, TABS objekt, renderTab() uuendatud
  - `setMinaPeriod()` / `setProgressChart()` → `renderTab('mina')`
- Tab 5 Mina uus järjekord: Minu info → Progress → BtB teekond → Varundus
- `renderRuleBasedAnalysis()` + `renderWeeklyWeightFeedback()` → Dashboard
- `renderSupplementsSection()` → Tab 3 Toitumiskava lõppu
- `renderMinaSettings()` — seadete kaart:
  - Rasvaprotsendi visuaalne viide (5 vahemikku, live highlight)
  - Bulk surplus vihjekast (BtB soovitused, live highlight)
  - BtB kaloritarve eelvaade (lean mass / RMR / TEF / puhkepäev / treeningupäev)
- `calcKcalTarget()` + `calcKcalTrainingDay()` — dünaamiline BtB valem
- `saveMinaSettings()` — salvestab `ttm_mina_settings`, uuendab STATE.user
- `showToast()` — visuaalne tagasiside (puudus varem)
- Salvesta-nupu roheline animatsioon + toast teade
- `previewKcal()` — live kalkulatsioon vormi täites
- Sintaksiviga parandatud (escaped backtick → tavaline backtick)

*Versioon:* v0.7.1 ✅

---

## 28.06.2026 (järg)

**v0.7.2 — Kalorite tulpdiagramm**

- `renderKcalChart(weeks)` lisatud — SVG tulpdiagramm Tab 5 Mina Progress sektsioonis
- Päevavaade (täna/1 nädal): kcal numbrid tulpadel, tabel kuupäev/kcal/% all
- Nädala koondvaade (4/8/12 nädalat): Ø kcal tulbad + nädala tabel
- Värvid 🟢/🟡/🔴, katkendlik sihtmäärjoon, perioodi kokkuvõte
- Integreeritud `renderProgress()`-sse pärast "On track" kaarti

*Versioon:* v0.7.2 ✅

---

## 28.06.2026 (järg 2)

**v0.7.3 — Meal Prep tab**

- Uus Tab 2 ostukorvi ja toidukava vahele
- `mpGenerate()` — 7-päeva plaan ttm_train_sched põhjal
- MP_MEALS (16 kirjet: M03/M08–M17 + 4 snäkki) + MP_WEEK_TEMPLATE (E–P vaikismall)
- Päevavaade, retseptide eelvaade, batch-cooking nõuanded
- `ttm_shopping_confirmed` integratsioon

*Versioon:* v0.7.3 ✅

---

## 28.06.2026 (järg 3)

**v0.7.4 — Toitumine tab ümberkirjutus**

- Loeb `meal_plan`-ist (mitte hardcoded)
- Tekstnupud (mitte checkbox), lisandid inline slottides
- Protein indikaator söögikorra kaupa

*Versioon:* v0.7.4 ✅

---

## 28.06.2026 (järg 4)

**v0.7.5–v0.7.9 — Väiksemad täiendused**

- v0.7.5: Dashboard motivatsioon random; surplus + rasvaprotsendi tabelid kokkupandavad
- v0.7.6: Soojendusprotokoll (Tab 4), BtB anaboliline aken, deload automaatika
- v0.7.7: Valgu 40g indikaator, kaseiinvalk enne und, hädaolukorra kalorid, satiatsioonivihjed
- v0.7.8: Alkoholi logimine Tab 5 (nädala loendur, 🟡/🔴 hoiatused)
- v0.7.9: Alkohol → kalorite bilanssi, Dashboard insight, nädalaanalüüs

*Versioonid:* v0.7.5–v0.7.9 ✅

---

## 28.06.2026 (järg 5)

**v0.8.0 — GitHub Pages + PWA + GitHub Actions**

- Kõik failid üles GitHubi (`visuaalmootor/treener`):
  - `app.html`, `manifest.json`, `service-worker.js`
  - `data/` (exercises, shopping, training-plan, prices, recipes, nutrition, supplements)
  - `scripts/update_prices.py`
  - `.github/workflows/update_prices.yml`
  - `icons/icon-192.png`, `icons/icon-512.png` (Python pure-stdlib PNG generaator)
- GitHub Pages aktiveeritud → **https://visuaalmootor.github.io/Treener/app.html**
- GitHub Actions "Uuenda hinnad" — manuaalne test läbis ✅ (36s)
- Üleslaadimismeetod: Python urllib skript (SSL fix, base64 from disk, SHA auto-fetch)

*Versioon:* v0.8.0 ✅

---

## Kokkuvõte

| Päev | Hinnanguline aeg | Põhitegevus |
|------|-----------------|-------------|
| 21.06 | ~2–3 h | Projekti algus, andmebaas |
| 22.06 | ~6–8 h | Suurim päev — andmed + UI |
| 23.06 | ~3–4 h | Nädalagraafik, ostukorv |
| 25.06 | ~4–5 h | BMX mode, hinnauuendus |
| 28.06 | ~10–12 h | v0.7.1–v0.8.0: Tab refactor, kaloriloogika, Meal Prep, Toitumine, alkohol, GitHub Pages + PWA |
| 19.07 | ~1 h | WORKLOG loomine, training-plan.json kohandus Decathlon 2×10kg hantlite järgi (Plan B) |
| **KOKKU** | **~26–34 h** | |

---

## 28.06.2026 (järg 6) — Selgitused + otsused

**Hindade süsteemi selgitus:**
- Refresh-nupp äpis laeb `prices.json` GitHubist — **ei käivita Python skripti**
- Python skript jookseb GitHub Actionsis kell 07:00 UTC = 10:00 Eesti suveaeg
- Kauplused uuendavad hindu tõenäoliselt öösel (00:00–04:00) → 10:00 on turvaline aeg
- Cron jäi 07:00 UTC-le (muutmine ei olnud vajalik)

**Üleslaadimistöövoog tulevikuks** (`upload_to_github.py`):
- Skript on workspace kaustas, FILES list on tühi — lisa sinna failid enne käivitamist
- Vajadusel: `python3 "/Users/ingmar/Claude/Projects/Trenn ja toitumine/upload_to_github.py"`

---

## 28.06.2026 (järg 7)

**v0.9.0 — Firebase sync**

- Firebase projekt `trenn-toitumine` (Spark plan)
- Firestore + Google Authentication seadistatud
- Firebase SDK (v10.12.0) CDN kaudu app.html-s
- Google login nupp headeris (paremas ülanurgas, ringikujuline)
- `lsSet()` kirjutab automaatselt ka Firestoresse (fire-and-forget)
- `syncFromFirestore()` — login järel laaditakse pilveandmed alla
- Esimene login: kogu localStorage push automaatselt pilve
- Mina tab: Firebase kaart (sisse/välja logitud olek)
- Firestore Security Rules: `request.auth.uid == uid` ✅
- Authorized domains: `visuaalmootor.github.io` ✅
- Andmestruktuur: `/users/{uid}/kv/{key}` → `{ v: value, ts: timestamp }`

*Versioon:* v0.9.0 ✅

---

## 13.–17.07.2026 — Quiet Data redesign (v0.9.3–v0.9.5.2)

**⚠️ Failistruktuur muutus:** kogu edasine arendus toimub `app2.html`-s (uus Quiet Data disain). Vana `app.html` on kustutatud. Push: `python3 scripts/push_app.py app2.html "sõnum"`.

- **v0.9.3.0–.6** — Claude Designi "Quiet Data" ümberkujundus, **kõik 6 tabi pikslitäpselt** (bg #F8F4ED, kaardid #FFF/#ECE4D5, tumedad kaardid #211E18, aktsent #2563eb, Space Grotesk + JetBrains Mono). Graafikutes säilib punane→kollane→roheline gradient (mitte sinine). Poe soovitus ainult hinnapõhine. Lihaskaart = olemasolev anatoomiline SVG. Meal Prep = päevapõhine plaan + prep-sessiooni tracker koos.
- **v0.9.4** — **harjutuse detailvaade**: `ttm_training_log`, puhketaimer, `ttm_exercise_notes`, double progression, soojendus. Meal Prep parandused: portsjonite vastuolu ("1 ports sel nädalal · tee 5") + puuduvad retseptid (energiapallid M04, M01), `mpIsBatch()`.
- **v0.9.4.1** — **söögiaegade seadistus kaskaadiga** (`ttm_meal_times`, UUS võti): hommikusööki hilisemaks → nihutab automaatselt teisi, aga ise muudetav (MP_SLOT_TIMES muteeritav).
- **v0.9.4.2** — alkoholi kalorid päeva bilanssi (addAlkohol uuendab kcal; Toitumine liidab alkoholi).
- **v0.9.4.3** — alkoholi joogid ei kadunud enam üleöö (Firebase sünk kirjutas terve objekti üle → ajatemplipõhine, hiljem union). Nädalavõti kohaliku aja järgi (UTC andis 00:00–03:00 vale võtme).
- **v0.9.4.4** — alkoholi päevavalija + nädalanavigatsioon + tagantjärele logimine valitud päeva peale.
- **v0.9.4.5** — Toitumine slotid: söögikorra nimi loetav + retsept avaneb inline.
- **v0.9.4.6** — toidu otsing: OFF `serving_size` auto-täitmine + elav grammiarvutus (varem leidis ainult 100g info).
- **v0.9.4.7** — "Lisa kirje" andis nüüd toasti (BUG: kohalik `log` muutuja varjutas globaalset `log()` funktsiooni → renderTab jäi käivitamata). Barkoodiskänner ZXing (@zxing/browser UMD, asendas polyfilli).
- **v0.9.4.8** — **reaalaja sünk** (onSnapshot) teistelt seadmetelt + fookuse/nähtavuse taassünk (throttle 8s) + header sünk-nupp.
- **v0.9.4.9** — headeri korrastus: sünk-nupp login-nupu kõrvale; hindade refresh+eelarve nupud → Ostukorvi tabi.
- **v0.9.5.0** — **sünk union-merge** (`_applyCloudDoc`, `_mergeLogValue`): nutrition_log/training_log/weight_log/meal_plan jt liidetakse, ei kaota kummagi seadme andmeid.
- **v0.9.5.1** — NEAT valik ei lähtu enam taustasünkist (`STATE.minaSettingsDirty` + `_syncRenderBlocked()`).
- **v0.9.5.2** — mobiili login signInWithRedirect (+ getRedirectResult) — EI töötanud lõpuni Brave iOS-is (vt allpool).

## 18.07.2026 (öine maraton) — Login + sünk + platvormi parandused (v0.9.5.3–v0.9.6.5)

**v0.9.5.3** — motivatsioonilause värelemise fix: kuupäeva-seemnega valik (mitte Math.random); eemaldatud onSnapshot lõputu silmus. Kalorite ebakõla fix: kõik kuva loeb `calcEatenKcal`, mitte vana `kcal_today_` skalaari.

**v0.9.5.4–.9** — mobiili Google-login **Google Identity Services** peale (SDK `signInWithCredential`), sest Brave iOS blokeerib Firebase auth'i sügavalt. Overlay Google-nupuga, `_gisLogin/_gisCallback`. OAuth JS origin `visuaalmootor.github.io` lisatud. fbInit puhastab 1× vigase `firebaseLocalStorageDb`. Diagnostika (`_gisDiagnose`) + ajapiirangud (`_withTimeout`).
→ **Tulemus:** Brave iOS login ei õnnestunud (autentimine blokeeritud). **Lahendus: telefonis kasuta SAFARIT** — seal töötab.

**v0.9.6.0** — "Kalorid puudu — kiire valik" (energiapallid jt) BUG FIX: kirjutas vanasse skalaari, ei loetud kokku. Nüüd `nutrition_log._custom` sisse → loeb kalorite kogusse, kuvatakse nimekirjas, eemaldatav.

**v0.9.6.1** — seadmete-vahelise konvergeerumise taastus: `_applyCloudDoc` kanooniline (`_canon`) tagasikirjutus → seadmed sulanduvad, silmuse-kindel.

**v0.9.6.2** — **AJAVÖÖND fix:** "täna" arvutati UTC järgi (`toISOString`) → Eestis kella 00:00–03:00 vahel vale (eilne) päev. Asendatud 46 kohta `_localDateStr(d)` (kohalik aeg).

**v0.9.6.3** — service-worker network-first KÕIGILE HTML-ile (varem ainult app.html → app2.html jäi cache-first, seadmed kinni vanas versioonis). push_app.py oskab nüüd ka .js. Firestore long-polling katse.

**v0.9.6.4** — pushAllToFirestore selge tagasiside + veakood.

**v0.9.6.5** — **Firestore KIRJUTAMINE REST-API kaudu** (`_fbRestWrite` + `_toFsValue`). Firestore SDK striimiv kirjutamiskanal on Safaris blokeeritud (batch.commit timeout 20s). REST = tavaline HTTPS PATCH → töötab. Lugemine jääb SDK peale.
→ **Tulemus: sünk töötab mõlemas suunas** (kinnitatud — telefoni märked jõuavad desktopile). ⚠️ Firebase tasuta kvoot (20k kirjutust/päev) ammendus maratoni-testimisega, lähtub ~10:00 Eesti hommikul.

*Versioonid:* v0.9.3.0 → v0.9.6.5 ✅

## 07.08.2026 — Trenn-chat arendused (v0.9.8.1–v0.9.8.4)

**v0.9.8.1–v0.9.8.2** *(eelmine sessioon, kokkuvõttest)* — SVG lihaskaardistus korrigeeritud (_FRONT_MAP/_BACK_MAP); graafiku kõigi punktide peal reppide numbrid; triitseps + käsivarred "Kõik" graafikus (secondary_category tugi); "Viimati söödud" pagination algus.

**v0.9.8.3** — "Viimati söödud" pagination: 10 kirjet lehel, ← Uuemad / Vanemad → navigatsioon; `getRecentCustomFoods()` piirang eemaldatud.

**v0.9.8.4** — Kalisteetika plaanid D (✈️ Festival, ainult põrand, 3×/näd 15-30 min) ja E (🏠 Kodus, tool+laud+sein); 10 uut harjutust (id 38–47); `extra_primary` tugi harjutustele (OG23: Selg+Biitseps mõlemad 1.0×, Käsivarred 0.5×); secondary_category 0.5× krediit kõigis lihasgraafikutes (getMuscleActivity, renderMuscleBarsChart, renderAllMusclesStackedChart).

⚠️ ~~HETKEL KEHTIV VERSIOON: v0.9.8.4~~ — ÜLEKIRJUTATUD toitumine-chati poolt

**v0.9.8.5** *(2026-08-07, trenn-chat)* — TAASTUS: toitumine-chat pushis v0.9.8.0 pärast v0.9.8.4, kaotades pagination + plaanid D/E. Taastatud kõik muutused + uuendused:
- "Viimati söödud" pagination: `← Uuemad` / `Vanemad →`, 10 kirjet lehel, 100 kirje preload, otsing resetib lehe
- Inline fallback: Plaanid D (✈️ Festival) ja E (🏠 Kodus kalisteetika) lisatud app2.html sisse
- `push_app.py` uuendatud: tunneb nüüd `.md`, `.json`, `.py` faililaiendeid

⚠️ **HETKEL KEHTIV VERSIOON: v0.9.8.5** — järgmine muutus peaks olema v0.9.8.6
