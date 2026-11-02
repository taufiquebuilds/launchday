# Launch posts

Write all posts into `LAUNCH.md`, so the user can copy-paste them on the day. Every claim in them must match the README and the code.

## Contents of LAUNCH.md

1. **Schedule:** the table from `scripts/launch_time.py`, in the user's time zone.
2. **Pre-launch checklist:**
   - [ ] Install command works from a clean directory
   - [ ] CI green, release has assets
   - [ ] Social preview uploaded
   - [ ] Demo GIF plays at the top of the README
   - [ ] Repo pinned on the profile
   - [ ] 2 to 3 free hours after posting, to reply
3. **Hacker News:** title, URL and first comment.
4. **Reddit:** 2 or 3 posts, each written for its subreddit.
5. **X, Bluesky or LinkedIn:** a short thread.
6. **After launch:** the day 1 to day 14 plan.

## Hacker News (Show HN)

**Rules that matter** (from HN's Show HN guidelines and community norms):

- Show HN is for things people can try now. A waitlist or a landing page doesn't count.
- The title is `Show HN: Name – what it does`. Use plain words, at most 80 characters, no hype, no emoji, no "the best".
- Post the repo URL, not a blog post about it.
- **Never ask anyone to upvote**, and don't share a direct link asking for votes. Voting rings get detected and the post gets killed. Sharing the link normally is fine.
- Post the first comment yourself, right after submitting.

**First comment template** (in the maker's own voice; fill it only with true things):

```
Hi HN, I built <name> because <the real reason, one or two sentences>.

<What it does, in 2 or 3 sentences, including the proof moment.>

<How it works: the one non-obvious technical detail, such as an algorithm, scoring or architecture choice.>

<Something real you learned or a limitation you hit, which invites discussion.>

It's <license>. I'd love feedback on <one specific thing>.
```

A technical detail and an honest limitation do better than a feature list. HN readers engage with trade-offs.

## Reddit

Pick 2 or 3 subreddits where the project is on-topic, and write each post for that community. Read each subreddit's rules first: many require a flair, a weekly self-promotion thread, or a minimum account age.

| Project | Subreddits |
| --- | --- |
| Rust | r/rust (use the project flair), r/commandline |
| CLI or terminal tool | r/commandline, r/linux, r/unixporn (if it looks good) |
| Self-hostable app | r/selfhosted, r/homelab |
| JavaScript or TypeScript | r/javascript, r/webdev, r/node, r/reactjs |
| Python | r/Python (Showcase flair), r/learnpython (only if it teaches) |
| AI or agents | r/LocalLLaMA (if it runs locally), r/ClaudeAI, r/ChatGPTCoding |
| Any open-source project | r/opensource, r/coolgithubprojects, r/SideProject |

Post format: the title says what it is, the body has 3 to 5 short paragraphs (what, why, the interesting technical detail, install line, ask for feedback), and the link goes in the body. Space posts about 30 minutes apart rather than cross-posting everything at once.

## X, Bluesky, LinkedIn

A thread of 3 to 5 posts:

1. The pain plus the demo GIF attached. This post carries the thread, so the GIF matters more than the words.
2. How it works, or the score breakdown.
3. The interesting thing you learned.
4. The install line and repo link.

On LinkedIn, write one post instead of a thread, with the GIF and the link in the first comment.

## After launch

- **First 3 hours:** reply to every comment, thank people for bug reports, and fix small things live ("fixed in v0.1.1, thanks"). Turn feature requests into issues and link them in your replies.
- **Day 2 or 3:** write a "What I learned building X" post on Dev.to or your blog about the most interesting technical problem. It reaches people who missed the launch.
- **Week 2:** release v0.1.1 with the launch feedback, and post a short changelog.
- **Measure it:** track stars per day, not totals, to see which channel actually worked. Any star-history tool works. The same author's `repoheat` shows star velocity in the terminal.

## Never

- Ask for upvotes, stars or "support" in a post.
- Invent a backstory, user numbers, testimonials or benchmarks.
- Post from many accounts, or have friends upvote within minutes.
- Spam the same post to 10 subreddits at once.
