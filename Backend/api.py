from flask import Flask, request, session
from utilities import *

from PIL import Image
import io
import base64

app = Flask(__name__)
app.secret_key = "hello"

#GLOBAL VARIABLES

def bytes_to_img(raw_data):
    b = bytes(raw_data, 'utf-8')
    image = b[b.find(b'/9'):]
    im = Image.open(io.BytesIO(base64.b64decode(image)))
    cv_img = np.array(im.convert('RGB'))
    cv_img = cv_img[:, :, ::-1].copy()
    return cv_img


@app.route('/api', methods=['GET', 'POST'])
def api():
    session.clear()
    print(request.method)
    #print(request.get_data())
    if request.method == "POST":

        data = request.get_json(force=True)
        result = data['data']
        b = bytes(result, 'utf-8')
        image = b[b.find(b'/9'):]
        im = Image.open(io.BytesIO(base64.b64decode(image)))
        #im.save('testing.jpg')

        cv_img = np.array(im.convert('RGB'))
        cv_img = cv_img[:,:,::-1].copy()
        #cv2.imwrite('testing2.jpg', cv_img)

        return {
            "data": str(request.get_json())
        }
    else:
        return{
            "status":"App has started"
        }


@app.route('/calibrate', methods = ['GET', 'POST'])
def calibrate():
    if request.method == 'POST':
        data = request.get_json(force=True)
        result = data['data']
        img_to_calibrate = bytes_to_img(result)

        session['cur_turn'] = 2
        session['position'] = 'rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1'
        session['board_array'] = [[2, 2, 2, 2, 2, 2, 2, 2],
                                  [2, 2, 2, 2, 2, 2, 2, 2],
                                  [0, 0, 0, 0, 0, 0, 0, 0],
                                  [0, 0, 0, 0, 0, 0, 0, 0],
                                  [0, 0, 0, 0, 0, 0, 0, 0],
                                  [0, 0, 0, 0, 0, 0, 0, 0],
                                  [1, 1, 1, 1, 1, 1, 1, 1],
                                  [1, 1, 1, 1, 1, 1, 1, 1]]
        if 'board_corners' in session:
            print("step 1")
            tmp_board_array = get_predictions(img_to_calibrate, np.array(session['board_corners']), '0')
            print("step 2")
            session['orientation'] = '-1'
            print("step 3")
            if tmp_board_array[0][4] == 2:
                session['orientation'] = '0'
            if tmp_board_array[4][7] == 2:
                session['orientation'] = '3'
            if tmp_board_array[7][4] == 2:
                session['orientation'] = '2'
            if tmp_board_array[4][0] == 2:
                session['orientation'] = '1'
            print(session['orientation'])
            if(session['orientation'] == '-1'):
                return{
                    'status': 'ERR',
                    'message': 'board not set up correctly',
                }

            cv2.imwrite('debug.jpg', rotate(crop_board(img_to_calibrate, np.array(session['board_corners'])), session['orientation']))
            return {
                'status': 'CALIBRATION_COMPLETE',
                'message': 'Calibration complete. Play some moves!',
            }
        else:
            print("calibrated")
            session['board_corners'] = find_board_corners(img_to_calibrate).tolist()
            #cv2.imwrite('debug.jpg', crop_board(img_to_calibrate, np.array(session['board_corners'])))
            return {
                'status': 'OK',
                'message': 'Next, press Calibrate again after setting up the board'
            }

        return {'status': 'idk what happened'}

@app.route('/make_move', methods = ['POST'])
def make_move():
    data = request.get_json(force=True)
    result = data['data']
    img = bytes_to_img(result)

    cur_chess_board = chess.Board(session['position'])
    cur_board_array = session['board_array']
    next_board_array = get_predictions(img, np.array(session['board_corners']), session['orientation'])
    start_pos, end_pos = get_move(cur_board_array, next_board_array, session['cur_turn'])

    if -1 in start_pos or -1 in end_pos:
        print("MOVE ERROR")
        print(next_board_array)
        return {
            'status': 'ERR',
            'message': 'there was an error in your move'
        }

    move = "{}{}{}{}".format(char_coords[start_pos[1]], start_pos[0] + 1, char_coords[end_pos[1]], end_pos[0] + 1)

    #handle promotion
    promote_to = data['promotionPiece']
    print(move[3])
    print(move[0:2])
    #print(cur_chess_board.piece_at(chess.square_name(move[0:2])))
    if (move[3] == '8' or move[3] == '1') and (cur_chess_board.piece_at(chess.parse_square(move[0:2])) == chess.Piece.from_symbol('p')
                                           or cur_chess_board.piece_at(chess.parse_square(move[0:2])) == chess.Piece.from_symbol('P')):
        move += promote_to

    print(move)
    if not chess.Move.from_uci(move) in cur_chess_board.legal_moves:
        print("MOVE ERROR")
        return {
            'status': 'ERR',
            'message': 'illegal move'
        }
    cur_move = cur_chess_board.san(chess.Move.from_uci(move))
    cur_chess_board.push(chess.Move.from_uci(move))
    print(cur_chess_board)

    game_result = 'PLAYING'
    if cur_chess_board.is_checkmate():
        if session['cur_turn'] == 2:
            game_result = 'WHITE_WIN'
        else:
            game_result = 'BLACK_WIN'

    if cur_chess_board.is_stalemate():
        game_result = 'DRAW'



    session['board_array'] = next_board_array
    session['position'] = cur_chess_board.fen()
    if session['cur_turn'] == 2:
        session['cur_turn'] = 1
    elif session['cur_turn'] == 1:
        session['cur_turn'] = 2


    return {'status': 'OK',
            'message': 'the move was successfully processed',
            'position': session['position'],
            'move': cur_move,
            'game_result': game_result,
    }


app.run(debug=True)

#TODO:
# 1. add promotion
# 2. handle checkmate
# 3. restart button