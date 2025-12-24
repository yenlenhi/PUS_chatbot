# 📁 Project Structure - Clean & Organized

> Cấu trúc project sau khi clean up - Updated: 24/12/2024

---

## 📂 Root Directory

```
uni_bot/
├── 📁 src/                          # Source code chính
│   ├── api/                         # API routes & endpoints
│   ├── services/                    # Business logic services
│   ├── models/                      # Data models & schemas
│   ├── middleware/                  # Request/response middleware
│   └── utils/                       # Utility functions
│
├── 📁 frontend/                     # Next.js 14 frontend
│   ├── src/                         # Frontend source
│   ├── public/                      # Static assets
│   └── package.json                 # Frontend dependencies
│
├── 📁 config/                       # Configuration files
│   └── settings.py                  # App settings & env vars
│
├── 📁 docs/                         # Documentation
│   ├── deployment/                  # Deployment guides
│   │   ├── RAILWAY_CHECKLIST.md
│   │   ├── RAILWAY_FIX_GUIDE.md
│   │   ├── RAILWAY_QUICK_FIX.md
│   │   └── DEPLOY_TO_RAILWAY.md
│   ├── guides/                      # User guides
│   │   ├── POSTGRES_SETUP_GUIDE.md
│   │   ├── README_GEMINI_SETUP.md
│   │   ├── HUONG_DAN_SUGGESTED_QUESTIONS.md
│   │   └── ATTACHMENTS_FEATURE_GUIDE.md
│   ├── architecture/                # Architecture docs
│   │   ├── KIEN_TRUC_HE_THONG.md
│   │   ├── DATA_LAYER_README.md
│   │   ├── SUGGESTED_QUESTIONS_IMPLEMENTATION.md
│   │   ├── STEP_7_RAG_SERVICE_UPDATE.md
│   │   └── STEP_8_TESTING_GUIDE.md
│   ├── DIAGRAMS.md                  # System diagrams
│   ├── REFERENCES.md                # Research references
│   ├── OPERATIONS_GUIDE.md          # Operations manual
│   └── TECHNICAL_ARCHITECTURE.md    # Technical details
│
├── 📁 scripts/                      # Utility scripts
│   ├── migrate_to_railway.ps1
│   ├── check_db_railway.py
│   └── ...
│
├── 📁 tests/                        # Test files
│   └── test_*.py
│
├── 📁 data/                         # Data storage
│   ├── pdfs/                        # PDF documents
│   ├── processed/                   # Processed files
│   └── embeddings/                  # Embedding cache
│
├── 📁 logs/                         # Application logs
│
├── 📄 main.py                       # FastAPI application entry
├── 📄 requirements.txt              # Python dependencies
├── 📄 README.md                     # Main documentation
├── 📄 START_HERE.md                 # Getting started guide
├── 📄 SECURITY.md                   # Security documentation
│
├── 🐳 docker-compose.yml            # Docker setup
├── 🐳 Dockerfile.frontend           # Frontend Docker image
├── 🚂 nixpacks.toml                 # Railway build config
├── 🚂 Procfile                      # Process file for Railway
├── 🚂 railway.json                  # Railway configuration
├── 🚂 runtime.txt                   # Python version
│
└── 📄 .gitignore                    # Git ignore rules

```

---

## 🗑️ Files Cleaned Up

### ❌ Removed:
- `backup.sql`, `backup_utf8.sql`, `fix_owner.sql` - Database backups (not for Git)
- `tmp_railway_dump.dump`, `tmp_pdfs.tar.gz` - Temporary files
- `data_bundle.zip` (200.99 MB) - Large data file
- `local_tables.txt`, `prod_tables.txt` - Temporary comparison files
- `test_gemini_max_tokens.py`, `test_normalization.py` - Ad-hoc test files
- `test_vietnamese_formatter.py`, `test_request.json` - Temporary test files
- `COMPLETION_SUMMARY.md`, `FINAL_SUMMARY.md` - Old summary files
- `DATA_LAYER_IMPLEMENTATION_COMPLETE.md` - Completion markers
- `DOCUMENTATION_COMPLETE.md`, `UNDERSTANDING_COMPLETE.md` - Status files
- `SYSTEM_UNDERSTANDING_SUMMARY.md`, `NEXT_STEPS.md` - Planning files
- `COMMIT_MESSAGE.md`, `GIT_PUSH_SUCCESS.md` - Git helper files
- `create_admin_dirs.py`, `create_admin_structure.bat` - Old setup scripts
- `create_api_dirs.py`, `check_db_documents.py` - Setup utilities
- `__pycache__/`, `.pytest_cache/` - Build artifacts
- `package.json`, `package-lock.json` (from root) - Belong in frontend/

### 📦 Organized:
- Deployment guides → `docs/deployment/`
- Setup guides → `docs/guides/`
- Architecture docs → `docs/architecture/`

---

## 📋 Important Files

### 🚀 Entry Points
- `main.py` - Backend server entry point
- `frontend/src/app/page.tsx` - Frontend entry point

### ⚙️ Configuration
- `config/settings.py` - Main configuration
- `.env` - Environment variables (not in Git)
- `.env.example` - Environment template

### 🧪 Testing
- `test_railway_config.py` - Railway deployment test
- `test_postgres_connection.py` - Database connection test
- `test_suggested_questions.py` - Feature test
- `tests/` - Unit tests directory

### 📚 Documentation
- `README.md` - Project overview
- `START_HERE.md` - Quick start guide
- `docs/DIAGRAMS.md` - System diagrams
- `docs/REFERENCES.md` - Research references

---

## 🎯 Next Steps After Clean

### 1. Update .gitignore
Ensure cleaned files stay ignored:
```bash
git status
# Should not show removed files as untracked
```

### 2. Commit Clean Structure
```bash
git add .
git commit -m "chore: clean up project structure

- Removed backup files and temporary data
- Organized documentation into folders
- Removed build artifacts and old completion markers
- Kept only essential files for production"
```

### 3. Verify Everything Works
```bash
# Test backend
python test_railway_config.py

# Test frontend (in frontend/ directory)
npm run dev
```

---

## 🛡️ Files Protected by .gitignore

These should never be committed:
- `data/` - User data and embeddings
- `logs/` - Log files
- `*.sql`, `*.dump` - Database dumps
- `*.zip`, `*.tar.gz` - Compressed archives
- `__pycache__/` - Python cache
- `node_modules/` - Node packages
- `.env` - Environment secrets

---

## 📊 Directory Sizes (Approximate)

| Directory | Size | Purpose |
|-----------|------|---------|
| `frontend/` | ~50 MB | Next.js app + node_modules |
| `src/` | ~2 MB | Python source code |
| `docs/` | ~500 KB | Documentation |
| `data/` | Varies | User PDFs and embeddings |
| `logs/` | Varies | Application logs |

---

## ✅ Clean Up Checklist

- [x] Removed backup files (*.sql, *.dump)
- [x] Removed temporary files (tmp_*, data_bundle.zip)
- [x] Removed old documentation markers
- [x] Organized docs into folders
- [x] Removed build artifacts (__pycache__)
- [x] Removed misplaced package files
- [x] Updated project structure documentation
- [ ] Commit clean structure
- [ ] Verify tests pass
- [ ] Deploy to Railway

---

*Project structure cleaned and organized - 24/12/2024*
