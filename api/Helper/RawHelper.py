from typing import List


class RawHelper:
    @classmethod
    def get_raw_object(cls, raw_string) -> List:
        list = []
        # raw is a list of 6 lists as string. We have to convert this one towards a List(List(Int)) object
        for item in raw_string.split('],['):
            item = item.replace('[', '').replace(']', '')
            item = item.split(',')
            item = [int(numeric_string) for numeric_string in item]
            list.append(item)

        return list

    @classmethod
    def get_raw_string(cls, raw_list):
        return str(raw_list).replace(' ', '')


    @classmethod
    def replace_umlaute(cls, raw_string):
        res = raw_string.replace('"', '')
        res = res.replace("Ö", 'Oe')
        res = res.replace("ö", 'oe')
        res = res.replace("Ü", 'Ue')
        res = res.replace("ü", 'ue')
        res = res.replace("Ä", 'Ae')
        res = res.replace("ä", 'ae')
        res = res.replace("ß", 'ss')
        return res


    @classmethod
    def replace_characters_with_codes(cls, raw_string):
        res = raw_string.replace("'", '{52}')
        res = res.replace('"', '{53}')
        return res
