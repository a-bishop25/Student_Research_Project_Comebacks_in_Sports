README: Late-Inning Performance After MLB Comebacks (2020–2025)
📘 Project Description
This project investigates whether Major League Baseball (MLB) teams that stage or allow significant comebacks—defined as overcoming a deficit of 3 or more runs—experience measurable changes in offensive performance during the later innings (7th through 9th).

The analysis combines two approaches:

T-Test Comparison:
We compare the post-7th-inning offensive stats (RBIs, hits, walks, and home runs) of:

Teams that complete comebacks

Teams that give up comebacks
against their respective season averages to determine if performance changes significantly after comeback events.

Multiple Linear Regression (MLR):
We model offensive performance (post-inning RBIs, hits, walks, HRs) as a function of:

allowed_vs_comeback: Indicator for whether the team gave up or completed the comeback

subs_used: Number of player substitutions (excluding pitchers)

pitchers_used: Number of pitchers used in the game

errors: Number of defensive errors

📊 Key Findings
T-Test Results
Comeback Teams did not show statistically significant differences in their late-inning offensive stats post-comeback. This suggests that the act of coming back is more of a temporary peak in performance than a sustained momentum shift.

Giveup Teams, however, performed significantly better than their seasonal averages in terms of RBIs and walks. This implies that despite giving up the lead, they remained competitively engaged and may have adjusted their approach at the plate with increased patience and discipline.

Regression Analysis
Response Variables: Post-Inning Offensive Stats
Post Hits:

🔹 Substitutions significantly predicted an increase in hits.

🔸 Other predictors (pitchers used, errors, team designation) had no significant effect.

🔹 Suggests fresh legs and lineup changes may revitalize offensive focus.

Post RBIs:

❌ No predictors were statistically significant.

🔸 Indicates that situational hitting and clutch performance—often psychological—may drive RBIs more than tactical choices.

Post Walks:

✅ Pitchers used significantly predicted more walks.

🔹 Points to possible fatigue or loss of command from pitching changes.

🔸 Suggests hitters display improved patience and discipline in those contexts.

Post HRs:

❌ None of the predictors showed significance.

🔸 Suggests power hitting is influenced by other factors (timing, confidence, pitch quality) not captured in the model.

🧠 Psychological Implications
These results suggest an important intersection between in-game strategy and sports psychology:

Comeback Teams may experience a temporary surge in motivation and unity during a rally, but that energy doesn’t necessarily sustain offensive dominance. This aligns with theories that sports momentum is fleeting and athletes must self-regulate to maintain peak performance.

Giveup Teams, contrary to expectations, often continue performing well at the plate—especially in drawing walks and driving in runs. This demonstrates resilience, emotional control, and adaptive focus under pressure—core components of mental toughness.

Strategic Factors, like substitutions or increased bullpen usage, only partially explain offensive outcomes. Player mindset, confidence, and focus are likely just as influential—particularly in pressure moments like RBIs or home runs.

📁 Data Sources
Baseball-Reference

FanGraphs

Retrosheet

🛠️ Tools & Methods
Python (BeautifulSoup, pandas, statsmodels)

T-Tests using scipy.stats.ttest_rel

Multiple Linear Regression using statsmodels.OLS

✅ Summary
This project offers data-driven insight into how MLB teams respond—both tactically and psychologically—after significant momentum shifts in late-game scenarios. The findings suggest that coaching strategies should account not just for physical substitutions, but also for managing player psychology, especially in games with high emotional stakes.
