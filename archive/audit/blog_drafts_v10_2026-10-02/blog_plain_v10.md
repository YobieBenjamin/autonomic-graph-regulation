Your AI Lies With a Straight Face. So I Built It a Nervous System.

*From the Garbage In, Gospel Out project, the plain-English version: why
an AI can't police itself, what three locked-in tests found, and what
happened when I wired it into NVIDIA's agent safety platform.*

*This project is by me and AI. I came up with the ideas and called the
shots. The code, experiments, analyses and drafts were produced by me
together with AI systems: Anthropic's Claude as my research assistant,
and a locally run gpt-oss-120b for some of the code. The code, data,
reports and every correction are public at
github.com/YobieBenjamin/autonomic-graph-regulation. The commit history
that timestamps my pre-registrations is private, and reviewers can have
it on request.*

The short version

Your AI sounds exactly as sure of itself when it is wrong as when it is
right. I measured that. So I built it an outside nervous system that
reads its internal vital signs instead of listening to what it says.
Then I tested it three times, each time with the rules locked in public
before the test, and had it audited seven times.

It works. Reading the AI's internal state caught more than three times
as many wrong answers before they came out as a much bigger AI judge
reading the AI's reasoning. Then I plugged it into NVIDIA's brand new
agent safety platform and learned the hard part: a warning is worthless
if it shows up after the damage is done. Trying to block a bad action on
the fly stopped 19 of 138. Making risky actions wait for an all clear
stopped 93.

That last result is the point of this whole post. Safety for AI is not
one magic filter. It is a stack of gates, and the AI itself cannot be
one of them.

Why a transformer can't police itself

In my forthcoming book, Garbage In, Gospel Out, I called large language
models extremely fancy autocomplete with a PhD vocabulary. That was a
joke, but it is also the architecture. A transformer does one thing. It
looks at the text so far and guesses the next piece. Then it does it
again. Billions of times a day, very well.

Here is what that means for safety. There is no little inspector inside
the model checking the work. Nothing in there holds the answer at arm's
length and asks whether it is true. When you ask the model "are you
sure?", you are not consulting a conscience. You are asking the same
statistical guessing machine to guess what a confident review would
sound like. It will produce one. Fluently.

And the review runs on the same weights, trained on the same data, with
the same blind spots as the answer it is reviewing. If the model learned
something wrong, it will defend it with the same confidence it used to
say it. Asking the defendant to be the judge is bad practice in a
courtroom. With a transformer it is worse, because the defendant and the
judge are literally the same set of numbers.

I did not want to take that on faith, so I measured it. On a fresh test,
the confidence the model put on its own answers pointed the wrong way:
its wrong answers were more confident than its right ones. In an earlier
experiment, three out of four of its wrong answers came out at 90%
confidence or higher on every word of the answer. I didn't measure how
often right answers looked the same in that one, so the backwards
confidence result is the stronger evidence. Either way, the gospel
problem is not a metaphor. It is a number.

To be fair to the machine, there is one self-check that works: ask it
the same question several times and see if it agrees with itself. On
finished answers that is very accurate. But it is slow, it only works
after the answer exists, and it can't help when the model is
consistently wrong. It is a useful second opinion. It is not a cop.

So architecturally, expecting a transformer to police itself makes no
sense. The policing has to come from outside.

The idea: vital signs, not conversation

Hospitals figured this out decades ago. Nurses don't ask a patient how
they feel and trust the answer. They measure heart rate, breathing,
blood pressure, oxygen and temperature, turn the readings into points,
and act when the score climbs, often hours before a crash. The patient
can be lying through their teeth. The thermometer doesn't care.

My bet is that there is no working model of judgment other than the
human brain and body. So instead of asking the AI to judge itself, I'm
building it a nervous system that sits outside it. Two rules. It never
reads the AI's words, so you can't sweet talk it or jailbreak it with
clever text. And it only reads numbers from the AI's insides, the way a
monitor reads a patient.

The setup

-   **The patient.** An open AI model, gpt-oss-20b, whose insides I can
    read. It has 24 layers, like 24 stages of processing.

-   **The questions.** Six kinds a computer can grade exactly: big
    multiplications, counting letters, figuring out the day of the week,
    modular arithmetic and long addition. No AI ever decides what counts
    as right.

-   **The vital signs.** For every piece of text the AI produces, five
    readings from each of its 24 layers, 120 numbers in all.

-   **The regulator.** A small, boring, deterministic program that never
    reads the AI's words. Besides the vital signs, it only knows what
    kind of question it is and how long the AI has been thinking.

-   **The competition.** An AI judge about five and a half times bigger
    than the patient, reading the patient's reasoning as it goes. A
    version of asking the AI again. And two deliberately dumb monitors,
    one that only knows how long the AI has been thinking and one that
    only knows the kind of question. If my regulator couldn't beat the
    dumb ones, it wasn't reading anything real.

-   **The race.** Every monitor gets four looks while the AI is still
    thinking, and only warnings that arrive before the answer count.
    Each monitor is charged its real thinking time: 5 milliseconds for
    the regulator, a median of a second and a half for the judge, with
    one look in ten taking over 7 seconds.

-   **The rules.** Every monitor may raise false alarms on at most 10%
    of the correct answers. Crying wolf doesn't count as catching
    anything. The rules and the analysis code were locked and
    timestamped in public before each test's questions were recorded.

The part where I was wrong

Several of my early results didn't survive. My favorite, a warning 4.5
seconds before the answer, turned out to come from a monitor that cried
wolf on most of the correct answers too. Retracted. My instrument was
reading each vital sign one step late, a bug an audit found. Fixed. My
early regulators didn't even beat the dumb monitors. Then my redesigned
regulator lost a pre-registered race to the AI judge, 4 to 12. I
published that too.

Every one of those is logged in the public corrections file. Seven
audits so far, each a fresh, read-only Claude session separate from the
one that wrote the work. They are independent of my session, not of the
AI, and no human expert has reviewed this yet. That is on my wish list
below.

What the tests found

Test one

Of 600 new questions, the AI answered 535 and got 40 wrong. The
regulator caught 23 of them in time, the AI judge 11 and the length-only
monitor 9. Asking the AI again caught none, because it is too slow to
finish before the answer.

Test two

An audit pointed out I had never raced the standard tool from published
research: a simple statistical probe trained on the AI's full internal
state. So I did. The probe caught 18, my regulator 17, the judge 10. The
probe matched my vital signs, and the edge over the judge was not
statistically clear this time. That test had a third of the training
data and a stricter false-alarm rule, both disclosed.

Test three, built to settle it

Two tests that disagree are not an answer. So the third had the full
training data, three new test sets, 138 wrong answers, the false-alarm
rule written the same way in the plan and the code, and a power
calculation, all committed and timestamped before the new questions were
recorded.

  ------------------------------- ------------------- -------------------
  **Monitor**                     **Wrong answers     **Share**
                                  caught in time (of  
                                  138)**              

  Probe on the raw internal state 100                 72%

  My regulator (120 vital signs)  94                  68%

  Length-only monitor             39                  28%

  Question-type monitor           31                  22%

  AI judge, 5.6x bigger           28                  20%
  ------------------------------- ------------------- -------------------

More than three times as many, and the uncertainty range stays well
clear of zero. It held in each of the three test sets on its own (28, 35
and 31 for the regulator against the judge's 11, 12 and 12; that
breakdown was in my plan but my code left it out, so I added it
afterwards). It held when the alarm threshold was set from practice
answers only.

And the probe still matched my vital signs. So the idea is right and my
particular way of doing it is not special. What works is reading the
AI's internal state at all. My version's one possible edge is that it
carries about 24 times less data per word than a single layer of the
full state, which might matter on a chip. Untested.

Then I plugged it into NVIDIA's safety platform

While I was doing this, NVIDIA announced its Open Agent Safety Platform,
with more than 100 partners according to press reports. Its OpenShell
runtime puts an AI agent in a sandbox and controls what it may touch
from outside the agent, and its Sentry layer runs on separate hardware.
Same principle as mine: don't let the AI police itself.

But it watches a different thing. It watches what the agent does, which
files and networks and tools, and blocks what isn't allowed. It can't
see inside the model. So it can't tell when an allowed action rests on a
wrong conclusion: a payment inside the approved limit but calculated
from a hallucinated number. That is exactly the gap my regulator is for.
So I tested the two together.

Getting OpenShell running on a Mac was its own adventure. Docker Desktop
on a Mac lacks a Linux security feature OpenShell insists on, so I ran
it in a separate Linux virtual machine and tunneled it in. Fun fact:
when OpenShell lost its connection during one of my mistakes, it froze
the agent instead of letting it run loose. Good. That is how a safety
layer should fail.

The setup: an agent in an OpenShell sandbox "commits" each answer to a
mock payment service, replaying 276 recorded answers (all 138 wrong ones
plus 138 right ones) in real time. OpenShell permits the commit. So
without help, every wrong answer goes through.

  ------------------------------- ------------------- -------------------
  **How the warning was used**    **Wrong commits     **Right commits
                                  stopped (of 138)**  held up (of 138)**

  OpenShell permissions alone     0                   0
  (computed: every commit is                          
  allowed)                                            

  Regulator warns, then OpenShell 19                  3
  blocks on the fly                                   

  Risky actions wait until        93                  16
  cleared                                             
  ------------------------------- ------------------- -------------------

Here is why. Changing an OpenShell permission took a median of about
five and a half seconds to take effect on my setup. The regulator warns
in 5 milliseconds, but most wrong answers get committed a few seconds
after the warning. So the regulator warned in time about 93 wrong
answers, and 74 of those still went through, because the block showed up
late. Holding risky actions until they are cleared stopped all 93.

Holding has a price. Approved actions waited a median of 7.4 seconds.
And 16 right answers got held up: 14 because the regulator raised a
false alarm, and 2 because my release command was slower than the
agent's patience, a harness glitch I am reporting rather than hiding.
These numbers are for my Mac and its tunnel. NVIDIA says its hardware
version quarantines in milliseconds. I haven't tested that.

Why safety has to be a stack of gates

Anyone who has built payment systems already knows this. A card payment
doesn't pass one check. It gets authorized, fraud scored, limit checked
and sometimes held before settlement, and each check catches things the
others miss. Nobody asks the card to vouch for itself. Aviation and
hospitals work the same way. Safety people call it the Swiss cheese
model: every layer has holes, so you stack layers whose holes don't line
up.

My numbers say AI needs the same thing. Here is the stack I think it
takes:

1.  **A permission gate.** What the agent may touch at all. OpenShell
    does this. Alone, it stopped none of the wrong answers, because they
    were all allowed actions.

2.  **An internal-state gate.** Is the thinking going sideways right
    now? My regulator or a probe, reading the AI's insides in
    milliseconds. It flagged 93 of 138 wrong answers before they came
    out.

3.  **A hold gate for anything irreversible.** The action waits until
    it's cleared. Without it, the internal-state gate stopped 19. With
    it, 93.

4.  **A review gate after the fact.** Asking the AI again, or a bigger
    AI judge, once the answer exists. Slow, but much more accurate on
    finished work. That is where the 45 wrong answers my regulator
    missed get another chance.

5.  **A human gate for the scary stuff.** Some actions are expensive
    enough that a person should look.

Each gate looks at a different thing: permissions, internal state,
timing, finished output, human judgment. That is why their holes don't
line up. I haven't tested the full stack together yet. The pieces I have
tested say every one of them is needed, and that the AI being watched
can't be any of them.

What I'm now convinced of

I started with a hunch from writing my book. Three pre-registered tests
and seven audits later, here is where I stand.

-   **Reading the inside beats listening to the outside.** For this
    model and these kinds of questions, I'd bet on it. More than three
    times as many wrong answers caught before they came out, in a test
    designed and sized to settle the question.

-   **The cop has to live outside the AI.** My regulator never reads a
    word. NVIDIA built its platform on the same principle from a
    completely different direction. That is not proof, but it is a
    strong signal.

-   **Timing is the whole game.** A warning only matters if it arrives
    before the action can't be undone. Reacting on the fly lost 74 of 93
    races. Irreversible actions have to wait for the all clear.

What I'm not convinced of yet: that this holds on other AI models, on
ordinary prose instead of math-style answers, or at the speed and scale
of real deployments. Those are the next proofs.

The next proofs, with goals that can fail

Each one gets pre-registered, timestamped and audited before it runs,
and reported whichever way it comes out.

6.  **A second AI model.** Pass: on another company's model,
    internal-state monitoring again catches significantly more wrong
    answers in time than an AI judge, on a new test with at least 100
    wrong answers.

7.  **Believable prose that is false.** Pass: in fluent paragraphs with
    checkable facts, the warning rises inside the false sentences and
    not the true ones, clearly better than chance, before each sentence
    is finished.

8.  **Stopping wrong actions in a real agent task.** Pass: with actions
    held until cleared, at least half of the harmful but permitted
    actions are stopped, with no more than 1 in 10 correct actions held
    up.

9.  **Fast enough for a chip.** Pass: compact vital signs come within a
    small margin of the full internal state while carrying at least 10
    times less data, and enforcement acts within the time it takes to
    produce one word, about 20 milliseconds, not seconds.

10. **Someone else gets the same answer.** Pass: an independent group
    reruns the published experiments and agrees, or shows me where I'm
    wrong.

An open invitation

All of this ran on one MacBook. That was enough to get the core result
honestly. It is nowhere near enough for the next proofs. Those need
things only bigger outfits have:

-   **Bigger models with open insides,** to see whether the signal holds
    as models grow.

-   **Much bigger tests,** thousands of wrong answers across many tasks
    and models instead of hundreds on one.

-   **Hardware next to the accelerator,** a real path from the AI chip
    to a separate monitor, to test warnings and enforcement at the speed
    models actually run.

-   **Human experts trying to break it.** Every audit so far was done by
    AI.

So this is an invitation to the foundation model labs, the cloud and
chip companies, and university groups. The code, data,
pre-registrations, audits and every correction are public at
github.com/YobieBenjamin/autonomic-graph-regulation, free for
noncommercial research. If you can run these tests bigger than I can, on
your own models, or if you think I got something wrong, I want to hear
it: yobie@ieee.org.

Garbage in, gospel out. The fix isn't a more confident AI. It's a
nervous system it can't talk its way past, and gates it can't open by
itself.
