import sqlite3


con = sqlite3.connect('db.sqlite', check_same_thread=False)

cur = con.cursor()




def create_table():
    query = '''
    CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY,
    user_id INTEGER,
    genre TEXT,
    the_main_character TEXT,
    place TEXT,
    info TEXT,
    gpt_story TEXT
    user_story TEXT
    ); 
    '''
    cur.execute(query)


def create_table2():
    query = '''
    CREATE TABLE IF NOT EXISTS prompts (
    id INTEGER PRIMARY KEY,
    user_id INTEGER,
    role TEXT,
    content TEXT,
    date INTEGER,
    tokens INTEGER,
    session_id INTEGER
    ); 
    '''
    cur.execute(query)


def select_all_from_session(user_id, session):
    cur.execute ("SELECT * FROM prompts WHERE user_id = ? AND session_id = ?;",
                 (user_id, session)
    )
    con.commit()



def get_size_of_session(user_id, session):
    cur.execute("SELECT tokens FROM prompts WHERE user_id = 1001 AND session_id = 2 ORDER BY date DESC LIMIT 1;" ,
                (user_id, session)
                )
    con.commit()



def update_genre(genre, user_id):
    cur.execute('UPDATE users SET genre = ? WHERE user_id = ?;',
                (genre, user_id))

    con.commit()

def update_data_the_main_character(user_id, the_main_character):
    cur.execute(
        '''UPDATE users SET the_main_character = ? WHERE user_id = ?;''',
        (the_main_character, user_id)
    )

def update_place(user_id, place):
    cur.execute(
        '''UPDATE users SET place = ? WHERE user_id = ?;''',
        (place, user_id)
    )



def update_info(user_id, info):
    cur.execute(
        '''UPDATE users SET info = ? WHERE user_id = ?;''',
        (user_id, info))

    con.commit()


def update_task(task, user_id):
    cur.execute('UPDATE users SET task = ? WHERE user_id = ?;', (task, user_id))

    con.commit()

def update_answer(answer, user_id):
    cur.execute('UPDATE users SET answer = ? WHERE user_id = ?;', (answer, user_id))
    con.commit()

def update_all(user_id, genre, the_main_character,place, info):
    cur.execute('INSERT or REPLACE INTO users (user_id, genre, the_main_character, place, info) VALUES(?, ?, ?, ?, ?);',
                (user_id, genre, the_main_character, place, info))

    con.commit()




#ssh -i key student@158.160.137.61





def select_data_all(user_id):
    results = cur.execute(f'''
                        SELECT * FROM
                        users
                        WHERE
                        user_id = "{user_id}"
                        LIMIT 1;
                        ''')
    return results



def select_data_genre(user_id):
    results = cur.execute(f'''
    SELECT genre FROM
    users
    WHERE
    user_id = "{user_id}"
    LIMIT 1;
    ''')
    for res in results:
        print(res)




def delete():
    cur.execute(
        '''DELETE FROM users WHERE 1;''')
    con.commit()

