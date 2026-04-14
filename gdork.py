import requests
import json
import time
import os
import re

# Configuration
SEARCHAPI_URL = "https://www.searchapi.io/api/v1/search"
KEYS_FILE = "api_keys.json"

# List Dorks (Lengkap)
DORKS = [
    # --- Original Dorks ---
    "site:{target} ext:doc | ext:docx | ext:odt | ext:rtf | ext:sxw | ext:psw | ext:ppt | ext:pptx | ext:pps | ext:csv",
    "site:{target} intitle:index.of",
    "site:{target} ext:xml | ext:conf | ext:cnf | ext:reg | ext:inf | ext:rdp | ext:cfg | ext:txt | ext:ora | ext:ini | ext:env",
    "site:{target} ext:sql | ext:dbf | ext:mdb",
    "site:{target} ext:log",
    "site:{target} ext:bkf | ext:bkp | ext:bak | ext:old | ext:backup",
    "site:{target} inurl:login | inurl:signin | intitle:Login | intitle:\"sign in\" | inurl:auth",
    "site:{target} intext:\"sql syntax near\" | intext:\"syntax error has occurred\" | intext:\"incorrect syntax near\" | intext:\"unexpected end of SQL command\"",
    
    # --- Documents & Files ---
    "site:{target} filetype:pdf",
    "site:{target} filetype:doc",
    "site:{target} filetype:docx",
    "site:{target} filetype:xls",
    "site:{target} filetype:xlsx",
    "site:{target} filetype:ppt",
    "site:{target} filetype:pptx",
    "site:{target} filetype:txt",
    "site:{target} filetype:csv",
    
    # --- Config & Secrets ---
    "site:{target} filetype:env",
    "site:{target} filetype:sql",
    "site:{target} filetype:bak",
    "site:{target} filetype:log",
    "site:{target} filetype:ini",
    "site:{target} filetype:yaml OR filetype:yml",
    "site:{target} inurl:web.config",
    "site:{target} inurl:config.php",
    "site:{target} inurl:.htaccess",
    "site:{target} ext:old OR ext:backup",
    
    # --- Admin & Login Panels ---
    "site:{target} inurl:login",
    "site:{target} inurl:admin",
    "site:{target} inurl:dashboard",
    "site:{target} inurl:register OR inurl:signup",
    "site:{target} inurl:wp-admin",
    "site:{target} inurl:phpmyadmin",
    "site:{target} inurl:cpanel",
    "site:{target} inurl:signin",
    "site:{target} inurl:manage",
    "site:{target} inurl:forgot-password OR inurl:reset-password",
    
    # --- Dev & Staging ---
    "site:dev.{target}",
    "site:staging.{target}",
    "site:test.{target}",
    "site:api.{target}",
    "site:beta.{target}",
    "site:{target} inurl:.git",
    "site:{target} inurl:swagger",
    "site:{target} inurl:api-docs OR inurl:openapi",
    "site:{target} inurl:graphql",
    "site:{target} intext:\"internal use only\"",
    
    # --- Sensitive Data ---
    "site:{target} intext:password",
    "site:{target} intext:username",
    "site:{target} intext:\"api_key\" OR intext:\"apikey\"",
    "site:{target} intext:\"secret\"",
    "site:{target} intext:\"access_token\"",
    "site:{target} intext:\"private key\" OR intext:\"RSA PRIVATE\"",
    "site:{target} intext:\"DB_PASSWORD\"",
    "site:{target} intext:\"AKIA\" OR intext:\"aws_access_key\"",
    "site:{target} intext:\"@{target}\"",
    "site:{target} intext:\"credit card\" OR intext:\"card number\"",
    
    # --- External Leaks ---
    "site:pastebin.com | site:trello.com | site:github.com \"{target}\""
]

class SearchAPIManager:
    def __init__(self, api_keys):
        self.api_keys = api_keys
        self.current_key_index = 0
        self.session = requests.Session()

    def get_current_key(self):
        return self.api_keys[self.current_key_index]

    def rotate_key(self):
        if len(self.api_keys) <= 1: return False
        self.current_key_index = (self.current_key_index + 1) % len(self.api_keys)
        print(f"\n[!] API Key Limit. Memutar ke Key #{self.current_key_index + 1}...")
        return True

    def search_dork(self, query):
        current_key = self.get_current_key()
        params = {"engine": "google", "q": query, "api_key": current_key, "num": 100}
        try:
            resp = self.session.get(SEARCHAPI_URL, params=params, timeout=25)
            if resp.status_code == 429:
                if self.rotate_key(): return self.search_dork(query)
                return None
            resp.raise_for_status()
            return resp.json()
        except:
            if self.rotate_key(): return self.search_dork(query)
            return None

def clean_filename(target):
    """
    Mengubah '*.bulog.co.id' atau 'https://bulog.co.id' menjadi 'bulog'
    """
    # Hapus protokol (http/https)
    name = re.sub(r'https?://', '', target)
    # Hapus asterisk dan dot di depan
    name = name.replace('*', '').lstrip('.')
    # Ambil bagian utama domain (sebelum titik pertama)
    # Misal: bulog.co.id -> bulog
    name = name.split('.')[0]
    # Jika hasil split kosong, gunakan default
    return name if name else "recon_results"

def main():
    print("\033[1;31m=== Hades Recon: Clean Filename & Full Mode ===\033[0m")
    
    # API Key Loading
    if os.path.exists(KEYS_FILE):
        with open(KEYS_FILE, 'r') as f: api_keys = json.load(f)
        print(f"✅ Loaded {len(api_keys)} keys from {KEYS_FILE}")
    else:
        inp = input("Enter API Keys (comma separated): ")
        api_keys = [k.strip() for k in inp.split(',') if k.strip()]
        if not api_keys: return
        with open(KEYS_FILE, 'w') as f: json.dump(api_keys, f)

    target_input = input("\nEnter Target (e.g., *.bulog.co.id): ").strip()
    if not target_input: return

    # Pembersihan nama file
    base_name = clean_filename(target_input)
    filename = f"{base_name}.txt"
    
    api_manager = SearchAPIManager(api_keys)

    with open(filename, "a", encoding="utf-8") as log_file:
        log_file.write(f"\n{'='*80}\nTARGET: {target_input} | FILE: {filename} | {time.ctime()}\n{'='*80}\n")
        
        print(f"[*] Target Query: {target_input}")
        print(f"[*] Saving all results to: \033[1;33m{filename}\033[0m")
        print("-" * 80)

        for i, dork_template in enumerate(DORKS, 1):
            query = dork_template.format(target=target_input)
            print(f"\n\033[1;34m[{i}/{len(DORKS)}] CHECKING: {query}\033[0m")
            
            results = api_manager.search_dork(query)
            
            if results and 'organic_results' in results:
                items = results['organic_results']
                if items:
                    print(f"\033[1;32m   ✅ FOUND {len(items)} RESULTS:\033[0m")
                    log_file.write(f"\nDORK: {query}\n{'-'*40}\n")
                    
                    for idx, res in enumerate(items, 1):
                        title = res.get('title', 'No Title')
                        link = res.get('link', 'No Link')
                        snippet = res.get('snippet', 'No Snippet').replace('\n', ' ')
                        
                        # TAMPILKAN SEMUA DI TERMINAL
                        print(f"   {idx}. {title}")
                        print(f"      🔗 {link}")
                        
                        # SIMPAN SEMUA DI FILE
                        log_file.write(f"{idx}. {title}\n   URL: {link}\n   DESC: {snippet}\n\n")
                    
                    log_file.write("="*40 + "\n")
                else:
                    print("   ❌ No results found.")
            else:
                print("   ❌ Request failed.")
            
            log_file.flush()
            time.sleep(1.2)

    print("\n" + "="*80)
    print(f"🏁 DONE! Full report saved in: {filename}")

if __name__ == "__main__":
    main()
