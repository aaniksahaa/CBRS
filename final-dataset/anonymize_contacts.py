import re
import sys

# Maps for digit conversion
BN_TO_EN = str.maketrans("০১২৩৪৫৬৭৮৯", "0123456789")
EN_TO_BN = str.maketrans("0123456789", "০১২৩৪৫৬৭৮৯")

def mask_number(match):
    number = match.group()
    
    # Normalize Bengali digits to English
    normalized = number.translate(BN_TO_EN)
    
    # Extract only digits
    digits = re.sub(r"\D", "", normalized)
    
    if len(digits) >= 7:
        # Replace last 5 digits with XXXXX
        masked_digits = digits[:-5] + "XXXXX"
        
        # Rebuild number, preserving separators (spaces, dashes, etc.)
        idx = 0
        result = []
        for ch in normalized:
            if ch.isdigit():
                result.append(masked_digits[idx])
                idx += 1
                if idx >= len(masked_digits):
                    break
            else:
                result.append(ch)
        result.extend(normalized[len(result):])
        masked = "".join(result)
        
        # If original was in Bengali digits, convert back
        if any(ch in "০১২৩৪৫৬৭৮৯" for ch in number):
            masked = masked.translate(EN_TO_BN)
        
        return masked
    
    return number


def anonymize_contacts(text: str) -> str:
    # Match Bangladeshi style numbers (English & Bengali)
    pattern = re.compile(
        r"(?:\+?8801[\d\s-]{6,}|01[\d\s-]{6,}|০১[\d\s-]{6,}|\+?৮৮০১[\d\s-]{6,})"
    )
    return pattern.sub(mask_number, text)


def process_file(filename: str):
    try:
        with open(filename, "r", encoding="utf-8") as f:
            content = f.read()
        
        anonymized = anonymize_contacts(content)
        
        with open(filename, "w", encoding="utf-8") as f:
            f.write(anonymized)
        
        print(f"✅ File '{filename}' anonymized.")
    except Exception as e:
        print(f"❌ Could not process '{filename}': {e}")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python anonymize_contacts.py <filename1> <filename2> ...")
        sys.exit(1)
    
    for fname in sys.argv[1:]:
        process_file(fname)
