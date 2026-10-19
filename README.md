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

My forecast comes from a model that gives every race one number, the expected margin for the Democrat (or the Democrat-backed independent), and then simulates the election 50,000 times to see how often each side wins. The expected margin blends three kinds of evidence. The first is a weighted polling average. Each poll counts more if it is recent (it loses about half its weight every 10 days), if it has a larger sample (weight scales with the square root of the sample size), and if it surveys likely rather than registered voters. Polls paid for by a party count only 60% as much and are shifted 1.5 points against the sponsor. For example, in the Texas Senate race a 6-day-old Siena poll showing Talarico +4 counted about twice as much as a 3-week-old poll showing Talarico +2, and the weighted average came out to Talarico +3.9. The second is a fundamentals estimate that ignores the race's polls and asks what a normal result would be, given the national mood and the state's lean. The formula is the national environment (D+7.5, slightly below the D+8.2 generic-ballot average because the generic ballot tends to overstate the final result), minus twice the state's Cook Partisan Voting Index (doubled because PVI measures vote share rather than margin), plus a bonus for incumbents (3 points for an elected senator, 1.5 for an appointed one, 4 for a governor). For open-seat Texas, which is 6 points more Republican than the nation, that gives 7.5 − 12 = R+4.5. The third is the expert ratings from Cook, Sabato, Nate Silver and others, converted into points (Toss-up = 0, Tilt = 2, Lean = 4.5, Likely = 9, Safe = 18) and averaged. Texas's ratings, split between Toss-up and Lean Democratic, average out to D+1. I blended the three as 65% polls, 15% fundamentals and 20% expert ratings, so Texas works out to 0.65(+3.9) + 0.15(−4.5) + 0.20(+1.0) = Talarico +2.1. Polls get the most weight because they are the most direct evidence this close to the election; safe races with no public polling use only fundamentals and ratings. Because a 2-point lead is not a guarantee, each simulation adds two kinds of random error to every race: a national error of about ±2.5 points that moves every race the same way at once (if polls underrate Republicans in Texas, they probably underrate them in Iowa and Ohio too, which is why upsets tend to come in waves), and a separate ±4.5-point error for each individual race. Across 50,000 simulations, Talarico won about 65% of the time. Each simulation's seat totals add the seats each party won to the seats not up this year, and I report the median outcome: 50 Democrats, 48 Republicans and 2 independents in the Senate, and 26 Democratic and 24 Republican governors. For the House, instead of modeling all 435 districts, I converted the national popular vote straight into seats with the curve Democratic seats = 435 ÷ (1 + e^(−0.025 × (V − 1))). V is the projected Democratic national margin (D+7, give or take 3 points). The "− 1" reflects that, under the current district maps, Democrats need to win the national vote by about a point just to reach a 218-seat majority, and the 0.025 sets each point of national vote at roughly 2.7 seats, calibrated to 2018, when a D+8.6 environment produced 235 Democratic seats. At D+7 the curve gives Democrats 234 seats. Finally, I made three judgment-based adjustments grounded in past results: I took 2 points from Jackson in Maine because Collins beat her final 2020 polls by about 10 points, 1 point from Peltola in Alaska because the state's polls have recently leaned Democratic, and I gave Osborn a 10-point boost in Nebraska's fundamentals because he ran about 14 points ahead of Kamala Harris there in 2024.

## Data sources

Polls collected from public releases reported by Political Wire, Newsweek, Marist, Suffolk, Emerson, YouGov, NYT/Siena, Fox News and others through October 18, 2026. Race ratings and nominees from Wikipedia's 2026 Senate and gubernatorial election pages (Cook, Sabato, Inside Elections, Silver Bulletin, DDHQ, Split Ticket). Partisan lean from the 2025 Cook PVI.
