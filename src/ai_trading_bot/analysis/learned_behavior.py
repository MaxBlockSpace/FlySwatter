import logging
import pandas as pd
from datetime import datetime
from typing import Dict, Any, Optional

class LearnedBehaviorModule:
    def __init__(self):
        self.logger = logging.getLogger('ai_trading_bot.analysis.learned_behavior')
        self.behavior_scores = pd.DataFrame(
            columns=['behavior_type', 'identifier', 'score', 'last_updated']
        )

    async def get_behavior_score(
        self,
        behavior_type: str,
        identifier: str
    ) -> float:
        record = self.behavior_scores[
            (self.behavior_scores['behavior_type'] == behavior_type) &
            (self.behavior_scores['identifier'] == identifier)
        ]
        if not record.empty:
            return float(record.iloc[0]['score'])
        return 0.5  # Default neutral score

    async def update_behavior_score(
        self,
        behavior_type: str,
        identifier: str,
        outcome: float
    ) -> None:
        try:
            current_time = datetime.now()
            record = self.behavior_scores[
                (self.behavior_scores['behavior_type'] == behavior_type) &
                (self.behavior_scores['identifier'] == identifier)
            ]

            if not record.empty:
                index = record.index[0]
                old_score = self.behavior_scores.at[index, 'score']
                adjustment = (outcome - 0.5) * 0.1
                new_score = max(0, min(1, old_score + adjustment))
                
                self.behavior_scores.at[index, 'score'] = new_score
                self.behavior_scores.at[index, 'last_updated'] = current_time
                
                self.logger.info(
                    f"Updated behavior score for {behavior_type} '{identifier}': "
                    f"{old_score:.2f} -> {new_score:.2f}"
                )
            else:
                new_score = 0.5 + ((outcome - 0.5) * 0.1)
                new_score = max(0, min(1, new_score))
                new_record = {
                    'behavior_type': behavior_type,
                    'identifier': identifier,
                    'score': new_score,
                    'last_updated': current_time
                }
                self.behavior_scores = pd.concat([
                    self.behavior_scores,
                    pd.DataFrame([new_record])
                ], ignore_index=True)
                
                self.logger.info(
                    f"Created new behavior score for {behavior_type} "
                    f"'{identifier}': {new_score:.2f}"
                )

        except Exception as e:
            self.logger.error(f"Failed to update behavior score: {e}")

    async def decay_behavior_scores(self) -> None:
        try:
            current_time = datetime.now()
            for index, row in self.behavior_scores.iterrows():
                last_updated = pd.to_datetime(row['last_updated'])
                time_delta = (current_time - last_updated).total_seconds()
                
                if time_delta > 86400:  # 1 day
                    decay_factor = 0.99 ** (time_delta / 86400)
                    old_score = row['score']
                    new_score = old_score * decay_factor
                    
                    self.behavior_scores.at[index, 'score'] = new_score
                    self.behavior_scores.at[index, 'last_updated'] = current_time
                    
                    self.logger.info(
                        f"Decayed behavior score for {row['behavior_type']} "
                        f"'{row['identifier']}': {old_score:.2f} -> {new_score:.2f}"
                    )

        except Exception as e:
            self.logger.error(f"Failed to decay behavior scores: {e}")

    def to_dict(self) -> Dict[str, Any]:
        return {
            'behavior_scores': self.behavior_scores.to_dict(orient='records')
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'LearnedBehaviorModule':
        instance = cls()
        if 'behavior_scores' in data:
            instance.behavior_scores = pd.DataFrame(data['behavior_scores'])
        return instance