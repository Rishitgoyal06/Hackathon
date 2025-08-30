from flask import *

app = Flask(__name__)

def increase_Attendance(slots_attended, total_slots, aim):
    temp_attended = slots_attended
    temp_total = total_slots
    count = 0

    while True:
        temp_attended += 1
        temp_total += 1
        count += 1
        attendance = (temp_attended / temp_total) * 100
        
        if attendance >= aim:
            break
    
    return {"message": f"Attend {count} more lectures to reach {aim}% attendance."}


def decrease_Attendance(slots_attended, total_slots, aim):
    temp_attended = slots_attended
    temp_total = total_slots
    count = 0

    while True:
        temp_total += 1
        count += 1
        attendance = (temp_attended / temp_total) * 100
        
        if attendance < aim:
            break
    
    return {"message": f"You can bunk {count - 1} lectures and still maintain at least {aim}% attendance."}


@app.route('/attendance', methods=['POST'])
def attendance():
    data = request.json
    
    total_slots = data.get("total_slots")
    slots_attended = data.get("slots_attended")
    aim = data.get("aim")
    
    if total_slots <= 0 or slots_attended < 0 or slots_attended > total_slots or aim <= 0:
        return jsonify({"error": "Invalid input values"}), 400
    
    current_attendance = (slots_attended / total_slots) * 100
    
    if current_attendance > aim:
        result = decrease_Attendance(slots_attended, total_slots, aim)
    elif current_attendance < aim:
        result = increase_Attendance(slots_attended, total_slots, aim)
    else:
        result = {"message": "You're exactly at your aim. Keep attending regularly."}
    
    return jsonify({
        "current_attendance": round(current_attendance, 2),
        "result": result
    })


if __name__ == '__main__':
    app.run(debug=True)
