import string
import pyfiglet
from simple_term_menu import TerminalMenu
import json
import secrets
import math


CHEMIN_ROCKYOU = "rockyou.txt"
PARAMS_FILE = "settings.json"

# Charger rockyou
def rockYouLoader(chemin_fichier):
    try:
        with open(chemin_fichier, 'r', encoding='utf-8', errors='ignore') as f:
            rockyou_set = {line.strip() for line in f}
        return rockyou_set
    except FileNotFoundError:
        print(f"Erreur: Le fichier {chemin_fichier} est introuvable.")
        return set()

wordlist_rockyou = rockYouLoader(CHEMIN_ROCKYOU)
print(f"Rockyou chargé. Nombre de mots de passe uniques : {len(wordlist_rockyou):,}")

def build_alphabet(settings):
    """Construit l'alphabet selon les paramètres"""
    alphabet = ""
    if settings.get("Alphabet lowercase", True):
        alphabet += string.ascii_lowercase
    if settings.get("Alphabet uppercase", True):
        alphabet += string.ascii_uppercase
    if settings.get("Alphabet digits", True):
        alphabet += string.digits
    if settings.get("Alphabet specials", False):
        alphabet += string.punctuation
    return alphabet

#def keyLen(key, alphabet):
    l_alphabet = len(alphabet)
    long = len(key)
    keySpace = l_alphabet ** long
    return keySpace

#def keyTime(key):
    h = 2 * 10000000  # 2 * attaque par seconde
    keyTime = key / h
    return keyTime

def checkLetterRep(password):
    password_list = list(password)
    repet = False
    for index, i in enumerate(password_list):
        if index >= 1 and i == password_list[index - 1]:
            print(f"Letter : {i} is repeated twice")
            repet = True
            return repet
    return repet

def checkCommonWord(password):
    if not password:
        return False
    return password.strip().lower() in wordlist_rockyou

def analyze_charsets(password):
    """Analyse les types de caractères présents dans le mot de passe."""
    pw = password or ""
    present = {
        "lowercase": any(c in string.ascii_lowercase for c in pw),
        "uppercase": any(c in string.ascii_uppercase for c in pw),
        "digits":    any(c in string.digits for c in pw),
        "specials":  any(c in string.punctuation for c in pw),
        "others":    any(c not in (string.ascii_letters + string.digits + string.punctuation) for c in pw)
    }
    missing = [k for k, v in present.items() if not v and k != "others"]
    present["missing"] = missing
    return present

def password_matches_settings(password, settings):
    """Vérifie si le mot de passe respecte les catégories activées dans les paramètres."""
    has = analyze_charsets(password)
    requirements = {
        "Alphabet lowercase": "lowercase",
        "Alphabet uppercase": "uppercase",
        "Alphabet digits":    "digits",
        "Alphabet specials":  "specials"
    }

    missing_required = []
    for opt_key, cat in requirements.items():
        if settings.get(opt_key, False) and not has[cat]:
            missing_required.append(opt_key)

    return {
        "has_categories": has,
        "missing_required": missing_required,
        "ok": len(missing_required) == 0
    }

def checkPswd(password, settings, alphabet):
    password = password.strip()

    # --- Vérification des mots de passe communs
    if settings.get("Common password detection", True):
        if checkCommonWord(password):
            print("⚠️ Common word found")
        else:
            print("✅ Common password not found")

    # --- Vérification de la longueur
    min_len = settings.get("Password length", 8)
    if len(password) < min_len:
        print(f"⚠️ Password too short (min {min_len})")
    else:
        print("✅ Password length OK")

    # --- Vérification des catégories activées dans les settings
    category_check = password_matches_settings(password, settings)
    if not category_check["ok"]:
        print("⚠️ Missing required categories :")
        for cat in category_check["missing_required"]:
            print(f"   - {cat}")
    else:
        print("✅ All required character categories are present")

    # --- Calcul de l’espace de clés
    #alphabet = build_alphabet(settings)
    #keys = keyLen(password, alphabet)
    #print(f"🔢 Keyspace : {keys:,}")
    #print(f"⏱️  Estimated time to brute-force : {keyTime(keys)} seconds")

    # --- Vérification des répétitions de lettres
    if checkLetterRep(password):
        print("⚠️ Repeated letters detected")
    else:
        print("✅ No repeated letters found")

    # Calcul de l'entrpy :
    charset_size = len(alphabet)
    entropy = estimate_entropy_bits(len(password), charset_size)
    print(f"Entropy: {entropy:.1f} bits")

def alphabet_menu(settings):
    while True:
        options = [
            f"Alphabet lowercase [{'ON' if settings['Alphabet lowercase'] else 'OFF'}]",
            f"Alphabet uppercase [{'ON' if settings['Alphabet uppercase'] else 'OFF'}]",
            f"Alphabet digits [{'ON' if settings['Alphabet digits'] else 'OFF'}]",
            f"Alphabet specials [{'ON' if settings['Alphabet specials'] else 'OFF'}]",
            "⬅️ Retour"
        ]

        terminal_menu = TerminalMenu(options)
        menu_entry_index = terminal_menu.show()
        if menu_entry_index is None or menu_entry_index == 4:  # Retour
            break

        choice = options[menu_entry_index]

        if "Alphabet lowercase" in choice:
            settings["Alphabet lowercase"] = not settings["Alphabet lowercase"]

        elif "Alphabet uppercase" in choice:
            settings["Alphabet uppercase"] = not settings["Alphabet uppercase"]

        elif "Alphabet digits" in choice:
            settings["Alphabet digits"] = not settings["Alphabet digits"]

        elif "Alphabet specials" in choice:
            settings["Alphabet specials"] = not settings["Alphabet specials"]

    return settings

def settings_menu(fichier=PARAMS_FILE):
    # Valeurs par défaut
    default_settings = {
        "Common password detection": True,
        "Max repeating letters": 2,
        "Password length": 16,
        "Alphabet lowercase": True,
        "Alphabet uppercase": True,
        "Alphabet digits": True,
        "Alphabet specials": False
    }

    # Charger paramètres si fichier existe
    try:
        with open(fichier, "r") as f:
            settings = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        settings = {}

    # Fusionner avec valeurs par défaut
    for key, value in default_settings.items():
        if key not in settings:
            settings[key] = value

    while True:
        options = [
            f"Common password detection [{'ON' if settings['Common password detection'] else 'OFF'}]",
            f"Max repeating letters [{settings['Max repeating letters']}]",
            f"Password length [{settings['Password length']}]",
            "🔤 Alphabet Settings",
            "💾 Sauvegarder et revenir au menu",
        ]

        terminal_menu = TerminalMenu(options)
        menu_entry_index = terminal_menu.show()
        if menu_entry_index is None:
            break

        choice = options[menu_entry_index]

        if "Common password detection" in choice:
            settings["Common password detection"] = not settings["Common password detection"]

        elif "Max repeating letters" in choice:
            menu = TerminalMenu([str(v) for v in range(1, 6)])
            idx = menu.show()
            if idx is not None:
                settings["Max repeating letters"] = int(menu.chosen_menu_entry)

        elif "Password length" in choice:
            menu = TerminalMenu([str(v) for v in range(4, 33)])
            idx = menu.show()
            if idx is not None:
                settings["Password length"] = int(menu.chosen_menu_entry)

        elif "Alphabet Settings" in choice:
            settings = alphabet_menu(settings)

        elif "Sauvegarder" in choice:
            with open(fichier, "w") as f:
                json.dump(settings, f, indent=4)
            print("\n✅ Paramètres sauvegardés :", settings)
            break

    return settings

def estimate_entropy_bits(length: int, charset_size: int) -> float:
    if charset_size <= 1:
        return 0.0
    return length * math.log2(charset_size)

def generate_password(settings, alphabet, max_attempts=500):
    longueur = settings.get("Password length", 8)
    if longueur <= 0:
        raise ValueError("La longueur doit être > 0")
    if not alphabet:
        raise ValueError("Au moins un type de caractère doit être activé.")

    rng = secrets.SystemRandom()
    attempt = 0

    while attempt < max_attempts:
        attempt += 1
        pw = "".join(rng.choice(alphabet) for _ in range(longueur))
        charset_size = len(alphabet)
        entropy = estimate_entropy_bits(len(pw), charset_size)

        return {
                "password": pw,
                "length": len(pw),
                "charset_size": charset_size,
                "entropy_bits": entropy,
                "attempts": attempt,
            }

def main():
    # Load settings once at startup
    try:
        with open(PARAMS_FILE, "r") as f:
            settings = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        # If file doesn't exist, create default settings
        settings = {
            "Common password detection": True,
            "Max repeating letters": 2,
            "Password length": 16,
            "Alphabet lowercase": True,
            "Alphabet uppercase": True,
            "Alphabet digits": True,
            "Alphabet specials": False
        }
        with open(PARAMS_FILE, "w") as f:
            json.dump(settings, f, indent=4)
    
    while True:
        FortiPass = pyfiglet.figlet_format("FortiPass", font='bubble')
        print(FortiPass)

        options = ["[c] Check Password", "[g] Generate Password", "[s] Settings", "[r] Credits", "[q] Quitter"]
        terminal_menu = TerminalMenu(options)
        menu_entry_index = terminal_menu.show()
        if menu_entry_index is None:
            break

        print(f"You chose : {options[menu_entry_index]}")

        if menu_entry_index == 0:
            # Reload settings before check (in case they were changed)
            with open(PARAMS_FILE, "r") as f:
                settings = json.load(f)
                alphabet = build_alphabet(settings)
            checkPswd(password=input("Password ? : "), settings=settings, alphabet=alphabet)

        elif menu_entry_index == 1:
            # Reload settings before generating
            with open(PARAMS_FILE, "r") as f:
                settings = json.load(f)
            alphabet = build_alphabet(settings)
            result = generate_password(settings=settings, alphabet=alphabet)
            print(f"\n🔐 Generated password: {result['password']}")
            print(f"Length: {result['length']} | Charset size: {result['charset_size']}")
            print(f"Entropy: {result['entropy_bits']:.1f} bits | Attempts: {result['attempts']}")

        elif menu_entry_index == 2:
            settings = settings_menu()  # Update settings and reload them

        elif menu_entry_index == 3:
            print("💡 Projet FortiPass - by You")

        elif menu_entry_index == 4:
            print("👋 Au revoir !")
            break

if __name__ == "__main__":
    main()