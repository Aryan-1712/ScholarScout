# Scholarship Finder – Django Backend

## Project Layout

```
scholarship_project/
├── scholarship_project/          # Django project package
│   ├── settings.py               # All settings (DB, CORS, DRF, …)
│   ├── urls.py                   # Root URL router
│   └── wsgi.py
│
├── users/                        # Auth app
│   ├── models.py                 # CustomUser (email-based login)
│   ├── serializers.py            # Register / Login / UserDetail
│   ├── views.py                  # register, login, logout, me
│   ├── signals.py                # Auto-create Token on user creation
│   ├── urls.py                   # /api/auth/…
│   └── admin.py
│
├── scholarships/                 # Scholarship catalogue + bookmarks
│   ├── models.py                 # Scholarship, SavedScholarship
│   ├── serializers.py
│   ├── views.py                  # list, detail, save/unsave, stats
│   ├── urls.py                   # /api/scholarships/…
│   ├── admin.py
│   └── management/commands/
│       └── seed_scholarships.py  # Populates the 10 sample scholarships
│
├── templates/                    # (reserved for future server-rendered pages)
├── static/                       # (reserved for shared static assets)
├── requirements.txt
├── manage.py
└── README.md                     # ← this file
```

---

## 1 – Quick Start

```bash
# 1. Create & activate a virtual environment
python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate

# 2. Install dependencies
pip install -r requirements.txt

# 3. Run migrations (creates tables + auth token table)
python manage.py migrate

# 4. Seed the 10 sample scholarships that appear on the dashboard
python manage.py seed_scholarships

# 5. (Optional) Create a Django admin super-user
python manage.py createsuperuser

# 6. Start the dev server
python manage.py runserver       # → http://127.0.0.1:8000
```

---

## 2 – API Endpoints

All responses are JSON. Token auth is required where noted — pass the token
in the `Authorization` header:

```
Authorization: Token <your_token_here>
```

### 2.1 Auth  (`/api/auth/`)

| Method | Endpoint         | Auth?  | Description                              |
|--------|------------------|--------|------------------------------------------|
| POST   | `/register/`     | No     | Create account → returns token + user    |
| POST   | `/login/`        | No     | Authenticate  → returns token + user     |
| POST   | `/logout/`       | Yes    | Invalidate current token                 |
| GET    | `/me/`           | Yes    | Return current user info                 |

**Register / Login request body:**
```json
{
  "full_name":        "John Doe",         // register only
  "email":            "john@example.com",
  "password":         "secret123",
  "confirm_password": "secret123"         // register only
}
```

**Success response (both endpoints):**
```json
{
  "token": "abc123…",
  "user": {
    "id": 1,
    "email": "john@example.com",
    "full_name": "John Doe",
    "initials": "JD",
    "date_joined": "2026-02-03T12:00:00Z"
  }
}
```

---

### 2.2 Scholarships  (`/api/scholarships/`)

| Method | Endpoint               | Auth?  | Description                              |
|--------|------------------------|--------|------------------------------------------|
| GET    | `/`                    | No     | List scholarships (filterable)           |
| GET    | `/<id>/`               | No     | Single scholarship detail                |
| GET    | `/stats/`              | No     | Dashboard stat-card aggregates           |
| GET    | `/saved/`              | Yes    | All scholarships the user has saved      |
| POST   | `/saved/<id>/`         | Yes    | Save (bookmark) a scholarship            |
| DELETE | `/saved/<id>/`         | Yes    | Remove a saved scholarship               |

#### List query-parameters

Every parameter is optional and maps directly to the sidebar filters
in your `dashboard.html`:

| Param            | Example             | Notes                                                   |
|------------------|---------------------|---------------------------------------------------------|
| `search`         | `?search=google`    | Full-text across name / org / description               |
| `max_amount`     | `?max_amount=20000` | Upper bound (omit or set 50000 for "show all")          |
| `field`          | `?field=Engineering`| Must match a `field_of_study` choice                    |
| `min_gpa`        | `?min_gpa=3.0`      | Returns scholarships whose required GPA ≤ this value    |
| `status`         | `?status=Undergraduate` | Student status filter                               |
| `type`           | `?type=Merit-Based,Diversity` | Comma-separated scholarship types            |
| `deadline_days`  | `?deadline_days=30` | Only scholarships due within N days from today          |
| `sort`           | `?sort=amount-high` | `amount-high` / `amount-low` / `deadline` / `relevant`  |

#### Stats response

```json
{
  "total_scholarships": 10,
  "total_awards":       200000,
  "matched":            8,
  "urgent":             3
}
```

---

## 3 – Connecting Your Frontend

Inside your `index.html` (login page) replace the `handleSubmit` function's
`alert(…)` with:

```js
async function handleSubmit() {
  const email    = document.getElementById('email').value;
  const password = document.getElementById('password').value;

  const endpoint = isLogin ? '/api/auth/login/' : '/api/auth/register/';
  const body     = isLogin
    ? { email, password }
    : { full_name: document.getElementById('fullName').value, email, password,
        confirm_password: document.getElementById('confirmPassword').value };

  try {
    const res  = await fetch(endpoint, {
      method:  'POST',
      headers: { 'Content-Type': 'application/json' },
      body:    JSON.stringify(body),
    });
    const data = await res.json();

    if (!res.ok) {
      // data.non_field_errors OR data.email etc.
      alert(JSON.stringify(data));
      return;
    }

    // Persist token & user for the dashboard
    sessionStorage.setItem('token',    data.token);
    sessionStorage.setItem('user',     JSON.stringify(data.user));
    window.location.href = 'dashboard.html';
  } catch (err) {
    alert('Network error – is the backend running?');
  }
}
```

Inside your `dashboard.html` replace the hard-coded `scholarships` array
and `init()` with API calls:

```js
const TOKEN = sessionStorage.getItem('token');
const headers = { 'Authorization': `Token ${TOKEN}` };

async function init() {
  // Stat cards
  const statsRes  = await fetch('/api/scholarships/stats/');
  const stats     = await statsRes.json();
  document.getElementById('totalCount').textContent  = stats.total_scholarships;
  document.getElementById('totalAwards').textContent = `${ (stats.total_awards/1000).toFixed(0) }K`;
  document.getElementById('matchedCount').textContent = stats.matched;
  document.getElementById('urgentCount').textContent  = stats.urgent;

  // Scholarship list
  const listRes   = await fetch('/api/scholarships/');
  scholarships    = await listRes.json();
  filteredScholarships = [...scholarships];
  renderScholarships();
}

// Update filterScholarships() to call the API with query params instead of
// filtering client-side:
async function filterScholarships() {
  const params = new URLSearchParams();
  const search = document.getElementById('searchInput').value;
  if (search)  params.set('search', search);

  const amount = document.getElementById('amountRange').value;
  params.set('max_amount', amount);

  const field  = document.getElementById('fieldFilter').value;
  if (field)   params.set('field', field);

  const gpa    = document.getElementById('gpaRange').value;
  if (gpa > 0) params.set('min_gpa', gpa);

  const status = document.getElementById('statusFilter').value;
  if (status)  params.set('status', status);

  const types  = [...document.querySelectorAll('input[type="checkbox"]:checked')]
                   .map(cb => cb.value);
  if (types.length) params.set('type', types.join(','));

  const deadlineDays = document.getElementById('deadlineFilter').value;
  if (deadlineDays)  params.set('deadline_days', deadlineDays);

  const sort   = document.getElementById('sortFilter').value;
  params.set('sort', sort);

  const res = await fetch(`/api/scholarships/?${params}`);
  filteredScholarships = await res.json();
  renderScholarships();
  updateStats();
}

// Save / unsave a scholarship
async function saveScholarship(id) {
  const res = await fetch(`/api/scholarships/saved/${id}/`, {
    method:  'POST',
    headers: { ...headers, 'Content-Type': 'application/json' },
  });
  const data = await res.json();
  alert(res.ok ? '✅ Scholarship saved!' : data.detail);
}
```

---

## 4 – Admin Panel

Visit **http://127.0.0.1:8000/admin/** after creating a super-user to
browse / edit users and scholarships through the Django admin UI.

---

## 5 – Production Notes

* Replace `SECRET_KEY` via an environment variable.
* Set `DEBUG=False` and configure `ALLOWED_HOSTS`.
* Swap SQLite for PostgreSQL (update `DATABASES` in settings).
* Tighten `CORS_ALLOWED_ORIGINS` to your actual frontend domain.
* Serve static files with `whitenoise` or your web-server (nginx).
* Run with `gunicorn scholarship_project.wsgi:application`.
