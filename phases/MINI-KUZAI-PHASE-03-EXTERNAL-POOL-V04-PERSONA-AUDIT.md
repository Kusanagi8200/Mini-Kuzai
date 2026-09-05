# MINI-KUZAI PHASE 03 - EXTERNAL POOL V0.4 PERSONA AUDIT

Version: 0.1
Status: REFINED AUDIT REQUIRED

## Result

The v0.4 build reported 7 persona residual user messages.

A targeted audit showed:

- input records: 8000
- matched records: 7
- matched user messages: 7
- source: smol-magpie-ultra-short only
- selection stage: retained-v0.3a only
- patterns involved: `act like`, `portray`, `play a role`

## Manual interpretation

The 7 matches are false positives of the broad lexical persona detector.

Examples include ordinary uses such as:

- asking whether to act like nothing is wrong in a meeting
- asking how an author portrays a character
- asking how to portray a fictional character as gentle
- asking whether experience plays a role in a decision
- asking how Pascal's Triangle plays a role in the binomial theorem
- asking how condensation plays a role in the water cycle

These are not instructions asking the assistant to adopt an identity or persona.

## Decision

Do not remove these 7 records solely because of the current persona regex.

The expressions `act like`, `portray`, and `play a role` are too broad when matched without grammatical context.

The persona detector must be changed from broad keyword matching to contextual instruction matching. It should detect instructions such as:

- `Act like you are a professor.`
- `Act as a detective.`
- `Portray a medieval knight.`
- `Play the role of a scientist.`
- `Assume the role of a teacher.`

while not flagging ordinary semantic uses such as:

- `Does experience play a role?`
- `How does Dickens portray Nancy?`
- `Do I act like nothing is wrong?`

## Current v0.4 state

The v0.4 pool has already satisfied these checks:

- total records: 8000
- source quotas: complete
- duplicate content extra: 0
- duplicate prompt extra: 0
- generic residual: 0
- benchmark residual: 0
- Unicode dash residual: 0
- strict duplicate pairs: 0

The reported persona residual count of 7 is not accepted as evidence of persona contamination because all 7 current matches are false positives.

v0.4 remains under review until the refined contextual persona detector is executed against the full pool and validated with positive and negative controls.

No training is authorized yet.
