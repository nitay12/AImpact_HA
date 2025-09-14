# Regu-Biz / רגו-ביז - מערכת הערכת רישוי עסקים

מערכת הערכת רישוי עסקים מבוססת בינה מלאכותית שעוזרת לבעלי עסקים בישראל להבין דרישות רגולטוריות ולקבל דוחות התאמה מותאמים אישית.

## תיאור הפרויקט

**Regu-Biz (רגו-ביז)** היא מערכת חכמה המעבדת נתוני רישוי ממסמכים רגולטוריים ויוצרת דוחות מותאמים אישית באמצעות בינה מלאכותית. המערכת מאפשרת לבעלי עסקים למלא שאלון קצר ולקבל הנחיות ברורות ומעשיות לגבי דרישות הרישוי הרלוונטיות לעסק שלהם.

### מטרות המערכת
- עיבוד חכם של מסמכים רגולטוריים בעברית
- יצירת שאלון דיגיטלי לאיסוף מאפייני העסק
- התאמה אוטומטית בין מאפייני העסק לדרישות הרגולציה
- יצירת דוחות מותאמים אישית באמצעות OpenAI API
- המרת "שפת חוק" לשפה עסקית ברורה ונגישה

## ארכיטקטורת המערכת

```
┌─────────────────────────┐      ┌─────────────────────────┐
│  React Frontend         │      │  FastAPI Backend        │
│  (TypeScript + Vite)    │◄────►│  (Python)               │
│                         │      │                         │
│  • Hebrew RTL Form      │      │  • Data Processing      │
│  • Report Display       │      │  • Matching Engine      │
│  • Accessible UI        │      │  • Business Logic       │
└─────────────────────────┘      └─────────────┬───────────┘
                                               │
                                               │ API Calls
                                               ▼
                                 ┌─────────────────────────┐
                                 │  OpenAI GPT-5-mini      │
                                 │  (AI Service)           │
                                 │                         │
                                 │  • Hebrew Report Gen.   │
                                 │  • Business Language    │
                                 │  • Custom Guidelines    │
                                 └─────────────────────────┘
```

## תכונות עיקריות

### עיבוד נתונים חכם
- קריאה ועיבוד של מסמכי PDF/Word בעברית
- המרה לפורמט JSON מובנה
- זיהוי אוטומטי  של נתוני גודל מקסימלי, תקנים ישראליים, ודרישות מיוחדות

### שאלון דיגיטלי
- **גודל העסק** (במ"ר)
- **תפוסה מקסימלית** (מספר אנשים)
- **מאפיינים מיוחדים**: בישול בגז, הגשת בשר, משלוחים, ישיבה חיצונית, הגשת אלכוהול

### מנוע התאמה מתקדם
- סינון לפי גודל ותפוסה
- התחשבות במאפיינים מיוחדים
- עיבוד חוקי עסק מורכבים
- פתרון קונפליקטים בין דרישות

### יצירת דוחות AI מתקדמת
- אינטגרציה מלאה עם OpenAI GPT-5-mini
- prompts מותאמים לרגולציה ישראלית
- המרת טקסט משפטי לשפה עסקית נגישה
- דוחות מותאמים אישית עם המלצות פעולה

## הוראות התקנה והרצה

### דרישות מקדימות
- **Python 3.9+** - סביבת פיתוח Python
- **Node.js 18.0+** - לפיתוח Frontend
- **Git** - לניהול קוד מקור
- **OpenAI API Key** - לשירות הבינה המלאכותית

### שלב 1: הכנת הסביבה
```bash
# שכפול הפרויקט
git clone <repository-url>
cd AImpact_HA

# בדיקת Python
python --version  # v3.9.0 ומעלה
```

### שלב 2: הגדרת Backend (Python/FastAPI)
```bash
cd backend

# יצירת סביבה וירטואלית
python -m venv .venv

# Windows:
.venv\Scripts\activate
# macOS/Linux:
source .venv/bin/activate

# התקנת dependencies
pip install -r requirements.txt

# הגדרת משתני סביבה
cp .env.example .env
# ערוך את .env והוסף את ה-OpenAI API Key שלך:
# OPENAI_API_KEY=sk-your-actual-key-here
```

### שלב 3: עיבוד נתוני הרגולציה
```bash
# הרצת סקריפט עיבוד הנתונים (חד פעמי)
python data/data_extractor.py

# בדיקת הנתונים המעובדים
ls -la fire_safety_regulatory_data.json
```

### שלב 4: הרצת שרת Backend
```bash
# הרצת שרת FastAPI
python main.py

# השרת יהיה זמין ב:
# http://127.0.0.1:8000
# תיעוד API ב: http://127.0.0.1:8000/docs
```

### שלב 5: הגדרת Frontend (React/TypeScript)
```bash
# פתח terminal חדש
cd ../frontend

# התקנת dependencies
npm install

# הרצת שרת פיתוח
npm run dev

# הפרונט יהיה זמין ב:
# http://localhost:5173
```

### שלב 6: בדיקת המערכת
1. פתח דפדפן וגש לכתובת: `http://localhost:5173`
2. מלא את השאלון עם פרטי עסק לדוגמה:
   - גודל: 200 מ"ר
   - תפוסה: 100 אנשים
   - בחר מאפיינים מיוחדים
3. לחץ על "צור דוח התאמה"
4. בדוק שהמערכת יוצרת דוח בעברית עם המלצות מותאמות

## רשימת Dependencies

### Backend (Python)
```txt
fastapi==0.104.1           # מסגרת עבודה API מהירה
uvicorn[standard]==0.24.0  # שרת ASGI
pydantic                   # validation נתונים
python-dotenv==1.0.0      # ניהול משתני סביבה
openai>=1.50.0            # OpenAI API client
pymupdf                   # עיבוד PDF
python-docx==1.1.0        # עיבוד Word
pytest==7.4.3            # בדיקות יחידה
```

### Frontend (React/TypeScript)
```json
{
  "react": "^18.2.0",
  "react-dom": "^18.2.0",
  "typescript": "^5.0.0",
  "vite": "^4.4.0"
}
```

## תיעוד API

### נקודות קצה עיקריות

#### `POST /api/generate-report`
יצירת דוח התאמה מותאם אישית עם בינה מלאכותית

**Request Body:**
```json
{
  "business_name": "מסעדת דוגמה",
  "business_size_sqm": 200,
  "seating_capacity": 100,
  "uses_gas": true,
  "serves_meat": true,
  "offers_delivery": false,
  "serves_alcohol": false
}
```

**Response:**
```json
{
  "report_content": "דוח מפורט בעברית...",
  "generation_timestamp": "2024-09-14T...",
  "model_used": "gpt-5-mini",
  "tokens_used": 1500,
  "processing_time": 3.2
}
```

#### `GET /api/health`
בדיקת תקינות המערכת

#### `GET /api/stats`
סטטיסטיקות על הנתונים הרגולטוריים הטעונים

#### `GET /api/docs`
תיעוד אינטראקטיבי מלא של ה-API

## מבנה הנתונים

### Business Profile Schema
```typescript
interface BusinessProfile {
  size_sqm: number;              // גודל במ"ר
  capacity_people: number;       // תפוסה מקסימלית
  special_features: string[];    // מאפיינים מיוחדים
  business_type: string;         // סוג עסק
  business_name?: string;        // שם העסק (אופציונלי)
}
```

### Regulatory Requirement Schema
```typescript
interface RequirementMatch {
  id: string;
  hebrew_text: string;           // טקסט בעברית
  category: string;              // קטגוריה (כיבוי אש, חשמל, וכו')
  threshold_type: string;        // סוג סף (area/capacity)
  threshold_value: number;       // ערך סף
  applicability_score: number;  // ציון רלוונטיות
}
```

## אלגוריתם ההתאמה

### שלב 1: סינון בסיסי
```python
# סינון לפי גודל
size_matches = filter_by_size(requirements, business.size_sqm)

# סינון לפי תפוסה
capacity_matches = filter_by_capacity(size_matches, business.capacity_people)
```

### שלב 2: התאמת מאפיינים מיוחדים
```python
# התאמת מאפיינים כמו גז, בשר, משלוחים
feature_matches = apply_feature_rules(capacity_matches, business.special_features)
```

### שלב 3: עיבוד חוקי עסק מתקדמים
```python
# פתרון קונפליקטים בין דרישות
# טיפול במקרי קצה
processed_matches = rule_processor.process_matches(feature_matches, business)
```

### שלב 4: הכנה לעיבוד AI
```python
# פורמט מותאם לבינה מלאכותית
ai_context = formatter.format_for_ai(processed_matches, business)
```

## תיעוד שימוש ב-AI

### כלי פיתוח AI שבהם נעשה שימוש:

#### 1. Claude Code (Anthropic)
- **שימוש**: עזרה בפיתוח הקוד, עיצוב ארכיטקטורה, פתרון בעיות
- **היקף**: כ-70% מהפיתוח נעשה בעזרת Claude Code

#### 2. Cursor AI
- **שימוש**: פתרון באגים מקומיים, תיקון סינטקס, וקוד ריוויו לתוצרים של CC
- **היקף**: כ-5% מהפיתוח נעשה בעזרת Cursor AI

### פרומפטים עיקריים ששימשו במערכת:

#### System Prompt לדוחות רגולטוריים:
```
אתה מומחה ברגולציות בטיחות אש למסעדות בישראל. המטרה שלך היא ליצור דוח ברור ומעשי לבעלי עסקים.

חשוב מאוד:
- כתב בעברית ברורה ונגישה
- המר "שפת חוק" לשפה עסקית מובנת
- תן המלצות מעשיות וקונקרטיות
- סדר לפי עדיפות (דחוף/חשוב/רצוי)
- הוסף הערכת עלות כללית כשאפשר
- הבהר את הצעדים הבאים הנדרשים

מבנה הדוח:
1. סיכום מנהלים (2-3 שורות)
2. דרישות דחופות (אם יש)
3. דרישות חובה
4. דרישות רצויות
5. המלצות לביצוע
6. איש קשר מומלץ (רשויות/מומחים)
```

#### User Prompt Template:
```
פרטי העסק:
- סוג עסק: מסעדה
- שם העסק: [שם העסק]
- גודל: [X] מ"ר
- תפוסה: [Y] אנשים
- מאפיינים מיוחדים: [רשימת מאפיינים]

נתוני הרגולציה החלים על העסק:
[נתונים מובנים מהמחסן]

בהתבסס על הנתונים האלה, צור דוח מותאם אישית לבעל העסק.
```