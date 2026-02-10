# ==========================================================
# USED TO CHECK IF EVERY USER REQUEST CONTAINS AUTH TOKEN
# ==========================================================


from fastapi import Depends, HTTPException, Request
from jose import jwt, JWTError
from core.security import SECRET_KEY, ALGORITHM
from core.database import get_connection


def get_current_user(request: Request):
    """
    Extract user from JWT cookie and return full user data
    """
    token = request.cookies.get("access_token")
    if not token:
        raise HTTPException(status_code=401, detail="Not authenticated")

    try:
        # Decode JWT to get user_id
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id = int(payload["sub"])
        
        # Fetch full user data from database
        con = get_connection()
        cur = con.cursor()
        
        try:
            cur.execute(
                "SELECT user_id, email, role FROM users WHERE user_id = %s",
                (user_id,)
            )
            user = cur.fetchone()
            
            if not user:
                raise HTTPException(status_code=401, detail="User not found")
            
            return {
                "user_id": user['user_id'],
                "email": user['email'],
                "role": user['role']
            }
        finally:
            cur.close()
            con.close()
            
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid or expired token")