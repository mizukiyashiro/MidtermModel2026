# 2026 Midterm Forecast Model

A polls-plus-fundamentals Monte Carlo forecast of the November 3, 2026 U.S. Senate, governor and House elections, using data available as of October 18, 2026.

## Run it

```bash
pip install -r requirements.txt
python midterm_model_2026.py
```

Results are deterministic (fixed random seed). The output from the latest run is saved in `results.txt`.

## Forecast

| Chamber | D | R | I |
|---|---|---|---|
| Senate | 50 | 48 | 2 |
| Governors | 26 | 24 | 0 |
| House | 234 | 201 | 0 |

Democrats control the Senate (51+ seats including the independents) in 71% of simulations and win the House in 98%.

### Key Senate races

| State | Projected winner | Win probability |
|---|---|---|
| Alaska | Mary Peltola (D) | 55% |
| Florida | Ashley Moody (R) | 79% |
| Georgia | Jon Ossoff (D) | 92% |
| Iowa | Ashley Hinson (R) | 53% |
| Kansas | Roger Marshall (R) | 60% |
| Maine | Troy Jackson (D) | 72% |
| Michigan | Abdul El-Sayed (D) | 74% |
| Minnesota | Peggy Flanagan (D) | 87% |
| Nebraska | Pete Ricketts (R) | 64% |
| New Hampshire | Chris Pappas (D) | 94% |
| Ohio | Sherrod Brown (D) | 72% |
| South Carolina | Darline Graham (R) | 73% |
| Texas | James Talarico (D) | 65% |

### Key governor races

| State | Projected winner | Win probability |
|---|---|---|
| Arizona | Katie Hobbs (D) | 89% |
| Florida | Byron Donalds (R) | 70% |
| Georgia | Rick Jackson (R) | 53% |
| Iowa | Rob Sand (D) | 82% |
| Michigan | Jocelyn Benson (D) | 85% |
| Nevada | Joe Lombardo (R) | 56% |
| Ohio | Amy Acton (D) | 76% |
| Texas | Greg Abbott (R) | 82% |
| Wisconsin | David Crowley (D) | 68% |

## Methodology

My forecast comes from a model that gives every race one number, the expected margin for the Democrat (or the Democrat-backed independent), and then simulates the election 50,000 times to see how often each side wins. The expected margin blends three kinds of evidence. The first is a weighted polling average. Recency is important, as each poll loses about half its weight every 10 days. A poll also has more strength if it has a larger sample since weight scales with the square root of the sample size. If a poll surveys likely rather than registered voters, it also has more weight. Polls paid for by a party count only 60% as much and are shifted 1.5 points against the sponsor. For example, in the Texas Senate race a 6-day-old Siena poll showing Talarico +4 counted about twice as much as a 3-week-old poll showing Talarico +2, and the weighted average came out to Talarico +3.9. The second is a fundamentals estimate that ignores the race’s polls and digs into what a normal result would be, given the national mood and the state’s lean. The formula is the national environment (D+7.5, slightly below the D+8.2 generic-ballot average because the generic ballot tends to overstate the final result), minus twice the state’s Cook Partisan Voting Index (doubled because PVI measures vote share rather than margin), plus a bonus for incumbents (3 points for an elected senator, 1.5 for an appointed one, 4 for a governor). For open-seat Texas, which is 6 points more Republican than the nation, that gives 7.5 − 12 = R+4.5. The third type of evidence used is the expert ratings from Cook, Sabato, Nate Silver and others, converted into points (Toss-up = 0, Tilt = 2, Lean = 4.5, Likely = 9, Safe = 18) and averaged. Texas’s ratings, split between Toss-up and Lean Democratic, average out to D+1. I blended the three as 65% polls, 15% fundamentals and 20% expert ratings, so Texas works out to 0.65(+3.9) + 0.15(−4.5) + 0.20(+1.0) = Talarico +2.1. Polls get the most weight because they are the most direct evidence this close to the election. Safe races with no public polling use only fundamentals and ratings. Because a 2-point lead is not a guarantee, each simulation adds two kinds of random error to every race. First, there is a national error of about ±2.5 points that moves every race the same way at once (if polls underrate Republicans in Texas, they probably underrate them in Iowa and Ohio too, which is why upsets tend to come in waves). Second, there is a separate ±4.5-point error for each individual race. Across 50,000 simulations, Talarico won about 65% of the time. Each simulation’s seat totals add the seats each party won to the seats not up this year, and I report the median outcome: 50 Democrats, 48 Republicans and 2 independents in the Senate, and 26 Democratic and 24 Republican governors. For the House, instead of modeling all 435 districts, I converted the national popular vote straight into seats with the curve Democratic seats = 435 ÷ (1 + e^(-0.025 × (V - 1))). V is the projected Democratic national margin (D+7, give or take 3 points). The “- 1” reflects that, under the current district maps, Democrats need to win the national vote by about a point just to reach a 218-seat majority, and the 0.025 sets each point of national vote at roughly 2.7 seats, calibrated to 2018, when a D+8.6 environment produced 235 Democratic seats. At D+7 the curve gives Democrats 234 seats. Finally, I made three adjustments grounded in past results. I took 2 points from Jackson in Maine because Collins beat her final 2020 polls by about 10 points, 1 point from Peltola in Alaska because the state’s polls have recently leaned Democratic, and I gave Osborn a 10-point boost in Nebraska’s fundamentals because he lost by only 7 points in 2024 in a state Trump carried by about 20.

## Data sources

**Ratings, nominees and partisan lean**

- Wikipedia: 2026 U.S. Senate elections: ratings table (Cook, Sabato, Inside Elections, Silver Bulletin, DDHQ, Split Ticket, Economist, RCP, Fox), nominees, and seats not up
- Wikipedia: 2026 U.S. gubernatorial elections: governor ratings, nominees, and the PVI column
- Cook PVI 2025, state list: I took the PVI values from the Wikipedia tables, which cite this page; I didn’t open it directly
- Political Wire: Sabato down to five Senate toss-ups (Oct 14) National environment and House
- Political.org: Silver Bulletin generic ballot at D+8.9 (Oct 8)
- Political Wire: Pew generic ballot D+8 (Oct 10)
- Brookings: Democrats on track to outperform House forecasts
- Denver Gazette: Cook shifts 11 House seats toward Democrats (Oct 16)
- Smoke-Filled Room: map now favors GOP by about 1 point after redistricting

**Senate polls**

**Alaska**

- Newsweek: InsiderAdvantage, ASR, NYT/Siena and Trafalgar polls
- Political Wire: Quantus tie (Oct 2)
- Political Wire: ASR (Oct 7)

**Florida**

- Political Wire: Mason-Dixon (Oct 6)
- Political Wire: St. Pete Polls (Oct 8)

**Georgia**

- Ground News: YouGov, Ossoff +10
- FOX 5 Atlanta: InsiderAdvantage, Ossoff +7

**Iowa**

- Political Wire: Suffolk (Oct 7)
- Political Wire: CNN (Oct 8)
- Political Wire: Emerson (Oct 9)
- Political Wire: YouGov (Oct 14)
- Marist Poll: Iowa, October 2026
- Newsweek: NYT/Siena and Quantus polls

**Kansas**

- Political Wire: Global Strategy Group (D) (Oct 2)
- Political Wire: NYT/Siena (Oct 3)
- Political Wire: YouGov (Oct 6)
- Newsweek: InsiderAdvantage and Trafalgar polls
- Fox Baltimore: Emerson, Hamilton +2

**Maine**

- Political Wire: AARP (Oct 1)
- Marist Poll: Maine, October 2026
- Political Wire: Washington Post–Schar (Oct 9)
- Political Wire: Suffolk (Oct 14)

**Michigan**

- Political Wire: Mitchell Research (Oct 5)
- Political Wire: YouGov (Oct 6)
- Political Wire: Quantus (Oct 7)

**Minnesota**

- Political Wire: Morning Consult (Oct 9)
- Political Wire: Star Tribune/Mason-Dixon (Oct 12)
- Political Wire: SurveyUSA (Oct 14)
- USPollingData: Big Data Poll

**Nebraska**

- Political Wire: YouGov (Oct 6)
- Political Wire: NPA (R) (Oct 12)
- Newsweek: Impact Research (D), August

**New Hampshire**

- Political Wire: AARP/St. Anselm (Oct 6)
- Political Wire: YouGov (Oct 6)
- Political Wire: NPA (Oct 16)
- USPollingData: NYT/Siena and UNH

**North Carolina**

- Political Wire: ECU (Oct 8)
- WSOC: WRAL/WSOC SurveyUSA poll
- Elon University Poll

**Ohio**

- Political Wire: CNN (Oct 8)
- NBC4: Suffolk/USA Today, Marist and BGSU polls

**South Carolina**

- Political Wire: InsiderAdvantage (Oct 2)

**Texas**

- Political Wire: Fox News (Oct 1)
- Political Wire: YouGov (Oct 6)
- Political Wire: Guidant (Oct 7)
- Political Wire: Siena/ReconMR (Oct 13)

**Governor Polls**

- **Arizona:** Axios: AARP, FOX 10: Noble Predictive, AZFamily: HighGround, USPollingData: all August polls
- **Georgia:** Political Wire: InsiderAdvantage (Oct 14), WTOC: YouGov, InsiderAdvantage and Rasmussen
- **Michigan:** Hoodline: Benson +7 (Oct 7)
- **Nevada:** Political Wire: Noble Predictive (Oct 6), DeFi Rate: Emerson (Sept)
- **Wisconsin:** Political Wire: YouGov/CFC (Oct 16), TMJ4: Badger Battleground
- **Florida (July poll):** Florida Phoenix: UNF

**Judgement Calls**

**Collins beat her 2020 polls by about 10 points**
- WLOS/Sinclair: “Sen. Collins won her reelection bid by nearly 10 points despite polls showing her behind”. Collins trailed Sara Gideon in every poll
- RealClearPolitics tracked, including Quinnipiac (Gideon +12) and late-October Emerson (Gideon +6), then won by nearly 10.
- Bangor Daily News op-ed on the 2020 polling miss: useful as a second, Maine-based source.

**Osborn ran about 14 points ahead of the top of the ticket in Nebraska in 2024**
- Akashic 2024 Nebraska Senate results: Fischer 53.2%, Osborn 46.5%, so Osborn lost by 6.7 points.
- Newsweek: “Trump to campaign in Nebraska as GOP faces close Senate race”: calls Osborn’s result an “overperformance” and says Trump won Nebraska by just over 20 points.
- Losing by 6.7 in a state Trump won by about 20.5 is about a 14-point overperformance.

**In 2018, Democrats won the House popular vote by 8.6 points and took 235 seats**
- Wikipedia: 2018 U.S. House elections: Democrats 53.4%, Republicans 44.8% (D+8.6), with 235 Democratic seats to 199 Republican.
- NBC News: Democrats won the House popular vote by the largest midterm margin since Watergate: a news source for the same fact.
