"""
Module for working with colors.
"""


class Colorer:
    """
    Colors everything.
    """
    def __init__(self, countries):
        self.max = 10 ** 10
        self.colors = ('red', 'blue', 'yellow', 'orange', 'azure', 'green',
                       'violet', 'cyan', 'magenta', 'pink', 'grey')
        self.number_of_colors_used = 0
        self.algorithm = 0
        self.countries = countries
        self.set_colors()

    def set_colors(self):
        """
        Chooses the algorithm and sets colors with chosen algorithm.
        """
        self._set_colors_greedy()

    def _set_colors_greedy(self):
        """
        Sets colors greedy for each country.
        """
        for country in self.countries.items:
            self._set_color_greedy(country)

    def _set_color_greedy(self, country):
        """
        Sets minimal possible color for given country
        :param country: Country
        """
        set_colors = set()
        for i, color in enumerate(self.colors):
            for neigh in self.countries.get_neighbours(country):
                if neigh[1] == color:
                    set_colors.add(i)
        for i in range(len(self.colors)):
            if i not in set_colors:
                country[1] = self.colors[i]
                max_set_colors = 0 if len(set_colors) == 0 else max(set_colors)
                self.number_of_colors_used = max(self.number_of_colors_used,
                                                 max_set_colors, i)
                return
