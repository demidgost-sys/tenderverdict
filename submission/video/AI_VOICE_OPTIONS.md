# Professional AI voice options — official-source review

Rechecked: **2026-08-09**. No account was opened, no trial or subscription was activated, no API
request was made, and no voice was generated or played.

## Primary recommendation — ElevenLabs Starter

- Current monthly price: **USD 6/month**, taxes excluded, with 30k credits and approximately
  30 minutes of Text to Speech in the web UI. The plan includes a **Commercial License**.
- ElevenLabs says the Free plan has no commercial license. All paid plans include commercial rights
  except Beta Services, and content generated while the paid subscription is active may continue to
  be used commercially after cancellation.
- Why it is primary: the voice-first Studio workflow, explicit pacing/emotional controls, and ample
  one-month allowance fit a one-off polished English product demo. Use a built-in licensed voice;
  do not clone a person.
- Minimum safe purchase if authorized: one month of Starter, not Creator. Generate the approved
  255-word script during the paid period, export a lossless WAV master, retain the invoice/license
  record, then cancel renewal if the owner wants a one-off plan.
- Do **not** generate on Free and later upgrade: ElevenLabs says commercial rights attach to content
  generated during the paid subscription, not retrospectively to Free output.

Official pages rechecked: ElevenLabs Plans; ElevenLabs Help Center, “Can I publish the content I
generate on the platform?” (both accessed 2026-08-09). External hyperlinks are intentionally
omitted from this public-tree artifact; the local handoff cites the official pages directly.

## Backup recommendation — OpenAI `gpt-4o-mini-tts`

- Usage price: **USD 0.60 per 1M text-input tokens** and **USD 12.00 per 1M audio-output tokens**.
  It is API usage rather than a monthly voice subscription; an API account with funded usage is
  still required.
- The official guide currently lists 13 built-in voices, says voices are optimized for English,
  and recommends `marin` or `cedar` for best quality. Start with `cedar` for a restrained technical
  read if the owner chooses this route.
- OpenAI's Services Agreement says the API customer owns Output as between the customer and OpenAI,
  subject to applicable law and the customer's responsibility for inputs/use.
- The TTS guide requires a clear disclosure that listeners are hearing an AI-generated voice.
- Why it is backup: it avoids a monthly voice subscription and supports explicit tone/speed
  instructions, but the project has not auditioned the voices and exact cost for a 1:49 take should
  be read from API usage rather than estimated as a guaranteed cent amount.

Official pages rechecked: OpenAI GPT-4o mini TTS model reference; OpenAI text-to-speech guide;
OpenAI Services Agreement (all accessed 2026-08-09). External hyperlinks are intentionally omitted
from this public-tree artifact; the local handoff cites the official pages directly.

## Decision rule

Choose **ElevenLabs Starter** when the priority is a voice-production UI and the owner approves the
USD 6 subscription. Choose **OpenAI API** when the owner already has funded API access or wants
usage-based billing. Neither route is authorized by this document; the separate permission must
name the provider and authorize generation of exactly `narration-en.txt`.
