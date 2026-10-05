Your AI Lies With a Straight Face. So I Built It a Nervous System.

*Part 1 of 2, the plain-English version. What held up, what didn't, and
what I'm building next.*

*Part 1 of 2. This is the story, no equations. Part 2 has the math, the
code and a link to every result on GitHub, for anyone who wants to check
my homework.*

The AI that never says "I don't know"

Ask an AI a question and it answers like a tenured professor. Ask it
something it gets wrong and it still answers like a tenured professor.
Same tone. Same swagger. Sometimes more swagger.

I wrote a whole book about this, Garbage In, Gospel Out. Then I got
curious enough to measure it. On one AI model, the wrong answers came
out more sure of themselves than the right ones. In an early test, three
out of four of its mistakes came with 90% confidence or more on every
word of the answer. (I didn't check how often right answers looked the
same in that test.)

Cute when it's trivia. Less cute when the same kind of machine moves
money, approves claims or gives out medical advice.

Quick warning before anyone gets excited: this research is young. Some
of my ideas held up. Some didn't. I'll show you both.

Why you can't just ask it "are you sure?"

Today's chatbots do one thing. They guess the next word, over and over.
There's no little inspector inside checking the work. Ask one to
double-check and the same guessing machine guesses what a careful
double-check would sound like. Plenty of times it signs off on its own
mistake, in beautiful prose.

It's like asking the guy who misread the map whether he read the map
right. Same map, same eyes, same answer: "Yep." So the check has to come
from outside the AI.

My theory, in plain words

I didn't start with computer science. I started with the body and the
hospital.

Your brain has brakes. Start to say something dumb in a meeting and you
can stop mid-sentence. Inside your head, a "go" signal and a "stop"
signal race each other. Your brain also has a mistake alarm that fires
about a tenth of a second after you slip, before you could even say
"oops." These systems are separate from the part that does the talking,
and they work on what's going on inside you, not on the story you tell
yourself.

Hospitals work the same way. A nurse doesn't ask "how do you feel?" and
write down "great." She checks heart rate, blood pressure and breathing.
The numbers turn into points. The points add up to a level: fine, watch,
worry, emergency. The patient can swear he's fine. The numbers win.

So here's my theory. To keep an AI in line, you need checks that:

1.  **Never let the AI judge its own work.** The defendant doesn't get
    to be the judge. Outside code does the checking.

2.  **Read what's going on inside the AI,** instead of only what it
    says.

3.  **Move faster than the AI acts.** A warning that shows up after the
    money is gone is just a receipt.

4.  **Come in layers,** so one check catches what another misses.

5.  **Give graded alarms, like a hospital,** instead of a plain yes or
    no.

6.  **Run on their own hardware,** so the AI's software can't mess with
    them.

That's the theory. Now the part where I tried to break it.

How I tested it

One MacBook. A free AI model from OpenAI called gpt-oss-20b, which lets
you look inside it. Thousands of questions a computer can grade exactly:
math problems, counting letters, calendar dates. No opinions, no wiggle
room.

Then a race. While the AI was still thinking, before it answered, could
a check tell the answer was going to be wrong? Every check got the same
strict limit on false alarms. You don't get credit for catching mistakes
by yelling fire every five minutes. And before every test, I wrote down
the rules and got them stamped with the time by outside services, so I
couldn't move the goalposts after peeking.

Round one: my watchdog crushed the AI judge

In the biggest test, the AI got 138 answers wrong. My watchdog, which
reads 120 numbers from inside the AI like a pulse and blood pressure,
caught 94 of them in time. A standard method researchers already use,
which also reads the inside, caught 100. A much bigger AI acting as a
judge, reading the first AI's reasoning, caught 28.

I was pretty pleased with myself. So I did what a good scientist should
do and tried to knock my own result down. Four new tests over two days,
each one written down and time-stamped before I ran it.

Test 1: is it just spotting hard questions?

Maybe the inside readers only learned that some questions are hard. Big
numbers, long strings, dates far in the future. You don't need to look
inside an AI to know that 401,445 times 290,110 is harder than 574 times
88.

So I built a check that only looks at how hard the question is. It never
touches the AI at all. It caught 75 of the 138 mistakes. That alone beat
the big AI judge by a mile, which tells you the judge was a pushover.

But the inside readers still beat the difficulty check. And when I added
the inside reading on top of the difficulty check, it caught more than
difficulty alone. So reading the inside does see something besides "this
question is hard." Test passed.

Test 2: what if you train a program to read the words?

The AI judge was never trained for this job. It just got a prompt.
That's not a fair fight. So I trained a simple program, not an AI
chatbot, to read the AI's own reasoning words and spot trouble. Same
training data the inside readers got.

It caught 90 of the 138. The inside reader caught 100. That gap was too
small to count as a real win. So the big win over the AI judge came
mostly from training a checker, not from looking inside. My headline
claim, "reading the inside beats reading the words," didn't survive.
Test failed.

Then I tried something harder. I trained the checks on some kinds of
problems and tested them on a kind they had never seen. The standard
inside reader still worked, though less well than on problems it knew.
The trained word reader fell apart. That's the real edge of looking
inside: it handles surprises better. And surprises are exactly what
safety is about.

One more piece of humble pie. My own 120 "vital signs" didn't beat the
standard inside reader in any test, and they didn't handle new kinds of
problems at all. The body and the hospital are a great blueprint for how
to build the system. They didn't give me better measurements.

Test 3: do layers beat one check?

I stacked all four checks together: difficulty, the word reader, the
standard inside reader and my vital signs. Then I built a hospital-style
score where each check earns zero to three points, and the points add up
to a level.

  --------------------------------------- -------------------------------
  **Level (hospital-style score)**        **How often the AI was wrong**

  Fine                                    about 4 in 100

  Watch                                   about 13 in 100

  Worry                                   about 24 in 100

  Emergency                               about 2 in 3
  --------------------------------------- -------------------------------

As a warning system, the hospital score works beautifully. The higher
the level, the more likely the AI is wrong, just like a hospital chart.
But as a single alarm, neither the stack nor the hospital score caught
more mistakes than the best single check. The stack caught 96. The best
single check caught 100.

Why? All four checks were looking at the same thing at the same moment,
so they mostly caught the same mistakes and missed the same ones. Four
smoke detectors in the same corner of the room don't help much. Layers
only help when they look at different things at different times.

Test 4: layers at different moments

So I built layers that look at different moments. Layer one reads the
AI's insides while it thinks, before it answers. Layer two waits for the
answer, then asks the AI the same question four more times, with a
little randomness thrown in, and outside code checks whether the answers
agree. If the AI keeps changing its answer, something is off.

Same false-alarm limit as before. The inside reader alone caught 100 of
the 138 mistakes. The two layers together caught 123, and raised fewer
false alarms. Of the 38 mistakes the inside reader missed, the second
layer caught 28. Test passed. Layers work when they look at different
moments.

Then the twist. The ask-it-again check, all by itself, caught 124.
That's as many as both layers together. On these problems, the strongest
single check I've found is watching whether the AI agrees with itself.

Doesn't that break my first rule? Not quite, and the difference matters.
I'm not asking the AI whether its answer is right. That's the defendant
judging himself. I'm counting, with outside code, whether it gives the
same answer every time. A witness who tells four different stories is
telling you something, whatever he says.

The ask-it-again check has two catches. It only works after the answer
exists, and it's slow: about 8 seconds in a typical case, about 20 in a
slow one. So the action has to wait for it. The inside reader warns
while the AI is still thinking, in a few thousandths of a second. Fast
and early, plus slow and strong. That's the pairing.

Being right too late

I also tested whether a warning can actually stop a bad action. NVIDIA
recently released a safety tool called OpenShell, basically a locked
room for an AI agent with a list of what it's allowed to touch. It
polices what the AI may do, not whether its thinking makes sense. If the
AI is allowed to make a payment, the payment goes through even if the AI
got the amount wrong.

So I replayed my watchdog's warnings into it. The watchdog warned in
time about 93 wrong answers. But changing OpenShell's permissions took
about five and a half seconds, and the AI usually acted within a few
seconds of the warning. 74 of those 93 wrong actions went through
anyway. Right, but too late.

The fix is boring, which is usually a good sign: make important actions
wait for an all clear. When every action had to wait, every warned
action was stopped, because nothing with a warning ever got released.
The cost was about a seven-second wait per action (the median), and 16
of 138 right answers got held up. Full disclosure: this was a replay of
recorded results through NVIDIA's free tool on my Mac, not a live system
on NVIDIA's hardware.

Why this matters more than a wrong math answer

A wrong math answer hurts nobody. Now picture an AI-guided combat drone
picking the wrong target with the same calm confidence it had when it
blew a big multiplication. There is no "oops" that un-bombs a school.

When a person makes a terrible call, we can investigate, fire, sue or
jail them. You can't put an algorithm on trial. The blame gets smeared
across the company that built it, the company that used it and the
person who flipped the switch, until it sticks to nobody. Philosophers
call this the responsibility gap. So with AI, the brakes have to be in
place before the action, not after.

What I think the system should look like now

The tests changed my mind twice. Layers matter, but each one has to see
something different, at a different moment:

7.  **Before the answer:** a check reading the AI's insides as it
    thinks.

8.  **After the answer:** ask the AI the same question a few times and
    let outside code check whether the answers agree. The strongest
    single check I found.

9.  **Before the action:** a hold on anything that can't be undone,
    until it's cleared.

10. **At the top:** a human, for anything that can kill someone or can't
    be taken back. A person can be held accountable. A machine can't.

And the hospital-style score sits across all of it, turning raw numbers
into a level that tells you how worried to be.

The chip idea

Long term, I want the inside-reading check to run on its own small chip,
sitting next to the AI's chip. Not an AI. A simple, boring, fixed piece
of hardware the AI's software can't touch. The math is tiny: about 6,000
multiplications for each word the AI writes. That's nothing by chip
standards.

Two honest catches. First, chip makers would have to give it a read-only
window into the AI's insides, and today they don't. Second, a separate
chip stops tampering, but it doesn't stop an AI that's been trained to
fake calm insides. That needs its own tests. I haven't built the chip.
It's a design, not a product.

What I'm sure of, and what I'm not

Sure, for this AI and these kinds of questions: the AI should never be
its own judge. Every check I built that runs as outside code beat the AI
judge, even the dumb difficulty check. Also sure: reading the inside
sees more than question difficulty, and it handles new kinds of problems
better than reading the words. Also sure: layers at different moments
beat the best inside check on its own. And timing decides whether a
warning protects anyone.

Not sure: whether reading the inside beats a well-trained word reader on
familiar problems. It didn't here. Not sure: whether layers beat the
ask-it-again check on its own. Here they tied. Not sure: whether any of
this holds on other AI models, everyday writing or real products.

Keeping myself honest

Several of my early results didn't survive, and I retracted them in
public. Earlier drafts of this post were checked eleven times by AI
reviewers from three companies, and every source I cite was read in
full. My four newest tests haven't been through outside review yet.
That's coming. My own process slipped in a few places too, like a setup
that could have run a test before its time stamp. I caught those before
they did damage, and every one is logged in public. No human expert has
reviewed any of this yet. I'd welcome that.

Who did what

-   **The AI being watched:** gpt-oss-20b, a free, open model from
    OpenAI.

-   **The AI judge:** gpt-oss-120b, OpenAI's bigger open model (about
    five and a half times larger overall, about 1.4 times larger in the
    part that does the work for each word). It also helped write some of
    the code.

-   **The safety tool:** OpenShell from NVIDIA, free and open source.

-   **My research assistant:** Claude, from Anthropic. It helped write
    the code, run the experiments, draft the text and review the work.

-   **Outside reviewers on earlier drafts:** Claude Fable and Opus
    (Anthropic), GPT-5.5 (OpenAI) and GLM (Z.ai).

-   **The hardware:** one MacBook. No cluster, no data center.

Coming up in Part 2

Part 2 is for people who want to check my homework: the math behind
every check, the actual code, the statistics, every result with its
confidence range, the time stamps, the mistakes I caught in my own
process, and every limit I know about. Every number in this post links
to a file on GitHub there.

An invitation

All of this ran on one laptop. The next round needs bigger AI models,
much bigger test sets and specialized hardware. If you work at an AI
lab, a chip or cloud company or a university and want to test this at
scale, or you think I got something wrong, I want to hear from you:
yobie@ieee.org. The code, data and every correction are free for
research at github.com/YobieBenjamin/autonomic-graph-regulation.

Garbage in, gospel out. The cure isn't a more confident AI. It's a set
of checks that don't care what the AI says, each watching something
different, inside a stack of locks the AI can't open by itself.

*This project is by me and AI: I came up with the ideas and directed the
work; the AI tools listed above helped with the code, the experiments,
the writing and the reviews. Part 2, the technical version, links every
number to its source on GitHub.*
