def can_user_make_request():
    today = datetime.now().strftime("%Y-%m-%d")
    
    cursor.execute("SELECT date, requests, purchased_requests FROM users WHERE user_id = ?", (user_id,))
    row = cursor.fetchone()

    if not row:
        initialize_user()
        cursor.execute("SELECT date, requests, purchased_requests FROM users WHERE user_id = ?", (user_id,))
        row = cursor.fetchone()

    date_last_request, normal_requests, purchased_requests = row

    # Réinitialiser les requêtes si la date a changé
    if date_last_request != today:
        cursor.execute("UPDATE users SET date = ?, requests = 5 WHERE user_id = ?", (today, user_id))
        conn.commit()
        return True

    # Vérifier si des requêtes normales sont disponibles
    if normal_requests > 0:
        return True

    # Vérifier si l'utilisateur a des requêtes achetées
    if purchased_requests > 0:
        return True

    return False
