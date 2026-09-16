# Case: pi-learning

[← Home](Home)

## Network — Continual learning across computers, services, and notebooks

<!-- https://w3id.org/ant/cases/pi-learning/network -->

A distributed personal-learning setup spanning multiple computers, some bespoke services, and paper notebooks, covering both hobby and academic interests. The habit currently holding it together is a daily ISO-dated markdown file (e.g. 2026-07-18.md) in which the author records what they learned, thought about, or worked on that day — carried over from Logseq (abandoned once it became too slow as the number of files grew) but kept as plain markdown so it can be retrieved later with 'git grep'. The author always keeps the current day's file open and looks back a day or two when feeling lost about recent work. The characteristic failure mode: interests and threads drop out of active habit and cool down — sometimes indefinitely — until a serendipitous rediscovery reactivates them and pulls them back into the current set of habits. Attempts to prevent this by building or adopting interfaces (e.g. kanban boards) tend to fail the same way: the system itself falls into disuse and is forgotten. No weekly review has been made to stick.

## Translations

### [Pulling a thread: from discovery to (attempted) retention](Translation-pi-learning--main)

The process by which a newly discovered interest is held, explored, selectively written down, and later rediscovered or taught — and by which it repeatedly cools out of active habit. Reads through all four Callon moments, with the strain concentrated at mobilization (reliable rediscovery).

**Problematization.** Problematization: a new thread declares itself worth pulling — A new field or idea surfaces — often via a minimally-described blog link — and, given the learner's academic habit of deep-dive thread-pulling, declares itself worth exploring. Discovery is recursive:…

**Interessement.** Interessement: hold the thread as open browser tabs — The learner locks the interest in at low friction by opening promising items as browser tabs, deliberately chosen over writing to markdown (which costs more friction and is not warranted for everythin…

**Enrolment.** Enrolment: some threads become notes, most stay tabs — Recursive exploration continues; some tabs are closed, others kept open as live placeholders. Only the subset judged worth writing down is enrolled into durable markdown notes — including 'why I rejec…

**Mobilization.** Mobilization: the system speaks for past-you (and to others) — Retention and rediscovery. Open tabs let the learner resume a thread; durable markdown notes speak for past-you later — a git grep recovers a thought, and condensed rejection-rationales are handed to …

_See the full trace: [Pulling a thread: from discovery to (attempted) retention](Translation-pi-learning--main)_

## Characterizations (observer-relative role assignments)

Each row records an analyst's claim *within a context*: the (target, network, practice, invariance) tuple grounds the role assignment. The same actant may appear with different roles across rows — that's not contradiction, it's [§4.1.1 observer-relativity](Concept-Characterization).

| Target | Role | Network | Practice | Invariance | Description |
| --- | --- | --- | --- | --- | --- |
| [The learner (me)](Actant-pi-learning--learner) | [Mediator](Concept-Mediator) | [Continual learning across computers, services, and notebooks](Case-pi-learning) | self-directed-learning | regulates to preserve: understanding-transformed-through-consumption | Read from the self-directed-learning practice, the learner is a Mediator: resources (videos, podcasts, publications, courses) exist on their own and merely carry their content, but the act of consuming them transforms the learner — the outputs (new understanding, notes, questions) are not predictable from the inputs. |
| [The learner (me)](Actant-pi-learning--learner) | [ObligatoryPassagePoint](Concept-ObligatoryPassagePoint) | [Continual learning across computers, services, and notebooks](Case-pi-learning) | self-directed-learning | attention-routing (interest, capture, retrieval, and teaching all currently pass through the learner, not through durable infrastructure) | Read from the self-directed-learning practice, the learner is the Obligatory Passage Point: in the system as it currently runs, essentially every interest, capture, rediscovery, and act of teaching routes through him rather than through durable non-human infrastructure. Because the learner is not himself a durable store — attention is finite and migrates to whatever is new — concentrating the OPP on a non-durable human actant is a principal source of the network's fragility: interests cool the moment attention moves on. The aspirational remedy is to delegate durability to git or a deliberate shelving ritual so that infrastructure becomes a passage point interests can rest in. |
| [The learner (me)](Actant-pi-learning--learner) | [Spokesperson](Concept-Spokesperson) | [Continual learning across computers, services, and notebooks](Case-pi-learning) | self-directed-learning | the-interests-I-can-represent-when-teaching | Read from the self-directed-learning practice, the learner speaks for and represents his accumulated interests when teaching a nerd friend — the Spokesperson role emerging through the mobilization moment. Teaching represents the knowledge to another and, in doing so, surfaces its gaps. |
| [Browser tabs](Actant-pi-learning--browser-tabs) | [Intermediary](Concept-Intermediary) | [Continual learning across computers, services, and notebooks](Case-pi-learning) | self-directed-learning | passes through: interest-content-preserved-for-later (the tab holds the interest; tab-count is deliberately not tracked) | Read from the self-directed-learning practice, browser tabs are an Intermediary: each tab transmits the content of an interest without transformation, holding it for later rediscovery. The overwhelming accumulation of tabs is real, but it is not the invariance being tracked here — the learner tracks whether the interest is preserved, not the number of tabs open. |


## Actants in this case

- **[Browser tabs](Actant-pi-learning--browser-tabs)** — Open browser tabs used as a low-friction hold for interests, deliberately chosen over markdown. They accumulate into the hundreds and spread across multiple computers. Periodic attempts to prune them …
- **[Codebase](Actant-pi-learning--codebase)** — A body of code (a repo or project) being learned from, built on, or maintained.
- **[Computer](Actant-pi-learning--computer)** — One of several machines. Some files or repos live on only one machine and can be out of sync; services, by contrast, are reachable from any of them.
- **[Course (Coursera, Udacity, etc.)](Actant-pi-learning--course)** — A structured online course; typically a fixed, finite sequence the learner is trying to complete.
- **[Daily dated markdown-note habit](Actant-pi-learning--daily-note-habit)** — The practice of keeping a daily ISO-dated markdown file (e.g. 2026-07-18.md) logging what was learned, thought about, or worked on that day. Currently the habit holding the system together, though it …
- **[Git](Actant-pi-learning--git)** — Version control holding the markdown notes and codebases; affords git grep retrieval, but repositories can fall out of sync across machines.
- **[Interest](Actant-pi-learning--interest)** — A topic or thread of curiosity, hobby or academic, that heats up into active habit and cools down into dormancy until some serendipitous rediscovery reactivates it.
- **[The learner (me)](Actant-pi-learning--learner)** — The person doing the learning: captures notes, retrieves them, and reactivates interests across all these media and machines.
- **[Markdown file](Actant-pi-learning--markdown-file)** — A plain-text markdown file holding notes; kept deliberately plain (after leaving Logseq) so it stays fast and searchable with git grep.
- **[Downloaded media file](Actant-pi-learning--media-file)** — A downloaded media item (a video or podcast) stored locally and consumed for its content. Collapsed from the former separate video-file and podcast-file actants: file format does not make a difference…
- **[Paper notes](Actant-pi-learning--paper-notes)** — Handwritten notes in paper notebooks for hobbies and academic interests. Part of the problem: they do not digitize well and resist search.
- **[Nerd friend / peer](Actant-pi-learning--peer)** — A fellow nerd the learner teaches or discusses interests with. Receives condensed rationales for rejected tools/paths; but more importantly, teaching reinforces the learner's knowledge and exposes gap…
- **[Podcast playlist](Actant-pi-learning--podcast-playlist)** — A queue or feed of podcast episodes to listen through; often open-ended and continually refreshed with new episodes.
- **[Publication (paper, book, blog post)](Actant-pi-learning--publication)** — A paper, book, or blog post to read; may be a fixed item (a specific paper or book) or an ongoing source (a blog that keeps posting).
- **[Service](Actant-pi-learning--service)** — A bespoke or third-party online service used to hold or process learning material; reachable from either computer even when local files are not.
- **[Video link](Actant-pi-learning--video-link)** — A URL pointing to a video (e.g. YouTube), saved as a pointer to something to watch or return to later.
- **[Video playlist](Actant-pi-learning--video-playlist)** — A collection of videos to work through; may be fixed (a finite set) or open-ended (a channel that keeps publishing new content).

## Perspectives

- [_default](Perspective-pi-learning--_default)

