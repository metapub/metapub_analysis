import sqlite3

db_path = "findit_results.db"

def init_db():
    conn = sqlite3.connect(db_path)
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS results
                 (pmid INTEGER PRIMARY KEY, journal TEXT, year INTEGER, url TEXT, reason TEXT, downloadable INTEGER)''')
    c.execute('''CREATE TABLE IF NOT EXISTS publication_years
                 (journal TEXT PRIMARY KEY, oldest_year INTEGER, recent_year INTEGER, valid_years TEXT)''')
    conn.commit()
    conn.close()

def save_result(pmid, journal, year, url, reason, downloadable):
    conn = sqlite3.connect(db_path)
    c = conn.cursor()
    c.execute("INSERT OR IGNORE INTO results (pmid, journal, year, url, reason, downloadable) VALUES (?, ?, ?, ?, ?, ?)",
              (pmid, journal, year, url, reason, downloadable))
    conn.commit()
    conn.close()

def save_publication_years(journal, oldest_year, recent_year, valid_years):
    valid_years_str = ",".join(map(str, valid_years))
    conn = sqlite3.connect(db_path)
    c = conn.cursor()
    c.execute("INSERT OR REPLACE INTO publication_years (journal, oldest_year, recent_year, valid_years) VALUES (?, ?, ?, ?)",
              (journal, oldest_year, recent_year, valid_years_str))
    conn.commit()
    conn.close()

def fetch_results(journal, year):
    conn = sqlite3.connect(db_path)
    c = conn.cursor()
    c.execute("SELECT pmid, url, reason, downloadable FROM results WHERE journal=? AND year=?", (journal, year))
    rows = c.fetchall()
    conn.close()
    return rows

def fetch_publication_years(journal):
    conn = sqlite3.connect(db_path)
    c = conn.cursor()
    c.execute("SELECT oldest_year, recent_year, valid_years FROM publication_years WHERE journal=?", (journal,))
    row = c.fetchone()
    conn.close()
    if row:
        oldest_year, recent_year, valid_years_str = row
        valid_years = list(map(int, valid_years_str.split(",")))
        return oldest_year, recent_year, valid_years
    return None

def fetch_result_for_pmid(pmid):
    conn = sqlite3.connect(db_path)
    c = conn.cursor()
    c.execute("SELECT url, reason, downloadable FROM results WHERE pmid=?", (pmid,))
    row = c.fetchone()
    conn.close()
    return row

