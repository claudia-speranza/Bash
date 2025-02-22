from typing import Optional

from models.basic import BasicTimedData


class Titoli(BasicTimedData):
    """
    Dataframe columns
    :param Titolo:
    :param ISIN:
    :param Simbolo:
    :param Mercato:
    :param Strumento:
    :param Valuta:
    """

    @classmethod
    def adapt_excel(cls, records):
        records = records.fillna('')
        return cls(records)

    def find_by_isin(self, isin: str) -> Optional[dict]:
        rows = self.loc[self['ISIN'] == isin]
        if len(rows) > 0:
            return rows.to_dict('records')[0]
        return None

