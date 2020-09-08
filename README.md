# NBA Predictor

### Goal
Predict the outcome of a given NBA regular season game based on the two teams' various metrics such as win rate, field goal percentage, 3pt percentage, assists per game, rebounds per game, etc.

### Tools
- [nba-api](https://github.com/swar/nba_api) to retrieve NBA statistics
- Keras for Machine Learning
- numpy and scikit-learn

### ML model
So far, the best model I have found is a DNN with a single hidden layer with n nodes where n is equal to the input size.

Adjusting the epochs, number of layers, input data size, or batch size didn't have much effect. 

### Findings
- So far, the best win / loss prediction accuracy I could achieve was a **~68%** accuracy.
- If we predict games based only on win rate (always predict that the team with higher win percentage wins, then we achieve **~62%** accuracy)
- With a simple DNN with one hidden layer and using the following metrics as input:
  - \# wins
  - \# losses
  - field goals (made / attempted / percentage) per game
  - 3pts (made / attempted / percentage) per game
  - free throws (made / attempted / percentage) per game
  - rebounds (offensive / defensive) per game
  - assists, turnovers, steals, blocks, personal fouls, personal fouls drawn per game
  - points per game
  - plus/minus
  
  we achieve **~63%** accuracy. Not really better than just considering win percentage.
- Accounting for "home team advantage" bumps up the accuracy to **~65%**
- Using v2 of the relevant metrics increases the accuracy to **~68%**
  - These metrics include things like offensive / defensive ratings, assist ratio and rebound percentage

### TODOs
- test out different combinations of metrics to use as input
- add the team's defensive and offensive rating to the input