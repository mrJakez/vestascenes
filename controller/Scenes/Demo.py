from vestaboard.formatter import Formatter


class Scene:
    def get_text(self):
        return "abstract text"

    def get_raw(self):
        return [
            Formatter().convertLine(self.__class__.__name__),
            Formatter().convertLine(''),
            Formatter().convertLine(''),
            Formatter().convertLine(self.get_text()),
            Formatter().convertLine(''),
            Formatter().convertLine('')
        ]



class DemoScene(Scene):
    def get_text(self):
        return "real demo scene"

    #def get_raw(self):
    #    return Formatter().convertLine('abstract demo scene!')


class DemoScene2(Scene):
    def get_text(self):
        return "second demo scene"
   # def get_raw(self):
   #     return Formatter().convertLine('abstract  demo two!')
