#!/usr/bin/env python3
"""
update_prices.py — ostukorvid.ee hindade automaatne uuendaja

Kasutus:
  python3 scripts/update_prices.py

Nõuded:
  pip install requests

Tööpõhimõte (2-sammuline meetod):
  1. Kategoorialeht → leia odavaim toode per pood (lo, hi, id, slug)
  2. Kui lo == hi: hind täpne, pole vaja edasi minna
     Kui lo < hi: fetši tootelehelt täpne per-pood hind (price/quantity)
"""

import os
import re
import sys
import json
import time
import requests
from datetime import date

# ── Seadistus ──────────────────────────────────────────────────────────────────

BASE_URL = 'https://ostukorvid.ee'

HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) '
                  'AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
    'Accept-Language': 'et-EE,et;q=0.9,en-US;q=0.8,en;q=0.7',
}

SLEEP = 0.6  # sekundit päringute vahel (bot-kaitse)

# Kategooria slug → toote võti prices.json-is
# Kui kategoorias on mitu tootevõtit, kasutatakse sama kategooria andmeid
CATEGORIES = {
    'kanaliha':        ['kana_koib', 'kana_filee'],
    'munad':           ['munad'],
    'kodujuust':       ['kodujuust'],
    'riis':            ['riis'],
    'kartul':          ['kartul'],
    'pasta':           ['pasta'],
    'helbed':          ['kaerahelbed'],
    'oliivioli':       ['oliivioli'],
    'pahklikreem':     ['maapahklivoi'],
    'banaanid':        ['banaanid'],
    'tuunikala':       ['tuunikala'],
    'lohefilee':       ['lohe'],
    'jogurt':          ['kreeka_jogurt'],
    'leib':            ['leib'],
    'pahklid':         ['cashew', 'pahklid'],
    'mustikad':        ['mustikad'],
    'keefir':          ['keefir'],
    'riivjuust':       ['parmesan'],
    'musli':           ['musli'],
    'ploomid':         ['ploomid'],
    'sokolaad':        ['shokolaad'],
    'hakkliha':        ['hakkliha'],
    'piim':            ['taispiim'],
    'proteiinipulber': ['vadakupulber'],
    'mesi':            ['mesi'],
}

# ── HTTP + __remixContext ──────────────────────────────────────────────────────

def fetch_page(url, retries=2):
    """Fetšib lehe HTML-i. Tagastab teksti või None."""
    for attempt in range(retries + 1):
        try:
            r = requests.get(url, headers=HEADERS, timeout=20)
            r.raise_for_status()
            return r.text
        except requests.RequestException as e:
            if attempt < retries:
                print(f'    ↺ retry {attempt + 1}: {e}')
                time.sleep(2)
            else:
                print(f'    ✗ päring ebaõnnestus: {e}')
                return None


def extract_remix_context(html):
    """
    Ekstraktib window.__remixContext JSON objekti HTML-ist.
    Kasutab json.JSONDecoder().raw_decode() — töötab ka suurte JSON-idega.
    """
    for marker in ('window.__remixContext=', 'window.__remixContext ='):
        idx = html.find(marker)
        if idx == -1:
            continue
        json_start = html.find('{', idx + len(marker))
        if json_start == -1:
            continue
        try:
            obj, _ = json.JSONDecoder().raw_decode(html[json_start:])
            return obj
        except json.JSONDecodeError as e:
            print(f'    ⚠ JSON parse viga: {e}')
            return None
    return None


def fetch_remix(url):
    """Fetšib lehe ja tagastab __remixContext dict-i või None."""
    html = fetch_page(url)
    if not html:
        return None
    ctx = extract_remix_context(html)
    if not ctx:
        print(f'    ⚠ __remixContext puudub: {url}')
    return ctx

# ── Kategooria andmed ──────────────────────────────────────────────────────────

def get_category_products(slug):
    """
    Tagastab kategooria kõik tooted.
    Struktuur: ctx['state']['loaderData']['routes/kategooriad/$categorySlug']['products']
    """
    url = f'{BASE_URL}/kategooriad/{slug}?price=unit'
    ctx = fetch_remix(url)
    if not ctx:
        return []
    try:
        key = 'routes/kategooriad/$categorySlug'
        return ctx['state']['loaderData'][key]['products']
    except (KeyError, TypeError):
        print(f'    ⚠ kategooria struktuur ei vasta ootustele')
        return []


def best_per_store(products):
    """
    Igast poest odavaim toode.
    Tagastab: { 'PRISMA': {'lo': 0.49, 'hi': 0.49, 'name': '...', 'id': '...', 'slug': '...'} }
    """
    by_store = {}
    for p in products:
        try:
            lo = float(p['unit']['lowPrice'])
            hi = float(p['unit']['highPrice'])
        except (KeyError, TypeError, ValueError):
            continue
        for store in p.get('stores', []):
            if store not in by_store or lo < by_store[store]['lo']:
                by_store[store] = {
                    'lo': lo, 'hi': hi,
                    'name': p.get('name', ''),
                    'id': p.get('id', ''),
                    'slug': p.get('slug', ''),
                }
    return by_store

# ── Tootelehe täpne hind ───────────────────────────────────────────────────────

def get_store_prices_from_detail(product_id, product_slug):
    """
    Fetšib tootelehe ja tagastab per-pood ühikuhinnad.
    Tagastab: { 'PRISMA': 0.49, 'SELVER': 0.49, ... }
    """
    url = f'{BASE_URL}/tooted/{product_id}/{product_slug}'
    ctx = fetch_remix(url)
    if not ctx:
        return {}
    try:
        key = 'routes/tooted/$productId/$productSlug'
        loader = ctx['state']['loaderData'][key]
        # Proovi mõlemat võtmenime
        sp = loader.get('storeProducts') or loader.get('store_products') or []
        result = {}
        for s in sp:
            try:
                unit_price = round(float(s['price']) / float(s['quantity']), 2)
                result[s['store']] = unit_price
            except (KeyError, TypeError, ZeroDivisionError, ValueError):
                pass
        return result
    except (KeyError, TypeError):
        print(f'    ⚠ tootelehe struktuur ei vasta ootustele')
        return {}

# ── Põhiloogika ────────────────────────────────────────────────────────────────

def resolve_prices(by_store):
    """
    Täpne hind per pood:
    - lo == hi → kasuta lo otse (täpne kategoorilehelt)
    - lo < hi  → fetši tootelehelt täpne hind

    Tagastab sorteeritud lista: [{'store': ..., 'price': ..., 'product_name': ...}]
    """
    # Grupeeri tooted mis vajavad detail-lehte
    # { product_id: {'slug': ..., 'stores': set()} }
    need_detail = {}
    for store, info in by_store.items():
        if abs(info['lo'] - info['hi']) > 0.001:
            pid = info['id']
            if pid not in need_detail:
                need_detail[pid] = {'slug': info['slug'], 'stores': set()}
            need_detail[pid]['stores'].add(store)

    # Fetši detail-lehed
    detail_prices = {}  # { product_id: { store: unit_price } }
    for pid, info in need_detail.items():
        print(f'      ↳ detail: {info["slug"]}')
        time.sleep(SLEEP)
        detail_prices[pid] = get_store_prices_from_detail(pid, info['slug'])

    # Kogu lõplikud hinnad
    result = []
    seen = set()
    for store, info in sorted(by_store.items(), key=lambda x: x[1]['lo']):
        if store in seen:
            continue
        seen.add(store)

        pid = info['id']
        exact = abs(info['lo'] - info['hi']) < 0.001

        if exact:
            price = info['lo']
        elif pid in detail_prices and store in detail_prices[pid]:
            price = detail_prices[pid][store]
        else:
            price = info['lo']  # fallback: kategooria lo

        result.append({
            'store': store,
            'price': price,
            'product_name': info['name'],
        })

    return sorted(result, key=lambda x: x['price'])

# ── Main ───────────────────────────────────────────────────────────────────────

def main():
    script_dir = os.path.dirname(os.path.abspath(__file__))
    prices_path = os.path.join(script_dir, '..', 'data', 'prices.json')
    prices_path = os.path.normpath(prices_path)

    # Lae olemasolev prices.json
    try:
        with open(prices_path, 'r', encoding='utf-8') as f:
            prices = json.load(f)
        print(f'✓ Laetud: {prices_path}')
    except FileNotFoundError:
        print(f'✗ prices.json ei leitud: {prices_path}')
        sys.exit(1)

    total = len(CATEGORIES)
    updated = 0
    errors = 0
    start_time = time.time()

    print(f'\n🔄 Uuendan {total} kategooriat...\n')

    for i, (slug, keys) in enumerate(CATEGORIES.items(), 1):
        print(f'[{i:2}/{total}] {slug}')
        time.sleep(SLEEP)

        products = get_category_products(slug)
        if not products:
            print(f'       ⚠ tühi vastus, jätan vahele\n')
            errors += 1
            continue

        by_store = best_per_store(products)
        if not by_store:
            print(f'       ⚠ poode ei leitud\n')
            errors += 1
            continue

        stores = resolve_prices(by_store)
        store_names = [s['store'] for s in stores[:4]]
        print(f'       ✓ {len(stores)} poodi: {", ".join(store_names)}{"..." if len(stores) > 4 else ""}\n')

        for key in keys:
            if key in prices.get('products', {}):
                prices['products'][key]['stores'] = stores
        updated += 1

    prices['updated'] = str(date.today())

    # Salvesta
    with open(prices_path, 'w', encoding='utf-8') as f:
        json.dump(prices, f, ensure_ascii=False, indent=2)

    elapsed = round(time.time() - start_time)
    print('─' * 50)
    print(f'✅ Valmis! Aeg: {elapsed}s')
    print(f'   Uuendatud: {updated}/{total} kategooriat')
    if errors:
        print(f'   Vigu: {errors}')
    print(f'   Salvestatud: {prices_path}')


if __name__ == '__main__':
    main()
