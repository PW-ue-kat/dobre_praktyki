import bcrypt
# hasło "nimda123" po zahashowaniu
hashed_pw = bcrypt.hashpw(b"nimda123", bcrypt.gensalt())
USERS_DB = {
"admin": hashed_pw
}