# virtual_painter.py  (main script)
import cv2 as cv
import numpy as np
import HandTracking
from datetime import datetime
from collections import deque

# ---------- Camera ----------
web_cam = cv.VideoCapture(0)
web_cam.set(3, 1280)
web_cam.set(4, 720)

# ---------- Hand tracking ----------
hand_tracking = HandTracking.HandTracking()

# ---------- State & config ----------
reset = {"up": True, "down": True, "peace": True, "pinch": True, "shape": True, "color_select": True}
color_selection_timer = 0
color_selection_threshold = 15  # frames to hover before selecting

colours = [(255, 0, 0), (0, 255, 0), (0, 0, 255), (255, 255, 0),
        (255, 0, 255), (0, 255, 255), (255, 128, 0), (128, 0, 255)]
colour_names = ["Blue", "Green", "Red", "Cyan", "Magenta", "Yellow", "Orange", "Purple"]
colour_index = 4  # start color
hand_tracking.draw_colour = colours[colour_index]  # ensure tracker color consistent

brush_sizes = [5, 10, 15, 25, 35, 50]
brush_index = 2
current_brush_size = brush_sizes[brush_index]

eraser_size = 20

x_prev, y_prev = 0, 0

canvas = np.zeros((720, 1280, 3), np.uint8)

canvas_history = deque(maxlen=50)
redo_stack = deque(maxlen=50)
canvas_history.append(canvas.copy())

shape_mode = False
shape_start = None
shape_types = ["Circle", "Rectangle", "Line", "Triangle"]
current_shape = 0
drawing_shape = False  # boolean: shape is being drawn (in progress)

position_buffer = deque(maxlen=3)  # smoothing

# ---------- Helpers ----------
def draw_ui(img, hovering_color_index=-1, selection_progress=0):
    overlay = img.copy()
    cv.rectangle(overlay, (0, 0), (1280, 100), (50, 50, 50), -1)
    cv.addWeighted(overlay, 0.7, img, 0.3, 0, img)

    color_size = 60
    padding = 10
    start_x = 20

    for i, color in enumerate(colours):
        x = start_x + i * (color_size + padding)
        y = 20
        cv.rectangle(img, (x, y), (x + color_size, y + color_size), color, -1)
        cv.rectangle(img, (x, y), (x + color_size, y + color_size), (255, 255, 255), 2)

        if i == colour_index:
            cv.rectangle(img, (x-5, y-5), (x + color_size+5, y + color_size+5), (0, 255, 0), 4)
        if i == hovering_color_index:
            cv.rectangle(img, (x-3, y-3), (x + color_size+3, y + color_size+3), (255, 255, 0), 3)
            if selection_progress > 0:
                bar_width = int((color_size * selection_progress) / color_selection_threshold)
                cv.rectangle(img, (x, y + color_size + 5), (x + bar_width, y + color_size + 10), (0, 255, 0), -1)

    tool_text = f"Color: {colour_names[colour_index]} | Brush: {current_brush_size}px"
    cv.putText(img, tool_text, (750, 40), cv.FONT_HERSHEY_SIMPLEX, 0.8, (255, 255, 255), 2)

    if shape_mode:
        mode_text = f"SHAPE MODE: {shape_types[current_shape]}"
        cv.putText(img, mode_text, (750, 70), cv.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 255), 2)

    instructions = [
        "1 finger: Draw | Fist: Erase | Peace: Clear | Hover on colors to select",
        "Thumbs Up/Down: Change Color | Pinch: Brush Size",
        "3 fingers: Shape Mode | Press 'S': Save | 'Z': Undo | 'Y': Redo | 'Q': Quit"
    ]
    y = 680
    for ins in instructions:
        cv.putText(img, ins, (10, y), cv.FONT_HERSHEY_SIMPLEX, 0.5, (200,200,200), 1)
        y += 20

def save_canvas():
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"drawing_{ts}.png"
    cv.imwrite(filename, canvas)
    print("Saved:", filename)
    return filename

def clear_canvas():
    global canvas
    canvas_history.append(canvas.copy())
    redo_stack.clear()
    canvas[:] = 0  # fill with zeros

def undo():
    global canvas
    if len(canvas_history) > 1:
        redo_stack.append(canvas.copy())
        canvas_history.pop()
        canvas[:] = canvas_history[-1].copy()

def redo():
    global canvas
    if len(redo_stack) > 0:
        canvas_history.append(canvas.copy())
        canvas[:] = redo_stack.pop().copy()

def save_state():
    canvas_history.append(canvas.copy())
    redo_stack.clear()

def smooth_position(x, y):
    position_buffer.append((x, y))
    # moving average (works even when buffer length is small)
    n = len(position_buffer)
    avg_x = int(sum(p[0] for p in position_buffer) / n)
    avg_y = int(sum(p[1] for p in position_buffer) / n)
    return avg_x, avg_y

def check_color_palette_hover(x, y):
    color_size = 60
    padding = 10
    start_x = 20
    y_top = 20
    y_bottom = 80
    if y < y_top or y > y_bottom:
        return -1
    for i in range(len(colours)):
        x_left = start_x + i * (color_size + padding)
        x_right = x_left + color_size
        if x_left <= x <= x_right:
            return i
    return -1

def draw_shape(img_preview, canvas_img, start, end, shape_type, color, thickness):
    """Draw preview shape on img_preview and commit shape on canvas_img inside same call (if desired)."""
    if shape_type == 0:  # circle
        center = start
        radius = int(np.hypot(end[0]-start[0], end[1]-start[1]))
        cv.circle(img_preview, center, radius, color, thickness)
        # do not commit to canvas here for preview; commit when finalizing
        cv.circle(canvas_img, center, radius, color, thickness)
    elif shape_type == 1:  # rectangle
        cv.rectangle(img_preview, start, end, color, thickness)
        cv.rectangle(canvas_img, start, end, color, thickness)
    elif shape_type == 2:  # line
        cv.line(img_preview, start, end, color, thickness)
        cv.line(canvas_img, start, end, color, thickness)
    elif shape_type == 3:  # triangle approximation
        mid_x = (start[0] + end[0]) // 2
        height = abs(end[1] - start[1])
        # Build triangle points (simple)
        third_point = (mid_x, start[1] - height if end[1] < start[1] else start[1] + height)
        points = np.array([start, end, third_point])
        cv.polylines(img_preview, [points], True, color, thickness)
        cv.polylines(canvas_img, [points], True, color, thickness)

# ---------- Main loop ----------
print("Starting Virtual Painter...")
print("Controls: S Save | Z Undo | Y Redo | C Clear | Q Quit")

hovering_color_index = -1

while True:
    success, img = web_cam.read()
    if not success:
        print("Camera read failed")
        break

    img = cv.flip(img, 1)  # mirror for intuitive drawing
    img = hand_tracking.find_hands(img)
    landmarks = hand_tracking.get_location(img, draw=True)

    if len(landmarks) != 0:
        x_index, y_index = landmarks[8][1], landmarks[8][2]
        x_smooth, y_smooth = smooth_position(x_index, y_index)

        hovering_color_index = check_color_palette_hover(x_index, y_index)

        # color selection by hover (requires drawing pose to avoid accidental picks)
        if hovering_color_index != -1 and hand_tracking.drawing():
            color_selection_timer += 1
            if color_selection_timer >= color_selection_threshold:
                colour_index = hovering_color_index
                hand_tracking.draw_colour = colours[colour_index]
                print("Color selected:", colour_names[colour_index])
                color_selection_timer = 0
                reset["color_select"] = False
        else:
            color_selection_timer = 0

        # peace sign -> clear canvas
        if hand_tracking.is_peace_sign() and reset["peace"]:
            save_state()
            clear_canvas()
            reset["peace"] = False
            print("Canvas cleared!")

        # toggle shape mode with 3-finger gesture
        elif hand_tracking.is_shape_mode() and reset["shape"]:
            shape_mode = not shape_mode
            if shape_mode:
                current_shape = (current_shape + 1) % len(shape_types)
                print("Shape mode ON:", shape_types[current_shape])
            else:
                print("Shape mode OFF")
            reset["shape"] = False
            shape_start = None
            drawing_shape = False

        # drawing (index finger) and not selecting color
        elif hand_tracking.drawing() and hovering_color_index == -1:
            # shape drawing
            if shape_mode:
                if not drawing_shape:
                    shape_start = (x_smooth, y_smooth)
                    drawing_shape = True
                    save_state()
                else:
                    # preview shape on a temp image (do not commit yet)
                    temp_img = img.copy()
                    temp_canvas = canvas.copy()
                    # draw preview only on temp_img; commit to temp_canvas for consistency
                    draw_shape(temp_img, temp_canvas, shape_start, (x_smooth, y_smooth),
                               current_shape, hand_tracking.draw_colour, current_brush_size)
                    img = temp_img
            else:
                # normal drawing with brush
                if x_prev == 0 and y_prev == 0:
                    x_prev, y_prev = x_smooth, y_smooth
                    save_state()
                cv.line(img, (x_prev, y_prev), (x_smooth, y_smooth), hand_tracking.draw_colour, current_brush_size)
                cv.line(canvas, (x_prev, y_prev), (x_smooth, y_smooth), hand_tracking.draw_colour, current_brush_size)
                x_prev, y_prev = x_smooth, y_smooth

        # if currently drawing a shape and user stops the drawing gesture, finalize it
        elif drawing_shape and not hand_tracking.drawing():
            # commit final shape to canvas
            draw_shape(img, canvas, shape_start, (x_smooth, y_smooth),
                       current_shape, hand_tracking.draw_colour, current_brush_size)
            drawing_shape = False
            shape_start = None
            x_prev, y_prev = 0, 0
            position_buffer.clear()

        # eraser when fist is detected
        elif hand_tracking.is_fist():
            if x_prev == 0 and y_prev == 0:
                x_prev, y_prev = x_smooth, y_smooth
                save_state()
            # draw thick black circle on canvas to erase
            cv.circle(img, (x_smooth, y_smooth), eraser_size, (0,0,0), -1)
            cv.circle(canvas, (x_smooth, y_smooth), eraser_size, (0,0,0), -1)
            x_prev, y_prev = x_smooth, y_smooth

        # pinch to set brush size (only once per pinch event)
        elif hand_tracking.is_pinching() and reset["pinch"]:
            distance = hand_tracking.get_pinch_distance()
            # map distance to brush index; clip & convert to int
            idx = int(np.clip((distance - 20) / 25, 0, len(brush_sizes)-1))
            brush_index = idx
            current_brush_size = brush_sizes[brush_index]
            print("Brush size:", current_brush_size)
            reset["pinch"] = False

        # thumbs up -> next color
        elif hand_tracking.is_thumbs_up() and reset["up"] and colour_index < len(colours)-1:
            colour_index += 1
            hand_tracking.draw_colour = colours[colour_index]
            print("Color:", colour_names[colour_index])
            reset["up"] = False

        # thumbs down -> previous color
        elif hand_tracking.is_thumbs_down() and reset["down"] and colour_index > 0:
            colour_index -= 1
            hand_tracking.draw_colour = colours[colour_index]
            print("Color:", colour_names[colour_index])
            reset["down"] = False

        else:
            # update prev pos if not drawing
            x_prev, y_prev = 0, 0
            position_buffer.clear()

    else:
        # no hand detected -> reset one-shot gesture flags
        reset = {k: True for k in reset}
        x_prev, y_prev = 0, 0
        position_buffer.clear()
        color_selection_timer = 0
        hovering_color_index = -1
        if drawing_shape:
            drawing_shape = False
            shape_start = None

    # merge canvas with frame (create mask & combine)
    img_gray = cv.cvtColor(canvas, cv.COLOR_BGR2GRAY)
    _, mask = cv.threshold(img_gray, 10, 255, cv.THRESH_BINARY)
    mask_inv = cv.bitwise_not(mask)
    mask_rgb = cv.cvtColor(mask_inv, cv.COLOR_GRAY2BGR)  # areas to keep from frame
    img = cv.bitwise_and(img, mask_rgb)
    img = cv.bitwise_or(img, canvas)

    draw_ui(img, hovering_color_index, color_selection_timer)

    cv.imshow(" Virtual Painter", img)

    key = cv.waitKey(1) & 0xFF
    if key == ord('s'):
        fname = save_canvas()
        # quick confirmation overlay
        tmp = img.copy()
        cv.putText(tmp, f"Saved: {fname}", (400, 360), cv.FONT_HERSHEY_SIMPLEX, 1, (0,255,0), 3)
        cv.imshow("AI Virtual Painter", tmp)
        cv.waitKey(500)
    elif key == ord('z'):
        undo(); print("Undo")
    elif key == ord('y'):
        redo(); print("Redo")
    elif key == ord('c'):
        save_state(); clear_canvas(); print("Cleared")
    elif key == ord('q'):
        print("Exiting...")
        break

web_cam.release()
cv.destroyAllWindows()
