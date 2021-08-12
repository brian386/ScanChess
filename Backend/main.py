from utilities import *
#---------------------------------MAIN-------------------------------------

#calibration
capture = cv2.VideoCapture(0)

while True:
    ret, calibrate_img = capture.read()
    cv2.imshow('test',calibrate_img)
    if cv2.waitKey(20) & 0xFF == ord('d'):
        break

corners = find_board_corners(calibrate_img)
cv2.destroyAllWindows()

while True:
    isTrue, frame = capture.read()
    cv2.imshow('window', crop_board(frame, corners))
    if cv2.waitKey(20) & 0xFF==ord('d'):
        break
cv2.destroyAllWindows()
#get orientation

capture = cv2.VideoCapture(0)
ret,frame = capture.read()
img = crop_board(frame,corners)
cells = get_cells(img)

board = [[None for i in range(8)] for j in range(8)]

for i in range(8):
    for j in range(8):
        cells[i][j] = cv2.resize(cells[i][j], (IMG_SIZE,IMG_SIZE))
        prediction = model.predict([cells[i][j].reshape(-1,IMG_SIZE,IMG_SIZE,3)])
        board[i][j] = prediction.argmax()

print(board)

if board[4][7] == 2:
    orientation = '3'
if board[7][4] == 2:
    orientation = '2'
if board[4][0] == 2:
    orientation = '1'

while True:
    isTrue, frame = capture.read()
    frame = crop_board(frame,corners)
    frame = rotate(frame, orientation)
    cv2.imshow('Video', frame)
    if cv2.waitKey(20) & 0xFF==ord('d'):
        break
cv2.destroyAllWindows()

chess_board = chess.Board()
board = [[None for i in range(8)] for j in range(8)]
is_first_turn = True
cur_turn = 1
while True:
    cv2.waitKey(0)
    ret, frame = capture.read()

    next_board = get_predictions(frame,corners,orientation)

    print(next_board)

    if not is_first_turn:
        start_pos, end_pos = get_move(board, next_board,cur_turn)

        if -1 in start_pos or -1 in end_pos:
            print("MOVE ERROR")
            continue

        move = "{}{}{}{}".format(char_coords[start_pos[1]], start_pos[0]+1, char_coords[end_pos[1]], end_pos[0]+1)
        print(move)
        if (not chess.Move.from_uci(move) in chess_board.legal_moves):
            print("MOVE ERROR")
            continue

        chess_board.push(chess.Move.from_uci(move))
        print(chess_board)

    board = next_board
    if cur_turn == 2:
        cur_turn = 1
    elif cur_turn == 1:
        cur_turn = 2
    is_first_turn = False
