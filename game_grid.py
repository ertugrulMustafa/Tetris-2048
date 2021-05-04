import pygame

import stddraw # the stddraw module is used as a basic graphics library
from color import Color # used for coloring the game grid
import numpy as np
from tile import Tile
from point import Point # fundamental Python module for scientific computing
import point
import math
import copy
from playsound import playsound
# Class used for modelling the game grid
class GameGrid:
	# Constructor for creating the game grid based on the given arguments
   def __init__(self, grid_h, grid_w):
      # set the dimensions of the game grid as the given arguments
      self.grid_height = grid_h
      self.grid_width = grid_w
      # create the tile matrix to store the tiles placed on the game grid
      self.tile_matrix = np.full((grid_h, grid_w), None)
      # the tetromino that is currently being moved on the game grid
      self.current_tetromino = None
      self.next_tetromino=None
      # game_over flag shows whether the game is over/completed or not
      self.game_over = False
      # set the color used for the empty grid cells
      self.empty_cell_color = Color(206, 195, 181)
      # set the colors used for the grid lines and the grid boundaries
      self.line_color = Color(189, 175, 162)
      self.boundary_color = Color(132, 122, 113)
      # thickness values used for the grid lines and the grid boundaries 
      self.line_thickness = 0.002
      self.box_thickness = 4* self.line_thickness
      self.score=0
      self.score_color=Color(0,0,0)
      pygame.mixer.init()
      self.clear_sound=pygame.mixer.Sound("clear.wav")
      self.game_speed=180

  

   # Method used for displaying the game grid
   def display(self):
     # playsound('pewdiepie-wow-sound-effect.mp3')
      # clear the background canvas to empty_cell_color
      stddraw.clear(self.empty_cell_color)
      # draw the game grid
      self.draw_grid()
      # draw the current (active) tetromino
      if self.current_tetromino != None:
         self.current_tetromino.draw()
      if self.next_tetromino != None:
         self.next_tetromino.draw()
      # draw a box around the game grid 
      self.draw_boundaries()
      ### show the score on the window
      stddraw.setFontFamily("Pacifico")
      stddraw.setFontSize(45)
      stddraw.setPenColor(self.score_color)
      text = "Score"
      real_score=self.score
      stddraw.text(15,18, text)
      stddraw.text(15,17,str(self.score))
      
      # show the resulting drawing with a pause duration = 250 ms
      #stddraw.show(250)
      if self.score<100 :
           stddraw.show(self.game_speed)
      elif self.score>100 and self.score<500:
         self.game_speed=150
         stddraw.show(self.game_speed)
      else:
         self.game_speed = 120
         stddraw.show(self.game_speed)
   # Method for drawing the cells and the lines of the grid
   def draw_grid(self):
       
      # draw each cell of the game grid
      for row in range(self.grid_height):
         for col in range(self.grid_width):
            # draw the tile if the grid cell is occupied by a tile
            if self.tile_matrix[row][col] != None :#and grid_w
               self.tile_matrix[row][col].draw() 
      # draw the inner lines of the grid
      stddraw.setPenColor(self.line_color)
      stddraw.setPenRadius(self.line_thickness)
      # x and y ranges for the game grid
      start_x, end_x = -0.5, self.grid_width - 0.5
      start_y, end_y = -0.5, self.grid_height - 0.5
      for x in np.arange(start_x + 1, end_x, 1):  # vertical inner lines
         stddraw.line(x, start_y, x, end_y)
      for y in np.arange(start_y + 1, end_y, 1):  # horizontal inner lines
         stddraw.line(start_x, y, end_x, y)
      stddraw.setPenRadius()  # reset the pen radius to its default value            
   
   # Method for drawing the boundaries around the game grid 
   def draw_boundaries(self):
      # draw a bounding box around the game grid as a rectangle
      stddraw.setPenColor(self.boundary_color)  # using boundary_color
      # set the pen radius as box_thickness (half of this thickness is visible 
      # for the bounding box as its lines lie on the boundaries of the canvas)
      stddraw.setPenRadius(self.box_thickness)
      # coordinates of the bottom left corner of the game grid
      pos_x, pos_y = -0.5, -0.5
      stddraw.rectangle(pos_x, pos_y, self.grid_width, self.grid_height)
      stddraw.setPenRadius()  # reset the pen radius to its default value

   # Method used for checking whether the grid cell with given row and column 
   # indexes is occupied by a tile or empty
   def is_occupied(self, row, col):
      # return False if the cell is out of the grid
      if not self.is_inside(row, col):
         return False
      # the cell is occupied by a tile if it is not None
      return self.tile_matrix[row][col] != None
      
   # Method used for checking whether the cell with given row and column indexes 
   # is inside the game grid or not
   def is_inside(self, row, col):
      if row < 0 or row >= self.grid_height:
         return False
      if col < 0 or col >= self.grid_width:
         return False
      return True


   # Method for updating the game grid by placing the given tiles of a stopped 
   # tetromino and checking if the game is over due to having tiles above the 
   # topmost game grid row. The method returns True when the game is over and
   # False otherwise.
   def update_grid(self, tiles_to_place):
      # place all the tiles of the stopped tetromino onto the game grid
      n_rows, n_cols = len(tiles_to_place), len(tiles_to_place[0])
      min_x=self.grid_width-1
      max_x=0
      for col in range(n_cols):
         for row in range(n_rows):
            # place each occupied tile onto the game grid
            if tiles_to_place[row][col] != None:
               pos = tiles_to_place[row][col].get_position()
               if self.is_inside(pos.y, pos.x) and not self.is_occupied(pos.y,pos.x):
                  self.tile_matrix[pos.y][pos.x] = tiles_to_place[row][col]
                  if pos.x<min_x:
                     min_x=pos.x
                  elif pos.x>max_x:
                     max_x=pos.x
               # the game is over if any placed tile is out of the game grid
               else:
                  self.game_over = True

      for col in range(min_x, max_x + 1):
         while self.ismergeble(col):
            self.merge(col)

      n = len(self.tile_matrix)
      for row in range(n):
         if self.line_is_full(n-1-row):
            self.clear_line(n-1-row)
            self.clear_sound.play()
            continue


      current_labels=self.for_connected_labelling()
      while(len(self.flying_tetromino(current_labels))!=0):
         for row in range(self.grid_height):
            for col in range(self.grid_width):
               # draw the tile if the grid cell is occupied by a tile
               if self.tile_matrix[row][col] != None:
                  if len(self.flying_tetromino(current_labels))!=0 and self.tile_matrix[row][col].label==self.flying_tetromino(current_labels)[0]:
                     self.tile_matrix[row][col].move(0,-1)
                     self.tile_matrix[row-1][col]=self.tile_matrix[row][col]
                     self.tile_matrix[row][col]=None
                     current_labels = self.for_connected_labelling()









      return self.game_over

   
   """
   It checks all cols in the same row.If all the tiles are
   empty in same row, it results False.
   """ 
   def line_is_full(self, row):
       n = len(self.tile_matrix[0])#ROW
       for i in range(n):
          if self.tile_matrix[row][i] == None:#goes on every column in a row
             return False
       return True
   
   """
   
   """
   def clear_line(self, row):

      nrow, ncolumn=len(self.tile_matrix), len(self.tile_matrix[0])
      for i in range(ncolumn):
          self.score+=self.tile_matrix[row][i].number
          self.score_color = Color(91, 251, 174)
          self.tile_matrix[row][i].background_color=Color(91, 251, 174)
      self.display()
      for i in range(ncolumn):
          self.tile_matrix[row][i]=None

          
          

      for i in range(row+1, nrow):
         for j in range(ncolumn):
            if self.tile_matrix[i][j]!=None:
               self.tile_matrix[i][j].move(0, -1)
               self.tile_matrix[i-1][j] = self.tile_matrix[i][j]#shift down
               self.tile_matrix[i][j]=None
   """
   If the tile on it and itself is full and they both have the same number, adds the number with itself.
   @param: inside- takes the logarithm of the number on the tile.
        
   """        

   def merge(self, col):
      colors = [Color(238, 228, 218), Color(237, 224, 200), Color(242, 177, 121), Color(245, 149, 99),Color(246, 124, 95),Color(178,102,255),Color(102,0,204),Color(51,255,255),Color(102,0,204),Color(42,70,183),Color(255,0,0)]
      for i in range(self.grid_height-1):
         if self.tile_matrix[i][col]!=None and self.tile_matrix[i+1][col]!=None:
            if self.tile_matrix[i][col].number==self.tile_matrix[i+1][col].number:
               self.tile_matrix[i+1][col].background_color=Color(91, 251, 174)
               self.tile_matrix[i][col].background_color=Color(91, 251, 174)
               self.game_speed=100
               self.display()
               if self.score < 100:
                  self.game_speed = 180
               elif self.score > 100 and self.score < 500:
                  self.game_speed = 150
               else:
                  self.game_speed = 120
                  stddraw.show(self.game_speed)
               self.tile_matrix[i][col].number += self.tile_matrix[i][col].number
               self.score+=self.tile_matrix[i][col].number 
               
               self.score_color=Color(91, 251, 174)
               self.display()
               self.score_color=Color(0, 0, 0)

               inside = int(math.log2(self.tile_matrix[i][col].number))#takes the logarithm of the number on the tile

               self.tile_matrix[i][col].background_color = colors[inside - 1]#According to logarithm result, takes
               if inside >= 3:
                  self.tile_matrix[i][col].foreground_color = Color(255, 255, 255)
                  #n.th element from colors array.Assign inside as a background colour
               self.tile_matrix[i + 1][col] = None#deletes the upper tile                          


               for j in range(i+2, self.grid_height):
                  if self.tile_matrix[j][col] == None:
                      return False
                  self.tile_matrix[j][col].move(0, -1)
                  self.tile_matrix[j - 1][col] = self.tile_matrix[j][col]
                  self.tile_matrix[j][col] = None
      self.display()    


               




   def ismergeble(self, col):
      for i in range(self.grid_height-1):
         if self.tile_matrix[i][col]!=None and self.tile_matrix[i+1][col]!=None:
            if self.tile_matrix[i][col].number==self.tile_matrix[i+1][col].number:
               return True
      return False
   def for_connected_labelling(self):
      self.all_labels=[0]
      current_label = 0
      for row in range(self.grid_height-1, -1, -1):
         for col in range(self.grid_width):
            if self.tile_matrix[row][col] != None:
               if row == 19 and col == 0:
                  self.tile_matrix[row][col].label = current_label
                  current_label += 1

               elif row == 19:
                  if self.tile_matrix[row][col - 1] != None:
                     self.tile_matrix[row][col].label = self.tile_matrix[row][col - 1].label
                  else:
                     self.tile_matrix[row][col].label = current_label
                     current_label += 1

               elif col == 0:
                  if self.tile_matrix[row + 1][col] != None:
                     self.tile_matrix[row][col].label = self.tile_matrix[row + 1][col].label
                  else:
                     self.tile_matrix[row][col].label = current_label
                     current_label += 1

               else:
                  if self.tile_matrix[row + 1][col] != None:

                     self.tile_matrix[row][col].label = self.tile_matrix[row + 1][col].label

                  if self.tile_matrix[row][col - 1] != None:
                     self.tile_matrix[row][col].label=self.tile_matrix[row][col-1].label
                     if self.tile_matrix[row + 1][col] != None:
                        if self.tile_matrix[row + 1][col].label<self.tile_matrix[row][col-1].label:
                           self.tile_matrix[row][col].label=self.tile_matrix[row + 1][col].label
                           point=col
                           if point>0:
                              while(point!=0 and self.tile_matrix[row][point-1]!=None):

                                 self.tile_matrix[row][point- 1].label=self.tile_matrix[row][point].label
                                 if self.tile_matrix[row+1][point- 1]!=None:
                                    self.tile_matrix[row + 1][point - 1].label=self.tile_matrix[row][point].label
                                    point2=row+1
                                    if point2<19:
                                       while(point2!=19 and self.tile_matrix[point2+1][point - 1]!=None ):
                                          self.tile_matrix[point2 + 1][point - 1].label=self.tile_matrix[row + 1][point - 1].label
                                          point2+=1
                                 point-=1
                        if self.tile_matrix[row + 1][col].label>self.tile_matrix[row][col-1].label:
                           self.tile_matrix[row + 1][col].label = self.tile_matrix[row][col-1].label
                           point = col
                           point1=row
                           point3=col
                           if point < 11:
                              while (point != 11 and self.tile_matrix[row+1][point+1] != None):
                                 self.tile_matrix[row+1][point + 1].label = self.tile_matrix[row][col].label
                                 point2=row+1
                                 if point2<19:
                                    while(point2!=19 and self.tile_matrix[point2+1][point+1]!=None):
                                       self.tile_matrix[point2 + 1][point + 1].label=self.tile_matrix[row][col].label
                                       point2+=1
                                 point += 1
                           if point1<19:
                              while(point1!=19 and self.tile_matrix[point1+1][col] != None):
                                 self.tile_matrix[point1+1][col].label=self.tile_matrix[point1][col].label
                                 if point3>0:
                                    while(point3!=0 and self.tile_matrix[point1+1][point3-1] != None):
                                       self.tile_matrix[point1 + 1][point3 - 1].label=self.tile_matrix[point1][col].label
                                       point3=1
                                 point1+=1
                  if self.tile_matrix[row][col - 1] == None and self.tile_matrix[row+1][col] == None:
                     self.tile_matrix[row][col].label = current_label
                     current_label += 1

      for row in range(self.grid_height):
         for col in range(self.grid_width):
            if self.tile_matrix[row][col] != None:
               if self.tile_matrix[row][col].label not in self.all_labels:
                  self.all_labels.append(self.tile_matrix[row][col].label)
      return self.all_labels

   def flying_tetromino(self,label_list):
      copy_labels= copy.deepcopy(label_list)
      i=0
      while(i<len(label_list)):
         for row in range(self.grid_height):
            for col in range(self.grid_width):
               if self.tile_matrix[row][col] != None and self.tile_matrix[row][col].label==label_list[i]:
                  position=self.tile_matrix[row][col].get_position()
                  if position.y==0:
                     if self.tile_matrix[row][col].label in copy_labels:
                        copy_labels.remove(self.tile_matrix[row][col].label)
                        row=0
                        col=0
         i+=1



      return copy_labels



   # def flyingtiles(self, row, col):
   #    if col != self.grid_height - 1 or col != 0:
   #      if self.tile_matrix[row][col] != None:
   #         if self.tile_matrix[row - 1][col] == None and self.tile_matrix[row + 1][col] == None:
   #          if self.tile_matrix[row][col - 1] == None and self.tile_matrix[row][col + 1] == None:
   #                self.tile_matrix[row][col].move(0, -1)
   #                self.tile_matrix[row - 1][col] = self.tile_matrix[row][col]
   #                self.tile_matrix[row][col] = None
                  
    



