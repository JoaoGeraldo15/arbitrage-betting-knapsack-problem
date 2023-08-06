from typing import List
import pandas as pd
from injectable import injectable

from src.config.connection import DBConnection
from src.model.models import Outcome


@injectable
class OutcomeRepository:

    def find_all_points(self) -> List[float]:
        with DBConnection() as db:
            return db.session.query(Outcome.point).filter(
                Outcome.point != None).group_by(Outcome.point).order_by(Outcome.point)

    def find_all(self, point=1.0) -> List[Outcome]:
        with DBConnection() as db:
            return db.session.query(Outcome).filter(
                Outcome.point == point).all()


if __name__ == '__main__':
    repository = OutcomeRepository()
    result = repository.find_all_points()
    outcomes = repository.find_all(2.5)

    # Supondo que você tenha uma lista de objetos chamada lista_objetos
    lista_dicionarios = [
        {
            'id':obj.id,
             'name': obj.name,
             'price': obj.price,
             'point': obj.point,
             'update_time': obj.update_time
        }
        for obj in outcomes]


    records = pd.DataFrame.from_records(lista_dicionarios)
    print(records.head())
