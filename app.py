import sqlite3
from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

app = FastAPI()
DB = "users.db"


def get_db():
    conn = sqlite3.connect(DB)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    conn = get_db()
    conn.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT,
            email TEXT UNIQUE,
            phone TEXT,
            city TEXT
        )
    """)
    if conn.execute("SELECT COUNT(*) FROM users").fetchone()[0] == 0:
        users = [
            ("Admin User", "admin@wpbrigade.com", "+923001112233", "Sialkot"),
            ("Asim Jameel", "asim.jameel7113@gmail.com", "+923167123862", "Sialkot"),
            ("Samantha", "samantha@xyz.com", "+923214455667", "Lahore"),
        ]
        conn.executemany(
            "INSERT INTO users (name, email, phone, city) VALUES (?, ?, ?, ?)",
            users,
        )
        conn.commit()
    conn.close()


init_db()


def get_users():
    conn = get_db()
    rows = conn.execute("SELECT * FROM users").fetchall()
    conn.close()
    return [dict(r) for r in rows]


def find_user(key: str):
    key = key.strip().strip('"').strip("'").lower()
    if "@" not in key and key.endswith("s"):
        key = key[:-1].rstrip("'")
    conn = get_db()
    row = conn.execute(
        "SELECT * FROM users WHERE LOWER(email) = ? OR LOWER(name) LIKE ?",
        (key, f"{key}%"),
    ).fetchone()
    conn.close()
    return dict(row) if row else None


def process_message(text: str) -> str:
    clean = text.replace('"', " ").replace("'", " ")
    words = clean.split()
    lower = text.lower()
    emails = [w for w in words if "@" in w]

    # 1. Add user
    if "add" in lower:
        if not emails:
            return "Please provide a valid email to add."
        email = emails[0]
        if find_user(email):
            return f"User {email} is already in the system."
        phones = [w for w in words if w.startswith("+") or w.isdigit()]
        phone = phones[0] if phones else "N/A"
        name = email.split("@")[0].replace(".", " ").title()

        conn = get_db()
        conn.execute(
            "INSERT INTO users (name, email, phone, city) VALUES (?, ?, ?, ?)",
            (name, email, phone, "Sialkot"),
        )
        conn.commit()
        conn.close()
        return f"Added user {name} ({email}) with phone {phone}."

    # 2. Remove user
    elif "remove" in lower or "delete" in lower:
        target = emails[0] if emails else words[-1]
        user = find_user(target)
        if not user:
            return f"User {target} not found."
        conn = get_db()
        conn.execute("DELETE FROM users WHERE id = ?", (user["id"],))
        conn.commit()
        conn.close()
        return f"Removed user {user['email']} from the system."

    # 3. Update user
    elif "update" in lower or "change" in lower:
        if " to " not in lower:
            return "Please use format: update <user> <field> to <value>"
        new_val = text.split(" to ")[-1].strip().strip('"').strip("'")

        field = "city"
        for f in ["city", "phone", "name", "email"]:
            if f in lower:
                field = f
                break

        if emails:
            target = emails[0]
        else:
            low_words = [w.lower() for w in words]
            idx = low_words.index("update") if "update" in low_words else low_words.index("change")
            target = words[idx + 1]
            if target.lower() in ("the", "user"):
                target = words[idx + 2]

        user = find_user(target)
        if not user:
            return f"User {target} not found."

        conn = get_db()
        conn.execute(f"UPDATE users SET {field} = ? WHERE id = ?", (new_val, user["id"]))
        conn.commit()
        conn.close()
        return f"Updated {user['name']} {field} to {new_val}."

    return "Command not recognized. You can add, remove, or update a user."


class LoginReq(BaseModel):
    email: str


class ChatReq(BaseModel):
    email: str
    message: str


@app.post("/api/login")
def login(req: LoginReq):
    user = find_user(req.email)
    if not user or user["email"].lower() != req.email.strip().lower():
        raise HTTPException(status_code=401, detail="Email not found in system.")
    return {"user": user, "users": get_users()}


@app.post("/api/chat")
def chat(req: ChatReq):
    if not find_user(req.email):
        raise HTTPException(status_code=401, detail="Please login first.")
    reply = process_message(req.message)
    return {"reply": reply, "users": get_users()}


app.mount("/static", StaticFiles(directory="static"), name="static")


@app.get("/")
def home():
    return FileResponse("static/index.html")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)