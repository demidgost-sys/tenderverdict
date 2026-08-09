# Режиссёрский handoff

## Что уже готово

Готов беззвучный animatic длительностью **1:49**: утверждённая драматургия, точные claims,
callouts, английский narration, синхронные captions, crop/privacy‑карта, provenance и
воспроизводимая сборка. В MP4 нет аудиопотока. Это монтажный прототип, а не опубликованный ролик.

## Драматургия

1. **Проблема:** один и тот же поток тендеров приходится оценивать для разных supplier profiles.
2. **Доверие:** данные локальные и синтетические; перед запуском видны тип, количество и пробелы в
   metadata.
3. **Ядро:** три человеческих next steps — Open documents, Watch, Reject — с причинами.
4. **Free:** первый профиль полностью рабочий, включая reasoning, source links, brief и JSON.
5. **Portfolio:** одинаковые notices сравниваются по независимым профилям без score/ranking.
6. **RevenueCat:** сначала отдельно показан датированный Test Store baseline, затем current Judge
   Access без покупки.
7. **Ценностный финал:** one feed / every supplier profile, затем короткая граница Test Store и no
   real charge.

## Как заменить stills на финальные screen captures

- Снимать только окно exact packaged Debug app, 1920×1080/30 fps, с committed synthetic fixtures.
- Кадры 1–5 заменить на hero → input preview → Run → Free queue → comparison drill-down.
- Кадры 6–7 оставить датированным baseline либо заменить только непрерывным Test Store take после
  отдельного разрешения. Нельзя скрывать failure между purchase sheet и entitlement.
- Кадр 8 — current Judge Access; предложение **No purchase was made** должно оставаться видимым.
- Кадр 9 можно заменить quit/relaunch capture без демонстрации key/code. VoiceOver не включать.
- Кадр 10 оставить детерминированной end card. Public repo URL добавлять только после logged-out QA.

## Монтаж

- Сначала picture lock по `timeline.json`; narration и SRT уже рассчитаны под 109 секунд.
- Сохранять hard cuts или короткие 4–6‑frame dissolves, не меняя общую длину.
- Не делать быстрые цифровые zooms на мелкий UI; лучше крупный crop с одним доказательством.
- Не прятать слова Test Store, Judge Access, No purchase, baseline/current.
- Музыку и SFX не добавлять в текущем проходе. Голос записывает владелец по
  `HUMAN_VOICE_RECORDING_GUIDE_RU.md`; raw voice stem сохранить сухим, а loudness проверить уже на
  финальном mix перед публикацией.
- Captions брать только из `captions-en.srt`; не использовать авто‑перефразирование платформы как
  источник истины.

## Выбранный маршрут озвучки

Владелец выбрал **собственный голос**. Использовать восемь блоков, teleprompter, take log и
metadata-only валидатор из human-voice handoff. AI voice и voice cloning не использовать.

## Финальный publish gate

После записи проверить весь файл на обычной скорости со звуком, синхронность SRT, runtime строго
меньше 2:00 и отсутствие секретов/уведомлений. Upload, YouTube/Vimeo, Devpost и RevenueCat account
остаются отдельными действиями с отдельным разрешением.
