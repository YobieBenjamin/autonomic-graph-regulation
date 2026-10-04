Your AI Lies With a Straight Face. So I Built It a Nervous System.

*Part 1 of 2, the plain-English version. Part 2 has the math and the
receipts.*

*Part 1 of 2. This is the story, no equations. Part 2 is the technical
version, with the math and a link to every result on GitHub, for anyone
who wants to check my homework.*

The AI that never says "I don't know"

Ask an AI a question and it answers like a tenured professor. Ask it
something it gets wrong and it still answers like a tenured professor.
Same tone, same swagger, sometimes more swagger. No hesitation, no "hmm,
not sure," just a wrong answer delivered like scripture.

I wrote a whole book about this, Garbage In, Gospel Out. Then I got
curious enough to measure it. On one AI model, the wrong answers came
out more confident than the right ones. In an early test, three out of
four of its mistakes came with 90% confidence or more on every word of
the answer. (I didn't check how often right answers looked the same in
that test.)

Cute when it's trivia. Less cute when the same kind of machine is moving
money, approving claims or handing out medical information.

Quick disclaimer before anyone gets excited: this research is young. The
results are promising, not proven, and there's plenty left to do. But
they already point one way. Keeping AI safe takes several layers of
protection, not one clever trick.

Why you can't just ask it "are you sure?"

That's everybody's first idea. It doesn't work as a safety brake.

Today's chatbots do one thing: guess the next word, over and over, based
on patterns in everything they've read. There's no little inspector in
there checking the work. Ask one to double-check and the same guessing
machine guesses what a careful double-check would sound like. Plenty of
times it signs off on its own mistake, beautifully worded. Asking the
same question again can catch some errors after the answer is out, but
it's slow, and it's useless when the AI is wrong the same way every
time.

It's like asking the guy who misread the map whether he read the map
right. Same map, same eyes, same answer: "Yep."

So the checking has to come from outside the AI.

Your brain has brakes. AI doesn't.

This project started with biology, not computer science. Your brain
drinks from a fire hose of sights, sounds, memories and feelings every
second and still gets most calls right. A big reason is that it has
brakes.

Ever started to say something in a meeting and caught yourself
mid-sentence? That's the brake. Scientists study it with a simple game:
start pressing a button, then a signal tells you to stop. Inside your
head, a "go" process and a "stop" process race each other. If the stop
gets there first, the button never gets pressed.

Your brain also has a mistake alarm. Within about a tenth of a second of
slipping up, well before you could tell anyone you'd made a mistake, a
specific brain signal fires that basically means "oops." These brakes
and alarms run on what's going on inside you, not on the story you tell
yourself.

Today's AI has none of it. No brakes, no alarm, no gut feeling that
something smells off. It just keeps guessing the next word. My watchdog
is an attempt to bolt the missing parts on from the outside.

Steal from the hospital

Hospitals solved a version of this decades ago. A nurse doesn't ask "how
are you feeling?" and write down "great." She checks heart rate, blood
pressure, breathing and temperature. A patient can swear he's fine while
the numbers say otherwise, and the numbers win.

So I built a watchdog that does the same thing for AI. It never listens
to what the AI says. It reads 120 numbers from inside the AI while it's
thinking, the machine version of a pulse and blood pressure, and raises
a flag when something looks off. Since it never reads the AI's words,
clever wording has nothing to argue with. (Whether someone could craft
inputs that fool its readings is a fair question, and I haven't tested
it yet.)

How I tested it

The lab: one MacBook. The patient: a free AI model from OpenAI called
gpt-oss-20b. The exam: thousands of questions a computer can grade
exactly, like math problems, counting letters and calendar dates. No
opinions, no essays, no wiggle room.

I picked that model because it's "open," meaning anyone can download it
and look at what's happening inside. That's exactly what my watchdog
needs. The big commercial chatbots keep the hood welded shut.

Then I ran a race. While the AI was still thinking, before it answered,
could my watchdog tell the answer was going to be wrong? Its opponent
was a bigger AI acting as judge, OpenAI's gpt-oss-120b, reading the
first AI's reasoning as it went. The judge is about five and a half
times bigger overall, though only about 1.4 times bigger in the part
that does the work for each word.

To keep myself honest, I wrote down the rules and locked them in before
each test, with a public timestamp from the second test on, so I
couldn't move the goalposts after peeking at the results. Every monitor
also got a strict budget of false alarms. You don't get credit for
catching mistakes by yelling fire every five minutes.

What I found

In the biggest test, the AI got 138 answers wrong. This is how many each
monitor caught before the wrong answer came out:

  --------------------------------------- -------------------------------
  **Monitor**                             **Wrong answers caught in time
                                          (of 138)**

  A standard method that reads the AI's   100
  inner state                             

  My watchdog (the 120 "vital signs")     94

  A bigger AI judge reading its reasoning 28
  --------------------------------------- -------------------------------

Reading the inside of the AI caught more than three times as many
mistakes as the bigger judge reading its words. It also beat the judge
in each of the three separate test sets in that experiment, where my
watchdog caught between 2.5 and 2.9 times as many (a breakdown I ran
afterwards).

Now the humbling part. A standard method researchers already use did
about as well as my watchdog. So the big idea holds up, reading the
inside beats listening to the outside, but my particular recipe isn't
magic. I'd rather find that out myself than have a reviewer find it for
me.

Being right too late

Next I pointed the watchdog's warnings at a real safety tool. NVIDIA
recently released one called OpenShell, basically a locked room for an
AI agent with a list of what it's allowed to touch. Good idea, with one
blind spot: if the AI is allowed to make a payment, OpenShell waves the
payment through even if the AI got the amount wrong. It polices what the
AI may do, not whether its thinking makes any sense.

So I replayed my watchdog's warnings into it to see whether they could
stop bad actions. With its alarm level fixed in advance, the watchdog
warned in time about 93 wrong answers. But changing OpenShell's
permissions took about five and a half seconds, and the AI usually acted
within a few seconds of the warning. Result: 74 of those 93 wrong
actions went through anyway. The watchdog was right. It was just right
too late.

The fix is boring, which is usually a good sign: make important actions
wait for an all clear. When every action had to wait, every warned
action got stopped, because nothing with a warning was ever released.
The cost was about seven seconds of waiting per action (the median), and
16 of 138 right answers got held up, mostly by false alarms.

Full disclosure: this was a replay of recorded results through NVIDIA's
free, open-source tool on my Mac, not a live system on NVIDIA's
hardware.

And yes, it's the same race your brain runs. The stop signal has to beat
the action. Your brain's brake works in about a fifth of a second. A
permission change that takes five seconds mostly doesn't make it.

Why this matters more than a wrong math answer

A wrong math answer hurts nobody. Now hand the same kind of AI something
that can't be undone. Picture an AI-guided combat drone picking the
wrong target with the same serene confidence it had when it blew a big
multiplication. There is no "oops" that un-bombs a school.

With people, we have a backstop called accountability. A soldier, a
pilot, a surgeon or a banker who makes a terrible call can be
investigated, fired, sued or sent to prison. That threat is part of what
keeps human judgment careful.

You can't put an AI on trial. You can't jail an algorithm, and legal
systems everywhere were built to judge people, not machines. When an AI
makes the call, the blame gets smeared across the company that built it,
the company that deployed it and the person who flipped the switch, and
it can end up sticking to nobody. Philosophers even have a name for it:
the responsibility gap.

So with AI, punishment after the fact isn't a plan. The brakes have to
go in before anything happens: an outside monitor reading the AI's vital
signs, a hold on anything that can't be undone, and a human who has to
sign off when lives are on the line. When the mistake is permanent and
nobody can be held to account, prevention is the only safety you get.

For the record, my tests used math questions on a laptop, not weapons.
But the higher the stakes, the stronger this argument gets.

Steal from the bank, too

Banks figured this out ages ago. A card payment doesn't pass one check.
It gets authorized, scored for fraud, checked against limits and
sometimes held before it settles. None of those checks is perfect, so
you stack checks that fail in different ways.

AI needs the same treatment:

1.  **A permission check:** what is the AI allowed to touch at all?

2.  **A vital-signs check:** is its thinking going sideways right now?

3.  **A hold on anything you can't undo,** until it's cleared.

4.  **A second opinion after the fact,** for whatever slips through.

5.  **A human** for the decisions that really matter, because a person
    can be held accountable and a machine can't.

The AI is welcome to give a second opinion on its own finished work. It
just doesn't get to hold the keys to its own actions.

What I'm sure of, and what I'm not

Sure, for this AI and these kinds of questions: reading what's going on
inside an AI gives a much better early warning than trusting what it
says. Also sure: the safety check has to live outside the AI, and timing
matters as much as accuracy.

Not sure yet: whether it works the same on other AI models, on everyday
writing instead of math problems, or at the speed and scale of real
products. Those are the next tests, each with a pass or fail line
written down before I start. This is the beginning of the research, not
the victory lap.

Who did what

-   **The AI being watched:** gpt-oss-20b, a free, open model from
    OpenAI.

-   **The AI judge it raced against:** gpt-oss-120b, OpenAI's bigger
    open model (about five and a half times larger overall). It also
    helped write some of the code.

-   **The safety tool:** OpenShell from NVIDIA, free and open source.

-   **My research assistant:** Claude, from Anthropic. It helped write
    the code, run the experiments, draft the text and review the work.

-   **A second, independent reviewer:** GLM-5.3-flash, from a different
    company, Z.ai, so the work wasn't only checked by the same AI that
    helped build it.

-   **The hardware:** one MacBook. No cluster, no data center.

Keeping myself honest

Several of my early results didn't survive scrutiny, and I retracted
them in public. One test failed to repeat before a bigger, better one
confirmed the result. The work has been checked eleven times by AI
reviewers, most recently by three AI systems from three different
companies at once: Anthropic's Claude Fable, OpenAI's GPT-5.5 and Z.ai's
GLM. Every source I cite was read in full. Every correction is public.
No human expert has reviewed it yet, and I would genuinely welcome one.

Coming up in Part 2

Part 2 is for the people who want to check my homework: how the watchdog
is built, the math behind it, the three monitoring tests plus the NVIDIA
experiment (all written down in advance), the outside reviews, every
source, and every loose end that's still unproven. Every number in this
post links to a file there.

An invitation

All of this ran on one laptop. The next round needs bigger AI models,
much bigger test sets and specialized hardware. If you work at an AI
lab, a chip or cloud company or a university and want to test this at
scale, or you think I got something wrong, I want to hear from you:
yobie@ieee.org. The code, data and every correction are free for
research at github.com/YobieBenjamin/autonomic-graph-regulation.

There's no single magic fix for AI safety. It takes layers, each
catching what the others miss, and the AI never gets to be the lock on
its own actions.

Garbage in, gospel out. The cure isn't a more confident AI. It's a
nervous system that doesn't care what the AI says, inside a stack of
locks the AI can't open by itself.

*This project is by me and AI: I came up with the ideas and directed the
work; the AI tools listed above helped with the code, the experiments,
the writing and the reviews. Part 2, the technical version, links every
number to its source on GitHub.*
