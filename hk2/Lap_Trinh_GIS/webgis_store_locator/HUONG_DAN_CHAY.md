# Huong dan chay du an WebGIS Store Locator

Tai lieu nay huong dan cach cai dat moi truong, cai thu vien va chay du an tren may local.

## 1. Yeu cau cai dat truoc

Can cai cac thanh phan sau:

- Python 3.12+ va da them vao `PATH`
- PostgreSQL 14+ hoac ban moi hon
- PowerShell (Windows)

## 2. Thu vien Python du an su dung

Noi dung trong `requirements.txt`:

- `Django>=5.2`
- `requests>=2.31`
- `psycopg2-binary>=2.9`
- `Pillow>=10.0`
- `reportlab>=4.0`

## 3. Cau hinh file `.env`

Du an doc bien moi truong tu file `.env`. Ban co the tao file nay bang cach copy tu `.env.example`.

Lenh PowerShell:

```powershell
Copy-Item .env.example .env
```

Sau do mo file `.env` va cap nhat toi thieu cac gia tri database:

```env
DJANGO_SECRET_KEY=change-me
DJANGO_DEBUG=true
DJANGO_ALLOWED_HOSTS=127.0.0.1,localhost

DB_ENGINE=django.db.backends.postgresql
DB_NAME=webgis_db
DB_USER=postgres
DB_PASSWORD=
DB_HOST=localhost
DB_PORT=5432
```

Luu y:

- Ban can tao san database PostgreSQL truoc khi chay migrate.
- Hay doi `DJANGO_SECRET_KEY` thanh gia tri rieng cua ban.
- Neu khong can gui email tren local, co the de trong cac bien SMTP.

## 4. Cach setup nhanh bang script co san

Du an da co script `scripts/setup_team.ps1` de tu dong:

- tao virtual environment `.venv`
- nang cap `pip`
- cai thu vien tu `requirements.txt`
- chay `migrate`
- nap fixture `modules/store/fixtures/store_data.json`
- chay `python manage.py check`

Lenh setup:

```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\setup_team.ps1
```

Mot so tuy chon huu ich:

Chay setup va mo server ngay:

```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\setup_team.ps1 -RunServer -Port 8000
```

Tao lai virtual environment:

```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\setup_team.ps1 -RecreateVenv
```

Xoa du lieu local va nap lai fixture:

```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\setup_team.ps1 -FlushData
```

## 5. Cach cai dat va chay thu cong

Neu ban muon tu thuc hien tung buoc, dung cac lenh sau trong thu muc goc du an.

### Buoc 1: Tao virtual environment

```powershell
python -m venv .venv
```

### Buoc 2: Kich hoat virtual environment

```powershell
.\.venv\Scripts\Activate.ps1
```

Neu PowerShell chan script, co the mo terminal moi va chay:

```powershell
Set-ExecutionPolicy -Scope Process Bypass
.\.venv\Scripts\Activate.ps1
```

### Buoc 3: Nang cap pip

```powershell
python -m pip install --upgrade pip
```

### Buoc 4: Cai thu vien

```powershell
python -m pip install -r requirements.txt
```

### Buoc 5: Tao database PostgreSQL

Tao 1 database, vi du:

- Ten DB: `webgis_db`
- User: `postgres`
- Password: theo may cua ban

Sau do cap nhat lai file `.env` cho dung thong tin.

### Buoc 6: Chay migrate

```powershell
python manage.py migrate
```

### Buoc 7: Nap du lieu mau

```powershell
python manage.py loaddata modules/store/fixtures/store_data.json
```

### Buoc 8: Kiem tra cau hinh Django

```powershell
python manage.py check
```

### Buoc 9: Chay server local

```powershell
python manage.py runserver 127.0.0.1:8000
```

Mo trinh duyet tai:

```text
http://127.0.0.1:8000
```

## 6. Cac lenh hay dung

Chay server:

```powershell
python manage.py runserver
```

Chay server voi port cu the:

```powershell
python manage.py runserver 127.0.0.1:8001
```

Tao migration moi:

```powershell
python manage.py makemigrations
```

Ap dung migration:

```powershell
python manage.py migrate
```

Nap lai du lieu mau:

```powershell
python manage.py loaddata modules/store/fixtures/store_data.json
```

Tao tai khoan admin:

```powershell
python manage.py createsuperuser
```

Kiem tra cau hinh:

```powershell
python manage.py check
```

## 7. Loi thuong gap

`python` khong duoc nhan:

- Kiem tra Python da cai va da them vao `PATH` chua.

Khong ket noi duoc PostgreSQL:

- Kiem tra PostgreSQL da chay chua.
- Kiem tra lai `DB_NAME`, `DB_USER`, `DB_PASSWORD`, `DB_HOST`, `DB_PORT` trong `.env`.

Loi kich hoat `.venv` tren PowerShell:

- Thu dung `Set-ExecutionPolicy -Scope Process Bypass`

Loi khi nap fixture:

- Dam bao da chay `python manage.py migrate` truoc.

## 8. Thu muc va lenh quan trong

- File khoi dong Django: `manage.py`
- Cau hinh chinh: `config/settings.py`
- Script setup nhanh: `scripts/setup_team.ps1`
- Du lieu mau: `modules/store/fixtures/store_data.json`

