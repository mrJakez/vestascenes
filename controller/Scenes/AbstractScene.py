from vestaboard.formatter import Formatter

class AbstractScene:
    def execute(self, vboard):
        raw_text = self.get_raw()
        vboard.raw(raw_text, pad='center')

    def get_raw(self):
        return [
            Formatter().convertLine(self.__class__.__name__),
            Formatter().convertLine(''),
            Formatter().convertLine(''),
            Formatter().convertLine("abstract text"),
            Formatter().convertLine(''),
            Formatter().convertLine('')
        ]



class DemoAbstractScene(AbstractScene):
    def execute(self, vboard):
        vboard.post("demo scene")
