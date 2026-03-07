import sqlite3

db = sqlite3.connect("data/votes.db")

members = [
    ("Joe LaCava", 1, "https://www.sandiego.gov/sites/default/files/cd1-joe-lacava-photo.jpg"),
    ("Jennifer Campbell", 2, "https://www.sandiego.gov/sites/default/files/cd2-jennifer-campbell-photo.jpg"),
    ("Stephen Whitburn", 3, "https://www.sandiego.gov/sites/default/files/cd3-stephen-whitburn-photo.jpg"),
    ("Henry Foster III", 4, "https://www.sandiego.gov/sites/default/files/cd4-henry-foster-photo.jpg"),
    ("Marni von Wilpert", 5, "https://www.sandiego.gov/sites/default/files/cd5-marni-vonwilpert-photo.jpg"),
    ("Kent Lee", 6, "https://www.sandiego.gov/sites/default/files/cd6-kent-lee-photo.jpg"),
    ("Raul Campillo", 7, "https://www.sandiego.gov/sites/default/files/cd7-raul-campillo-photo.jpg"),
    ("Vivian Moreno", 8, "https://www.sandiego.gov/sites/default/files/cd8-vivian-moreno-photo.jpg"),
    ("Sean Elo-Rivera", 9, "https://www.sandiego.gov/sites/default/files/cd9-sean-elorivera-photo.jpg"),
]

for name, district, photo in members:
    db.execute("UPDATE members SET district=?, photo_url=? WHERE name=?", (district, photo, name))

db.commit()

for row in db.execute("SELECT name, district FROM members ORDER BY district"):
    print(f"  D{row[1]}: {row[0]}")

db.close()
print("Done")
