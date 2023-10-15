from typing import List

from injectable import injectable
from sqlalchemy import func
from sqlalchemy.orm import aliased

from src.config.connection import DBConnection
from src.model.models import Surebet


@injectable
class SurebetRepository:

    def save_all(self, surebets: List[Surebet]):
        with DBConnection() as db:
            db.session.add_all(surebets)
            db.session.commit()

    def find_all(self) -> List[Surebet]:
        with (DBConnection() as db):
            return db.session.query(Surebet).all()

    def find_all_between(self, start_date='2023-09-02 00:00:00', end_date='2023-09-02 23:59:59') -> List[Surebet]:
        with (DBConnection() as db):
            return db.session.query(Surebet).filter(
                Surebet.last_update_UNDER.between(start_date, end_date)).all()

    def find_all_unique_between(self, start_date='2023-09-02 00:00:00', end_date='2023-09-02 23:59:59') -> List[Surebet]:
        # Alias para usar a mesma tabela duas vezes
        s1 = aliased(Surebet)
        s2 = aliased(Surebet)

        with DBConnection() as db:
            subquery = (
                db.session.query(
                    s2.game_id,
                    s2.bookmaker_key_OVER,
                    s2.bookmaker_key_UNDER,
                    func.max(s2.odd_OVER).label("max_odd_OVER")
                )
                .filter(
                    s2.last_update_OVER > start_date,
                    s2.last_update_OVER < end_date
                )
                .group_by(
                    s2.game_id,
                    s2.bookmaker_key_OVER,
                    s2.bookmaker_key_UNDER
                )
                .subquery()
            )

            query = (
                db.session.query(
                    s1.game_id,
                    s1.outcome_id_OVER,
                    s1.outcome_id_UNDER,
                    s1.bookmaker_key_OVER,
                    s1.bookmaker_key_UNDER,
                    s1.odd_OVER,
                    func.max(s1.odd_UNDER),
                    s1.profit,
                    s1.last_update_OVER,
                    s1.last_update_UNDER
                )
                .filter(
                    s1.last_update_OVER > start_date,
                    s1.last_update_OVER < end_date,
                    s1.game_id == subquery.c.game_id,
                    s1.bookmaker_key_OVER == subquery.c.bookmaker_key_OVER,
                    s1.bookmaker_key_UNDER == subquery.c.bookmaker_key_UNDER,
                    s1.odd_OVER == subquery.c.max_odd_OVER
                )
                .group_by(
                    s1.game_id,
                    s1.outcome_id_OVER,
                    s1.outcome_id_UNDER,
                    s1.bookmaker_key_OVER,
                    s1.bookmaker_key_UNDER,
                    s1.odd_OVER,
                    subquery.c.max_odd_OVER,
                    s1.last_update_OVER,
                    s1.last_update_UNDER,
                    s1.profit
                )
            )

            result = set()
            for i in query.all():
                surebet = Surebet(i[0], i[1], i[2], i[3], i[4], i[5], i[6], i[7])
                surebet.last_update_OVER = i[8]
                surebet.last_update_UNDER = i[9]
                result.add(surebet)
            return list(result)


if __name__ == '__main__':
    repository = SurebetRepository()
    results = repository.find_all_unique_between('2023-10-09', '2023-10-10')
    print(len(results))

    # print(len(results))
    # print(len(set(results)))
    # dados = set()
    for i in results:
        print(i)
    #     dados.add(Surebet(i[0], i[1], i[2], i[3], i[4], i[5], i[6], i[7]))
    # print(len(dados))
