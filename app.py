from flask import Flask,render_template,request,jsonify,session
from werkzeug.security import generate_password_hash,check_password_hash
from functools import wraps
from database import init_db,query

app=Flask(__name__)
app.secret_key="change-this-secret-key"

def login_required(f):
    @wraps(f)
    def w(*a,**k):
        if not session.get("user_id"): return jsonify({"ok":False,"error":"تسجيل الدخول مطلوب"}),401
        return f(*a,**k)
    return w

def admin_required(f):
    @wraps(f)
    def w(*a,**k):
        if session.get("role")!="admin": return jsonify({"ok":False,"error":"صلاحية المشرف مطلوبة"}),403
        return f(*a,**k)
    return w

def audit(action,details=""):
    query("INSERT INTO audit_log(username,action,details) VALUES(%s,%s,%s)",
          (session.get("username","system"),action,details))

@app.route("/")
def home(): return render_template("index.html")

@app.post("/api/login")
def login():
    d=request.get_json(silent=True) or request.form
    rows=query("SELECT * FROM users WHERE username=%s AND active=1",(str(d.get("username","")).strip(),),True)
    if rows and check_password_hash(rows[0]["password_hash"],str(d.get("password",""))):
        u=rows[0]; session["user_id"]=u["id"]; session["username"]=u["username"]; session["role"]=u["role"]
        audit("تسجيل دخول"); return jsonify({"ok":True,"role":u["role"]})
    return jsonify({"ok":False,"error":"اسم المستخدم أو كلمة المرور غير صحيحة"}),401

@app.post("/api/logout")
def logout():
    audit("تسجيل خروج"); session.clear(); return jsonify({"ok":True})

@app.get("/api/people")
@login_required
def people():
    q=request.args.get("q","").strip(); g=request.args.get("governorate","").strip()
    sql="SELECT * FROM people WHERE 1=1"; p=[]
    if q:
        sql+=" AND (full_name LIKE %s OR national_no LIKE %s OR phone LIKE %s OR employment LIKE %s)"
        x=f"%{q}%"; p += [x,x,x,x]
    if g: sql+=" AND governorate=%s"; p.append(g)
    sql+=" ORDER BY id DESC"
    return jsonify(query(sql,tuple(p),True))

@app.post("/api/people")
@login_required
def add_person():
    d=request.get_json(force=True)
    query("""INSERT INTO people
    (national_no,full_name,age,gender,family_members,governorate,residence,employment,salary,education,marital_status,phone)
    VALUES(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)""",
    (d.get("national_no") or None,d["full_name"],int(d["age"]),d["gender"],
     int(d.get("family_members",1)),d["governorate"],d.get("residence",""),
     d.get("employment",""),float(d.get("salary",0) or 0),d.get("education","غير محدد"),
     d.get("marital_status","غير محدد"),d.get("phone","")))
    audit("إضافة شخص",d["full_name"]); return jsonify({"ok":True})

@app.put("/api/people/<int:pid>")
@login_required
def edit_person(pid):
    d=request.get_json(force=True)
    query("""UPDATE people SET national_no=%s,full_name=%s,age=%s,gender=%s,family_members=%s,
    governorate=%s,residence=%s,employment=%s,salary=%s,education=%s,marital_status=%s,phone=%s WHERE id=%s""",
    (d.get("national_no") or None,d["full_name"],int(d["age"]),d["gender"],
     int(d.get("family_members",1)),d["governorate"],d.get("residence",""),
     d.get("employment",""),float(d.get("salary",0) or 0),d.get("education","غير محدد"),
     d.get("marital_status","غير محدد"),d.get("phone",""),pid))
    audit("تعديل شخص",str(pid)); return jsonify({"ok":True})

@app.delete("/api/people/<int:pid>")
@login_required
@admin_required
def delete_person(pid):
    query("DELETE FROM people WHERE id=%s",(pid,)); audit("حذف شخص",str(pid))
    return jsonify({"ok":True})

@app.get("/api/stats")
@login_required
def stats():
    total=query("SELECT COUNT(*) total FROM people",fetch=True)[0]["total"]
    males=query("SELECT COUNT(*) total FROM people WHERE gender='ذكر'",fetch=True)[0]["total"]
    females=query("SELECT COUNT(*) total FROM people WHERE gender='أنثى'",fetch=True)[0]["total"]
    avg=query("SELECT COALESCE(AVG(age),0) value FROM people",fetch=True)[0]["value"]
    gov=query("SELECT governorate,COUNT(*) total FROM people GROUP BY governorate ORDER BY total DESC",fetch=True)
    return jsonify({"total":total,"males":males,"females":females,"avg_age":round(float(avg),1),"by_governorate":gov})

if __name__=="__main__":
    init_db()
    if not query("SELECT id FROM users LIMIT 1",fetch=True):
        query("INSERT INTO users(username,password_hash,role) VALUES(%s,%s,%s)",
              ("admin",generate_password_hash("admin123"),"admin"))
    app.run(host="127.0.0.1",port=5000,debug=True)
