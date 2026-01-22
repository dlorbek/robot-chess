import cv2
import numpy as np
from matplotlib import pyplot as plt
import PIL.Image as Image
import math
from boardClass import BoardManager
import sys



class Chessvision():
    def __init__(self):
        self.board_manager = BoardManager()

        self.last_board_state = self.load_img("Slike/Chessboard0.jpg")
        self.ref = self.load_img("Slike/Chessboard37.jpg")
        self.params = self.geometric_rectification(self.ref, getParams=True)
        self.corners = self.geometric_rectification(self.ref, getRectifiedCorners=True)
        self.game_index = 1



    def plot3D(self, data):
        nx = data.shape[0]
        ny = data.shape[1]
        x = range(nx)
        y = range(ny)


        hf = plt.figure()
        ha = hf.add_subplot(111, projection='3d')

        X, Y = np.meshgrid(x, y)  # `plot_surface` expects `x` and `y` data to be 2D
        ha.plot_surface(X.T, Y.T, data)

        plt.show()


    def convertToGray(self, image):
        oImage = 0.333*image[:,:,0] + 0.333*image[:,:,1] + 0.333*image[:,:,2]
        return oImage

    def thresholdImage(self, iImage, iThreshold, half=False):
        dtype = iImage.dtype
        if dtype.kind in ('i','u'):
            dtypemax = np.iinfo(dtype).max
            dtypemin = np.iinfo(dtype).min
        else:
            dtypemax = iImage.max()
            dtypemin = iImage.min()
        
        if half:
            oImage = dtypemax*0.5 * (iImage > iThreshold)
        else:
            oImage = dtypemax * (iImage > iThreshold)
                
        return oImage.astype(dtype)

    def showimg(self, image, title='image', show=False):
        plt.figure()
        plt.imshow(image, cmap='gray')
        plt.title(title)
        if show:
            plt.show()



    def load_img(self, path) -> np.ndarray:
        img = Image.open(path)
        h, w = 3024, 4032
        img = img.resize((w//8, h//8))
        img = np.array(img)
        img = self.convertToGray(img)
        img = cv2.rotate(img, cv2.ROTATE_180)
        return np.array(img).astype(np.uint8)









    def get_edge_corners(self, corners):

        mid = corners[24]

        e1 = corners[0]
        e2 = corners[6]
        e3 = corners[42]
        e4 = corners[48]

        e = [e1,e2,e3,e4]

        for el in e:
            if el[0] < mid[0] and el[1] < mid[1]:
                top_left = el
            elif el[0] < mid[0] and el[1] > mid[1]:
                bottom_left = el
            elif el[0] > mid[0] and el[1] < mid[1]:
                top_right = el
            else:
                bottom_right = el

        



        edges_inner = np.array([top_left, top_right, bottom_left, bottom_right])

        dx = (top_right[0] - top_left[0]) / 6
        dy = (top_right[1] - top_left[1]) / 6

        

        
        
        coord1 = [round(top_left[0]-dx), round(top_left[1]-dy)]
        top_left_1 = [round(coord1[0]+dy), round(coord1[1]-dx)]

        coord1 = [round(top_right[0]+dx), round(top_right[1]+dy)]
        top_right_1 = [round(coord1[0]+dy), round(coord1[1]-dx)]

        coord1 = [round(bottom_left[0]-dx), round(bottom_left[1]-dy)]
        bottom_left_1 = [round(coord1[0]-dy), round(coord1[1]+dx)]

        coord1 = [int(bottom_right[0]+dx), int(bottom_right[1]+dy)]
        bottom_right_1 = [int(coord1[0]-dy), int(coord1[1]+dx)]
        
        
        return np.array([top_left_1, top_right_1, bottom_left_1, bottom_right_1, mid, [dx, dy]])


    def geometric_rectification(self, img, getParams=False, params=None, getRectifiedCorners=False):
        '''function assumes input image to contain a chessboard'''
        '''params = (center, angle_deg, y_start, y_end, x_start, x_end)'''
        edge_offset = 20

        if params != None:
            y_start = params[2]
            y_end = params[3]
            x_start = params[4]
            x_end = params[5]
            rotationMatrix = cv2.getRotationMatrix2D(params[0],params[1],1)
            rotated_im = cv2.warpAffine(img, rotationMatrix,(img.shape[1], img.shape[0]))
            new_img = rotated_im[y_start:y_end, x_start:x_end]
            return new_img

        ret, corners = cv2.findChessboardCorners(img, (7, 7), None)
        corners = np.round(corners.reshape(49,2)).astype(int)
        if not ret:
            print("nah")
            return
        
        edges = self.get_edge_corners(corners)
        mid = edges[-2]
        dx = edges[-1][0]
        dy = edges[-1][1]
        angle = math.atan(dy/dx)
        angle_deg = math.degrees(angle)


        rotationMatrix = cv2.getRotationMatrix2D(mid,angle_deg,1)
        rotated_im = cv2.warpAffine(img, rotationMatrix,(img.shape[1], img.shape[0]))

        ret, corners = cv2.findChessboardCorners(rotated_im, (7, 7), None)
        corners = np.round(corners.reshape(49,2)).astype(int)
        if not ret:
            print("nah 2")
            return
        
        
        
        edges = self.get_edge_corners(corners)
        top_left = edges[0]
        top_right = edges[1]
        bottom_left = edges[2]
        bottom_right = edges[3]

        y_start = int(top_left[1])
        y_end = int(bottom_left[1])
        x_start = int(top_left[0])
        x_end = int(top_right[0])

        if getParams:
            return (mid, angle_deg, y_start, y_end, x_start, x_end)
        
        
        
        new_img = rotated_im[y_start:y_end, x_start:x_end]

        if getRectifiedCorners:
            ret, corners = cv2.findChessboardCorners(new_img, (7, 7), None)
            corners = np.round(corners.reshape(49,2)).astype(int)
            if not ret:
                print("nah 3")
                return
            return corners
        

        return new_img


    def img_diff(self, im1, im2):
        '''im1 is old board state, im2 is new board state'''
        '''old position has lower intensity'''
        dtype = im1.dtype
        if dtype.kind in ('i', 'u'):
            dtype_max = np.iinfo(dtype).max
            dtype_min = np.iinfo(dtype).min

        else:
            dtype_max = im1.max()
            dtype_min = im1.min()

        im1 = im1.astype(np.float64)
        im2 = im2.astype(np.float64)

        oImage1 = im1 - im2
        return oImage1



        oImage1[oImage1 > dtype_max] = dtype_max
        oImage1[oImage1 < dtype_min] = dtype_min
        showimg(oImage1)
        
        oImage1 = thresholdImage(oImage1.astype(dtype), 50, half=True)
        

        oImage2 = im2 - im1
        #showimg(oImage2)
        oImage2[oImage2 > dtype_max] = dtype_max
        oImage2[oImage2 < dtype_min] = dtype_min
        
        oImage2 = thresholdImage(oImage2.astype(dtype), 50)
        
        plt.show()

        oImage = oImage1 + oImage2
        oImage[oImage > dtype_max] = dtype_max
        oImage[oImage < dtype_min] = dtype_min
        
        #oImage = thresholdImage(oImage, 30)

        
        return oImage.astype(dtype)


    def coordinates_to_move_notation(self, coords):
        file = chr(coords[0] + ord('a'))
        rank = str(coords[1] + 1)
        return file + rank


    def img_diff_filtered(self, im1, im2):
        diff = self.img_diff(im1, im2)
        k = 7
        diff_blur = cv2.GaussianBlur(diff, (k,k), 5)
        laplace = np.abs(cv2.Laplacian(diff_blur, cv2.CV_64F))
        laplace *= 255.0 / laplace.max()
        return laplace.astype(np.uint8)
    
    def img_diff_filtered_V2(self, im1, im2):
        diff = self.img_diff(im1, im2)
        k = 7
        diff_blur = cv2.GaussianBlur(diff, (k,k), 5)
        laplace = np.abs(cv2.Laplacian(diff_blur, cv2.CV_64F))
        laplace *= 255.0 / laplace.max()
        laplace = laplace.astype(np.uint8)
        canny = cv2.Canny(laplace, 100, 200)
        # sobel_x = cv2.Sobel(diff_blur, cv2.CV_64F, 1, 0)
        # sobel_y = cv2.Sobel(diff_blur, cv2.CV_64F, 0, 1)
        # grad = np.sqrt(sobel_x**2 + sobel_y**2)
        # grad *= 255.0 / grad.max()
        return canny.astype(np.uint8)
    

    def get_squares(self, ref, extendedOuterSquares, searchSquarePercent=0.6):

        extendedOuterSquares = not extendedOuterSquares

        ref_new = self.geometric_rectification(ref)

        corners = self.geometric_rectification(ref, getRectifiedCorners=True)
        corners = corners.reshape(7,7,2)

        squares = []
        square_width = corners[0][1][0] - corners[0][0][0]
        offset = (1 - searchSquarePercent) * square_width
        offset = round(offset / 2)


        for i in range(8):
            for j in range(8):
                if i == 0:
                    y_start = 0 + offset*extendedOuterSquares
                else:
                    if j != 7:
                        y_start = corners[i-1][j][1] + offset
                    else:
                        y_start = corners[i-1][6][1] + offset
                if i == 7:
                    y_end = ref_new.shape[0] - 1 - offset*extendedOuterSquares
                else:
                    y_end = corners[i][5][1] - offset
                
                if j == 0:
                    x_start = 0 + offset*extendedOuterSquares
                else:
                    if i != 7:
                        x_start = corners[i][j-1][0] + offset
                    else:
                        x_start = corners[6][j-1][0] + offset
                if j == 7:
                    x_end = ref_new.shape[1] - 1 - offset*extendedOuterSquares
                    
                else:
                    if i != 7:
                        x_end = corners[i][j][0] - offset
                    else:
                        x_end = corners[6][j][0] - offset
                
                squares.append([y_start, y_end, x_start, x_end])

        return squares



    def get_move(self, board_state_new : np.ndarray, board_state_old : np.ndarray):
        '''Function accepts rectified game images and returns the move played'''

        diff = self.img_diff_filtered(board_state_old, board_state_new)
        means = np.zeros((8,8))
        first_found = False
        second_found = False
        third_found = False
        fourth_found = False
        queenside_castled = False
        kingside_castled = False
        brejk = False

        

        # y_start, y_end, x_start, x_end
        squares = self.get_squares(self.ref, extendedOuterSquares=True)
        

        # Calculate and store mean value of each square
        for i in range(8):
            for j in range(8):
                idx = i*8 + j
                bounds = squares[idx]
                square = diff[bounds[0]:bounds[1], bounds[2]:bounds[3]]
                mean = np.round(np.mean(square)).astype(int)
                means[i][j] = mean
        
        

        # Find both squares of the played move
        means = np.array(means)
        sort = np.sort(means.flatten())

        # self.showimg(diff, show=True)
        for sqr in squares:
            diff = cv2.rectangle(diff, (sqr[2], sqr[0]), (sqr[3], sqr[1]), color=255, thickness=1)
        
        self.showimg(diff, show=True)
        second = sort[-1]
        first = sort[-2]
        third = sort[-3]
        fourth = sort[-4]
        
        for i in range(8):
            if brejk:
                break
            for j in range(8):
                if means[i][j] == second and not second_found:
                    second_pos = self.coordinates_to_move_notation((j,7-i))
                    second_found = True
                    
                elif means[i][j] == first and not first_found:
                    first_pos = self.coordinates_to_move_notation((j,7-i))
                    first_found = True
                    
                elif means[i][j] == third and not third_found:
                    third_pos = self.coordinates_to_move_notation((j,7-i))
                    third_found = True
                    
                elif means[i][j] == fourth and not fourth_found:
                    fourth_pos = self.coordinates_to_move_notation((j,7-i))
                    fourth_found = True
                    
                if second_found and first_found and third_found and fourth_found:
                    if second_pos[1] == first_pos[1] == third_pos[1] == fourth_pos[1]:
                        if 'a' in [second_pos[0], first_pos[0], third_pos[0], fourth_pos[0]]:
                            queenside_castled = True
                            print("Queenside castle")
                        else:
                            kingside_castled = True
                            print("Kingside castle")

                    else:
                        queenside_castled = False
                        kingside_castled = False
                    
                    brejk = True
                    break
                    #return first_pos + second_pos
                
        

        # Find which square was first and which second based on board info
        if self.board_manager.has_move == self.board_manager.WHITE_MOVE:
            if queenside_castled:
                move = 'e1c1'
                self.board_manager.play_move(move)
                return move
            elif kingside_castled:
                move = 'e1g1'
                self.board_manager.play_move(move)
                return move
            
            if self.board_manager.is_occupied(first_pos) == 1:
                first_move = first_pos
                second_move = second_pos
            else:
                first_move = second_pos
                second_move = first_pos
        else:
            if queenside_castled:
                move = 'e8c8'
                self.board_manager.play_move(move)
                return move
            elif kingside_castled:
                move = 'e8g8'
                self.board_manager.play_move(move)
                return move
            
            if self.board_manager.is_occupied(first_pos) == -1:
                first_move = first_pos
                second_move = second_pos
            else:
                first_move = second_pos
                second_move = first_pos

        move = first_move + second_move
        self.board_manager.play_move(move)
        return move





    def print_moves(self, game):
        
        for i in range(len(game) - 1):
            game_old = game[i]
            game_new = game[i + 1]

            self.get_move(game_new, game_old)
        
        self.board_manager.print_board_state()


    


    def load_game(self, n_moves, rect_params):
        game = []
        for i in range(n_moves):
            path = f"Slike/Chessboard{i}.jpg"
            game_state = self.load_img(path)
            
            game_state_new = self.geometric_rectification(game_state, params=rect_params)
            game.append(game_state_new)
        return game
    
    def capture_and_update_last_board_state(self):
        new_board_state = self.load_img(f"Slike/Chessboard{self.game_index}.jpg")
        self.game_index += 1
        if self.game_index == 33:
            print("Game positions exausted, stopping execution")
            sys.exit()
        
        self.last_board_state = new_board_state
        
        

    

    def capture_and_get_move(self):
        '''Captures the current board state and calculates the played move. Also updates last board state'''


        new_board_state = self.load_img(f"Slike/Chessboard{self.game_index}.jpg")
        self.game_index += 1
        if self.game_index == 33:
            print("Game positions exausted, stopping execution")
            sys.exit()
        
        game_old = self.geometric_rectification(self.last_board_state, params=self.params)
        self.last_board_state = new_board_state

        game_new = self.geometric_rectification(new_board_state, params=self.params)

        move = self.get_move(game_new, game_old)

        return move
    

    






if __name__ == '__main__':

    vision = Chessvision()

    ref = vision.load_img("Slike/Chessboard37.jpg")
    params = vision.geometric_rectification(ref, getParams=True)
    corners = vision.geometric_rectification(ref, getRectifiedCorners=True)

    game20 = vision.load_img('Slike/Chessboard20.jpg')
    game21 = vision.load_img('Slike/Chessboard21.jpg')

    game20_new = vision.geometric_rectification(game20, params=params)
    game21_new = vision.geometric_rectification(game21, params=params)

    diff = np.abs(vision.img_diff(game20_new, game21_new))
    diff_2 = vision.img_diff_filtered(game20_new, game21_new)
    diff_3 = vision.img_diff_filtered_V2(game20_new, game21_new)
    vision.showimg(diff  , show=True)
    vision.showimg(diff_2, show=True)
    vision.showimg(diff_3, show=True)
    

    




