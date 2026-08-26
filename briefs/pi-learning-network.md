# Network Brief: Continual learning across computers, services, and notebooks

<!-- compiled from https://w3id.org/ant/cases/pi-learning/network -->

## Positionality

_This is one frame's reading (Self-directed learning (Paul Ivanov / pi)), not a neutral account._

- **Held by:** pi
- **Grounding practice:** Self-directed continual learning

## Description

A distributed personal-learning setup spanning multiple computers, some bespoke services, and paper notebooks, covering both hobby and academic interests. The habit currently holding it together is a daily ISO-dated markdown file (e.g. 2026-07-18.md) in which the author records what they learned, thought about, or worked on that day — carried over from Logseq (abandoned once it became too slow as the number of files grew) but kept as plain markdown so it can be retrieved later with 'git grep'. The author always keeps the current day's file open and looks back a day or two when feeling lost about recent work. The characteristic failure mode: interests and threads drop out of active habit and cool down — sometimes indefinitely — until a serendipitous rediscovery reactivates them and pulls them back into the current set of habits. Attempts to prevent this by building or adopting interfaces (e.g. kanban boards) tend to fail the same way: the system itself falls into disuse and is forgotten. No weekly review has been made to stick.

## Participating actants

| Actant | Description | Local name |
| --- | --- | --- |
| Browser tabs | Open browser tabs used as a low-friction hold for interests, deliberately chosen over markdown. They accumulate into the hundreds and spread across multiple computers. Periodic attempts to prune them paradoxically reactivate dormant interests, spawning more tabs than were closed — a net increase — so they resist reduction to a manageable set. | browser-tabs |
| Codebase | A body of code (a repo or project) being learned from, built on, or maintained. | codebase |
| Computer | One of several machines. Some files or repos live on only one machine and can be out of sync; services, by contrast, are reachable from any of them. | computer |
| Course (Coursera, Udacity, etc.) | A structured online course; typically a fixed, finite sequence the learner is trying to complete. | course |
| Daily dated markdown-note habit | The practice of keeping a daily ISO-dated markdown file (e.g. 2026-07-18.md) logging what was learned, thought about, or worked on that day. Currently the habit holding the system together, though it strains when switching computers. | daily-note-habit |
| Git | Version control holding the markdown notes and codebases; affords git grep retrieval, but repositories can fall out of sync across machines. | git |
| Interest | A topic or thread of curiosity, hobby or academic, that heats up into active habit and cools down into dormancy until some serendipitous rediscovery reactivates it. | interest |
| The learner (me) | The person doing the learning: captures notes, retrieves them, and reactivates interests across all these media and machines. | learner |
| Markdown file | A plain-text markdown file holding notes; kept deliberately plain (after leaving Logseq) so it stays fast and searchable with git grep. | markdown-file |
| Downloaded media file | A downloaded media item (a video or podcast) stored locally and consumed for its content. Collapsed from the former separate video-file and podcast-file actants: file format does not make a difference in this network — the role (a durable offline item consumed for content) is the same. Consumption mode (screen-bound vs ambient audio) is noted but not individuated. | media-file |
| Paper notes | Handwritten notes in paper notebooks for hobbies and academic interests. Part of the problem: they do not digitize well and resist search. | paper-notes |
| Nerd friend / peer | A fellow nerd the learner teaches or discusses interests with. Receives condensed rationales for rejected tools/paths; but more importantly, teaching reinforces the learner's knowledge and exposes gaps (unanswerable questions, observed failure modes), which loops back into new thread-pulling. | peer |
| Podcast playlist | A queue or feed of podcast episodes to listen through; often open-ended and continually refreshed with new episodes. | podcast-playlist |
| Publication (paper, book, blog post) | A paper, book, or blog post to read; may be a fixed item (a specific paper or book) or an ongoing source (a blog that keeps posting). | publication |
| Service | A bespoke or third-party online service used to hold or process learning material; reachable from either computer even when local files are not. | service |
| Video link | A URL pointing to a video (e.g. YouTube), saved as a pointer to something to watch or return to later. | video-link |
| Video playlist | A collection of videos to work through; may be fixed (a finite set) or open-ended (a channel that keeps publishing new content). | video-playlist |


## Translations

### Pulling a thread: from discovery to (attempted) retention

<!-- https://w3id.org/ant/cases/pi-learning/translation/main -->

The process by which a newly discovered interest is held, explored, selectively written down, and later rediscovered or taught — and by which it repeatedly cools out of active habit. Reads through all four Callon moments, with the strain concentrated at mobilization (reliable rediscovery).

| Moment | Label | Description |
| --- | --- | --- |
| Enrolment | Enrolment: some threads become notes, most stay tabs | Recursive exploration continues; some tabs are closed, others kept open as live placeholders. Only the subset judged worth writing down is enrolled into durable markdown notes — including 'why I rejected this' evaluations. Periodic pruning paradoxically reactivates dormant interests and spawns more tabs than it closes, so the tabs resist enrolment into any smaller, manageable set. |
| Interessement | Interessement: hold the thread as open browser tabs | The learner locks the interest in at low friction by opening promising items as browser tabs, deliberately chosen over writing to markdown (which costs more friction and is not warranted for everything). Tabs keep the interest active and rediscoverable; being cheap to open, they accumulate into the hundreds across multiple computers. |
| Mobilization | Mobilization: the system speaks for past-you (and to others) | Retention and rediscovery. Open tabs let the learner resume a thread; durable markdown notes speak for past-you later — a git grep recovers a thought, and condensed rejection-rationales are handed to a nerd friend with an analogous need. Teaching a peer reinforces the knowledge and exposes gaps, looping back into new thread-pulling. Precarious: tabs are fragile and interests cool until serendipitous rediscovery reactivates them. |
| Problematization | Problematization: a new thread declares itself worth pulling | A new field or idea surfaces — often via a minimally-described blog link — and, given the learner's academic habit of deep-dive thread-pulling, declares itself worth exploring. Discovery is recursive: each promising item spawns further promising items. |


## Characterizations within this network

| Target | Role | Per practice | Invariance | Description |
| --- | --- | --- | --- | --- |
| The learner (me) | Mediator | self-directed-learning | regulates to preserve: understanding-transformed-through-consumption | Read from the self-directed-learning practice, the learner is a Mediator: resources (videos, podcasts, publications, courses) exist on their own and merely carry their content, but the act of consuming them transforms the learner — the outputs (new understanding, notes, questions) are not predictable from the inputs. |
| The learner (me) | ObligatoryPassagePoint | self-directed-learning | attention-routing (interest, capture, retrieval, and teaching all currently pass through the learner, not through durable infrastructure) | Read from the self-directed-learning practice, the learner is the Obligatory Passage Point: in the system as it currently runs, essentially every interest, capture, rediscovery, and act of teaching routes through him rather than through durable non-human infrastructure. Because the learner is not himself a durable store — attention is finite and migrates to whatever is new — concentrating the OPP on a non-durable human actant is a principal source of the network's fragility: interests cool the moment attention moves on. The aspirational remedy is to delegate durability to git or a deliberate shelving ritual so that infrastructure becomes a passage point interests can rest in. |
| The learner (me) | Spokesperson | self-directed-learning | the-interests-I-can-represent-when-teaching | Read from the self-directed-learning practice, the learner speaks for and represents his accumulated interests when teaching a nerd friend — the Spokesperson role emerging through the mobilization moment. Teaching represents the knowledge to another and, in doing so, surfaces its gaps. |
| Browser tabs | Intermediary | self-directed-learning | passes through: interest-content-preserved-for-later (the tab holds the interest; tab-count is deliberately not tracked) | Read from the self-directed-learning practice, browser tabs are an Intermediary: each tab transmits the content of an interest without transformation, holding it for later rediscovery. The overwhelming accumulation of tabs is real, but it is not the invariance being tracked here — the learner tracks whether the interest is preserved, not the number of tabs open. |


<!-- generated by ant-rdf; see https://w3id.org/ant/cases/pi-learning/network -->

---

**See also:** [Reading guide](pi-learning-guide.md) · [Synopsis](pi-learning-synopsis.md) · [Positionality](pi-learning-positionality.md) · [Glossary](pi-learning-glossary.md)
