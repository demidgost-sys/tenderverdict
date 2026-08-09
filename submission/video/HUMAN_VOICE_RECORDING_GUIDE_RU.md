# Запись озвучки своим голосом

Ваша задача — только спокойно прочитать утверждённый английский текст. Выбирать дубли, вырезать
оговорки, расставлять паузы, синхронизировать речь с видео, собирать субтитры и экспортировать
финальный ролик будет монтажёр.

AI voice, voice cloning, платные сервисы, музыка и звуковые эффекты для этого ролика не нужны.

## Самый простой способ: один файл

Запишите одну непрерывную сессию с именем `TV_VO_session_T01.wav`. Самостоятельно нарезать её на
блоки не нужно.

1. В начале запишите **10 секунд тишины комнаты**, не меняя положение микрофона.
2. Прочитайте блоки `01–08` по порядку, каждый по два раза.
3. Перед дублем можно сказать по-русски: «Блок один, дубль один», подождать секунду и начать
   английский текст. Эта служебная фраза будет вырезана.
4. После каждого дубля оставьте около трёх секунд тишины.
5. Если ошиблись, не продолжайте фразу с середины: остановитесь, скажите «pickup» и перечитайте
   целое предложение.
6. Не останавливайте запись из-за небольшой оговорки. Сохраните исходный файл без обработки.

Полный непрерывный проход всего текста в конце сессии полезен как интонационный референс, но не
обязателен, если у каждого блока есть два чистых дубля.

## Утверждённый текст

Читайте только английские абзацы в кавычках. Номера, таймкоды и русские пояснения не произносить.
Не перефразировать: эти слова уже совпадают с таймлайном и английскими субтитрами.

### 01 · Problem · цель 9,6 секунды

Спокойное начало. Небольшая пауза между предложениями; выделить `human next step`.

> Procurement teams often review one tender feed for several supplier profiles. TenderVerdict
> turns each notice into a human next step: open, watch, or skip.

### 02 · Local workflow · цель 11,5 секунды

Точно и спокойно. Короткая пауза после `Mac`.

> The workflow starts with synthetic supplier profiles and normalized notice metadata. Files stay
> on this Mac. Before analysis, a preview shows counts, sample records, and metadata gaps.

### 03 · Three verdicts · цель 13,3 секунды

Одинаково отчётливо произнести `Open documents`, `Watch` и `Reject`; без тревожной интонации.

> One canonical engine evaluates the same notices and review date for every profile. It returns
> three verdicts: Open documents, Watch, or Reject, with visible reasons. A human decides what to do
> next.

### 04 · Free · цель 12,1 секунды

Уверенно, но не рекламно. Выделить `complete` и `Free`.

> Free is a complete first-profile workflow, not a disabled demo. It includes the full queue,
> verdict reasoning, supplied source links, a shareable review brief, and deterministic
> schema-three JSON export.

### 05 · Portfolio · цель 13,7 секунды

Выделить `independent` и `never changes a verdict`.

> Portfolio Workspace applies the same feed to up to five independent supplier profiles.
> RevenueCat unlocks comparison and full portfolio export, but never changes a verdict, creates a
> score, or makes a bid recommendation.

### 06 · Test Store · цель 13,3 секунды

Фактический тон. Последние два предложения произнести отдельно и особенно ясно.

> In the verified Test Store baseline, the Apple SDK loaded a development-only purchase sheet.
> CustomerInfo then confirmed the entitlement was active. It was not an App Store payment. No real
> charge occurred.

### 07 · Judge Access · цель 14,2 секунды

Не торопить перечисление восстановления доступа, возврата на передний план и перезапуска.

> For this evaluation build, RevenueCat Judge Access grants the entitlement without a purchase. A
> fresh check unlocked the screen. Restoring access, returning to the foreground, and a full
> relaunch all kept the workspace unlocked.

### 08 · Honest boundary · цель 9,1 секунды

Сдержанное завершение, не интонация запуска потребительского продукта.

> Synthetic data. No usable key is stored. This is not production billing. TenderVerdict is
> open-source macOS software under Apache two point zero.

## Произношение

Потренируйте этот список до записи; сам список в сессию читать не нужно.

| Написано | Произнести |
|---|---|
| TenderVerdict | **TEN-der VER-dict** |
| procurement | **pruh-KYOOR-ment** |
| supplier | **suh-PLY-er** |
| RevenueCat | **REV-uh-new Cat** |
| CustomerInfo | **customer info** |
| entitlement | **en-TY-təl-ment** |
| Judge Access | **judge access** |
| SDK | отдельные буквы **S-D-K** |
| JSON | **JAY-son** |
| schema-three | **SKEE-muh three** |
| Apache | **uh-PATCH-ee** |
| macOS | **Mac O-S** |

Акцент специально маскировать не нужно. Важнее ясность, ровный темп и естественный голос без
«трейлерной» подачи.

## Настройки записи

- Предпочтительно: `WAV`, mono, PCM 24-bit, 48 kHz.
- Записывать сухой голос без музыки, реверберации, компрессии, EQ, нормализации, voice enhancement,
  auto gain и шумоподавления, если эти функции можно отключить.
- Ориентир по пикам: от −12 до −6 dBFS; индикатор не должен доходить до 0 dBFS или красной зоны.
- Микрофон держать на уровне рта, примерно в 15–20 см и немного в стороне от воздушной струи.
  Положение и уровень не менять в течение всей сессии.
- Закрыть окна, отключить уведомления и по возможности убрать постоянный шум вентилятора.
- Если рекордер не умеет нужный WAV, передайте его **исходный файл** в лучшем доступном качестве
  (`AIFF` или `M4A` допустимы как запасной вариант). Не конвертируйте и не отправляйте запись как
  голосовое сообщение в мессенджере.

Точные длительности выше — ориентир, а не повод ускоряться. Используйте локальный
[`human-voice-teleprompter.html`](human-voice-teleprompter.html): он показывает текст и бесшумный
таймер, не включает микрофон, сеть или звук. Если чистый дубль заметно не помещается в цель,
перезапишите его с более короткими паузами, но не тараторьте.

## Если удобнее записывать отдельными файлами

Один непрерывный файл предпочтителен из-за простоты. Альтернативный комплект:

```text
TV_VO_roomtone.wav
TV_VO_01_problem_T01.wav
TV_VO_01_problem_T02.wav
TV_VO_02_local_workflow_T01.wav
TV_VO_02_local_workflow_T02.wav
...
TV_VO_08_boundary_T01.wav
TV_VO_08_boundary_T02.wav
```

Оставляйте около секунды тишины до и после речи и не подрезайте raw takes.

## Как передать запись

Передайте исходный файл вложением в эту задачу либо положите его без переименования в локальный
игнорируемый каталог `submission/video/human-voice-takes/` внутри рабочей копии проекта.

Вместе с файлом достаточно написать название микрофона и программы записи. Заполнять монтажный
лог, нарезать WAV, удалять шум и попадать голосом в итоговые 109 секунд самостоятельно не нужно.

## Что будет сделано после передачи

Монтажёр:

1. проверит формат и целостность файла без изменения оригинала;
2. выберет лучшие дубли и вырежет служебные фразы и оговорки;
3. синхронизирует восемь блоков с таймлайном, используя room tone для естественных пауз;
4. соберёт сухой mono voice master ровно **109,000 секунды** без time-stretch;
5. добавит голос и `captions-en.srt` к финальному видео;
6. подготовит локальный review-файл и отчёт по метаданным.

Финальную запись нужно будет один раз прослушать владельцу целиком на нормальной скорости и
подтвердить, что слова, громкость и синхронность устраивают. Публикация видео и отправка Devpost
останутся отдельными действиями и не выполняются без отдельного подтверждения.
