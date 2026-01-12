README: Late-Inning Performance After MLB Comebacks (2020–2025)
Project Description

This project examines how Major League Baseball teams perform offensively after major momentum swings. Specifically, it focuses on games where a team either completes or allows a comeback of three or more runs, and asks a simple but interesting question: does that moment change how teams hit in the later innings?

Late innings are defined as the 7th through 9th. The idea is to see whether comebacks create lasting momentum, expose fatigue, or trigger adjustments—at the plate or on the bench—that show up in the data.

To approach this, the analysis uses two complementary methods: direct statistical comparison and regression modeling.

Analysis Approach
T-Test Comparison

The first step compares late-inning offensive production to a team’s own season baseline. For each comeback game, post–7th inning stats are measured against season averages for the same team.

This comparison is done separately for:

Teams that completed a comeback

Teams that gave up a comeback

The offensive metrics considered are RBIs, hits, walks, and home runs. The goal here is to see whether performance meaningfully shifts after a comeback event, rather than just fluctuating randomly.

Multiple Linear Regression (MLR)

The second approach models late-inning offensive output directly using multiple linear regression. Each offensive stat (RBIs, hits, walks, home runs after the 7th inning) is treated as a response variable.

Predictors include:

allowed_vs_comeback: whether the team completed or allowed the comeback

subs_used: number of non-pitcher substitutions

pitchers_used: total pitchers used in the game

errors: defensive errors committed

This helps separate strategic or situational factors from effects that might be more psychological or context-driven.

Key Findings
T-Test Results

Teams that completed comebacks did not show statistically significant changes in late-inning offensive performance compared to their season averages. In practice, this suggests that the comeback itself is more of a short-term surge than a signal of sustained offensive momentum.

Teams that gave up comebacks showed a different pattern. These teams performed significantly better than their season averages in RBIs and walks during the later innings. Despite losing the lead, they often remained productive at the plate, possibly by slowing the game down, becoming more selective, or responding with a more disciplined approach.

Regression Results

Post-7th Inning Hits
Substitutions were a significant predictor of increased hits. Other variables—pitchers used, errors, and team designation—were not significant. This points toward lineup changes and fresh players having a modest but measurable impact.

Post-7th Inning RBIs
No predictors reached statistical significance. This reinforces how context-dependent RBIs are. Situational hitting, timing, and pressure likely matter more here than broad tactical choices.

Post-7th Inning Walks
The number of pitchers used was a significant predictor of walks. This likely reflects fatigue, loss of command, or hitters adjusting their approach against frequent pitching changes.

Post-7th Inning Home Runs
No predictors were significant. Power outcomes appear to depend more on factors not captured in the model, such as pitch quality, timing, and confidence.

Psychological Interpretation

Taken together, the results highlight the limits of momentum as a sustained force. Teams that complete comebacks often experience an emotional spike, but that energy doesn’t reliably carry forward into continued offensive dominance.

On the other hand, teams that give up comebacks frequently show resilience. Increased walks and continued run production suggest emotional control and adaptability rather than collapse. From a sports psychology perspective, this points to mental toughness and self-regulation playing a major role after high-stress moments.

Strategic decisions—like substitutions or bullpen usage—do matter, but they only explain part of the story. Late-inning offense, especially RBIs and home runs, seems heavily influenced by mindset, focus, and pressure handling.

Data Sources

Baseball-Reference

FanGraphs

Retrosheet

Tools & Methods

Python (BeautifulSoup, pandas, statsmodels)

Paired t-tests using scipy.stats.ttest_rel

Multiple linear regression using statsmodels.OLS

Summary

This project provides a data-driven look at how MLB teams respond after major momentum shifts late in games. The results suggest that comebacks are emotionally powerful but not always predictive of sustained performance, while teams that lose leads often remain competitive through discipline and adjustment.

From a coaching or analytical standpoint, the takeaway is simple: managing player psychology may be just as important as managing matchups, especially when games swing suddenly and emotions run high.
