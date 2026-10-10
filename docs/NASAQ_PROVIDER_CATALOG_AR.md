# كتالوج نَسَق: اختيار التخصصات والأدوات حسب المشروع

**تاريخ مراجعة المصادر: 9 أكتوبر 2026.** يعرض النص الأصلي 68 مصدرًا في 38 مجموعة قدرات. أصبح السجل المحلي الموسع 108 مداخل و47 قدرة بعد تجهيز أبحاث الويب؛ العدد للتنظيم وليس دليل قوة. المصادر تشمل مهارات وأدوات ومراجع رسمية ومعايير؛ ليست كلها برامج تثبت.

هذه قائمة قصيرة عملية لكل مجال، مبنية على الوثائق الأصلية وقراءة مداخل مختارة، وليست مسحًا شاملًا لكل GitHub ولا benchmark يثبت الأقوى مطلقًا. الترتيب سياقي: الاحتفاظ بالمناسب القائم، ثم التخصص والنسخة والجودة والأدلة والخصوصية والتكلفة. حالات التشغيل والاختبار والتراخيص للإدماج الفعلي لم تُعتمد في هذا الإصدار.

**لا تثبّت القائمة كاملة.** اختر 1–3 مرشحين للدور المتنافس، ثم مالكًا واحدًا لكل جزء ومرحلة. الأدوات المكملة ليست بدائل متنافسة بالضرورة، ولكن إدراجها لا يثبت عدم تعارض إعداداتها أو حق الوصول للبيانات. النواة هي المنسّق والبديل مع توثيق الإصدار عند غياب تخصص موثوق، وليست ادعاء أنها أفضل خبير لكل تقنية.

كل رابط فرع متحرك للاكتشاف فقط؛ التفعيل لاحقًا يتطلب تثبيت نسخة وبصمة ورخصة وصلاحيات واختبار واجهة. لا تحتوي الحزمة على كود الأطراف الثالثة أو نصوص مهاراتهم. لا تفترض أن أداة قديمة مثل CodeQL أو jscpd يجب حذفها إذا لم تكن ضمن القائمة الجديدة؛ ما يلائم مشروعًا قائمًا يبقى ويُراجع.

المراجع التقنية المحايدة مثل arc42/C4 ومعايير الأمان والإتاحة لا تصبح أصحاب تصميم متنافسين. عند استخدام نفس المصدر في أكثر من مجال، حمّل الإجراء المحدد أو نسخة مرجعية واحدة، لا تكرر الحزمة في كل نطاق.

## فهرس القدرات

- [اكتشاف المنتج والمنافسين وترتيب الاحتياجات](#product-discovery)

- [المواصفات والخطة والمهام](#process-specification)

- [اختيار التقنية والمعمارية وتصميم الحدود](#architecture-system)

- [فهم المشروع والخرائط والمعرفة المستمرة](#knowledge-mapping)

- [هوية الواجهة وتجربة الاستخدام ونظام التصميم](#ui-direction)

- [العربية وRTL وإتاحة الاستخدام](#ui-accessibility)

- [تنفيذ واجهة React وNext.js](#frontend-react)

- [تنفيذ Angular](#frontend-angular)

- [تنفيذ Vue](#frontend-vue)

- [الخادم في Laravel](#backend-laravel)

- [الخادم في ASP.NET Core و.NET](#backend-dotnet)

- [خادم Python](#backend-python)

- [خادم Node.js](#backend-node)

- [Android الأصلي](#mobile-android)

- [Flutter وDart](#mobile-flutter)

- [Expo وReact Native](#mobile-expo)

- [SwiftUI وiOS](#mobile-swiftui)

- [ويندوز وسطح المكتب](#desktop-windows)

- [بوتات تليجرام](#bots-telegram)

- [تصميم PostgreSQL وتحسينه](#data-postgres)

- [MongoDB](#data-mongodb)

- [SQLite أو MySQL](#data-local-relational)

- [تصميم API وعقوده](#api-contract)

- [المصادقة والتفويض والعزل](#auth-identity)

- [التخزين المؤقت والطلبات والطوابير](#backend-cache-jobs)

- [تخطيط منظومة الاختبارات](#testing-strategy)

- [تنفيذ اختبارات الويب](#testing-web)

- [اختبارات واجهات الهاتف وويندوز](#testing-native)

- [تكامل البيانات والخدمات](#testing-integration)

- [الحمل والتحمل وكفاءة الموارد](#testing-performance)

- [مراجعة الأمان](#security-review)

- [كشف الأسرار](#security-secrets)

- [النظافة والاعتماديات وحدود الوحدات](#quality-static)

- [التشغيل والبنية والتوزيع](#operations-deployment)

- [المراقبة والتكلفة والتعافي](#operations-observability)

- [الدفع والاشتراكات والعمليات التجارية](#business-payments)

- [ميزات الذكاء الاصطناعي وتقييم نَسَق](#ai-evaluation)

- [المحتوى والفهرسة للمواقع العامة](#public-web-discovery)



<a id="product-discovery"></a>

## اكتشاف المنتج والمنافسين وترتيب الاحتياجات

**مرشحو التوجيه/الملكية، بالشرط لا بترتيب عالمي:** [PM Skills — phuryn](https://github.com/phuryn/pm-skills) / [BMAD Method](https://github.com/bmad-code-org/BMAD-METHOD) / Nasaq core

**مراجع أو أدوات مكملة مشروطة:** [Context7](https://github.com/upstash/context7)

**قاعدة الاختيار:** ابدأ بإجراء PM محدد مع بحث فعلي؛ استخدم BMAD هنا فقط إذا اختير مزود العملية الأوسع؛ لا تنشئ PRD آخر مستقلًا

**المخرجات المطلوبة:** مشكلة وجمهور ورحلات ومميزات مرتبة ومقارنة موثقة وافتراضات

**التحقق:** المصادر بتاريخها؛ الميزة غير المرصودة مجهولة لا غائبة؛ عدم اختلاق مقابلات أو أرقام سوق



<a id="process-specification"></a>

## المواصفات والخطة والمهام

**مرشحو التوجيه/الملكية، بالشرط لا بترتيب عالمي:** [OpenSpec](https://github.com/Fission-AI/OpenSpec) / [GitHub Spec Kit](https://github.com/github/spec-kit) / [BMAD Method](https://github.com/bmad-code-org/BMAD-METHOD)

**مراجع أو أدوات مكملة مشروطة:** [Superpowers — selected procedures](https://github.com/obra/superpowers)

**قاعدة الاختيار:** احتفظ بالمناسب الموجود؛ OpenSpec للتغييرات المرنة وSpec Kit للعملية المنظمة وBMAD للعمل الأوسع؛ ترتيب حسب المشروع لا جديد/قديم فقط

**المخرجات المطلوبة:** مصدر مواصفات واحد ومعرفات وربط قرارات ومهام ومعايير قبول

**التحقق:** لا ملفان مرجعيان لنفس المتطلب؛ أوامر نَسَق فقط؛ لا تخطي الموافقة



<a id="architecture-system"></a>

## اختيار التقنية والمعمارية وتصميم الحدود

**مرشحو التوجيه/الملكية، بالشرط لا بترتيب عالمي:** Nasaq core

**مراجع أو أدوات مكملة مشروطة:** [arc42](https://arc42.org/overview/), [C4 model](https://c4model.com/), [Context7](https://github.com/upstash/context7)

**قاعدة الاختيار:** قيود المنتج أولًا ثم مقارنة 2–3 تقنيات وتجربة نقطة الخطر؛ الوثائق مدخل وليست منسقًا آخر

**المخرجات المطلوبة:** ADR ونموذج بيانات وحدود وحدات ومخطط نشر وتقدير موارد

**التحقق:** تبرير البنية وعدم فرض microservices أو استضافة مرتبطة بمهارة



<a id="knowledge-mapping"></a>

## فهم المشروع والخرائط والمعرفة المستمرة

**مرشحو التوجيه/الملكية، بالشرط لا بترتيب عالمي:** Nasaq core

**مراجع أو أدوات مكملة مشروطة:** [Serena](https://github.com/oraios/serena), [CodeBoarding](https://github.com/CodeBoarding/CodeBoarding), [Mermaid](https://github.com/mermaid-js/mermaid), [Repomix](https://github.com/yamadashy/repomix)

**قاعدة الاختيار:** ابدأ بفهرس وقراءة الكود ثم أضف استرجاع الرموز أو توليد الخرائط عند فائدة مثبتة؛ تصدير انتقائي فقط

**المخرجات المطلوبة:** خريطة مميزات ومكونات وبيانات ومسارات مهمة ومصدر كل استنتاج

**التحقق:** provenance وبصمة نسخة ومجهول واضح؛ تحديث الأثر فقط لا مسح شامل كل جلسة



<a id="ui-direction"></a>

## هوية الواجهة وتجربة الاستخدام ونظام التصميم

**مرشحو التوجيه/الملكية، بالشرط لا بترتيب عالمي:** [Impeccable](https://github.com/pbakaus/impeccable/blob/main/.agents/skills/impeccable/SKILL.md) / [Anthropic frontend-design](https://github.com/anthropics/skills/blob/main/skills/frontend-design/SKILL.md) / [UI UX Pro Max](https://github.com/nextlevelbuilder/ui-ux-pro-max-skill)

**مراجع أو أدوات مكملة مشروطة:** [Agency UI Finish-Gate Reviewer](https://github.com/msitarzewski/agency-agents/blob/main/design/design-ui-finish-gate-reviewer.md)

**قاعدة الاختيار:** لمشروع ويب بلا هوية: أميل لتجربة Impeccable أولًا؛ frontend-design أخف؛ UI UX Pro Max عندما يلزم بحث أنماط موسع؛ اختر مصممًا واحدًا

**المخرجات المطلوبة:** اتفاق تصميم ورحلات وشاشة ممثلة وtokens وألوان وخطوط وحالات

**التحقق:** مراجعة تصميم بعينة فعلية؛ احترام هوية موجودة؛ لا كتابة tokens من موجهين معًا



<a id="ui-accessibility"></a>

## العربية وRTL وإتاحة الاستخدام

**مرشحو التوجيه/الملكية، بالشرط لا بترتيب عالمي:** Nasaq core

**مراجع أو أدوات مكملة مشروطة:** [W3C WCAG](https://www.w3.org/WAI/standards-guidelines/wcag/), [axe-core](https://github.com/dequelabs/axe-core)

**قاعدة الاختيار:** المتطلبات قيود قبول لا ذوق منافس؛ استخدم إرشادات المنصة مع WCAG للويب

**المخرجات المطلوبة:** خريطة حالات RTL ونص مختلط وتكبير ولوحة مفاتيح وقارئ شاشة

**التحقق:** اختبار آلي وجولة يدوية؛ عدم الادعاء بامتثال شامل من scanner



<a id="frontend-react"></a>

## تنفيذ واجهة React وNext.js

**مرشحو التوجيه/الملكية، بالشرط لا بترتيب عالمي:** [Vercel React best practices](https://github.com/vercel-labs/agent-skills/blob/main/skills/react-best-practices/SKILL.md)

**مراجع أو أدوات مكملة مشروطة:** [Context7](https://github.com/upstash/context7), [Playwright CLI for agents](https://github.com/microsoft/playwright-cli)

**قاعدة الاختيار:** التقنية مختارة مسبقًا؛ هذه إرشادات تنفيذ وأداء لا مصدر ثان للألوان أو الهوية

**المخرجات المطلوبة:** مكونات وعقود بيانات وإدارة حالة وميزانية حزم وطلبات

**التحقق:** قياس waterfall وحجم الحزمة واختبارات الرحلات؛ قواعد تطابق النسخة



<a id="frontend-angular"></a>

## تنفيذ Angular

**مرشحو التوجيه/الملكية، بالشرط لا بترتيب عالمي:** [Angular official skills](https://angular.dev/ai/agent-skills)

**مراجع أو أدوات مكملة مشروطة:** [Context7](https://github.com/upstash/context7), [Playwright CLI for agents](https://github.com/microsoft/playwright-cli)

**قاعدة الاختيار:** أولوية لإرشادات Angular الرسمية المتوافقة مع إصدار المشروع

**المخرجات المطلوبة:** قواعد مكونات وحالة واختبارات وأداء حسب الإصدار

**التحقق:** عدم نقل افتراضات change detection بين إصدارات مختلفة دون تحقق



<a id="frontend-vue"></a>

## تنفيذ Vue

**مرشحو التوجيه/الملكية، بالشرط لا بترتيب عالمي:** Nasaq core / [Vue AI skills](https://github.com/vuejs-ai/skills) / [antfu skills — selected Vue procedures](https://github.com/antfu/skills)

**مراجع أو أدوات مكملة مشروطة:** [Context7](https://github.com/upstash/context7), [Playwright CLI for agents](https://github.com/microsoft/playwright-cli)

**قاعدة الاختيار:** الافتراضي مرجع Vue الرسمي عبر بحث مطابق للنسخة؛ المرشحان المجتمعيان للتجربة المحدودة لا رسميان

**المخرجات المطلوبة:** قواعد Vue وإدارة حالة وعقود ومكونات

**التحقق:** اختبر مهارة مجتمع قبل ترقيتها؛ لا تفرض مدير حزم أو conventions غير معتمدة



<a id="backend-laravel"></a>

## الخادم في Laravel

**مرشحو التوجيه/الملكية، بالشرط لا بترتيب عالمي:** [Laravel Boost](https://github.com/laravel/boost)

**مراجع أو أدوات مكملة مشروطة:** [Context7](https://github.com/upstash/context7), [Testcontainers](https://testcontainers.com/)

**قاعدة الاختيار:** اختر Boost إذا Laravel هو قرار المشروع؛ راجع اكتشافه وMCP والملفات التي ينشئها

**المخرجات المطلوبة:** وحدات وصلاحيات ومعاملات وjobs واختبارات وعقود

**التحقق:** لا تكرار تعليمات قاعدة البيانات ولا تشغيل migrations دون اعتماد



<a id="backend-dotnet"></a>

## الخادم في ASP.NET Core و.NET

**مرشحو التوجيه/الملكية، بالشرط لا بترتيب عالمي:** [dotnet/skills](https://github.com/dotnet/skills)

**مراجع أو أدوات مكملة مشروطة:** [Context7](https://github.com/upstash/context7), [Testcontainers](https://testcontainers.com/)

**قاعدة الاختيار:** حمّل إجراءات .NET الفعلية للـAPI والبيانات والأداء فقط

**المخرجات المطلوبة:** حدود وتفويض وتزامن واتصالات وأخطاء واختبارات

**التحقق:** مطابقة runtime؛ اختبارات تفويض وعزل ومعاملات وأداء



<a id="backend-python"></a>

## خادم Python

**مرشحو التوجيه/الملكية، بالشرط لا بترتيب عالمي:** [FastAPI official documentation](https://fastapi.tiangolo.com/deployment/concepts/) / [Django official documentation](https://docs.djangoproject.com/) / Nasaq core

**مراجع أو أدوات مكملة مشروطة:** [Context7](https://github.com/upstash/context7), [Testcontainers](https://testcontainers.com/)

**قاعدة الاختيار:** المنافسة بين تقنيات تحدد قبل المهارة؛ وثائق FastAPI لمشروعه وDjango لمشروعه؛ لا توجد هنا مهارة عامة مثبتة لكل Python

**المخرجات المطلوبة:** خطة workers وذاكرة واتصالات وتهيئة واختبارات وصلاحيات

**التحقق:** ميزانية عمليات وذاكرة؛ اختيار أدوات اللغة؛ لا قواعد Django على FastAPI



<a id="backend-node"></a>

## خادم Node.js

**مرشحو التوجيه/الملكية، بالشرط لا بترتيب عالمي:** [NestJS official documentation](https://docs.nestjs.com/) / Nasaq core

**مراجع أو أدوات مكملة مشروطة:** [Context7](https://github.com/upstash/context7), [Testcontainers](https://testcontainers.com/)

**قاعدة الاختيار:** استخدم NestJS فقط إذا كان اختيار المشروع؛ غيره يحتاج توثيق إطاره الرسمي بدل فرض Nest

**المخرجات المطلوبة:** عقود ووحدات وصلاحيات وتزامن وتحديد معدلات

**التحقق:** اختبار event loop والأخطاء والمهلات والتحميل الحقيقي



<a id="mobile-android"></a>

## Android الأصلي

**مرشحو التوجيه/الملكية، بالشرط لا بترتيب عالمي:** [Android official skills](https://github.com/android/skills)

**مراجع أو أدوات مكملة مشروطة:** [OWASP MASVS and MASTG](https://mas.owasp.org/), [Maestro](https://github.com/mobile-dev-inc/maestro)

**قاعدة الاختيار:** المهارات الرسمية للمناطق المتاحة مع وثائق Android/Compose وقياس native

**المخرجات المطلوبة:** تنقل وحالة وصلاحيات وتخزين وتزامن وخلفية وحجم حزمة

**التحقق:** أجهزة ممثلة وتشغيل بارد وذاكرة وطاقة وبيانات؛ ليست E2E وحدها قياس أداء



<a id="mobile-flutter"></a>

## Flutter وDart

**مرشحو التوجيه/الملكية، بالشرط لا بترتيب عالمي:** [Flutter and Dart official AI tools](https://docs.flutter.dev/ai/tools)

**مراجع أو أدوات مكملة مشروطة:** [Maestro](https://github.com/mobile-dev-inc/maestro), [Context7](https://github.com/upstash/context7)

**قاعدة الاختيار:** اختر مهارات Dart/Flutter الرسمية والأداة المناسبة للمضيف بعد قرار التقنية

**المخرجات المطلوبة:** بنية وحالة وإتاحة ومنصات واختبارات وprofiling

**التحقق:** النتائج على كل منصة مستهدفة؛ دعم plugin لا يثبت كل host



<a id="mobile-expo"></a>

## Expo وReact Native

**مرشحو التوجيه/الملكية، بالشرط لا بترتيب عالمي:** [Expo official skills](https://github.com/expo/skills)

**مراجع أو أدوات مكملة مشروطة:** [Maestro](https://github.com/mobile-dev-inc/maestro), [Context7](https://github.com/upstash/context7)

**قاعدة الاختيار:** إرشادات Expo الرسمية إن انطبقت نسخة المشروع ونمطه؛ لا تضف EAS إلا عند حاجة واعتماد

**المخرجات المطلوبة:** تنقل وأداء وتجميع وصلاحيات واختبارات وتحديثات

**التحقق:** لا اعتبار نجاح web preview نجاحًا على جهاز الهاتف



<a id="mobile-swiftui"></a>

## SwiftUI وiOS

**مرشحو التوجيه/الملكية، بالشرط لا بترتيب عالمي:** [SwiftUI Agent Skill — AvdLee](https://github.com/AvdLee/SwiftUI-Agent-Skill) / Nasaq core

**مراجع أو أدوات مكملة مشروطة:** [OWASP MASVS and MASTG](https://mas.owasp.org/), [Context7](https://github.com/upstash/context7)

**قاعدة الاختيار:** مرشح متخصص مجتمعي مع وثائق Apple الرسمية وSDK؛ النواة مع الوثائق عند عدم اعتماده

**المخرجات المطلوبة:** حالة وتنقل وتزامن وإتاحة وأداء وتوزيع

**التحقق:** اختبار على أدوات Apple فعلية؛ غير المتاح not_run



<a id="desktop-windows"></a>

## ويندوز وسطح المكتب

**مرشحو التوجيه/الملكية، بالشرط لا بترتيب عالمي:** [dotnet/skills](https://github.com/dotnet/skills) / Nasaq core

**مراجع أو أدوات مكملة مشروطة:** [FlaUI](https://github.com/FlaUI/FlaUI), [Context7](https://github.com/upstash/context7)

**قاعدة الاختيار:** اختر .NET skills للأطر المشمولة؛ WPF/WinUI/Tauri/Electron حسب تقنية المشروع ووثائقها لا بالاسم العام

**المخرجات المطلوبة:** نوافذ واختصارات وDPI وتثبيت وتحديث وملفات وعمليات طويلة

**التحقق:** اختبار أصلي على Windows؛ واجهة لا تتجمد؛ حساب موارد runtime والتثبيت



<a id="bots-telegram"></a>

## بوتات تليجرام

**مرشحو التوجيه/الملكية، بالشرط لا بترتيب عالمي:** [aiogram official documentation](https://docs.aiogram.dev/en/latest/dispatcher/long_polling.html) / [grammY official documentation](https://grammy.dev/advanced/deployment) / Nasaq core

**مراجع أو أدوات مكملة مشروطة:** [Context7](https://github.com/upstash/context7)

**قاعدة الاختيار:** إرشادات مكتبة البوت المختارة؛ لا تضف خدمات جانبية لمجرد اسم المهارة

**المخرجات المطلوبة:** تصميم محادثة وحالة وتحديثات وتكرار وحدود ومهلات وطابور

**التحقق:** مضاعفات API للاختبار؛ لا ضغط على Telegram؛ منع آثار مزدوجة



<a id="data-postgres"></a>

## تصميم PostgreSQL وتحسينه

**مرشحو التوجيه/الملكية، بالشرط لا بترتيب عالمي:** [Supabase Postgres best practices](https://github.com/supabase/agent-skills/blob/main/skills/supabase-postgres-best-practices/SKILL.md)

**مراجع أو أدوات مكملة مشروطة:** [Context7](https://github.com/upstash/context7), [Testcontainers](https://testcontainers.com/)

**قاعدة الاختيار:** مهارة Supabase الرسمية لإرشادات Postgres مع وثائق النسخة؛ لا يلزم Supabase hosting

**المخرجات المطلوبة:** كيانات وقيود وفهارس وأمان صفوف وخطة ترحيل واستعادة

**التحقق:** EXPLAIN حسب الحالة لا قاعدة scan جيد/سيئ مطلقة؛ اختبارات معاملات وعزل



<a id="data-mongodb"></a>

## MongoDB

**مرشحو التوجيه/الملكية، بالشرط لا بترتيب عالمي:** [MongoDB official agent skills](https://github.com/mongodb/agent-skills)

**مراجع أو أدوات مكملة مشروطة:** [Context7](https://github.com/upstash/context7), [Testcontainers](https://testcontainers.com/)

**قاعدة الاختيار:** عند اختيار نموذج مستندات مناسب؛ المهارة لا تقرر ضرورة MongoDB

**المخرجات المطلوبة:** نمط وصول ومخطط مستند وفهارس وحدود أحجام واتساق

**التحقق:** اختبارات الاستعلامات والقيود والمهاجرة؛ لا Atlas إجباري



<a id="data-local-relational"></a>

## SQLite أو MySQL

**مرشحو التوجيه/الملكية، بالشرط لا بترتيب عالمي:** [SQLite official documentation](https://sqlite.org/docs.html) / [MySQL official documentation](https://dev.mysql.com/doc/) / Nasaq core

**مراجع أو أدوات مكملة مشروطة:** [Context7](https://github.com/upstash/context7)

**قاعدة الاختيار:** اختَر توثيق المحرك الفعلي؛ ليسا بديلين متساويين لكل مشروع؛ دون مهارة عامة مخترعة

**المخرجات المطلوبة:** نموذج ومعاملات وترحيل ونسخ واستعادة ومزامنة عند الحاجة

**التحقق:** اختبارات التزامن والأقفال وفقد الاتصال وسلامة البيانات



<a id="api-contract"></a>

## تصميم API وعقوده

**مرشحو التوجيه/الملكية، بالشرط لا بترتيب عالمي:** Nasaq core

**مراجع أو أدوات مكملة مشروطة:** [Spectral](https://github.com/stoplightio/spectral), [Schemathesis](https://github.com/schemathesis/schemathesis)

**قاعدة الاختيار:** حدد مالك OpenAPI/AsyncAPI ومصدر توليده ثم تحقق static وruntime؛ المهارات التنفيذية تتبع العقد

**المخرجات المطلوبة:** أخطاء وصلاحيات وإصدارات وتقسيم وidempotency وإلغاء وwebhooks

**التحقق:** اختبارات عقد وتوافق وتفويض وحالات سلبية؛ المخطط وحده لا يثبت منطق العمل



<a id="auth-identity"></a>

## المصادقة والتفويض والعزل

**مرشحو التوجيه/الملكية، بالشرط لا بترتيب عالمي:** Nasaq core / [Better Auth best practices](https://github.com/better-auth/skills/blob/main/better-auth/best-practices/SKILL.md)

**مراجع أو أدوات مكملة مشروطة:** [OWASP ASVS](https://owasp.org/projects/asvs), [OWASP MASVS and MASTG](https://mas.owasp.org/)

**قاعدة الاختيار:** اختر حل الهوية حسب المخاطر والمنصة ثم فعّل مرجع المزود؛ Better Auth لمنتج اختاره بالفعل

**المخرجات المطلوبة:** مصفوفة صلاحيات وجلسات واسترجاع حساب وtenant isolation

**التحقق:** اختبار الرفض والانتهاء والإلغاء والتسريب؛ لا تفويض على الواجهة فقط



<a id="backend-cache-jobs"></a>

## التخزين المؤقت والطلبات والطوابير

**مرشحو التوجيه/الملكية، بالشرط لا بترتيب عالمي:** [Redis official agent skills](https://github.com/redis/agent-skills) / Nasaq core

**مراجع أو أدوات مكملة مشروطة:** [Context7](https://github.com/upstash/context7)

**قاعدة الاختيار:** أضف Redis عند دليل احتياج؛ وإلا مرجع runtime/queue الفعلي؛ هذه القدرة لا تتطلب Redis

**المخرجات المطلوبة:** cache invalidation وTTL وbackpressure وتحديد التوازي وDLQ

**التحقق:** اختبار retry storms وتكرار الرسائل وlimits؛ لا cache لمعلومات حساسة بلا عزل



<a id="testing-strategy"></a>

## تخطيط منظومة الاختبارات

**مرشحو التوجيه/الملكية، بالشرط لا بترتيب عالمي:** Nasaq core / [BMAD Test Engineering Architect](https://github.com/bmad-code-org/bmad-method-test-architecture-enterprise)

**مراجع أو أدوات مكملة مشروطة:** [Superpowers — selected procedures](https://github.com/obra/superpowers)

**قاعدة الاختيار:** الخفيف بالخطة القائمة؛ TEA مرشح deep للمخاطر والتتبع عندما يضيف قيمة؛ مصدر خطة اختبار واحد

**المخرجات المطلوبة:** متطلب إلى اختبار وأولوية وبيئة وبيانات ودليل وحدود

**التحقق:** اختبارات نجاح وفشل وتوصيف وproperty/fuzz/mutation عند الحاجة؛ رفض التغطية الشكلية



<a id="testing-web"></a>

## تنفيذ اختبارات الويب

**مرشحو التوجيه/الملكية، بالشرط لا بترتيب عالمي:** [Playwright test agents](https://playwright.dev/docs/test-agents) / Nasaq core

**مراجع أو أدوات مكملة مشروطة:** [Playwright CLI for agents](https://github.com/microsoft/playwright-cli), [axe-core](https://github.com/dequelabs/axe-core)

**قاعدة الاختيار:** أدوار Playwright planner/generator/healer تتبع الخطة المعتمدة ولا تعيد تعريف النجاح

**المخرجات المطلوبة:** حالات E2E وبصرية وإتاحة وfixtures معزولة

**التحقق:** التخطي أو إعادة كتابة assertions ليس نجاحًا؛ reviewer يوافق على snapshot الجديد



<a id="testing-native"></a>

## اختبارات واجهات الهاتف وويندوز

**مرشحو التوجيه/الملكية، بالشرط لا بترتيب عالمي:** Nasaq core

**مراجع أو أدوات مكملة مشروطة:** [Maestro](https://github.com/mobile-dev-inc/maestro), [FlaUI](https://github.com/FlaUI/FlaUI)

**قاعدة الاختيار:** اختر أداة المنصة المناسبة واختبارات الإطار الأصلية؛ الأداة لا تنشئ اعتماد إنتاج

**المخرجات المطلوبة:** رحلات أصلية واختبارات جهاز وتثبيت وترقية وإزالة

**التحقق:** سجل الأجهزة وOS والبناء؛ لا تحوّل عدم توفر البيئة إلى pass



<a id="testing-integration"></a>

## تكامل البيانات والخدمات

**مرشحو التوجيه/الملكية، بالشرط لا بترتيب عالمي:** Nasaq core

**مراجع أو أدوات مكملة مشروطة:** [Testcontainers](https://testcontainers.com/), [Schemathesis](https://github.com/schemathesis/schemathesis)

**قاعدة الاختيار:** اختبارات اللغة مع تبعيات فعلية معزولة حيث يتاح runtime حاويات

**المخرجات المطلوبة:** بيانات اختبار ومهاجرات وعقود وفشل خدمات

**التحقق:** عدم ربط الاختبارات بقاعدة إنتاج أو اعتماد نتيجة mock كتكامل حقيقي



<a id="testing-performance"></a>

## الحمل والتحمل وكفاءة الموارد

**مرشحو التوجيه/الملكية، بالشرط لا بترتيب عالمي:** [Grafana k6 skill](https://github.com/grafana/skills/blob/main/skills/grafana-k6/k6/SKILL.md) / Nasaq core

**مراجع أو أدوات مكملة مشروطة:** [Web Vitals official reference](https://web.dev/articles/vitals)

**قاعدة الاختيار:** Grafana k6 لخطة الحمل التي يناسبها؛ قياسات native لكل منصة؛ لا تفرض أداة واحدة لكل نوع قياس

**المخرجات المطلوبة:** أهداف p95 وطلب/ث وbytes/action وCPU/RAM وبيئة وحدود توقف

**التحقق:** حمل وطفرة واستمرار وتعافي وسلامة بيانات؛ ذكر ما قيس لا ادعاء مستخدمين مطلق



<a id="security-review"></a>

## مراجعة الأمان

**مرشحو التوجيه/الملكية، بالشرط لا بترتيب عالمي:** [Trail of Bits selected security skills](https://github.com/trailofbits/skills) / Nasaq core

**مراجع أو أدوات مكملة مشروطة:** [Semgrep](https://github.com/semgrep/semgrep), [OSV-Scanner](https://github.com/google/osv-scanner), [ZAP](https://www.zaproxy.org/), [OWASP ASVS](https://owasp.org/projects/asvs), [OWASP MASVS and MASTG](https://mas.owasp.org/)

**قاعدة الاختيار:** إجراء Trail of Bits مطابق للمرحلة ثم أدوات متكاملة للتغطية؛ لا bootstrap شامل

**المخرجات المطلوبة:** نموذج تهديد وفروق ومخاطر وأدلة وتوصيات

**التحقق:** تفويض واختبارات سلبية؛ لا تشغيل DAST على المنافسين؛ لا ضمان صفر ثغرات



<a id="security-secrets"></a>

## كشف الأسرار

**مرشحو التوجيه/الملكية، بالشرط لا بترتيب عالمي:** Nasaq core

**مراجع أو أدوات مكملة مشروطة:** [Gitleaks](https://github.com/gitleaks/gitleaks), [Betterleaks](https://github.com/betterleaks/betterleaks), [TruffleHog](https://github.com/trufflesecurity/trufflehog)

**قاعدة الاختيار:** احتفظ بـGitleaks إن مناسب؛ قيّم Betterleaks لتغيير جديد؛ TruffleHog للمصادر والتحقق المتقدم بعد إذن

**المخرجات المطلوبة:** تقرير منقح ومسار إصلاح وتدوير أسرار عند الانكشاف

**التحقق:** اختبار corpus آمن؛ التحقق الحي من secret ممنوع دون اعتماد؛ لا طباعة السر



<a id="quality-static"></a>

## النظافة والاعتماديات وحدود الوحدات

**مرشحو التوجيه/الملكية، بالشرط لا بترتيب عالمي:** Nasaq core

**مراجع أو أدوات مكملة مشروطة:** [Knip](https://github.com/webpro-nl/knip), [dependency-cruiser](https://github.com/sverweij/dependency-cruiser), [Renovate](https://github.com/renovatebot/renovate)

**قاعدة الاختيار:**  أدوات اللغة الفعلية؛ مدقق تنسيق واحد لكل نطاق وقواعد مشتركة مع CI

**المخرجات المطلوبة:** ميزانية دين تقني وbaseline وحدود معمارية ومرشحات حذف

**التحقق:** لا حذف ديناميكي بلا دليل؛ لا duplicate formatters متعارضين؛ لا إخفاء تحذير لتنجح البوابة



<a id="operations-deployment"></a>

## التشغيل والبنية والتوزيع

**مرشحو التوجيه/الملكية، بالشرط لا بترتيب عالمي:** Nasaq core / [HashiCorp agent skills](https://github.com/hashicorp/agent-skills) / [Cloudflare official skills](https://github.com/cloudflare/skills)

**مراجع أو أدوات مكملة مشروطة:** [Renovate](https://github.com/renovatebot/renovate)

**قاعدة الاختيار:** مزود التشغيل يختار بعد قرار البيئة؛ مهارات HashiCorp أو Cloudflare لا تختار البيئة لنفسها

**المخرجات المطلوبة:** خطة بيئات وأسرار وCI ونشر وترحيل وrollback وتوقيع

**التحقق:** اختبار تثبيت وترقية واستعادة ومراقبة؛ فصل plan عن apply وإنتاج عن staging



<a id="operations-observability"></a>

## المراقبة والتكلفة والتعافي

**مرشحو التوجيه/الملكية، بالشرط لا بترتيب عالمي:** Nasaq core

**مراجع أو أدوات مكملة مشروطة:** [OpenTelemetry](https://opentelemetry.io/docs/)

**قاعدة الاختيار:** OpenTelemetry مدخل instrumentation؛ اختر backend دون فرض خدمة إضافية

**المخرجات المطلوبة:** SLO ومقاييس وتنبيهات واحتفاظ وعينات وخطة حوادث

**التحقق:** اختبر وصول الإشارة والإنذار واسترجاع نسخة؛ راقب كلفة البيانات وحمايتها



<a id="business-payments"></a>

## الدفع والاشتراكات والعمليات التجارية

**مرشحو التوجيه/الملكية، بالشرط لا بترتيب عالمي:** Nasaq core / [Stripe AI skills](https://github.com/stripe/ai)

**مراجع أو أدوات مكملة مشروطة:** [OWASP ASVS](https://owasp.org/projects/asvs)

**قاعدة الاختيار:** مرجع مزود الدفع المختار؛ Stripe مشروط بتوفر الخدمة والبلد والقرار؛ بقية المزودين بحث رسمي

**المخرجات المطلوبة:** webhook وتوقيع وidempotency وتسوية واسترداد وحساب نقدي سليم

**التحقق:** sandbox وسيناريوهات تكرار/فشل/تسوية؛ لا مدفوعات حقيقية دون إذن



<a id="ai-evaluation"></a>

## ميزات الذكاء الاصطناعي وتقييم نَسَق

**مرشحو التوجيه/الملكية، بالشرط لا بترتيب عالمي:** Nasaq core

**مراجع أو أدوات مكملة مشروطة:** [Promptfoo](https://github.com/promptfoo/promptfoo)

**قاعدة الاختيار:** فعّل فقط عند وجود نموذج/استرجاع/وكيل أو تقييم النواة؛ الأدلة قبل ترقية المزود

**المخرجات المطلوبة:** مجموعة حالات وعينات ومعايير جودة وحقن تعليمات وتكلفة

**التحقق:** مقارنة نفس المهمة والموديل والميزانية؛ فصل تقييم حتمي عن حكم LLM



<a id="public-web-discovery"></a>

## المحتوى والفهرسة للمواقع العامة

**مرشحو التوجيه/الملكية، بالشرط لا بترتيب عالمي:** Nasaq core

**مراجع أو أدوات مكملة مشروطة:** [Google Search Central](https://developers.google.com/search/docs/fundamentals/seo-starter-guide), [Web Vitals official reference](https://web.dev/articles/vitals)

**قاعدة الاختيار:** للموقع العام الذي يحتاج اكتشافًا؛ لا تجبر تطبيقًا داخليًا على SEO أو تحليلات تسويقية

**المخرجات المطلوبة:** معلومات صفحات ولغات وروابط وcanonical وخصوصية القياس

**التحقق:** لا فهرسة صفحات حساسة؛ لا وعود بترتيب البحث؛ اختبر الأداء وإتاحة المحتوى



## سجل المصادر وحدودها

روابط المصادر التالية مباشرة إلى المستودعات أو الوثائق الأصلية. `selected_entrypoints` يعني قراءة مدخل محدد مع الوثائق، و`primary_docs` يعني مراجعة وثائق المصدر لا تدقيق كامل لشفرة المستودع. جميع الترشيحات الخارجية غير مثبتة وغير مختبرة داخل نَسَق في هذا التسليم. `local_instructions` يخص تعليمات نَسَق الأصلية فقط. رخصة الاستخدام أو النسخ والتكييف تُراجع على النسخة المراد دمجها؛ الحقول المتروكة غير محسومة متعمدة وليست إذنًا بالتثبيت.



### `nasaq-core` - Nasaq core

التنسيق والأوامر والعقود ومعايير القبول وحفظ الحالة، وليس بديلًا مزعومًا لكل تخصص

**حدود وحذر:** الجزء الإرشادي يعمل بواسطة الوكيل المضيف؛ التكاملات الآلية الكاملة ما زالت تكليف بناء

**مستوى المراجعة:**  `local_instructions`; `benchmark: not_run`; `integration: catalog_only`.



### `pm-skills` - [PM Skills — phuryn](https://github.com/phuryn/pm-skills)

اكتشاف المشكلة وتحليل المنافسين والمتطلبات؛ اختر إجراءً محددًا لا المكتبة كاملة

**حدود وحذر:** مصدر مجتمعي؛ ادعم الاستنتاجات بأبحاث فعلية ولا تختلق سوقًا أو مقابلات؛ بعض الأوامر تخص مضيفًا معينًا

**مستوى المراجعة:**  `selected_entrypoints`; `benchmark: not_run`; `integration: catalog_only`.



### `spec-kit` - [GitHub Spec Kit](https://github.com/github/spec-kit)

مزود مواصفات وخطط ومهام وتحقق لعملية منظمة قابلة للتخصيص

**حدود وحذر:** بديل لـOpenSpec وBMAD على نفس التغيير؛ لا تخلط أوامر المحادثة والطرفية

**مستوى المراجعة:**  `primary_docs`; `benchmark: not_run`; `integration: catalog_only`.



### `openspec` - [OpenSpec](https://github.com/Fission-AI/OpenSpec)

مواصفات وتغييرات وتصميم ومهام مرتبطة بالمشروع

**حدود وحذر:** اختره لمرونة التغييرات واستمرار المعرفة؛ لا تحوله إلى مزود ثان لنفس المواصفات

**مستوى المراجعة:**  `primary_docs`; `benchmark: not_run`; `integration: catalog_only`.



### `bmad` - [BMAD Method](https://github.com/bmad-code-org/BMAD-METHOD)

مسار أوسع لاكتشاف المنتج والتخطيط والأدوار عند الحاجة

**حدود وحذر:** أثقل من سير عمل صغير؛ لا تثبت كل الوحدات ولا تشغله منسقًا منافسًا لنَسَق

**مستوى المراجعة:**  `primary_docs`; `benchmark: not_run`; `integration: catalog_only`.



### `superpowers` - [Superpowers — selected procedures](https://github.com/obra/superpowers)

إجراءات محددة للتخطيط المصغر وTDD وتصحيح الأخطاء والتحقق

**حدود وحذر:** افحص تعليمات التفعيل وhooks؛ تجنب استيراد bootstrap شامل يغير مدير العملية

**مستوى المراجعة:**  `primary_docs`; `benchmark: not_run`; `integration: catalog_only`.



### `arc42` - [arc42](https://arc42.org/overview/)

تنظيم وصف المعمارية والقيود وقراراتها ومخاطرها

**حدود وحذر:** مرجع توثيق لا محرك بناء؛ حجم التوثيق حسب المشروع؛ راجع ترخيص أي نص يُنسخ

**مستوى المراجعة:**  `primary_docs`; `benchmark: not_run`; `integration: catalog_only`.



### `c4` - [C4 model](https://c4model.com/)

مستويات خرائط السياق والمكونات والتشغيل والنشر

**حدود وحذر:** الخرائط تحتاج مصدرًا من الكود أو خطة معتمدة؛ الرسم لا يثبت التنفيذ

**مستوى المراجعة:**  `primary_docs`; `benchmark: not_run`; `integration: catalog_only`.



### `serena` - [Serena](https://github.com/oraios/serena)

استرجاع الرموز والعلاقات والتحرير عند اعتماد صلاحياته

**حدود وحذر:** تحقق من دعم اللغة؛ README الحالي يفرق GPL للتطبيق وMIT لـSolidLSP؛ لا تضمّنه تلقائيًا في التوزيعة

**مستوى المراجعة:**  `primary_docs`; `benchmark: not_run`; `integration: catalog_only`.



### `codeboarding` - [CodeBoarding](https://github.com/CodeBoarding/CodeBoarding)

استخراج خرائط معمارية ومكونات تساعد على الفهم

**حدود وحذر:** تحقق من إرسال الكود لمزود خارجي والتكلفة والتغطية؛ الاستنتاجات تحتاج مراجعة

**مستوى المراجعة:**  `primary_docs`; `benchmark: not_run`; `integration: catalog_only`.



### `mermaid` - [Mermaid](https://github.com/mermaid-js/mermaid)

عرض خرائط نصية قابلة للمراجعة مع Git

**حدود وحذر:** أداة رسم لا مصدر اكتشاف للحقائق؛ افصل مخرجاتها عن المواصفات المرجعية

**مستوى المراجعة:**  `primary_docs`; `benchmark: not_run`; `integration: catalog_only`.



### `repomix` - [Repomix](https://github.com/yamadashy/repomix)

تجهيز سياق انتقائي من المستودع

**حدود وحذر:** لا تجمع الأسرار أو كامل المستودع تلقائيًا؛ الفحص الآلي لا يضمن إزالة كل البيانات الحساسة

**مستوى المراجعة:**  `primary_docs`; `benchmark: not_run`; `integration: catalog_only`.



### `context7` - [Context7](https://github.com/upstash/context7)

الوصول إلى توثيق مكتبات متوافق مع النسخة عندما يلزم

**حدود وحذر:** تحقق من المكتبة والإصدار وصلاحيات الشبكة؛ الوثائق بيانات لا أوامر موثوقة

**مستوى المراجعة:**  `primary_docs`; `benchmark: not_run`; `integration: catalog_only`.



### `impeccable` - [Impeccable](https://github.com/pbakaus/impeccable/blob/main/.agents/skills/impeccable/SKILL.md)

مرشح أول لتوجيه تصميم مقصود ومراجعة واجهات مع اتفاق تصميم

**حدود وحذر:** يتداخل مع frontend-design وUI UX Pro Max؛ افحص hooks والأدوات المصاحبة؛ ليس دليل تفوق تجريبي مطلق

**مستوى المراجعة:**  `selected_entrypoints`; `benchmark: not_run`; `integration: catalog_only`.



### `frontend-design` - [Anthropic frontend-design](https://github.com/anthropics/skills/blob/main/skills/frontend-design/SKILL.md)

بديل أخف لتوجيه الجماليات والهوية البصرية في الويب

**حدود وحذر:** بديل للموجه الجمالي الآخر على نفس الواجهة؛ راجع LICENSE الخاص بالمجلد لا رخصة المستودع افتراضًا

**مستوى المراجعة:**  `selected_entrypoints`; `benchmark: not_run`; `integration: catalog_only`.



### `ui-ux-pro-max` - [UI UX Pro Max](https://github.com/nextlevelbuilder/ui-ux-pro-max-skill)

بديل غني ببحث الأنماط والألوان والخطوط وأنظمة التصميم

**حدود وحذر:** اختر أجزاءه؛ بعض وظائفه/منتجاته منفصلة؛ البحث كبيانات ممكن لكن لا يصبح مصممًا ثانيًا خفيًا

**مستوى المراجعة:**  `selected_entrypoints`; `benchmark: not_run`; `integration: catalog_only`.



### `agency-ui-review` - [Agency UI Finish-Gate Reviewer](https://github.com/msitarzewski/agency-agents/blob/main/design/design-ui-finish-gate-reviewer.md)

مراجعة الواجهة مقابل اتفاق التصميم المعتمد

**حدود وحذر:** اختياري فقط عند فجوة مراجعة؛ قراءة وإصدار ملاحظات بلا تغيير الذوق أو الرموز تلقائيًا

**مستوى المراجعة:**  `selected_entrypoints`; `benchmark: not_run`; `integration: catalog_only`.



### `wcag` - [W3C WCAG](https://www.w3.org/WAI/standards-guidelines/wcag/)

مرجع متطلبات إتاحة الاستخدام

**حدود وحذر:** ليس Scanner ولا شهادة امتثال؛ يلزم فحص يدوي ومراعاة متطلبات المنصة

**مستوى المراجعة:**  `primary_docs`; `benchmark: not_run`; `integration: catalog_only`.



### `axe` - [axe-core](https://github.com/dequelabs/axe-core)

فحوصات آلية لإتاحة الواجهات

**حدود وحذر:** لا تغطي كل المتطلبات؛ لا تعادل اختبار قارئ الشاشة والتفاعل اليدوي

**مستوى المراجعة:**  `primary_docs`; `benchmark: not_run`; `integration: catalog_only`.



### `vercel-react` - [Vercel React best practices](https://github.com/vercel-labs/agent-skills/blob/main/skills/react-best-practices/SKILL.md)

تحسين بنية وأداء React وNext.js وتقليل تسلسل الطلبات والحزم

**حدود وحذر:** لا يختار الهوية البصرية؛ طبّق قواعد النسخة والسياق فقط؛ لا تفعّل نشر Vercel ضمنيًا

**مستوى المراجعة:**  `selected_entrypoints`; `benchmark: not_run`; `integration: catalog_only`.



### `angular` - [Angular official skills](https://angular.dev/ai/agent-skills)

إرشادات تطوير Angular المطابقة للإصدار

**حدود وحذر:** لا تنقل قواعد إصدار حديث إلى مشروع أقدم؛ لا تستخدمها في React أو Vue

**مستوى المراجعة:**  `primary_docs`; `benchmark: not_run`; `integration: catalog_only`.



### `vue-community` - [Vue AI skills](https://github.com/vuejs-ai/skills)

بديل تجريبي متخصص في Vue

**حدود وحذر:** المصدر يصف نفسه مشروعًا مجتمعيًا مبكرًا وليس رسميًا؛ راجع كل قاعدة مع توثيق Vue

**مستوى المراجعة:**  `primary_docs`; `benchmark: not_run`; `integration: catalog_only`.



### `antfu-vue` - [antfu skills — selected Vue procedures](https://github.com/antfu/skills)

بديل مجتمعي انتقائي لعمل Vue ومنظومته

**حدود وحذر:** ليس معيار Vue رسميًا؛ افصل آراء مدير الحزم والتنسيق عن قواعد المشروع

**مستوى المراجعة:**  `primary_docs`; `benchmark: not_run`; `integration: catalog_only`.



### `laravel-boost` - [Laravel Boost](https://github.com/laravel/boost)

إرشادات Laravel وسياق الحزم وتوثيقها وإجراءات متخصصة

**حدود وحذر:** قد يضيف MCP وتعليمات اكتشاف؛ راجع الآثار ولا تكرر توجيهات متضاربة

**مستوى المراجعة:**  `primary_docs`; `benchmark: not_run`; `integration: catalog_only`.



### `dotnet` - [dotnet/skills](https://github.com/dotnet/skills)

مهارات .NET الرسمية للبيانات والأداء والاختبارات والويب وواجهات مدعومة

**حدود وحذر:** اختر مهارة الإطار الفعلي؛ وجود WinForms أو MAUI لا يثبت تغطية WPF أو WinUI بالكامل

**مستوى المراجعة:**  `primary_docs`; `benchmark: not_run`; `integration: catalog_only`.



### `fastapi-docs` - [FastAPI official documentation](https://fastapi.tiangolo.com/deployment/concepts/)

مرجع FastAPI للتشغيل والموارد والتزامن وعمليات التهيئة

**حدود وحذر:** لا توجد في هذا البحث مهارة عامة مثبتة تتفوق على المرجع؛ لا تعِد بعدد workers ثابت

**مستوى المراجعة:**  `primary_docs`; `benchmark: not_run`; `integration: catalog_only`.



### `django-docs` - [Django official documentation](https://docs.djangoproject.com/)

مرجع Django الرسمي وفق نسخة المشروع

**حدود وحذر:** اختر نسخة التوثيق من lockfile ولا تفترض أن latest مناسب

**مستوى المراجعة:**  `primary_docs`; `benchmark: not_run`; `integration: catalog_only`.



### `nestjs-docs` - [NestJS official documentation](https://docs.nestjs.com/)

مرجع NestJS لوحدات الخادم والعقود والاختبارات

**حدود وحذر:** مرجع تقني لا اختيار تلقائي للمنصة؛ لا تفرض NestJS على كل Backend

**مستوى المراجعة:**  `primary_docs`; `benchmark: not_run`; `integration: catalog_only`.



### `android` - [Android official skills](https://github.com/android/skills)

مهارات Android الرسمية في مجالات محددة مثل الأداء والاختبار والأمان والتحسين

**حدود وحذر:** ليست تغطية تلقائية لكل Android؛ اربطها بإصدار SDK والأجهزة وإرشادات المنصة

**مستوى المراجعة:**  `primary_docs`; `benchmark: not_run`; `integration: catalog_only`.



### `flutter` - [Flutter and Dart official AI tools](https://docs.flutter.dev/ai/tools)

مهارات وإضافات Flutter وDart والأدوات الرسمية ذات الصلة

**حدود وحذر:** اختر plugin أو MCP المناسب للمضيف؛ بعض الميزات خاصة بأداة معينة؛ لا تثبت الكل

**مستوى المراجعة:**  `primary_docs`; `benchmark: not_run`; `integration: catalog_only`.



### `expo` - [Expo official skills](https://github.com/expo/skills)

إرشادات بناء وتحديث Expo وReact Native

**حدود وحذر:** راجع التوافق مع مشروع bare React Native؛ لا تضف حساب EAS أو نشرًا مدفوعًا تلقائيًا

**مستوى المراجعة:**  `primary_docs`; `benchmark: not_run`; `integration: catalog_only`.



### `swiftui` - [SwiftUI Agent Skill — AvdLee](https://github.com/AvdLee/SwiftUI-Agent-Skill)

مرشح مجتمعي متخصص لحالة SwiftUI وبنيته وأدائه

**حدود وحذر:** ليس مهارة رسمية من Apple؛ يجب تحقق SDK واختبارات على أدوات Apple فعلية

**مستوى المراجعة:**  `primary_docs`; `benchmark: not_run`; `integration: catalog_only`.



### `aiogram-docs` - [aiogram official documentation](https://docs.aiogram.dev/en/latest/dispatcher/long_polling.html)

إرشادات بوتات Python وإدارة التحديثات والتشغيل

**حدود وحذر:** قاعدة عملية polling واحدة لكل token هنا خاصة بالمنظومة؛ لا تضغط على Telegram لاختبار خادمك

**مستوى المراجعة:**  `primary_docs`; `benchmark: not_run`; `integration: catalog_only`.



### `grammy-docs` - [grammY official documentation](https://grammy.dev/advanced/deployment)

بوتات TypeScript والتوازي والتشغيل والwebhooks

**حدود وحذر:** راجع القيد على الجلسات والتكرار والمهلات؛ لا تفترض أن webhook أفضل دائمًا

**مستوى المراجعة:**  `primary_docs`; `benchmark: not_run`; `integration: catalog_only`.



### `postgres` - [Supabase Postgres best practices](https://github.com/supabase/agent-skills/blob/main/skills/supabase-postgres-best-practices/SKILL.md)

تخطيط PostgreSQL واستعلاماته وفهارسه وأمانه وقواعده

**حدود وحذر:** يصلح للإرشاد حول Postgres دون فرض استضافة Supabase؛ تحقق من الإصدار والقياس الفعلي

**مستوى المراجعة:**  `selected_entrypoints`; `benchmark: not_run`; `integration: catalog_only`.



### `mongodb` - [MongoDB official agent skills](https://github.com/mongodb/agent-skills)

تصميم بيانات MongoDB واستعلاماتها وتحسينها

**حدود وحذر:** لا تضف Atlas أو MCP cloud ضمنيًا؛ مرجع فقط إن لم تختر MongoDB

**مستوى المراجعة:**  `primary_docs`; `benchmark: not_run`; `integration: catalog_only`.



### `redis` - [Redis official agent skills](https://github.com/redis/agent-skills)

TTL والذاكرة والاتصالات والعمليات عند وجود حاجة لـRedis

**حدود وحذر:** لا يقرر هذا المرجع ضرورة إضافة Redis؛ رخصة المهارة تختلف عن المنتج أو الخدمة

**مستوى المراجعة:**  `primary_docs`; `benchmark: not_run`; `integration: catalog_only`.



### `sqlite-docs` - [SQLite official documentation](https://sqlite.org/docs.html)

التخزين المحلي والمعاملات والتزامن وفق SQLite

**حدود وحذر:** قاعدة محلية لا تعني تعافيًا أو مزامنة تلقائيين؛ صمم conflict resolution عند الحاجة

**مستوى المراجعة:**  `primary_docs`; `benchmark: not_run`; `integration: catalog_only`.



### `mysql-docs` - [MySQL official documentation](https://dev.mysql.com/doc/)

المعاملات والفهارس والنسخ والتخطيط وفق نسخة MySQL

**حدود وحذر:** لا تطبق قواعد Postgres أو أرقام فهارس عمياء عليها

**مستوى المراجعة:**  `primary_docs`; `benchmark: not_run`; `integration: catalog_only`.



### `spectral` - [Spectral](https://github.com/stoplightio/spectral)

تحقق آلي من قواعد عقود API واتساقها

**حدود وحذر:** لا يثبت أمان التفويض أو سلوك التنفيذ؛ صاحب عقد واحد يملك تعديله

**مستوى المراجعة:**  `primary_docs`; `benchmark: not_run`; `integration: catalog_only`.



### `schemathesis` - [Schemathesis](https://github.com/schemathesis/schemathesis)

اختبارات مشتقة من مخطط API وحالات حدودية وتسلسلية

**حدود وحذر:** لا يغطي منطق العمل أو كل حالات الصلاحيات من المخطط وحده؛ استهدف بيئة مأذونة

**مستوى المراجعة:**  `primary_docs`; `benchmark: not_run`; `integration: catalog_only`.



### `better-auth` - [Better Auth best practices](https://github.com/better-auth/skills/blob/main/better-auth/best-practices/SKILL.md)

إرشادات تنفيذ المصادقة عند اختيار Better Auth مسبقًا

**حدود وحذر:** لا يختار مزود الهوية عن المشروع؛ لا تنفذ migrations أو @latest دون مراجعة

**مستوى المراجعة:**  `selected_entrypoints`; `benchmark: not_run`; `integration: catalog_only`.



### `tea` - [BMAD Test Engineering Architect](https://github.com/bmad-code-org/bmad-method-test-architecture-enterprise)

استراتيجية اختبار قائمة على المخاطر والتتبع والقرار للمشاريع المعقدة

**حدود وحذر:** اختياري كمالك خطة الاختبار فقط؛ لا تضف دورة BMAD كاملة أو خطة اختبار مرجعية ثانية

**مستوى المراجعة:**  `primary_docs`; `benchmark: not_run`; `integration: catalog_only`.



### `playwright-agents` - [Playwright test agents](https://playwright.dev/docs/test-agents)

تخطيط اختبارات الويب وتوليدها والتحقيق في إخفاقاتها

**حدود وحذر:** healer قد يقترح تخطي اختبار عند عطل المنتج؛ المنع افتراضي ولا يُحتسب التخطي نجاحًا

**مستوى المراجعة:**  `primary_docs`; `benchmark: not_run`; `integration: catalog_only`.



### `playwright-cli` - [Playwright CLI for agents](https://github.com/microsoft/playwright-cli)

قيادة المتصفح وتسجيل الأدلة واختبارات الويب

**حدود وحذر:** اختر قناة تحكم واحدة للجلسة؛ ادعاءات توفير السياق ليست benchmark خاصًا بنَسَق

**مستوى المراجعة:**  `primary_docs`; `benchmark: not_run`; `integration: catalog_only`.



### `maestro` - [Maestro](https://github.com/mobile-dev-inc/maestro)

اختبارات رحلات الهاتف وتفاعلات واجهته

**حدود وحذر:** اختبار السلوك لا يقيس الطاقة والأداء الأصليين؛ CLI وStudio وCloud منتجات مختلفة

**مستوى المراجعة:**  `primary_docs`; `benchmark: not_run`; `integration: catalog_only`.



### `flaui` - [FlaUI](https://github.com/FlaUI/FlaUI)

اختبارات واجهة ويندوز عند توافق تقنية الواجهة

**حدود وحذر:** تحتاج بيئة Windows مناسبة فعلًا؛ لا يُستنتج تشغيلها من Linux

**مستوى المراجعة:**  `primary_docs`; `benchmark: not_run`; `integration: catalog_only`.



### `testcontainers` - [Testcontainers](https://testcontainers.com/)

تبعيات تكامل اختبارية فعلية حسب لغة المشروع

**حدود وحذر:** تحتاج runtime حاويات وصلاحيات وموارد؛ لا تستخدم بيانات الإنتاج

**مستوى المراجعة:**  `primary_docs`; `benchmark: not_run`; `integration: catalog_only`.



### `k6` - [Grafana k6 skill](https://github.com/grafana/skills/blob/main/skills/grafana-k6/k6/SKILL.md)

كتابة ومراجعة اختبارات الحمل بمعايير وبيانات واضحة

**حدود وحذر:** المهارة ليست تنفيذ الحمل؛ يلزم k6 وبيئة وحدود توقف؛ cloud اختياري

**مستوى المراجعة:**  `selected_entrypoints`; `benchmark: not_run`; `integration: catalog_only`.



### `web-vitals` - [Web Vitals official reference](https://web.dev/articles/vitals)

قياس تجربة الويب بمؤشرات حالية مع فصل المختبر عن الواقع

**حدود وحذر:** لا تنقل FID من ملفات قديمة؛ استخدم القياسات الحالية والبيئة المناسبة

**مستوى المراجعة:**  `primary_docs`; `benchmark: not_run`; `integration: catalog_only`.



### `trail-of-bits` - [Trail of Bits selected security skills](https://github.com/trailofbits/skills)

مراجعة الأمان وبناء سياق التدقيق والاختبار المتخصص

**حدود وحذر:** اختر المهارة المناسبة؛ differential-review يحتاج baseline؛ ليست شهادة خلو من الثغرات

**مستوى المراجعة:**  `selected_entrypoints`; `benchmark: not_run`; `integration: catalog_only`.



### `semgrep` - [Semgrep](https://github.com/semgrep/semgrep)

تحليل ثابت حسب اللغة والقواعد المناسبة

**حدود وحذر:** تحقق من لغة المشروع ورخصة المحرك والقواعد والإضافات؛ false positives وfalse negatives ممكنة

**مستوى المراجعة:**  `primary_docs`; `benchmark: not_run`; `integration: catalog_only`.



### `osv` - [OSV-Scanner](https://github.com/google/osv-scanner)

فحص ثغرات الاعتماديات وفق بياناتها

**حدود وحذر:** لا يراجع منطق العمل؛ فحص توفر بيانات الثغرات ووقت تحديثها

**مستوى المراجعة:**  `primary_docs`; `benchmark: not_run`; `integration: catalog_only`.



### `gitleaks` - [Gitleaks](https://github.com/gitleaks/gitleaks)

كشف الأسرار في المشاريع ذات الإعدادات القائمة

**حدود وحذر:** README يعلن التحديثات الأمنية فقط ويوجه إلى Betterleaks؛ احتفظ بالمناسب ولا تبدل تلقائيًا

**مستوى المراجعة:**  `primary_docs`; `benchmark: not_run`; `integration: catalog_only`.



### `betterleaks` - [Betterleaks](https://github.com/betterleaks/betterleaks)

مرشح لفحص الأسرار بعد انتقال تركيز مطور Gitleaks

**حدود وحذر:** مرشح يحتاج مقارنة على corpus اختبار آمن؛ ليس تفوقًا مثبتًا بسبب الاسم أو الإعلان

**مستوى المراجعة:**  `primary_docs`; `benchmark: not_run`; `integration: catalog_only`.



### `trufflehog` - [TruffleHog](https://github.com/trufflesecurity/trufflehog)

بديل لكشف الأسرار من مصادر متعددة والتحقق منها عند الإذن

**حدود وحذر:** التحقق قد يرسل طلبات باستخدام السر الحقيقي؛ عطله افتراضيًا أو اطلب إذنًا مستقلًا؛ راجع AGPL

**مستوى المراجعة:**  `primary_docs`; `benchmark: not_run`; `integration: catalog_only`.



### `zap` - [ZAP](https://www.zaproxy.org/)

اختبارات أمان ديناميكية مأذونة

**حدود وحذر:** لا تفحص منافسين؛ خطط المصادقة وحدود الاختبار والبيانات والآثار

**مستوى المراجعة:**  `primary_docs`; `benchmark: not_run`; `integration: catalog_only`.



### `asvs` - [OWASP ASVS](https://owasp.org/projects/asvs)

متطلبات تحقق أمنية للتطبيقات

**حدود وحذر:** اختر ضوابط وإصدارًا؛ ليست أداة تشغيل أو شهادة امتثال

**مستوى المراجعة:**  `primary_docs`; `benchmark: not_run`; `integration: catalog_only`.



### `masvs` - [OWASP MASVS and MASTG](https://mas.owasp.org/)

متطلبات واختبارات أمن الموبايل

**حدود وحذر:** اربط البنود بأدلة جهاز وتطبيق مناسبين؛ لا تعتمد اسم المعيار وحده

**مستوى المراجعة:**  `primary_docs`; `benchmark: not_run`; `integration: catalog_only`.



### `knip` - [Knip](https://github.com/webpro-nl/knip)

كشف مرشحات الملفات والاعتماديات والصادرات غير المستخدمة

**حدود وحذر:** لا تحذف تلقائيًا؛ افحص الاستدعاءات الديناميكية وواجهات الحزمة العامة

**مستوى المراجعة:**  `primary_docs`; `benchmark: not_run`; `integration: catalog_only`.



### `dependency-cruiser` - [dependency-cruiser](https://github.com/sverweij/dependency-cruiser)

قواعد حدود الوحدات والاعتماديات وتمثيلها

**حدود وحذر:** قواعد المشروع هي المرجع؛ ليس سببًا لإعادة تقسيم المشروع اعتباطًا

**مستوى المراجعة:**  `primary_docs`; `benchmark: not_run`; `integration: catalog_only`.



### `otel` - [OpenTelemetry](https://opentelemetry.io/docs/)

تخطيط وإضافة traces وmetrics وlogs وفق اللغة

**حدود وحذر:** ليس منصة تخزين للمراقبة؛ حدد exporter والاحتفاظ والعينات والخصوصية والتكلفة

**مستوى المراجعة:**  `primary_docs`; `benchmark: not_run`; `integration: catalog_only`.



### `hashicorp` - [HashiCorp agent skills](https://github.com/hashicorp/agent-skills)

إرشادات IaC عندما يختار المشروع Terraform أو Packer

**حدود وحذر:** لا تفرض IaC؛ رخصة المهارات لا تحسم رخصة المحرك؛ خطط state والأسرار والموافقة على apply

**مستوى المراجعة:**  `primary_docs`; `benchmark: not_run`; `integration: catalog_only`.



### `cloudflare` - [Cloudflare official skills](https://github.com/cloudflare/skills)

إرشادات منصة Cloudflare عندما يعتمدها القرار التقني

**حدود وحذر:** لا تجعل مهارة المزود تختار الاستضافة لصالحه؛ راجع حدود الخدمة والكلفة والبيانات

**مستوى المراجعة:**  `primary_docs`; `benchmark: not_run`; `integration: catalog_only`.



### `stripe` - [Stripe AI skills](https://github.com/stripe/ai)

تنفيذ تكامل Stripe بعد اختيار مزود الدفع وتحقق ملاءمته

**حدود وحذر:** تأكد من البلد والعملات والمتطلبات؛ sandbox فقط للتجارب؛ اختبر التكرار والتسوية والاسترداد

**مستوى المراجعة:**  `primary_docs`; `benchmark: not_run`; `integration: catalog_only`.



### `promptfoo` - [Promptfoo](https://github.com/promptfoo/promptfoo)

تقييم مخرجات LLM وسلامتها وتكلفتها في المنتج أو نَسَق

**حدود وحذر:** التشغيل المحلي لا يعني أن النماذج البعيدة لا تستقبل البيانات؛ راجع المزود وحدود الاختبار

**مستوى المراجعة:**  `primary_docs`; `benchmark: not_run`; `integration: catalog_only`.



### `renovate` - [Renovate](https://github.com/renovatebot/renovate)

اقتراح تحديثات تبعيات مضبوطة مع CI

**حدود وحذر:** لا دمج تلقائي لتغيير رخصة أو صلاحية أو major؛ لا تنشر أسرارًا إلى PR غير موثوق

**مستوى المراجعة:**  `primary_docs`; `benchmark: not_run`; `integration: catalog_only`.



### `seo-google` - [Google Search Central](https://developers.google.com/search/docs/fundamentals/seo-starter-guide)

مرجع فهرسة ومحتوى وروابط للمواقع العامة

**حدود وحذر:** لا تحتاجه لوحة داخلية؛ لا وعود بالتصدر أو بنسخ محتوى المنافسين

**مستوى المراجعة:**  `primary_docs`; `benchmark: not_run`; `integration: catalog_only`.
