
class RawHelper:
    @classmethod
    def get_raw_object(cls, raw_string):
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
