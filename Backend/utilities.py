import cv2
import numpy as np
import tensorflow as tf
import chess

###############################################
HEIGHT = 560
WIDTH = 560
IMG_SIZE = 70
orientation = '0'
model = tf.keras.models.load_model('chess_model_v5')
# Model v1 works well. v4 also works but fails on bright images. v5 uses more bright images for training but
# sometimes misclassfies empty as white.

char_coords = {0: 'h', 1: 'g', 2: 'f', 3: 'e', 4: 'd', 5: 'c', 6: 'b', 7: 'a', -1: 'E'}


# White Piece: 2, Black Piece: 1, Empty: 0
#################################################


# --------------------------HELPERS----------------------------------------------
# preprocesses the image
def preprocess(img):
    img_gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    img_blur = cv2.GaussianBlur(img_gray, (3, 3), 1)
    img_threshold = cv2.adaptiveThreshold(img_blur, 255, 1, 1, 11, 2)
    return img_threshold


# reorders the corners of the chess board consistently (for warping)
def reorder(pts):
    pts = pts.reshape((4, 2))
    new_pts = np.zeros((4, 1, 2))
    sum = pts.sum(1)
    new_pts[0] = pts[np.argmin(sum)]
    new_pts[3] = pts[np.argmax(sum)]
    diff = np.diff(pts, axis=1)
    new_pts[1] = pts[np.argmin(diff)]
    new_pts[2] = pts[np.argmax(diff)]
    return new_pts


# finds the corners of the biggest contour given contours
def findBiggestContour(contours):
    pts = np.array([])
    max_area = 0
    for i in contours:
        area = cv2.contourArea(i)
        if area > 50:
            peri = cv2.arcLength(i, True)
            approx = cv2.approxPolyDP(i, 0.02 * peri, True)
            if area > max_area and len(approx) == 4:
                pts = approx
                max_area = area
    return reorder(pts), max_area


# finds the corners of the largest contour given an image
def find_board_corners(img):
    maxArea = 0
    processed_img = preprocess(img)
    contours, heirarchy = cv2.findContours(processed_img, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    biggest, maxArea = findBiggestContour(contours)
    return biggest


# returns a birds eye view of the cropped chess board given a raw image
def crop_board(img, corners):
    original_img = np.float32(corners)
    new_img = np.float32([[0, 0], [WIDTH, 0], [0, HEIGHT], [WIDTH, HEIGHT]])
    matrix = cv2.getPerspectiveTransform(original_img, new_img)
    imgWarpColored = cv2.warpPerspective(img, matrix, (WIDTH, HEIGHT))
    return imgWarpColored


# gets the 64 cells as images from a big chess board image assuming the chessboard is already processed and warped
def get_cells(img):
    rows = np.vsplit(img, 8)
    cells = [[], [], [], [], [], [], [], []]
    for r in range(8):
        cols = np.hsplit(rows[r], 8)
        for c in cols:
            cells[r].append(c)
    return cells


# rotates an image so that (0,0) corresponds to h1 square
def rotate(img, orientation):
    rotated_img = None
    if orientation == '0':
        rotated_img = img
    if orientation == '1':
        rotated_img = cv2.rotate(img, cv2.ROTATE_90_CLOCKWISE)
    if orientation == '2':
        rotated_img = cv2.rotate(img, cv2.ROTATE_180)
    if orientation == '3':
        rotated_img = cv2.rotate(img, cv2.ROTATE_90_COUNTERCLOCKWISE)
    return rotated_img


# returns a move as a string based on 2 2d arrays,
# one representing the current position and one representing the previous position (eg. "e2e4")
def get_move(board, next_board, turn):
    start_pos = []
    end_pos = []

    for i in range(8):
        for j in range(8):
            if next_board[i][j] == 0 and board[i][j] == turn:
                start_pos.append((i, j))
            if next_board[i][j] == turn and board[i][j] != turn:
                end_pos.append((i, j))

    if len(start_pos) == 1 and len(end_pos) == 1:
        # normal move
        return start_pos[0], end_pos[0]
    elif len(start_pos) == 2 and len(end_pos) == 2:
        # castling
        if ((0, 0) in start_pos) or ((7, 0) in start_pos):
            if turn == 2:
                return (0, 3), (0, 1)
            else:
                return (7, 3), (7, 1)
        elif ((0, 7) in start_pos) or ((7, 7) in start_pos):
            if turn == 2:
                return (0, 3), (0, 5)
            else:
                return (7, 3), (7, 5)
        else:
            return (-1, -1), (-1, -1)
    else:
        return (-1, -1), (-1, -1)


# returns a 2d array corresponding to the current position given an image
def get_predictions(frame, corners, orientation):
    img = crop_board(frame, corners)
    img = rotate(img, orientation)
    cells = get_cells(img)

    position = [[None for i in range(8)] for j in range(8)]
    for i in range(8):
        for j in range(8):
            cells[i][j] = cv2.resize(cells[i][j], (IMG_SIZE, IMG_SIZE))
            prediction = model.predict([cells[i][j].reshape(-1, IMG_SIZE, IMG_SIZE, 3)])
            position[i][j] = int(prediction.argmax())

    return position
