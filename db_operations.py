import aiosqlite

DATABASE_PATH = "lowCoster.db"


# Connect to SQLite database (or create it if it doesn't exist)
async def initialize_db():
    async with aiosqlite.connect(DATABASE_PATH) as db:
        await db.execute('''
        CREATE TABLE IF NOT EXISTS country (
            typename TEXT,
            id TEXT PRIMARY KEY,
            legacyId TEXT,
            name TEXT,
            slug TEXT,
            slugEn TEXT,
            code TEXT,
            region_legacyId TEXT,
            region_id TEXT
        )
        ''')

        await db.execute('''
        CREATE TABLE IF NOT EXISTS city (
            typename TEXT,
            id TEXT PRIMARY KEY,
            legacyId TEXT,
            name TEXT,
            slug TEXT,
            slugEn TEXT,
            code TEXT,
            country_legacyId TEXT,
            country_id TEXT,
            FOREIGN KEY (country_id) REFERENCES country(id)
        )
        ''')

        await db.execute('''
        CREATE TABLE IF NOT EXISTS airport (
            typename TEXT,
            id TEXT PRIMARY KEY,
            legacyId TEXT,
            name TEXT,
            slug TEXT,
            slugEn TEXT,
            type TEXT,
            code TEXT,
            city_legacyId TEXT,
            city_id TEXT,
            FOREIGN KEY (city_id) REFERENCES airport(id)
        )
        ''')

        await db.commit()


async def save_countries(countries):
    async with aiosqlite.connect(DATABASE_PATH) as db:
        for data in countries:
            await db.execute('''
            INSERT OR REPLACE INTO country (
                typename, id, legacyId, name, slug, slugEn, code, region_legacyId, region_id)
            VALUES (:typename, :id, :legacyId, :name, :slug, :slugEn, :code, :region_legacyId, :region_id)
            ''', (
                data['typename'],
                data['id'],
                data['legacyId'],
                data['name'],
                data['slug'],
                data['slugEn'],
                data['code'],
                data['region_legacyId'],
                data['region_id']
            ))

        await db.commit()


async def save_cities(cities):
    async with aiosqlite.connect(DATABASE_PATH) as db:
        for data in cities:
            await db.execute('''
                INSERT OR REPLACE INTO city (
                    typename, id, legacyId, name, slug, slugEn, code, country_legacyId, country_id)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    data['typename'], data['id'], data['legacyId'], data['name'],
                    data['slug'], data['slugEn'], data['code'],
                    data['country_legacyId'], data['country_id']
                ))

        await db.commit()


async def save_airports(airports):
    async with aiosqlite.connect(DATABASE_PATH) as db:
        for data in airports:
            await db.execute('''
                INSERT INTO airport (typename, id, legacyId, name, slug, slugEn, type, code, city_legacyId, city_id)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    data['typename'], data['id'], data['legacyId'], data['name'], data['slug'],
                    data['slugEn'], data['type'], data['code'], data['city_legacyId'], data['city_id']
                ))

        await db.commit()
