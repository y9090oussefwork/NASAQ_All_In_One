## 26. رسالة التشغيل الجاهزة لوكيل البناء

ضع هذه الوثيقة في مجلد تريد بناء نَسَق داخله، ثم افتح المجلد في وكيل البرمجة. فتح الملف وحده ليس طلب تنفيذ؛ أرسل الرسالة التالية:

```text
اقرأ docs/NASAQ_BUILD_SPEC_AR_v1_1.md كاملًا، ولو على أجزاء، وابنِ منظومة «نَسَق — Nasaq» وفقه.

أريد تنفيذ المنظومة نفسها، لا تلخيص الملف ولا بناء تطبيق مثال بدلها.
العربية هي الافتراضية، والإنجليزية اختيار مدعوم، والأوامر موحدة من خلال نَسَق.
لا تربط النواة بمزود نموذج واحد، ولا تطلب مني استخدام أوامر الأدوات الفرعية.

ابدأ بفحص مجلد العمل وإمكانات البيئة، ثم أنشئ سجل متطلبات وخطة مراحل قصيرة.
بعدها نفذ المراحل المحلية الآمنة تدريجيًا مع الاختبارات والأدلة.
لا تنسخ هذه الوثيقة الطويلة كما هي إلى SKILL.md؛ حوّلها إلى نواة موجزة ومراجع تُحمّل عند الحاجة.

راجع الوثائق الرسمية عند بناء محولات Codex وClaude Code وCursor ومزودي المواصفات.
ميّز التنفيذ الأصلي من اتباع تعليمات مزود، والاختبار الحقيقي من المحاكاة.
لا تستبدل ملفات موجودة أو تنشر على GitHub أو تثبت عالميًا أو تستخدم خدمة مدفوعة دون إذني.
توقف فقط عند قرار مؤثر أو صلاحية لازمة، ولا تعِد طرح أسئلة أجاب عنها الملف.

سلّم مصدرًا منظمًا وskill.zip ودليلًا عربيًا وإنجليزيًا، مع تقرير صريح عن المنفذ وغير المنفذ،
والاختبارات التي شُغلت، والمنصات التي جُربت، والأجزاء المحجوبة أو غير المختبرة.

Project-specific workspace notes (read after the Arabic prompt):
- The latest editable baseline already exists at skills/nasaq/. Preserve and extend it.
- Use docs/NASAQ_BUILD_SPEC_AR_v1_1.md as the authoritative build specification.
- The current version is an instructional prototype (v0.2.0), not a finished orchestration engine.
- Use docs/NASAQ_PROVIDER_CATALOG_AR.md for discovery. Do not install the whole catalog.
- Preserve the baseline tests and add tests for each real adapter.
- Separate actual execution evidence from mocks, plans, documentation, and catalog entries.
- Keep all writing confined to this workspace until explicitly authorized otherwise.
- The legacy/ directory is historical reference material, not another active skill.
- Before releasing, review license notices and make real checks on each named host.
```
