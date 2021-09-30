from io import BytesIO
from flask import Flask, request, redirect, make_response, send_file
from pyboy import PyBoy, WindowEvent

pyboy = PyBoy("red.gb", window_type="headless", window_scale=3, debug=True, game_wrapper=True)
pyboy.set_emulation_speed(0)

print("starting emulator...")
for _ in range(60 * 100):
    pyboy.tick()

app = Flask(__name__)

KEYMAP = {
    'A': (WindowEvent.PRESS_BUTTON_A, WindowEvent.RELEASE_BUTTON_A),
    'B': (WindowEvent.PRESS_BUTTON_B, WindowEvent.RELEASE_BUTTON_B),
    'START': (WindowEvent.PRESS_BUTTON_START, WindowEvent.RELEASE_BUTTON_START),
    'SELECT': (WindowEvent.PRESS_BUTTON_SELECT, WindowEvent.RELEASE_BUTTON_SELECT),
    'UP': (WindowEvent.PRESS_ARROW_UP, WindowEvent.RELEASE_ARROW_UP),
    'DOWN': (WindowEvent.PRESS_ARROW_DOWN, WindowEvent.RELEASE_ARROW_DOWN),
    'LEFT': (WindowEvent.PRESS_ARROW_LEFT, WindowEvent.RELEASE_ARROW_LEFT),
    'RIGHT': (WindowEvent.PRESS_ARROW_RIGHT, WindowEvent.RELEASE_ARROW_RIGHT),
}

def advance_game(key):
    press, release = KEYMAP[key]
    pyboy.send_input(press)
    # hold it for 10 frames
    for _ in range(10):
        pyboy.tick()
    pyboy.send_input(release)
    # tap button and wait 5s
    for frame in range(60*5-10):
        pyboy.tick()

@app.route('/input/<key>')
def do_input(key):
    if key in KEYMAP:
        advance_game(key)
        return redirect("https://github.com/arxenix", code=302)
    else:
        return "invalid key", 400

@app.route('/game')
def game():
    pil_img = pyboy.screen_image()
    img_io = BytesIO()
    pil_img.save(img_io, 'PNG')
    img_io.seek(0)

    response = make_response(send_file(img_io, mimetype='image/png'))
    response.headers['Cache-Control'] = 'private, max-age=0, no-cache'
    return response

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000)
