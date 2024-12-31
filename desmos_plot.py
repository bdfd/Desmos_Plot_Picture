import os
import cv2
import re


folder_path = os.getcwd()
for filename in os.listdir(folder_path):
    file_path = os.path.join(folder_path, filename)
    if os.path.isfile(file_path) and (filename.lower().endswith('.jpg') or filename.lower().endswith('.jpeg') or filename.lower().endswith('.png')):
        frame = cv2.imread(file_path)
        blurred_image = cv2.GaussianBlur(frame, (3, 3), 1.5)

        low_threshold = 100
        high_threshold = 150

        gray_image = cv2.cvtColor(blurred_image, cv2.COLOR_BGR2GRAY)
        edges = cv2.Canny(gray_image, low_threshold, high_threshold)
        cv2.imwrite("temp.jpg", edges)


jpg = os.path.join(folder_path, "temp.jpg")
pnm = os.path.join(folder_path, "temp.pnm")
svg = os.path.join(folder_path, "temp.svg")
os.system(f'magick "{jpg}" "{pnm}"')
os.system(f'potrace "{pnm}" -s -o "{svg}"')


def write_js(filename):
    max_x = 0
    max_y = 0
    svg_file_path = filename
    with open(svg_file_path, 'r', encoding='utf-8') as file:
        pic = file.read()

    pattern = r'<path d="'
    match = re.search(pattern, pic)

    if match:
        pic = pic[match.end():-16]

    remove = re.sub('''"/>
<path d="''', "", pic)
    components = re.findall(r'-?\d+\.\d+|-?\d+|[a-zA-Z]', remove)
    list = components
    newlist = [10, 10, 10, 10, 10, 10, 10]

    for i in range(len(list)):

        if newlist[-3] == 'l':
            if list[i].isalpha() == False:
                newlist.append('l')
        if newlist[-7] == 'c':
            if list[i].isalpha() == False:
                newlist.append('c')
        newlist.append(list[i])


    desmos_string = ''''''

    list = newlist[7:]
    last_x = 0
    last_y = 0
    start_x = 0
    start_y = 0
    for i in range(len(list)):
        if list[i] == 'M':
            start_x = int(list[i + 1])
            start_y = int(list[i + 2])
            last_x = int(list[i + 1])
            last_y = int(list[i + 2])
        if list[i] == 'm':
            start_x = int(list[i + 1]) + last_x
            start_y = int(list[i + 2]) + last_y
            last_x = start_x
            last_y = start_y
        if list[i] == 'l':
            new_x = int(list[i + 1]) + last_x
            new_y = int(list[i + 2]) + last_y
            desmos_string += f'''calculator.setExpression({{latex: '({str(last_x)}, {str(last_y)})*(1-t)+({str(new_x)}, {str(new_y)})*t' }});
'''
            last_x = new_x
            last_y = new_y
        if list[i] == 'c':
            c_1 = (last_x, last_y)
            c_2 = (int(list[i + 1]) + last_x, int(list[i + 2]) + last_y)
            c_3 = (int(list[i + 3]) + last_x, int(list[i + 4]) + last_y)
            c_4 = (int(list[i + 5]) + last_x, int(list[i + 6]) + last_y)
            desmos_string += f'''calculator.setExpression({{latex: '({str(c_1[0])}, {str(c_1[1])})*(1-t)^3+3*({str(c_2[0])}, {str(c_2[1])})*(1-t)^2*t+3*({str(c_3[0])}, {str(c_3[1])})*(1-t)*t^2+({str(c_4[0])}, {str(c_4[1])})*t^3' }});
'''
            last_x = c_4[0]
            last_y = c_4[1]

        if list[i] == 'z':
            last_x = start_x
            last_y = start_y

        if last_x > max_x:
            max_x = last_x
        if last_y > max_y:
            max_y = last_y


    if max_x/max_y>1.436:
        max_x, max_y = max_x, max_x/1.436
    else:
        max_x, max_y = max_y*1.436, max_y

    max_x, max_y = round(max_x), round(max_y)


    js_string = f'''var elt = document.getElementById('calculator');
var calculator = Desmos.GraphingCalculator(elt, {{
    showGrid: false, 
    showXAxis: false, 
    showYAxis: false, 
    zoomButtons: false, 
    settingsMenu: false,
    expressionsTopbar: false, 
    keypad: false
}});

{desmos_string}
var t = calculator.HelperExpression({{latex: 't'}});
state=calculator.getState();
for (i=0;i<state.expressions.list.length;i++) {{
    state.expressions.list[i].color="#000000"
}}
calculator.setState(state);
calculator.setMathBounds({{
  left: 0,
  bottom: 0,
  right: {max_x},
  top: {max_y}
}});
'''


    with open("desmos_api.js", "w") as js_file:
        js_file.write(js_string)


write_js(f"temp.svg")
os.system(f'rm "{jpg}"')
os.system(f'rm "{pnm}"')
os.system(f'rm "{svg}"')

