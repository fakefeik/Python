This is program for coloring maps.

File save/load:
You can save and load your custom maps. These are text files that consists of countries 
represented by sets of coordinates in 2 dimensional space.

Drawing maps:
This program allows you to draw your own maps. To do that you just need to click your left mouse 
button over a point where you want to start, continue to form a polygon and then finally press 
enter to complete your new country.

Algorithms:
This program uses so called 'greedy' algorithm which consists of the following: 
    1. Color first vertex with first color.
    2. Do following for remaining V-1 vertices.
        a) Consider the currently picked vertex and color it with the 
        lowest numbered color that has not been used on any previously
        colored vertices adjacent to it. If all previously used colors 
        appear on vertices adjacent to v, assign a new color to it.

Program recolors all polygons automatically right when new polygon is added. Number of colors used for 
drawing is displayed in the top left corner of the screen.