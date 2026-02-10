from fastapi import APIRouter, HTTPException, Request, Response, Depends
from core.database import get_connection
from core.security import hash_password, verify_password, create_access_token
from api.deps import get_current_user
from schemas.auth import (
    RegisterRequest,
    LoginRequest,
    UserResponse,
    MessageResponse
)

router = APIRouter(prefix="/auth", tags=["auth"])


# ==========================================================
# REGISTER
# ==========================================================

@router.post(
    "/register",
    response_model=UserResponse,
    status_code=201
)
def register(
    data: RegisterRequest,
    request: Request,
    response: Response
):
    con = get_connection()
    cur = con.cursor()
    client_ip = request.client.host

    try:
        # Check if user exists
        cur.execute("SELECT user_id FROM users WHERE email = %s", (data.email,))
        if cur.fetchone():
            raise HTTPException(status_code=400, detail="Email already registered")

        # Create user
        cur.execute(
            """
            INSERT INTO users (email, password_hash)
            VALUES (%s, %s)
            RETURNING user_id, role
            """,
            (data.email, hash_password(data.password))
        )

        result = cur.fetchone()
        user_id = result['user_id']
        role = result['role']

        # Log auth
        cur.execute(
            "INSERT INTO auth_logs (user_id, auth_status, ip_address) VALUES (%s, %s, %s)",
            (user_id, "success", client_ip)
        )

        con.commit()

        # Create session cookie
        token = create_access_token({"sub": str(user_id)})
        
       
        response.set_cookie(
            key="access_token",
            value=token,
            httponly=True,
            secure=False,           # False for localhost (HTTP)
            samesite="lax",        
            path="/",
            max_age=60 * 60 * 24    # 24 hours
        )

        return {
            "user_id": user_id,
            "email": data.email,
            "role": role
        }
    
    except HTTPException:
        con.rollback()
        raise
    except Exception as e:
        con.rollback()
        print(f"Registration error: {e}")
        raise HTTPException(status_code=500, detail="Registration failed")
    finally:
        cur.close()
        con.close()


# ==========================================================
# LOGIN
# ==========================================================

@router.post(
    "/login",
    response_model=UserResponse
)
def login(
    data: LoginRequest,
    request: Request,
    response: Response
):
    con = get_connection()
    cur = con.cursor()
    client_ip = request.client.host

    try:
        cur.execute(
            "SELECT user_id, password_hash, role FROM users WHERE email = %s",
            (data.email,)
        )
        row = cur.fetchone()

        if not row or not verify_password(data.password, row['password_hash']):
            # Log failed attempt
            if row:
                cur.execute(
                    "INSERT INTO auth_logs (user_id, auth_status, ip_address) VALUES (%s, %s, %s)",
                    (row['user_id'], "failed", client_ip)
                )
                con.commit()
            raise HTTPException(status_code=401, detail="Invalid credentials")

        user_id = row['user_id']
        role = row['role']

        # Log success
        cur.execute(
            "INSERT INTO auth_logs (user_id, auth_status, ip_address) VALUES (%s, %s, %s)",
            (user_id, "success", client_ip)
        )

        con.commit()

        # Create cookie
        token = create_access_token({"sub": str(user_id)})
        
       
        response.set_cookie(
            key="access_token",
            value=token,
            httponly=True,
            secure=False,           # False for localhost (HTTP)
            samesite="lax",        
            path="/",
            max_age=60 * 60 * 24    # 24 hours
        )

        return {
            "user_id": user_id,
            "email": data.email,
            "role": role
        }
    
    except HTTPException:
        con.rollback()
        raise
    except Exception as e:
        con.rollback()
        print(f"Login error: {e}")
        raise HTTPException(status_code=500, detail="Login failed")
    finally:
        cur.close()
        con.close()


# ==========================================================
# LOGOUT
# ==========================================================

@router.post(
    "/logout",
    response_model=MessageResponse
)
def logout(response: Response):
    response.delete_cookie(
        key="access_token",
        path="/",
        samesite="lax"  )
    return {"message": "Logged out successfully"}


# ==========================================================
# CURRENT USER
# ==========================================================

@router.get(
    "/me",
    response_model=UserResponse
)
def me(user=Depends(get_current_user)):
    """
    Get current authenticated user
    user is a dict with {user_id, email, role}
    """
    return user