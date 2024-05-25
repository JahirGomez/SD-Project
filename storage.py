import json

FILE_PATH = 'purchases.txt'

def save_purchase(purchase):
    purchases = load_purchases()
    purchases.append(purchase)
    with open(FILE_PATH, 'w') as file:
        json.dump(purchases, file, indent=4)

def load_purchases():
    try:
        with open(FILE_PATH, 'r') as file:
            purchases = json.load(file)
    except FileNotFoundError:
        purchases = []
    except json.JSONDecodeError:
        purchases = []
    return purchases
