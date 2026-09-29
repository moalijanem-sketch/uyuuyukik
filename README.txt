المشروع الكامل: HTML + Python Flask + MySQL SQL

التشغيل:
1. شغّل MySQL.
2. عدّل DB_PASSWORD في config.py.
3. pip install -r requirements.txt
4. python app.py
5. افتح http://127.0.0.1:5000

الدخول الافتراضي:
admin
admin123

الواجهة الأصلية موجودة في templates/index.html.
الـBackend موجود في app.py.
قاعدة البيانات في database/schema.sql.

API:
POST /api/login
POST /api/logout
GET /api/people
POST /api/people
PUT /api/people/<id>
DELETE /api/people/<id> (Admin)
GET /api/stats
